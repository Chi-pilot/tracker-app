import dataclasses
import os
import sqlite3
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import requests
from flask import Flask, flash, jsonify, redirect, render_template, request, url_for

DATABASE_FILE = Path("flight_log.db")
BASE_API_URL = "https://airportgap.com/api"
AIRPORTGAP_TOKEN = os.environ.get("AIRPORTGAP_TOKEN")

app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key")


@dataclasses.dataclass
class FlightLeg:
    leg_number: int
    departure: str
    arrival: str
    distance_miles: float
    is_cross_country: bool
    departure_name: Optional[str] = None
    departure_city: Optional[str] = None
    departure_state: Optional[str] = None
    departure_country: Optional[str] = None
    arrival_name: Optional[str] = None
    arrival_city: Optional[str] = None
    arrival_state: Optional[str] = None
    arrival_country: Optional[str] = None


@dataclasses.dataclass
class FlightEntry:
    id: int
    date: str
    aircraft_make_model: str
    registration: str
    total_time: float
    pic_time: float
    solo_time: float
    dual_received_time: float
    day_landings: int
    night_landings: int
    cross_country_hours: float
    total_distance_miles: float
    is_cross_country: bool
    notes: Optional[str] = ""
    legs: List[FlightLeg] = dataclasses.field(default_factory=list)
    created_at: Optional[str] = None


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_db()
    with conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS flights (
                id INTEGER PRIMARY KEY,
                date TEXT NOT NULL,
                aircraft_make_model TEXT NOT NULL,
                registration TEXT NOT NULL,
                total_time REAL NOT NULL,
                pic_time REAL NOT NULL,
                solo_time REAL NOT NULL,
                dual_received_time REAL NOT NULL,
                day_landings INTEGER NOT NULL,
                night_landings INTEGER NOT NULL,
                cross_country_hours REAL NOT NULL,
                total_distance_miles REAL NOT NULL,
                is_cross_country INTEGER NOT NULL,
                notes TEXT,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS legs (
                id INTEGER PRIMARY KEY,
                flight_id INTEGER NOT NULL,
                leg_number INTEGER NOT NULL,
                departure TEXT NOT NULL,
                arrival TEXT NOT NULL,
                distance_miles REAL NOT NULL,
                is_cross_country INTEGER NOT NULL,
                departure_name TEXT,
                departure_city TEXT,
                departure_state TEXT,
                departure_country TEXT,
                arrival_name TEXT,
                arrival_city TEXT,
                arrival_state TEXT,
                arrival_country TEXT,
                FOREIGN KEY(flight_id) REFERENCES flights(id)
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_legs_flight_id ON legs(flight_id)")
    conn.close()


def normalize_airport_code(value: Optional[str]) -> str:
    return value.strip().upper() if value else ""


def api_headers() -> Dict[str, str]:
    headers: Dict[str, str] = {}
    if AIRPORTGAP_TOKEN:
        headers["Authorization"] = f"Bearer token={AIRPORTGAP_TOKEN}"
    return headers


def get_airport_distance(departure: str, arrival: str) -> float:
    payload = {"from": departure, "to": arrival}
    response = requests.post(
        f"{BASE_API_URL}/airports/distance",
        data=payload,
        headers=api_headers(),
        timeout=15,
    )
    response.raise_for_status()
    body = response.json()
    return float(body["data"]["attributes"]["miles"])


def get_airport_metadata(code: str) -> Dict[str, Optional[str]]:
    result: Dict[str, Optional[str]] = {}
    try:
        response = requests.get(
            f"{BASE_API_URL}/airports/{code}",
            headers=api_headers(),
            timeout=15,
        )
        response.raise_for_status()
        attributes = response.json()["data"]["attributes"]
        result = {
            "name": attributes.get("name"),
            "city": attributes.get("city"),
            "state": attributes.get("state") or attributes.get("region"),
            "country": attributes.get("country"),
        }
    except requests.RequestException:
        pass
    return result


def build_leg(leg_number: int, departure: str, arrival: str) -> FlightLeg:
    distance = get_airport_distance(departure, arrival)
    departure_meta = get_airport_metadata(departure)
    arrival_meta = get_airport_metadata(arrival)
    return FlightLeg(
        leg_number=leg_number,
        departure=departure,
        arrival=arrival,
        distance_miles=distance,
        is_cross_country=distance > 50,
        departure_name=departure_meta.get("name"),
        departure_city=departure_meta.get("city"),
        departure_state=departure_meta.get("state"),
        departure_country=departure_meta.get("country"),
        arrival_name=arrival_meta.get("name"),
        arrival_city=arrival_meta.get("city"),
        arrival_state=arrival_meta.get("state"),
        arrival_country=arrival_meta.get("country"),
    )


def save_flight(entry: FlightEntry) -> None:
    conn = get_db()
    with conn:
        cursor = conn.execute(
            """
            INSERT INTO flights (
                date,
                aircraft_make_model,
                registration,
                total_time,
                pic_time,
                solo_time,
                dual_received_time,
                day_landings,
                night_landings,
                cross_country_hours,
                total_distance_miles,
                is_cross_country,
                notes,
                created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                entry.date,
                entry.aircraft_make_model,
                entry.registration,
                entry.total_time,
                entry.pic_time,
                entry.solo_time,
                entry.dual_received_time,
                entry.day_landings,
                entry.night_landings,
                entry.cross_country_hours,
                entry.total_distance_miles,
                int(entry.is_cross_country),
                entry.notes,
                datetime.utcnow().isoformat(),
            ),
        )
        flight_id = cursor.lastrowid
        for leg in entry.legs:
            conn.execute(
                """
                INSERT INTO legs (
                    flight_id,
                    leg_number,
                    departure,
                    arrival,
                    distance_miles,
                    is_cross_country,
                    departure_name,
                    departure_city,
                    departure_state,
                    departure_country,
                    arrival_name,
                    arrival_city,
                    arrival_state,
                    arrival_country
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    flight_id,
                    leg.leg_number,
                    leg.departure,
                    leg.arrival,
                    leg.distance_miles,
                    int(leg.is_cross_country),
                    leg.departure_name,
                    leg.departure_city,
                    leg.departure_state,
                    leg.departure_country,
                    leg.arrival_name,
                    leg.arrival_city,
                    leg.arrival_state,
                    leg.arrival_country,
                ),
            )
    conn.close()


def load_entries() -> List[FlightEntry]:
    conn = get_db()
    flights_rows = conn.execute(
        "SELECT * FROM flights ORDER BY date DESC, created_at DESC"
    ).fetchall()
    legs_rows = conn.execute(
        "SELECT * FROM legs ORDER BY flight_id, leg_number"
    ).fetchall()
    conn.close()

    legs_by_flight: Dict[int, List[FlightLeg]] = {}
    for row in legs_rows:
        flight_id = row["flight_id"]
        legs_by_flight.setdefault(flight_id, []).append(
            FlightLeg(
                leg_number=row["leg_number"],
                departure=row["departure"],
                arrival=row["arrival"],
                distance_miles=row["distance_miles"],
                is_cross_country=bool(row["is_cross_country"]),
                departure_name=row["departure_name"],
                departure_city=row["departure_city"],
                departure_state=row["departure_state"],
                departure_country=row["departure_country"],
                arrival_name=row["arrival_name"],
                arrival_city=row["arrival_city"],
                arrival_state=row["arrival_state"],
                arrival_country=row["arrival_country"],
            )
        )

    return [
        FlightEntry(
            id=row["id"],
            date=row["date"],
            aircraft_make_model=row["aircraft_make_model"],
            registration=row["registration"],
            total_time=row["total_time"],
            pic_time=row["pic_time"],
            solo_time=row["solo_time"],
            dual_received_time=row["dual_received_time"],
            day_landings=row["day_landings"],
            night_landings=row["night_landings"],
            cross_country_hours=row["cross_country_hours"],
            total_distance_miles=row["total_distance_miles"],
            is_cross_country=bool(row["is_cross_country"]),
            notes=row["notes"],
            legs=legs_by_flight.get(row["id"], []),
            created_at=row["created_at"],
        )
        for row in flights_rows
    ]


def month_to_range(month_value: str) -> Tuple[str, str]:
    year_str, month_str = month_value.split("-")
    year = int(year_str)
    month = int(month_str)
    start = date(year, month, 1)
    if month == 12:
        end = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end = date(year, month + 1, 1) - timedelta(days=1)
    return start.isoformat(), end.isoformat()


def search_flights(query: str, start_month: str, end_month: str) -> List[FlightEntry]:
    conn = get_db()
    params: List[Any] = []
    conditions: List[str] = []
    base_query = "SELECT DISTINCT f.* FROM flights f LEFT JOIN legs l ON l.flight_id = f.id"

    normalized_query = query.strip().upper()
    if normalized_query:
        like_query = f"%{normalized_query}%"
        conditions.append(
            "(" +
            " OR ".join(
                [
                    "upper(f.aircraft_make_model) LIKE ?",
                    "upper(f.registration) LIKE ?",
                    "upper(l.departure) LIKE ?",
                    "upper(l.arrival) LIKE ?",
                    "upper(l.departure_name) LIKE ?",
                    "upper(l.arrival_name) LIKE ?",
                    "upper(l.departure_city) LIKE ?",
                    "upper(l.arrival_city) LIKE ?",
                    "upper(l.departure_state) LIKE ?",
                    "upper(l.arrival_state) LIKE ?",
                    "upper(l.departure_country) LIKE ?",
                    "upper(l.arrival_country) LIKE ?",
                ]
            ) +
            ")"
        )
        params.extend([like_query] * 12)

    if start_month:
        start_date, _ = month_to_range(start_month)
        if end_month:
            _, end_date = month_to_range(end_month)
            if start_date > end_date:
                start_date, end_date = end_date, start_date
            conditions.append("f.date >= ? AND f.date <= ?")
            params.extend([start_date, end_date])
        else:
            conditions.append("f.date >= ?")
            params.append(start_date)
    elif end_month:
        _, end_date = month_to_range(end_month)
        conditions.append("f.date <= ?")
        params.append(end_date)

    query_sql = base_query
    if conditions:
        query_sql += " WHERE " + " AND ".join(conditions)
    query_sql += " ORDER BY f.date DESC, f.created_at DESC"

    rows = conn.execute(query_sql, params).fetchall()
    flight_ids = [row["id"] for row in rows]

    legs_by_flight: Dict[int, List[FlightLeg]] = {}
    if flight_ids:
        placeholders = ",".join("?" for _ in flight_ids)
        legs_rows = conn.execute(
            f"SELECT * FROM legs WHERE flight_id IN ({placeholders}) ORDER BY flight_id, leg_number",
            flight_ids,
        ).fetchall()
        for row in legs_rows:
            flight_id = row["flight_id"]
            legs_by_flight.setdefault(flight_id, []).append(
                FlightLeg(
                    leg_number=row["leg_number"],
                    departure=row["departure"],
                    arrival=row["arrival"],
                    distance_miles=row["distance_miles"],
                    is_cross_country=bool(row["is_cross_country"]),
                    departure_name=row["departure_name"],
                    departure_city=row["departure_city"],
                    departure_state=row["departure_state"],
                    departure_country=row["departure_country"],
                    arrival_name=row["arrival_name"],
                    arrival_city=row["arrival_city"],
                    arrival_state=row["arrival_state"],
                    arrival_country=row["arrival_country"],
                )
            )

    conn.close()

    return [
        FlightEntry(
            id=row["id"],
            date=row["date"],
            aircraft_make_model=row["aircraft_make_model"],
            registration=row["registration"],
            total_time=row["total_time"],
            pic_time=row["pic_time"],
            solo_time=row["solo_time"],
            dual_received_time=row["dual_received_time"],
            day_landings=row["day_landings"],
            night_landings=row["night_landings"],
            cross_country_hours=row["cross_country_hours"],
            total_distance_miles=row["total_distance_miles"],
            is_cross_country=bool(row["is_cross_country"]),
            notes=row["notes"],
            legs=legs_by_flight.get(row["id"], []),
            created_at=row["created_at"],
        )
        for row in rows
    ]


@app.route("/", methods=["GET"])
def index() -> str:
    active_tab = request.args.get("tab", "add")
    if active_tab not in {"add", "list", "search"}:
        active_tab = "add"
    entries: List[FlightEntry] = []
    search_results: Optional[List[FlightEntry]] = None
    if active_tab == "list":
        entries = load_entries()

    current_date = date.today().isoformat()
    return render_template(
        "index.html",
        active_tab=active_tab,
        entries=entries,
        search_results=search_results,
        search_query="",
        start_month="",
        end_month="",
        current_date=current_date,
    )


@app.route("/add", methods=["POST"])
def add_flight() -> str:
    form = request.form
    date_value = form.get("date", date.today().isoformat()).strip()
    aircraft_make_model = form.get("aircraft_make_model", "").strip()
    registration = form.get("registration", "").strip()
    notes = form.get("notes", "").strip()

    def parse_float(value: str, name: str) -> Optional[float]:
        try:
            return float(value)
        except (TypeError, ValueError):
            flash(f"{name} must be a number.", "error")
            return None

    def parse_int(value: str, name: str) -> Optional[int]:
        try:
            return int(value)
        except (TypeError, ValueError):
            flash(f"{name} must be an integer.", "error")
            return None

    total_time = parse_float(form.get("total_time", ""), "Total time")
    pic_time = parse_float(form.get("pic_time", ""), "PIC time")
    solo_time = parse_float(form.get("solo_time", ""), "Solo time")
    dual_received_time = parse_float(form.get("dual_received_time", ""), "Dual received time")
    day_landings = parse_int(form.get("day_landings", ""), "Day landings")
    night_landings = parse_int(form.get("night_landings", ""), "Night landings")

    if not aircraft_make_model or not registration:
        flash("Aircraft make/model and registration are required.", "error")
        return redirect(url_for("index", tab="add"))

    legs: List[FlightLeg] = []
    for index in range(1, 4):
        departure = normalize_airport_code(form.get(f"departure_{index}", ""))
        arrival = normalize_airport_code(form.get(f"arrival_{index}", ""))
        if departure or arrival:
            if not departure or not arrival:
                flash(f"Leg {index} must include both departure and arrival.", "error")
                return redirect(url_for("index", tab="add"))
            if departure == arrival:
                flash(f"Leg {index} departure and arrival codes must be different.", "error")
                return redirect(url_for("index", tab="add"))
            try:
                legs.append(build_leg(index, departure, arrival))
            except requests.RequestException:
                flash(
                    f"Unable to calculate distance for leg {index}. Check airport codes and the Airport Gap token.",
                    "error",
                )
                return redirect(url_for("index", tab="add"))

    if not legs:
        flash("Please add at least one flight leg.", "error")
        return redirect(url_for("index", tab="add"))

    if None in {total_time, pic_time, solo_time, dual_received_time, day_landings, night_landings}:
        return redirect(url_for("index", tab="add"))

    total_distance = sum(leg.distance_miles for leg in legs)
    cross_country_flight = any(leg.is_cross_country for leg in legs)
    cross_country_hours = total_time if cross_country_flight else 0.0

    flight = FlightEntry(
        id=0,
        date=date_value,
        aircraft_make_model=aircraft_make_model,
        registration=registration,
        total_time=total_time,
        pic_time=pic_time,
        solo_time=solo_time,
        dual_received_time=dual_received_time,
        day_landings=day_landings,
        night_landings=night_landings,
        cross_country_hours=cross_country_hours,
        total_distance_miles=total_distance,
        is_cross_country=cross_country_flight,
        notes=notes,
        legs=legs,
        created_at=datetime.utcnow().isoformat(),
    )
    save_flight(flight)

    flash("Flight saved successfully.", "success")
    return redirect(url_for("index", tab="list"))


@app.route("/search", methods=["POST"])
def search_route() -> str:
    query = request.form.get("query", "").strip()
    start_month = request.form.get("start_month", "").strip()
    end_month = request.form.get("end_month", "").strip()
    search_results = search_flights(query, start_month, end_month)

    current_date = date.today().isoformat()
    return render_template(
        "index.html",
        active_tab="search",
        entries=[],
        search_results=search_results,
        search_query=query,
        start_month=start_month,
        end_month=end_month,
        current_date=current_date,
    )


@app.route("/api/distance", methods=["POST"])
def airport_distance() -> str:
    payload = request.get_json(silent=True) or request.form
    departure = normalize_airport_code(payload.get("departure", ""))
    arrival = normalize_airport_code(payload.get("arrival", ""))

    if not departure or not arrival:
        return jsonify(error="Both departure and arrival airport codes are required."), 400
    if departure == arrival:
        return jsonify(error="Departure and arrival codes must be different."), 400

    try:
        distance_miles = get_airport_distance(departure, arrival)
    except requests.RequestException:
        return jsonify(error="Failed to calculate distance from Airport Gap."), 502

    return jsonify(
        distance_miles=distance_miles,
        is_cross_country=distance_miles > 50,
        threshold=50,
    )


init_db()

if __name__ == "__main__":
    print("Flight Log Tracker is running at http://127.0.0.1:5000")
    print("Press Ctrl-C to stop the server.")
    app.run(debug=True, use_reloader=False, host="127.0.0.1", port=5000)
