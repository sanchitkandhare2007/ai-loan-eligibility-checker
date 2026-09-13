"""
seed_demo_data.py - Populates the database with realistic demo records for immediate viva presentation.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import init_db, save_application, get_dashboard_stats
from eligibility_engine import evaluate_eligibility
from ai_advisor import generate_ai_explanation

def seed():
    init_db()
    stats = get_dashboard_stats()
    if stats["total"] >= 3:
        print(f"Database already has {stats['total']} applications. Skipping seed.")
        return

    demos = [
        {
            "applicant_name": "Rahul Sharma",
            "age": 29,
            "monthly_income": 90000,
            "employment_type": "Salaried",
            "credit_score": 785,
            "existing_emi": 6000,
            "required_loan_amount": 550000,
            "employment_experience": 5.5,
            "loan_tenure_years": 5
        },
        {
            "applicant_name": "Priya Patel",
            "age": 34,
            "monthly_income": 52000,
            "employment_type": "Self-Employed",
            "credit_score": 665,
            "existing_emi": 14500,
            "required_loan_amount": 600000,
            "employment_experience": 3.0,
            "loan_tenure_years": 5
        },
        {
            "applicant_name": "Amit Verma",
            "age": 22,
            "monthly_income": 28000,
            "employment_type": "Freelancer",
            "credit_score": 510,
            "existing_emi": 15000,
            "required_loan_amount": 750000,
            "employment_experience": 0.5,
            "loan_tenure_years": 3
        }
    ]

    for p in demos:
        eval_result = evaluate_eligibility(p)
        explanation = generate_ai_explanation(p, eval_result)
        full_record = {
            **p,
            **eval_result,
            "ai_explanation": explanation
        }
        app_id = save_application(full_record)
        print(f"Seeded #{app_id}: {p['applicant_name']} -> {eval_result['status']} (Score: {eval_result['eligibility_score']})")

if __name__ == "__main__":
    seed()
