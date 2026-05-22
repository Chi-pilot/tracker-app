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

## Dependencies

- Primary dependencies are listed in `requirements.txt` and should be installed into a virtual environment.
- The project was developed and tested with Python 3.11; newer 3.x versions should work but may require dependency updates.

To install the exact dependency set:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Contributing & Troubleshooting

- To run the app locally, ensure the virtual environment is activated and dependencies are installed, then run `python flight_log_tracker.py`.
- If Airport Gap API calls fail, set the `AIRPORTGAP_TOKEN` environment variable with your token:

```bash
export AIRPORTGAP_TOKEN="your_token_here"
```

- The SQLite database file `flight_log.db` is ignored by Git. Back up or export it before deleting or moving it.
- If you want to run the app using an existing system Python virtualenv, adjust the activation command accordingly.

## Development

- Consider creating `requirements-dev.txt` for development-only tools (linters, formatters, test runners).
- To prepare a clean development environment:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

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
