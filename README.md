# Flight Log Tracker

A simple personal flight log tracker for tracking flight details and pilot experience.

This repository is backed up to GitHub at: https://github.com/Chi-pilot/tracker-app

## Getting started

1. Activate your Python environment:
   ```bash
   source /home/iggykhan/venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. (Optional) Configure your Airport Gap token:
   ```bash
   export AIRPORTGAP_TOKEN="your_token_here"
   ```
4. Run the web tracker:
   ```bash
   python flight_log_tracker.py
   ```
5. Open your browser at `http://127.0.0.1:5000`

## GitHub backup

This project is stored in a public GitHub repository. If you want to work from another machine:

```bash
git clone https://github.com/Chi-pilot/tracker-app.git
cd tracker-app
source /home/iggykhan/venv/bin/activate
pip install -r requirements.txt
```

## Data storage

Logged flights are stored in `flight_log.db` in the project root using SQLite.

Local files that should not be committed are excluded by `.gitignore`.

## Tracked fields

- Date
- Aircraft make/model
- Registration/tail number
- Departure and arrival airport codes
- Total flight time
- PIC hours
- Solo hours
- Dual received hours
- Day landings
- Night landings
- Distance in miles
- Automatic cross-country hours for flights longer than 50 miles
- Notes

## Requirements file

Requirements are maintained in `flight-log-requirements.md`.
