# Bincom Election Portal (Django)

A Django + MySQL web application built for the Bincom interview test.

This app allows users to:
- View results for an individual polling unit
- View summed results for all polling units under a selected LGA
- Add new polling unit results for all parties

## Interview Questions Coverage

### Question 1
Create a page to display the result of any individual polling unit.

Implemented at:
- `/`
- `/polling-unit-result/`

Behavior:
- User selects a polling unit from a dropdown
- App displays party scores for that polling unit

### Question 2
Create a page to display summed total results of all polling units under one LGA.

Implemented at:
- `/lga-results/`

Behavior:
- User selects an LGA from a dropdown
- App fetches all polling units under that LGA
- App sums `announced_pu_results` by party using ORM aggregation
- App displays ranked totals

Note:
- `announced_lga_results` is intentionally not used for summation logic

### Question 3
Create a page to store results for all parties for a new polling unit.

Implemented at:
- `/add-result/`

Behavior:
- User selects a polling unit
- User enters scores for all parties
- App inserts results into `announced_pu_results`

## Tech Stack

- Python 3.x
- Django 6.x
- MySQL
- PyMySQL
- Bootstrap 5

## Project Structure

- `results/models.py`: unmanaged models mapped to existing MySQL tables
- `results/views.py`: core business logic for result retrieval and insertion
- `results/urls.py`: application routes
- `results/templates/results/`: UI templates (`base`, polling unit view, LGA view, add result)
- `election_portal/settings.py`: database and app configuration

## Navigation and UX

Responsive navigation is implemented in the shared base layout with working links to:
- Election Result Portal
- Polling Unit Result
- Add Result

Features:
- Active button highlighting for the current page
- Bootstrap mobile menu toggle
- Feedback alerts for successful form submissions

## Setup Instructions

### 1) Clone and enter project

```powershell
git clone <your-repo-url>
cd election_portal
```

### 2) Create and activate virtual environment

```powershell
python -m venv ..\venv
..\venv\Scripts\Activate.ps1
```

### 3) Install dependencies

```powershell
pip install django pymysql mysqlclient
```

If `mysqlclient` fails on your machine, PyMySQL is already configured in the app and is sufficient.

### 4) Configure database

Update database settings in `election_portal/settings.py`:
- `NAME`
- `USER`
- `PASSWORD`
- `HOST`
- `PORT`

### 5) Load SQL data

Import your provided SQL dump data for:
- `lga`
- `polling_unit`
- `announced_pu_results`
- (optional) `states`, `ward`

Example:

```powershell
Get-Content "C:\path\to\dump.sql" | mysql -h 127.0.0.1 -u root -p<password> <database_name>
```

### 6) Run app

```powershell
python manage.py check
python manage.py runserver
```

Open:
- `http://127.0.0.1:8000/`

## Key ORM Logic

LGA summed results use Django aggregation:
- Fetch polling units by `lga_id`
- Extract `uniqueid` list
- Filter `AnnouncedPUResult` by `polling_unit_uniqueid__in`
- Group by party and sum scores with `Sum('party_score')`

## Notes for Recruiter

- This implementation intentionally uses unmanaged Django models (`managed = False`) to map onto pre-existing Bincom SQL tables.
- The app includes defensive handling for empty/default selection states and user feedback messages.
- Routing and template wiring are complete, and all primary navigation buttons are functional.

## Author

Joshua Monday Alfa Candidate Submission
