import os
import sys
import re

# Ensure application directory is in sys.path and UTF-8 console output
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, abort
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

from database import (
    init_db,
    save_application,
    get_application_by_id,
    get_all_applications,
    get_dashboard_stats,
    delete_application
)
from eligibility_engine import evaluate_eligibility, calculate_monthly_emi
from ai_advisor import generate_ai_explanation

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "college_demo_secret_2025_safe_token")

# Initialize database tables on app start
with app.app_context():
    init_db()

# Custom Jinja template filters
@app.template_filter("currency")
def currency_filter(value):
    """Format numeric values with thousand separators."""
    try:
        val = float(value)
        return f"{val:,.2f}"
    except (ValueError, TypeError):
        return "0.00"

@app.template_filter("simple_markdown")
def simple_markdown_filter(text):
    """
    Lightweight markdown-to-HTML converter for AI output.
    Safely renders bold, headers, list items, and blockquotes.
    """
    if not text:
        return ""

    lines = text.strip().split("\n")
    html_lines = []
    in_list = False

    for line in lines:
        line_str = line.strip()
        if not line_str:
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            continue

        # Headers
        if line_str.startswith("### "):
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            content = line_str[4:]
            html_lines.append(f"<h4 class='ai-subheading mt-3 mb-2 font-bold text-slate-800'>{content}</h4>")
            continue
        elif line_str.startswith("## "):
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            content = line_str[3:]
            html_lines.append(f"<h3 class='ai-heading mt-4 mb-2 font-bold text-indigo-900'>{content}</h3>")
            continue

        # Blockquote
        if line_str.startswith("> "):
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            content = line_str[2:]
            html_lines.append(f"<blockquote class='ai-quote border-l-4 border-indigo-500 pl-3 py-1 my-2 text-sm italic text-slate-600 bg-indigo-50/50 rounded-r'>{content}</blockquote>")
            continue

        # Unordered list items
        if line_str.startswith("- ") or line_str.startswith("* "):
            if not in_list:
                html_lines.append("<ul class='ai-list space-y-1.5 my-2 pl-4 list-disc text-slate-700'>")
                in_list = True
            content = line_str[2:]
            # Bold parsing within list item
            content = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", content)
            html_lines.append(f"<li>{content}</li>")
            continue

        # Regular paragraph
        if in_list:
            html_lines.append("</ul>")
            in_list = False

        content = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", line_str)
        html_lines.append(f"<p class='mb-2 text-slate-700 leading-relaxed'>{content}</p>")

    if in_list:
        html_lines.append("</ul>")

    return "\n".join(html_lines)


# ==========================================
# ROUTES
# ==========================================

@app.route("/")
def index():
    """Home landing page with hero, process overview, and feature highlights."""
    stats = get_dashboard_stats()
    return render_template("index.html", stats=stats)


