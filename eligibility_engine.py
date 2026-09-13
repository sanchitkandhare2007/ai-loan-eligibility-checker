"""
eligibility_engine.py - Transparent, viva-friendly scoring and loan assessment engine.

This module evaluates an applicant's loan eligibility using established banking metrics:
1. FOIR (Fixed Obligation to Income Ratio) - Repayment capacity (35% weight)
2. Credit Score (CIBIL / FICO tiering) - Creditworthiness history (30% weight)
3. Loan-to-Income (LTI) Ratio - Debt sizing relative to annual earning (15% weight)
4. Employment Stability & Type - Income reliability (10% weight)
5. Age Criteria - Earning horizon (10% weight)

Total Score = 0 to 100 points:
- Score >= 70 : Eligible
- Score 50-69 : Needs Review
- Score < 50  : Not Eligible
"""

def calculate_monthly_emi(principal, annual_interest_rate=10.5, tenure_years=5):
    """
    Calculate estimated monthly EMI using the standard banking amortization formula:
    EMI = P * r * (1 + r)^n / ((1 + r)^n - 1)
    """
    if principal <= 0 or tenure_years <= 0:
        return 0.0

    monthly_rate = (annual_interest_rate / 12) / 100
    months = tenure_years * 12

    try:
        numerator = principal * monthly_rate * ((1 + monthly_rate) ** months)
        denominator = ((1 + monthly_rate) ** months) - 1
        emi = numerator / denominator
        return round(emi, 2)
    except (ZeroDivisionError, OverflowError):
        return round(principal / months, 2)

