# Flight Log Tracker Requirements

## Purpose
Create a personal flight log tracker that stores flight records locally and provides a simple web UI.

## Implemented features
- Track basic flight information.
- Persist logged flights in a local SQLite database.
- Display entered flight records in a web UI.
- Search flights by airport code, airport metadata, registration, and date range.
- Allow up to three flight legs per entry.
- Automatically calculate distance between airports using the Airport Gap API.
- Mark flights as cross-country when any leg is longer than 50 miles.
- Store airport metadata including name, city, state, and country.

## Web UI requirements
- Use Flask for the web interface.
- Provide a responsive UI with a top navigation menu.
- Show content below the selected option (Add flight, View flights, Search).
- Use a blue background with white text in the UI.

## Flight data fields
- Date
- Aircraft make/model
- Registration / tail number
- Total flight time
- Pilot-in-command (PIC) time
- Solo time
- Dual received time
- Day landings
- Night landings
- Cross-country hours
- Total distance in miles
- Notes
- Up to three legs per flight

## Search requirements
- Support search by airport code, airport name, city, state, or country.
- Support search by date range using month/year values.
- Accept start and end dates in either order and return results between them.
- Include flights where either departure or arrival matches the search criteria.

## Airport metadata requirements
- Retrieve airport information from Airport Gap.
- Store city and state for each airport.
- Use the Airport Gap token from the `AIRPORTGAP_TOKEN` environment variable when available.

## Storage requirements
- Store data in a local SQLite database.
- Ignore local database and temporary files in Git.

## Future improvements
- Add CSV export.
- Add flight summaries for currency requirements.
- Add pilot review and currency tracking.