@app.route("/apply", methods=["GET", "POST"])
def apply():
    """Loan eligibility application form with client and server-side validation."""
    if request.method == "GET":
        return render_template("apply.html", form_data={})

    # POST - Process submission
    form_data = request.form.to_dict()
    errors = []

    applicant_name = form_data.get("applicant_name", "").strip() or "Anonymous Applicant"

    # Age validation
    try:
        age = int(form_data.get("age", 0))
        if age < 18 or age > 100:
            errors.append("Age must be between 18 and 100 years.")
    except ValueError:
        errors.append("Please enter a valid age.")
        age = 25

    # Monthly income validation
    try:
        monthly_income = float(form_data.get("monthly_income", 0))
        if monthly_income <= 0:
            errors.append("Monthly income must be greater than 0.")
    except ValueError:
        errors.append("Please enter a valid monthly income.")
        monthly_income = 0

    # Employment type validation
    employment_type = form_data.get("employment_type", "Salaried")
    valid_types = ["Salaried", "Self-Employed", "Business Owner", "Freelancer"]
    if employment_type not in valid_types:
        employment_type = "Salaried"

    # Credit score validation
    try:
        credit_score = int(form_data.get("credit_score", 0))
        if credit_score < 300 or credit_score > 900:
            errors.append("Credit score must be between 300 and 900.")
    except ValueError:
        errors.append("Please enter a valid credit score (300-900).")
        credit_score = 650

    # Existing EMI validation
    try:
        existing_emi = float(form_data.get("existing_emi", 0))
        if existing_emi < 0:
            errors.append("Existing EMI cannot be negative.")
    except ValueError:
        errors.append("Please enter a valid existing EMI amount.")
        existing_emi = 0

    # Required loan amount validation
    try:
        required_loan = float(form_data.get("required_loan_amount", 0))
        if required_loan <= 0:
            errors.append("Required loan amount must be greater than 0.")
    except ValueError:
        errors.append("Please enter a valid loan amount.")
        required_loan = 0

    # Employment experience validation
    try:
        experience = float(form_data.get("employment_experience", 0))
        if experience < 0:
            errors.append("Work experience cannot be negative.")
    except ValueError:
        errors.append("Please enter valid work experience in years.")
        experience = 0

    # Loan tenure validation
    try:
        tenure = int(form_data.get("loan_tenure_years", 5))
        if tenure < 1 or tenure > 30:
            tenure = 5
    except ValueError:
        tenure = 5

    if errors:
        for err in errors:
            flash(err, "error")
        return render_template("apply.html", form_data=form_data)

    # Prepare payload for eligibility engine
    applicant_payload = {
        "applicant_name": applicant_name,
        "age": age,
        "monthly_income": monthly_income,
        "employment_type": employment_type,
        "credit_score": credit_score,
        "existing_emi": existing_emi,
        "required_loan_amount": required_loan,
        "employment_experience": experience,
        "loan_tenure_years": tenure
    }

    # Evaluate eligibility using transparent rules
    eval_result = evaluate_eligibility(applicant_payload)

    # Generate Gemini AI explanation (or smart fallback)
    ai_explanation = generate_ai_explanation(applicant_payload, eval_result)

    # Combine data for database persistence
    full_record = {
        **applicant_payload,
        **eval_result,
        "ai_explanation": ai_explanation
    }

    # Save to SQLite
    app_id = save_application(full_record)

    flash("Loan eligibility calculation completed successfully!", "success")
    return redirect(url_for("result", app_id=app_id))


@app.route("/result/<int:app_id>")
def result(app_id):
    """Display comprehensive results, score meter, factors, and Gemini AI analysis."""
    record = get_application_by_id(app_id)
    if not record:
        flash("Application record not found.", "error")
        return redirect(url_for("history"))

    return render_template("result.html", app=record)


@app.route("/history")
def history():
    """Display application history with search and status filtering."""
    status_filter = request.args.get("status", "").strip()
    search_query = request.args.get("q", "").strip()

    applications = get_all_applications(
        limit=100,
        status_filter=status_filter if status_filter else None,
        search_query=search_query if search_query else None
    )

    return render_template(
        "history.html",
        applications=applications,
        current_status=status_filter,
        current_query=search_query
    )


@app.route("/delete/<int:app_id>", methods=["POST"])
def delete_record(app_id):
    """Delete an application record from the database."""
    deleted = delete_application(app_id)
    if deleted:
        flash("Application record deleted successfully.", "success")
    else:
        flash("Could not find the record to delete.", "error")
    return redirect(url_for("history"))


@app.route("/dashboard")
def dashboard():
    """Analytics dashboard showing aggregate statistics, approval metrics, and charts."""
    stats = get_dashboard_stats()
    return render_template("dashboard.html", stats=stats)


# ==========================================
# REST API ENDPOINTS
# ==========================================

@app.route("/api/calculate", methods=["POST"])
def api_calculate():
    """
    Live estimation endpoint for instant client-side updates
    as users slide or type numbers in the application form.
    """
    data = request.get_json(silent=True) or request.form.to_dict()
    try:
        eval_result = evaluate_eligibility(data)
        return jsonify({
            "status": "success",
            "data": eval_result
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400


@app.route("/api/stats")
def api_stats():
    """Return JSON metrics for frontend charts."""
    stats = get_dashboard_stats()
    return jsonify(stats)


# ==========================================
# ERROR HANDLERS
# ==========================================

@app.errorhandler(404)
def page_not_found(e):
    return render_template("base.html", error_title="404 - Page Not Found", error_message="The page you requested does not exist."), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template("base.html", error_title="500 - Server Error", error_message="An unexpected internal server error occurred."), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "True").lower() in ("true", "1", "yes")
    print(f"\n=======================================================")
    print(f">> AI Loan Eligibility Checker running on http://127.0.0.1:{port}")
    print(f">> College Project Demo Mode Active")
    print(f"=======================================================\n")
    app.run(host="0.0.0.0", port=port, debug=debug)
