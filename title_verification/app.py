
from flask import Flask, render_template, request, redirect, url_for, session
import csv
import sqlite3
from datetime import datetime
import os
import pandas as pd

from modules.normalization import normalize_title
from modules.disallowed_words import load_disallowed_words, check_disallowed_words
from modules.edit_distance import similarity_score
from modules.phonetic import phonetic_similarity
from modules.prefix_suffix import prefix_suffix_similarity
from modules.tfidf_similarity import tfidf_cosine_similarity
from modules.scoring import classify_title

app = Flask(__name__)
app.secret_key = "admin_secret_key"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "12345"

latest_top_5 = []

ALL_TITLES = []
# ---------------- DATABASE ---------------- #

def init_db():
    conn = sqlite3.connect("database/titles.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS submission_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            decision TEXT NOT NULL,
            score REAL,
            timestamp TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def store_submission(title, decision, score):
    conn = sqlite3.connect("database/titles.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO submission_history (title, decision, score, timestamp)
        VALUES (?, ?, ?, ?)
    """, (
        title,
        decision,
        score,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()


# ---------------- LOAD TITLES ---------------- #

def load_existing_titles(folder_path="data/registered_titles"):
    titles = []

    for filename in os.listdir(folder_path):

        if filename.endswith(".csv"):

            file_path = os.path.join(folder_path, filename)

            with open(file_path, newline='', encoding='utf-8') as file:

                reader = csv.reader(file)

                for row in reader:

                    if row:
                        title = row[0].strip()

                        normalized_title = normalize_title(title)["base_title"]

                        titles.append(normalized_title)

    # remove duplicates
    titles = list(set(titles))

    return titles


# ---------------- MAIN PAGE ---------------- #

@app.route("/", methods=["GET", "POST"])
def index():
    global latest_top_5
    result = None

    if request.method == "POST":
        new_title = request.form["title"]
        normalized = normalize_title(new_title)
        base_title = normalized["base_title"]

        disallowed = load_disallowed_words()
        violations = check_disallowed_words(base_title, disallowed)

        if violations:
            result = {
                "decision": "Rejected",
                "reason": f"Disallowed words found: {violations}"
            }
            store_submission(new_title, "Rejected", 0)

        else:
            existing_titles = load_existing_titles()

            # -------- Exact Match --------
            if base_title.strip() in existing_titles:
                latest_top_5 = []

                result = {
                    "decision": "Duplicate",
                    "score": 1.0,
                    "reason": "Exact title already registered",
                    "edit_percent": 100,
                    "phonetic_percent": 100,
                    "tfidf_percent": 100,
                    "final_percent": 100
                }

                store_submission(new_title, "Duplicate", 1.0)
                return render_template("index.html", result=result)

            similarity_results = []
            max_edit = 0
            max_phonetic = 0
            prefix_violation = False

            for existing in existing_titles:

                edit = similarity_score(base_title, existing)
                phonetic = phonetic_similarity(base_title, existing)
                tfidf = tfidf_cosine_similarity(base_title, [existing])
                final_score = max(edit, phonetic, tfidf)
                similarity_results.append({
                    "title": existing,
                    "edit_score": round(edit,3),
                    "phonetic_score": round(phonetic,3),
                    "tfidf_score": round(tfidf,3),
                    "final_score": round(final_score,3)
    })

                max_edit = max(max_edit, edit)
                max_phonetic = max(max_phonetic, phonetic)

            latest_top_5 = sorted(
                similarity_results,
                key=lambda x: x["final_score"],
                reverse=True
            )[:5]

            tfidf_score = tfidf_cosine_similarity(base_title, existing_titles)

            combined = max(max_edit, max_phonetic, tfidf_score)

            if prefix_violation:
                combined = 1.0

            decision = classify_title(combined)

            result = {
                "decision": decision,
                "score": round(combined, 3),
                "reason": "Similarity based decision",
                "edit_percent": round(max_edit * 100, 1),
                "phonetic_percent": round(max_phonetic * 100, 1),
                "tfidf_percent": round(tfidf_score * 100, 1),
                "final_percent": round(combined * 100, 1)
            }

            store_submission(new_title, decision, combined)

    return render_template("index.html", result=result)


# ---------------- SIMILARITY PAGE ---------------- #

@app.route("/similarity")
def similarity():
    return render_template("similarity.html", top_5=latest_top_5)


# ---------------- HISTORY PAGE ---------------- #

@app.route("/history")
def history():
    conn = sqlite3.connect("database/titles.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM submission_history ORDER BY id DESC")
    records = cursor.fetchall()
    conn.close()
    return render_template("history.html", records=records)


# ---------------- ADMIN DASHBOARD ---------------- #

@app.route("/admin")
def admin():

    if not session.get("admin_logged_in"):
        return redirect(url_for("login"))

    conn = sqlite3.connect("database/titles.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM submission_history")
    total_submissions = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM submission_history WHERE decision='Duplicate'")
    total_duplicates = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "admin.html",
        total_submissions=total_submissions,
        total_duplicates=total_duplicates
    )

@app.route("/add_title", methods=["POST"])
def add_title():
    new_title = request.form["new_title"]

    # normalize before saving
    normalized = normalize_title(new_title)
    clean_title = normalized["base_title"]

    with open("data/registered_titles/existing_titles.csv", "a", newline='', encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([clean_title])

    return redirect(url_for("admin"))


@app.route("/delete_title/<title>")
def delete_title(title):
    titles = load_existing_titles()
    titles = [t for t in titles if t != title]

    with open("data/existing_titles.csv", "w", newline='', encoding="utf-8") as file:
        writer = csv.writer(file)
        for t in titles:
            writer.writerow([t])

    return redirect(url_for("admin"))

@app.route("/clear_history")
def clear_history():
    conn = sqlite3.connect("database/titles.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM submission_history")

    conn.commit()
    conn.close()

    return redirect(url_for("history"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["admin_logged_in"] = True
            return redirect(url_for("admin"))
        else:
            return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("admin_logged_in", None)
    return redirect(url_for("index"))

@app.route("/analytics")
def analytics():

    # protect page (admin only)
    if not session.get("admin_logged_in"):
        return redirect(url_for("login"))

    conn = sqlite3.connect("database/titles.db")
    cursor = conn.cursor()

    # total submissions
    cursor.execute("SELECT COUNT(*) FROM submission_history")
    total = cursor.fetchone()[0]

    # acceptable
    cursor.execute("SELECT COUNT(*) FROM submission_history WHERE decision='Acceptable'")
    acceptable = cursor.fetchone()[0]

    # duplicate
    cursor.execute("SELECT COUNT(*) FROM submission_history WHERE decision='Duplicate'")
    duplicate = cursor.fetchone()[0]

    # rejected
    cursor.execute("SELECT COUNT(*) FROM submission_history WHERE decision='Rejected'")
    rejected = cursor.fetchone()[0]

    # submissions per hour
    cursor.execute("""
        SELECT strftime('%H', timestamp), COUNT(*)
        FROM submission_history
        GROUP BY strftime('%H', timestamp)
        ORDER BY strftime('%H', timestamp)
    """)
    daily = cursor.fetchall()

    conn.close()

    dates = [row[0] for row in daily]
    counts = [row[1] for row in daily]

    return render_template(
        "analytics.html",
        total=total,
        acceptable=acceptable,
        duplicate=duplicate,
        rejected=rejected,
        dates=dates,
        counts=counts
    )


if __name__ == "__main__":
    init_db()

    ALL_TITLES = load_existing_titles()

    print(f"Loaded {len(ALL_TITLES)} titles from CSV files.")

    app.run(debug=True)
