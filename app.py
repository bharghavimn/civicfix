import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "civicfix.db")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024


def connect_database():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row

    connection.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT NOT NULL,
            location TEXT NOT NULL,
            priority TEXT NOT NULL,
            photo TEXT,
            status TEXT NOT NULL DEFAULT 'Submitted'
        )
    """)

    connection.commit()
    return connection


def create_database():
    connection = connect_database()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT NOT NULL,
            location TEXT NOT NULL,
            priority TEXT NOT NULL,
            photo TEXT,
            status TEXT NOT NULL DEFAULT 'Submitted'
        )
    """)

    connection.commit()
    connection.close()


def allowed_file(filename):
    if "." not in filename:
        return False

    extension = filename.rsplit(".", 1)[1].lower()
    return extension in ALLOWED_EXTENSIONS


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/report", methods=["GET", "POST"])
def report():
    error = ""

    if request.method == "POST":
        title = request.form["title"]
        category = request.form["category"]
        description = request.form["description"]
        location = request.form["location"]
        priority = request.form["priority"]

        photo = request.files.get("photo")
        photo_name = ""

        if photo and photo.filename:
            if not allowed_file(photo.filename):
                error = "Please upload JPG, JPEG, PNG, GIF or WEBP image."
                return render_template("report.html", error=error)

            original_name = secure_filename(photo.filename)
            photo_name = original_name

            base_name, extension = os.path.splitext(original_name)
            number = 1

            while os.path.exists(os.path.join(UPLOAD_FOLDER, photo_name)):
                photo_name = base_name + "_" + str(number) + extension
                number += 1

            photo.save(os.path.join(UPLOAD_FOLDER, photo_name))

        connection = connect_database()

        cursor = connection.execute("""
            INSERT INTO reports
            (title, category, description, location, priority, photo)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (title, category, description, location, priority, photo_name))

        report_id = cursor.lastrowid

        connection.commit()
        connection.close()

        return render_template("success.html", report_id=report_id)

    return render_template("report.html", error=error)


@app.route("/track", methods=["GET", "POST"])
def track():
    report = None
    searched = False

    if request.method == "POST":
        searched = True
        report_id = request.form["report_id"]

        connection = connect_database()
        report = connection.execute(
            "SELECT * FROM reports WHERE id = ?", (report_id,)
        ).fetchone()
        connection.close()

    return render_template("track.html", report=report, searched=searched)


@app.route("/admin")
def admin():
    connection = connect_database()
    reports = connection.execute(
        "SELECT * FROM reports ORDER BY id DESC"
    ).fetchall()
    connection.close()

    return render_template("admin.html", reports=reports)


@app.route("/admin/update/<int:report_id>", methods=["POST"])
def update_status(report_id):
    status = request.form["status"]

    connection = connect_database()
    connection.execute(
        "UPDATE reports SET status = ? WHERE id = ?",
        (status, report_id)
    )
    connection.commit()
    connection.close()

    return redirect(url_for("admin"))


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    from flask import send_from_directory
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


os.makedirs(UPLOAD_FOLDER, exist_ok=True)
create_database()

if __name__ == "__main__":
    app.run(debug=True)
