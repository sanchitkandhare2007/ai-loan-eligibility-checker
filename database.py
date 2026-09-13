import sqlite3
import json
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "loan_checker.db")

def get_db_connection():
    """Establish and return a connection to the SQLite database with dict-like row access."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the SQLite database schema if not already created."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            applicant_name TEXT NOT NULL,
            age INTEGER NOT NULL,
            monthly_income REAL NOT NULL,
            employment_type TEXT NOT NULL,
            credit_score INTEGER NOT NULL,
            existing_emi REAL NOT NULL,
            required_loan_amount REAL NOT NULL,
            employment_experience REAL NOT NULL,
            loan_tenure_years INTEGER NOT NULL DEFAULT 5,
            estimated_emi REAL NOT NULL,
            foir_percentage REAL NOT NULL,
            eligibility_score INTEGER NOT NULL,
            status TEXT NOT NULL,
            positive_factors TEXT NOT NULL,
            negative_factors TEXT NOT NULL,
            ai_explanation TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    conn.close()

def save_application(data):
    """
    Save an application and its assessment result to the SQLite database.
    data is expected to be a dictionary containing inputs and calculated outputs.
    Returns the integer id of the inserted record.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # JSON encode the factor lists for clean relational storage
    positive_json = json.dumps(data.get("positive_factors", []))
    negative_json = json.dumps(data.get("negative_factors", []))

    cursor.execute("""
        INSERT INTO applications (
            applicant_name,
            age,
            monthly_income,
            employment_type,
            credit_score,
            existing_emi,
            required_loan_amount,
            employment_experience,
            loan_tenure_years,
            estimated_emi,
            foir_percentage,
            eligibility_score,
            status,
            positive_factors,
            negative_factors,
            ai_explanation,
            created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("applicant_name", "Applicant"),
        int(data.get("age", 25)),
        float(data.get("monthly_income", 0)),
        data.get("employment_type", "Salaried"),
        int(data.get("credit_score", 650)),
        float(data.get("existing_emi", 0)),
        float(data.get("required_loan_amount", 0)),
        float(data.get("employment_experience", 0)),
        int(data.get("loan_tenure_years", 5)),
        float(data.get("estimated_emi", 0)),
        float(data.get("foir_percentage", 0)),
        int(data.get("eligibility_score", 0)),
        data.get("status", "Needs Review"),
        positive_json,
        negative_json,
        data.get("ai_explanation", ""),
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    inserted_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return inserted_id

def get_application_by_id(app_id):
    """Retrieve a single application by its ID and deserialize JSON fields."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM applications WHERE id = ?", (app_id,))
    row = cursor.fetchone()
    conn.close()

    if row is None:
        return None

    app_dict = dict(row)
    try:
        app_dict["positive_factors"] = json.loads(app_dict["positive_factors"])
    except Exception:
        app_dict["positive_factors"] = []

    try:
        app_dict["negative_factors"] = json.loads(app_dict["negative_factors"])
    except Exception:
        app_dict["negative_factors"] = []

    return app_dict

def get_all_applications(limit=100, status_filter=None, search_query=None):
    """
    Retrieve application records with optional filtering by status or applicant name.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM applications WHERE 1=1"
    params = []

    if status_filter and status_filter in ["Eligible", "Needs Review", "Not Eligible"]:
        query += " AND status = ?"
        params.append(status_filter)

    if search_query:
        query += " AND (applicant_name LIKE ? OR id LIKE ?)"
        params.append(f"%{search_query}%")
        params.append(f"%{search_query}%")

    query += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)

    cursor.execute(query, tuple(params))
    rows = cursor.fetchall()
    conn.close()

    results = []
    for r in rows:
        item = dict(r)
        try:
            item["positive_factors"] = json.loads(item["positive_factors"])
        except Exception:
            item["positive_factors"] = []
        try:
            item["negative_factors"] = json.loads(item["negative_factors"])
        except Exception:
            item["negative_factors"] = []
        results.append(item)

    return results

def get_dashboard_stats():
    """
    Aggregate statistics for the analytics dashboard:
    - Total counts
    - Status breakdown
    - Approval rate %
    - Average credit score
    - Average loan requested
    - Average monthly income
    - Recent applications
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as total FROM applications")
    total = cursor.fetchone()["total"]

    if total == 0:
        conn.close()
        return {
            "total": 0,
            "eligible": 0,
            "needs_review": 0,
            "not_eligible": 0,
            "approval_rate": 0,
            "avg_credit_score": 0,
            "avg_loan_amount": 0,
            "avg_income": 0,
            "status_counts": {"Eligible": 0, "Needs Review": 0, "Not Eligible": 0},
            "recent_applications": []
        }

    cursor.execute("SELECT COUNT(*) as cnt FROM applications WHERE status = 'Eligible'")
    eligible = cursor.fetchone()["cnt"]

    cursor.execute("SELECT COUNT(*) as cnt FROM applications WHERE status = 'Needs Review'")
    needs_review = cursor.fetchone()["cnt"]

    cursor.execute("SELECT COUNT(*) as cnt FROM applications WHERE status = 'Not Eligible'")
    not_eligible = cursor.fetchone()["cnt"]

    cursor.execute("SELECT AVG(credit_score) as avg_cs, AVG(required_loan_amount) as avg_loan, AVG(monthly_income) as avg_inc FROM applications")
    averages = cursor.fetchone()

    cursor.execute("SELECT * FROM applications ORDER BY created_at DESC LIMIT 5")
    recent_rows = cursor.fetchall()
    recent = [dict(r) for r in recent_rows]

    conn.close()

    approval_rate = round((eligible / total) * 100, 1) if total > 0 else 0

    return {
        "total": total,
        "eligible": eligible,
        "needs_review": needs_review,
        "not_eligible": not_eligible,
        "approval_rate": approval_rate,
        "avg_credit_score": round(averages["avg_cs"] or 0),
        "avg_loan_amount": round(averages["avg_loan"] or 0, 2),
        "avg_income": round(averages["avg_inc"] or 0, 2),
        "status_counts": {
            "Eligible": eligible,
            "Needs Review": needs_review,
            "Not Eligible": not_eligible
        },
        "recent_applications": recent
    }

def delete_application(app_id):
    """Delete an application record by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM applications WHERE id = ?", (app_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted
