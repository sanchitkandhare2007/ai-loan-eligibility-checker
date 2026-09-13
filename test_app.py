"""
test_app.py - Automated verification and test suite for AI Loan Eligibility Checker.
Run with: python test_app.py
"""

import unittest
import json
import os
import sys

# Ensure local modules are found
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from eligibility_engine import evaluate_eligibility, calculate_monthly_emi
import database
from ai_advisor import generate_ai_explanation
from app import app

class TestLoanEligibilityEngine(unittest.TestCase):

    def test_monthly_emi_calculation(self):
        """Test the standard banking EMI formula."""
        emi = calculate_monthly_emi(500000, annual_interest_rate=10.5, tenure_years=5)
        # For 500k @ 10.5% for 5 yrs, standard EMI is approx ~10,747
        self.assertGreater(emi, 10000)
        self.assertLess(emi, 11500)

    def test_prime_applicant_eligible(self):
        """High income, low existing debt, prime CIBIL score should be Eligible."""
        prime_data = {
            "applicant_name": "Test Prime",
            "age": 30,
            "monthly_income": 95000,
            "employment_type": "Salaried",
            "credit_score": 790,
            "existing_emi": 5000,
            "required_loan_amount": 400000,
            "employment_experience": 5.0,
            "loan_tenure_years": 5
        }
        result = evaluate_eligibility(prime_data)
        self.assertEqual(result["status"], "Eligible")
        self.assertGreaterEqual(result["eligibility_score"], 70)
        self.assertGreater(len(result["positive_factors"]), 0)

    def test_borderline_applicant_needs_review(self):
        """Moderate income, higher debt, fair credit should trigger Needs Review."""
        borderline_data = {
            "applicant_name": "Test Borderline",
            "age": 32,
            "monthly_income": 45000,
            "employment_type": "Self-Employed",
            "credit_score": 640,
            "existing_emi": 12000,
            "required_loan_amount": 500000,
            "employment_experience": 2.5,
            "loan_tenure_years": 5
        }
        result = evaluate_eligibility(borderline_data)
        self.assertEqual(result["status"], "Needs Review")
        self.assertTrue(50 <= result["eligibility_score"] < 70)

    def test_high_risk_applicant_not_eligible(self):
        """Low income, subprime credit, excessive debt obligations should be Not Eligible."""
        risky_data = {
            "applicant_name": "Test Risky",
            "age": 22,
            "monthly_income": 25000,
            "employment_type": "Freelancer",
            "credit_score": 510,
            "existing_emi": 15000,
            "required_loan_amount": 600000,
            "employment_experience": 0.5,
            "loan_tenure_years": 3
        }
        result = evaluate_eligibility(risky_data)
        self.assertEqual(result["status"], "Not Eligible")
        self.assertLess(result["eligibility_score"], 50)
        self.assertGreater(len(result["negative_factors"]), 0)

    def test_zero_income_edge_case(self):
        """Zero or negative income should be safely rejected without zero-division error."""
        zero_income_data = {
            "applicant_name": "Test Zero",
            "age": 25,
            "monthly_income": 0,
            "employment_type": "Salaried",
            "credit_score": 700,
            "existing_emi": 0,
            "required_loan_amount": 100000,
            "employment_experience": 1.0,
            "loan_tenure_years": 5
        }
        result = evaluate_eligibility(zero_income_data)
        self.assertEqual(result["status"], "Not Eligible")
        self.assertEqual(result["eligibility_score"], 0)


class TestDatabaseOperations(unittest.TestCase):

    def setUp(self):
        database.init_db()

    def test_crud_lifecycle(self):
        """Test insert, retrieve, list, stats, and delete."""
        sample_record = {
            "applicant_name": "Unit Test User",
            "age": 28,
            "monthly_income": 60000.0,
            "employment_type": "Salaried",
            "credit_score": 750,
            "existing_emi": 5000.0,
            "required_loan_amount": 300000.0,
            "employment_experience": 3.5,
            "loan_tenure_years": 5,
            "estimated_emi": 6448.0,
            "foir_percentage": 19.1,
            "eligibility_score": 82,
            "status": "Eligible",
            "positive_factors": ["Great credit score", "Low FOIR"],
            "negative_factors": [],
            "ai_explanation": "Eligible for pre-approval."
        }

        # 1. Insert
        inserted_id = database.save_application(sample_record)
        self.assertIsNotNone(inserted_id)

        # 2. Retrieve by ID
        fetched = database.get_application_by_id(inserted_id)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched["applicant_name"], "Unit Test User")
        self.assertEqual(fetched["status"], "Eligible")
        self.assertIsInstance(fetched["positive_factors"], list)

        # 3. Retrieve all
        all_apps = database.get_all_applications(limit=10)
        self.assertGreater(len(all_apps), 0)

        # 4. Check dashboard statistics
        stats = database.get_dashboard_stats()
        self.assertGreaterEqual(stats["total"], 1)

        # 5. Clean up delete
        deleted = database.delete_application(inserted_id)
        self.assertTrue(deleted)


class TestAIAdvisor(unittest.TestCase):

    def test_ai_advisor_fallback(self):
        """Verify AI advisor produces rich structured markdown even with no API key."""
        applicant = {
            "applicant_name": "Demo Student",
            "age": 24,
            "monthly_income": 50000,
            "credit_score": 720,
            "required_loan_amount": 250000
        }
        eval_result = {
            "status": "Eligible",
            "eligibility_score": 78,
            "foir_percentage": 26.5,
            "estimated_emi": 5374.0,
            "positive_factors": ["Solid credit score"],
            "negative_factors": []
        }
        explanation = generate_ai_explanation(applicant, eval_result)
        self.assertIn("Assessment Summary", explanation)
        self.assertIn("Demo Student", explanation)
        self.assertIn("Recommendations", explanation)


class TestFlaskWebRoutes(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()
        app.config["TESTING"] = True

    def test_index_page(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"AI Loan Eligibility", response.data)
        self.assertIn(b"educational eligibility estimate only", response.data)

    def test_apply_get_page(self):
        response = self.client.get("/apply")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Loan Eligibility Assessment", response.data)

    def test_apply_post_valid_submission(self):
        payload = {
            "applicant_name": "Ananya Roy",
            "age": "27",
            "monthly_income": "80000",
            "employment_type": "Salaried",
            "credit_score": "770",
            "existing_emi": "7000",
            "required_loan_amount": "450000",
            "employment_experience": "4",
            "loan_tenure_years": "5"
        }
        response = self.client.post("/apply", data=payload, follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        redirect_url = response.headers["Location"]
        self.assertIn("/result/", redirect_url)

        # Follow redirect and verify result page
        result_page = self.client.get(redirect_url)
        self.assertEqual(result_page.status_code, 200)
        self.assertIn(b"Ananya Roy", result_page.data)
        self.assertIn(b"ELIGIBLE", result_page.data)

    def test_apply_post_invalid_inputs(self):
        """Invalid inputs should stay on apply page and show flash errors."""
        invalid_payload = {
            "applicant_name": "Invalid Tester",
            "age": "15", # underage
            "monthly_income": "-5000", # negative
            "employment_type": "Salaried",
            "credit_score": "1200", # exceeds 900
            "existing_emi": "-100", # negative
            "required_loan_amount": "0", # 0
            "employment_experience": "2",
            "loan_tenure_years": "5"
        }
        response = self.client.post("/apply", data=invalid_payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Age must be between 18 and 100", response.data)

    def test_history_page(self):
        response = self.client.get("/history")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Application History", response.data)

    def test_dashboard_page(self):
        response = self.client.get("/dashboard")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Credit Risk Dashboard", response.data)

    def test_api_calculate_endpoint(self):
        payload = {
            "monthly_income": 70000,
            "credit_score": 750,
            "required_loan_amount": 500000,
            "existing_emi": 5000,
            "loan_tenure_years": 5,
            "employment_experience": 3,
            "age": 28,
            "employment_type": "Salaried"
        }
        response = self.client.post(
            "/api/calculate",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["status"], "success")
        self.assertIn("eligibility_score", data["data"])

    def test_api_stats_endpoint(self):
        response = self.client.get("/api/stats")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("total", data)
        self.assertIn("approval_rate", data)


if __name__ == "__main__":
    unittest.main(verbosity=2)
