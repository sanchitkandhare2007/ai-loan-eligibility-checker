"""
ai_advisor.py - Generates human-friendly financial explanations using Gemini AI.
Includes a graceful heuristic fallback engine to guarantee zero downtime during college vivas.
"""

import os

def _generate_fallback_explanation(applicant_data, eval_result):
    """
    Intelligent heuristic explanation generator used when Gemini API is unavailable or unconfigured.
    Generates personalized, professional financial advice based on applicant metrics.
    """
    name = applicant_data.get("applicant_name", "Applicant")
    status = eval_result["status"]
    score = eval_result["eligibility_score"]
    foir = eval_result["foir_percentage"]
    credit_score = applicant_data.get("credit_score", 650)
    loan_amount = applicant_data.get("required_loan_amount", 0)
    monthly_income = applicant_data.get("monthly_income", 0)

    if status == "Eligible":
        summary = (
            f"**Congratulations {name}!** Based on your financial profile, your loan application demonstrates "
            f"strong credit health with an Eligibility Score of **{score}/100**."
        )
        strengths = [
            f"Your Debt-to-Income ratio (FOIR) is **{foir:.1f}%**, comfortably within the recommended 45% safety ceiling.",
            f"A credit score of **{credit_score}** reflects disciplined repayment history and minimal default risk.",
            f"Your requested loan of ₹{loan_amount:,.2f} aligns proportionally with your monthly income of ₹{monthly_income:,.2f}."
        ]
        recommendations = [
            "Maintain your low credit utilization below 30% across all credit cards.",
            "Compare interest rates and processing fees across multiple lenders to lock in the most competitive terms.",
            "Keep emergency savings equivalent to at least 3-6 months of EMI obligations."
        ]
    elif status == "Needs Review":
        summary = (
            f"**Hello {name}.** Your loan application has received an Eligibility Score of **{score}/100** (**Needs Review**). "
            f"While you meet foundational requirements, certain metrics require adjustments before automated approval."
        )
        strengths = [
            f"Stable income base of ₹{monthly_income:,.2f} per month demonstrates ongoing repayment capacity.",
            f"Employment profile is active, providing foundational creditworthiness."
        ]
        recommendations = [
            f"Your total debt obligations (FOIR) stand at **{foir:.1f}%**. Consider paying down short-term credit card debts to lower this ratio.",
            f"Consider adjusting the loan amount slightly down or extending the tenure to reduce your monthly EMI burden.",
            "Adding a creditworthy co-applicant or guarantor can significantly bolster your approval probability."
        ]
    else: # Not Eligible
        summary = (
            f"**Hello {name}.** At this stage, your loan application shows an Eligibility Score of **{score}/100** (**Not Eligible**). "
            f"Lending criteria are strict to protect borrowers from excessive financial strain."
        )
        strengths = [
            "Initiating this assessment is a proactive first step toward optimizing your personal balance sheet."
        ]
        recommendations = [
            f"**Reduce Debt Commitments:** Your FOIR of **{foir:.1f}%** is high. Prioritize clearing existing EMIs before seeking new loans.",
            f"**Credit Score Enhancement:** If your credit score ({credit_score}) is below 650, review your credit report for inaccuracies and ensure 100% on-time bill payments for the next 6-12 months.",
            f"**Right-size Request:** A smaller initial loan amount will reduce required EMI and bring your obligations into a healthy range."
        ]

    advice_md = f"### 📌 Assessment Summary\n{summary}\n\n"
    advice_md += "### 💡 Key Financial Highlights\n"
    for s in strengths:
        advice_md += f"- {s}\n"
    advice_md += "\n### 🛠️ Actionable Recommendations\n"
    for r in recommendations:
        advice_md += f"- {r}\n"

    advice_md += "\n> *Note: This explanation was synthesized by the built-in Financial Rule Advisor (Demo Mode). Configure a Google Gemini API Key in `.env` for real-time generative AI insights.*"

    return advice_md

def generate_ai_explanation(applicant_data, eval_result):
    """
    Generate an AI-powered financial advisory explanation.
    Uses Google Gemini API if GEMINI_API_KEY is configured; otherwise uses the fallback heuristic engine.
    """
    api_key = os.getenv("GEMINI_API_KEY", "").strip()

    # If no API key is set or key is placeholder, use the intelligent fallback
    if not api_key or api_key == "your_gemini_api_key_here":
        return _generate_fallback_explanation(applicant_data, eval_result)

    # Attempt to query Google Gemini API
    try:
        prompt = f"""
You are an expert, empathetic financial advisor for an educational AI Loan Eligibility system.
Analyze the following applicant loan profile and write a structured, encouraging explanation for a college demonstration.

APPLICANT PROFILE:
- Name: {applicant_data.get('applicant_name', 'Applicant')}
- Age: {applicant_data.get('age')} years
- Employment Type: {applicant_data.get('employment_type')}
- Work Experience: {applicant_data.get('employment_experience')} years
- Monthly Income: ₹{applicant_data.get('monthly_income', 0):,.2f}
- Existing Monthly EMI: ₹{applicant_data.get('existing_emi', 0):,.2f}
- Requested Loan Amount: ₹{applicant_data.get('required_loan_amount', 0):,.2f}
- Credit Score: {applicant_data.get('credit_score')}

CALCULATED METRICS:
- Overall Eligibility Score: {eval_result['eligibility_score']}/100
- Outcome Verdict: {eval_result['status']}
- Estimated New Monthly EMI: ₹{eval_result['estimated_emi']:,.2f}
- Fixed Obligation to Income Ratio (FOIR): {eval_result['foir_percentage']}%
- Loan to Annual Income Ratio (LTI): {eval_result['lti_ratio']}x
- Identified Positive Factors: {', '.join(eval_result['positive_factors'])}
- Identified Risk Factors: {', '.join(eval_result['negative_factors'])}

INSTRUCTIONS:
1. Start with a warm, personalized Assessment Summary explaining the verdict clearly.
2. Provide 'Key Financial Highlights' highlighting specific strengths in bullet points.
3. Provide 'Actionable Steps to Improve' with 2-3 specific, practical recommendations (e.g. tenure, FOIR, credit utilization).
4. Use clean Markdown formatting with clear section headers. Keep the tone professional, supportive, and accessible for college examiners.
"""

        # Try Google GenAI SDK
        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
            )
            if response and response.text:
                return response.text.strip()
        except ImportError:
            # Fallback to legacy google.generativeai if installed
            import google.generativeai as genai_legacy
            genai_legacy.configure(api_key=api_key)
            model = genai_legacy.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            if response and response.text:
                return response.text.strip()

    except Exception as e:
        # If API quota exceeded, invalid key, or network issue, fallback cleanly
        print(f"[Gemini AI Notice] API call failed ({e}). Reverting to built-in heuristic advisor.")
        return _generate_fallback_explanation(applicant_data, eval_result)

    return _generate_fallback_explanation(applicant_data, eval_result)
