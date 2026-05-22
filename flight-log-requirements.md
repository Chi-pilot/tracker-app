# Flight Log Tracker Requirements

## Purpose
Build a flight log tracker for personal pilot use. Requirements should be stored in this file and updated as the project evolves.

## Minimum viable features
- Track basic flight information.
- Persist logged flights in a local file.
- Display entered flight records.
- Provide interactive menu interface for ease of use.
- RUser Interface
- Interactive menu system that displays when running without arguments
- Menu options include:
  - Add a new flight
  - View all logged flights
  - Search for a flight
  - Exit application
- Optional command-line interface for scripting (add/list commands)

## un without requiring command-line arguments (defaults to interactive menu).

## Web enable the UI experience
- Use flask 
- I want the experience to be in  full frame UI
- The background should be blue and the text should be white
- The option menu should be at the top of the window
- when I select an option (add flight, view flights), it should show up underneath the menu
- the manu can collapse when various options are selected

## Storing data
- I want the data stored in a random access database

## Automatically calculate the distance between two airports
- When I select two airports, I want the app to determine the distance between those aiports
 - the app should refer to this https://airportgap.com/docs
 - there is an API there that will determine the distance between the airfield identifiers
 - I'd like the program to handle the API key
 - if the distance is longer than 50 miles, the flight should be a cross country
 - cross country time should be automatically logged for each flight

## Adding up to three legs at a time
- I would like to be able to add up to three legs at at time
- If the distance between any two airports is greater than 50 miles, then the flight should be considered a cross country

## Searching for flights
- I want to add a third option which is search for a flight
- The search could either be by airport, by date range, or by state
- The data range should be from month/year to month/year. I can enter the dates either in chronological order or reverse chronological order. Either way, you should search out the flights between the resepctive dates 
- For instance, if if enter IL, the report should show all flights which either originated or ended in Illinois. Alternatively, if I enter FL, it should show all flights which originated or ended in Florida


## Required Fields
- Flight Info:
  - Date
  - Aircraft make/model
  - Exact registration / tail number
- Route:
  - Departure airport identifier
  - Arrival airport identifier
- Pilot Experience:
  - Total flight time
  - Pilot-In-Command (PIC) time
  - Solo time
  - Dual received time
- Landings:
  - Day landings
  - Night landings
- Cross-Country:
  - Total cross-country hours logged

## Notes
- Night landings should count only when the flight includes an hour after sunset.
- Cross-country should be measured by total hours, with the user responsible for ensuring the 50 nm rule.
- The first implementation should be simple and local, using a JSON file for storage.

## Future enhancements
- Add airport name lookups or metadata.
- Add currency and biannual flight review tracking.
- Add export to CSV or PDF.
- Add summaries for 90-day passenger currency and cross-country requirements.