def evaluate_eligibility(applicant_data):
    """
    Evaluate loan eligibility based on user inputs.

    applicant_data expected fields:
    - age (int)
    - monthly_income (float)
    - employment_type (str)
    - credit_score (int)
    - existing_emi (float)
    - required_loan_amount (float)
    - employment_experience (float)
    - loan_tenure_years (int, optional, defaults to 5)

    Returns a dictionary containing:
    - eligibility_score (0 - 100)
    - status ('Eligible', 'Needs Review', 'Not Eligible')
    - estimated_emi (float)
    - total_monthly_obligation (float)
    - foir_percentage (float)
    - lti_ratio (float)
    - positive_factors (list of str)
    - negative_factors (list of str)
    - breakdown (dict of score components)
    """
    age = int(applicant_data.get("age", 25))
    monthly_income = float(applicant_data.get("monthly_income", 0))
    employment_type = str(applicant_data.get("employment_type", "Salaried"))
    credit_score = int(applicant_data.get("credit_score", 650))
    existing_emi = float(applicant_data.get("existing_emi", 0))
    required_loan = float(applicant_data.get("required_loan_amount", 0))
    experience = float(applicant_data.get("employment_experience", 0))
    tenure_years = int(applicant_data.get("loan_tenure_years", 5))

    positive_factors = []
    negative_factors = []
    score_breakdown = {}

    # Guard against invalid or 0 income
    if monthly_income <= 0:
        return {
            "eligibility_score": 0,
            "status": "Not Eligible",
            "estimated_emi": 0.0,
            "total_monthly_obligation": existing_emi,
            "foir_percentage": 100.0,
            "lti_ratio": 99.0,
            "positive_factors": [],
            "negative_factors": ["Monthly income must be greater than zero."],
            "breakdown": {"foir": 0, "credit_score": 0, "lti": 0, "employment": 0, "age": 0}
        }

    # 1. Estimated EMI and FOIR calculation
    estimated_emi = calculate_monthly_emi(required_loan, annual_interest_rate=10.5, tenure_years=tenure_years)
    total_obligation = existing_emi + estimated_emi
    foir = (total_obligation / monthly_income) * 100

    # FOIR Scoring (Max 35 points)
    if foir <= 35:
        foir_score = 35
        positive_factors.append(f"Low Debt-to-Income (FOIR is {foir:.1f}%), well below the safe 40% threshold.")
    elif foir <= 45:
        foir_score = 27
        positive_factors.append(f"Moderate Debt-to-Income (FOIR is {foir:.1f}%), leaves healthy disposable income.")
    elif foir <= 55:
        foir_score = 16
        negative_factors.append(f"Elevated Debt-to-Income (FOIR is {foir:.1f}%), exceeding the recommended 45% limit.")
    elif foir <= 65:
        foir_score = 7
        negative_factors.append(f"High Debt-to-Income burden (FOIR is {foir:.1f}%), limiting financial flexibility.")
    else:
        foir_score = 0
        negative_factors.append(f"Critical Debt-to-Income ratio ({foir:.1f}%). Total obligations consume most of monthly income.")

    score_breakdown["foir"] = foir_score

    # 2. Credit Score Scoring (Max 30 points)
    if credit_score >= 750:
        cs_score = 30
        positive_factors.append(f"Prime credit score of {credit_score} indicates an exceptional debt repayment track record.")
    elif credit_score >= 700:
        cs_score = 22
        positive_factors.append(f"Good credit score of {credit_score} satisfies standard institutional lending benchmarks.")
    elif credit_score >= 650:
        cs_score = 15
        negative_factors.append(f"Fair credit score of {credit_score} is acceptable but may lead to higher risk margins.")
    elif credit_score >= 550:
        cs_score = 7
        negative_factors.append(f"Sub-prime credit score of {credit_score} signals past payment delays or low credit depth.")
    else:
        cs_score = 0
        negative_factors.append(f"Credit score of {credit_score} is below minimum underwriting tolerance (550+ required).")

    score_breakdown["credit_score"] = cs_score

    # 3. Loan to Annual Income Ratio (LTI) (Max 15 points)
    annual_income = monthly_income * 12
    lti = required_loan / annual_income if annual_income > 0 else 99

    if lti <= 2.5:
        lti_score = 15
        positive_factors.append(f"Prudent loan sizing: Requested amount is {lti:.1f}x annual income (within safe 3x boundary).")
    elif lti <= 4.0:
        lti_score = 10
        positive_factors.append(f"Reasonable loan request: Amount is {lti:.1f}x annual income.")
    elif lti <= 6.0:
        lti_score = 5
        negative_factors.append(f"High loan multiple: Requested amount is {lti:.1f}x annual income, which raises leverage risk.")
    else:
        lti_score = 0
        negative_factors.append(f"Excessive loan multiple: Requested amount is {lti:.1f}x annual income.")

    score_breakdown["lti"] = lti_score

    # 4. Employment Stability & Type (Max 10 points)
    emp_score = 0
    # Experience component (Max 6 points)
    if experience >= 4:
        emp_score += 6
        positive_factors.append(f"Solid career stability with {experience:.1f} years of professional experience.")
    elif experience >= 2:
        emp_score += 4
        positive_factors.append(f"Established work tenure with {experience:.1f} years in the workforce.")
    elif experience >= 1:
        emp_score += 2
    else:
        negative_factors.append("Employment experience is under 1 year, indicating entry-level job stability.")

    # Employment category component (Max 4 points)
    emp_type_clean = employment_type.strip().lower()
    if "salaried" in emp_type_clean:
        emp_score += 4
        positive_factors.append("Salaried profile provides predictable, recurring monthly cash flow.")
    elif "business" in emp_type_clean:
        emp_score += 3
        positive_factors.append("Business ownership demonstrates established commercial cash flows.")
    elif "self" in emp_type_clean:
        emp_score += 3
    else:
        emp_score += 2
        negative_factors.append("Freelance or contract income may exhibit periodic cash flow volatility.")

    emp_score = min(10, emp_score)
    score_breakdown["employment"] = emp_score

    # 5. Age Criteria (Max 10 points)
    if 24 <= age <= 52:
        age_score = 10
        positive_factors.append(f"Applicant is in prime earning age bracket ({age} years old) with long repayment horizon.")
    elif 21 <= age <= 23:
        age_score = 7
        positive_factors.append(f"Early-career applicant ({age} years old) with growth trajectory.")
    elif 53 <= age <= 60:
        age_score = 6
        negative_factors.append(f"Applicant age ({age} years old) is approaching typical retirement horizon.")
    elif age > 60:
        age_score = 3
        negative_factors.append(f"Applicant age ({age} years old) past standard retirement age; pension or co-borrower required.")
    else:
        age_score = 2
        negative_factors.append(f"Applicant age ({age}) is at minimum legal eligibility limit.")

    score_breakdown["age"] = age_score

    # Total composite score (0 - 100)
    total_score = foir_score + cs_score + lti_score + emp_score + age_score
    total_score = max(0, min(100, total_score))

    # Automatic hard caps for extreme risk conditions
    if foir > 75:
        total_score = min(total_score, 45)
    if credit_score < 500:
        total_score = min(total_score, 45)

    # Determine status verdict
    if total_score >= 70:
        status = "Eligible"
    elif total_score >= 50:
        status = "Needs Review"
    else:
        status = "Not Eligible"

    return {
        "eligibility_score": total_score,
        "status": status,
        "estimated_emi": estimated_emi,
        "total_monthly_obligation": round(total_obligation, 2),
        "foir_percentage": round(foir, 1),
        "lti_ratio": round(lti, 1),
        "positive_factors": positive_factors,
        "negative_factors": negative_factors,
        "breakdown": score_breakdown
    }
