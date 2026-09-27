# CivicFix

Simple civic issue reporting website made with Python Flask, HTML, CSS and SQLite.

## Features

- Report a civic issue
- Upload a picture
- Store reports in a SQLite database
- Automatic Report ID
- Track a report
- Admin dashboard
- Change report status
- No Supabase/API keys required for the local version

## Run

Open the terminal inside the CivicFix folder.

Install Flask:

```bash
python -m pip install Flask
```

Run:

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

The database `civicfix.db` is created automatically.

Uploaded pictures are saved inside the `uploads` folder.

## Database

The database table is created automatically by `create_database()` in `app.py`.

## Main explanation

The website has three simple parts:

1. HTML pages are the frontend.
2. Flask (`app.py`) is the backend.
3. SQLite (`civicfix.db`) stores report information.

When a user uploads a picture, Flask checks the file type and saves the picture inside `uploads`.
The picture filename is then stored in the database.
