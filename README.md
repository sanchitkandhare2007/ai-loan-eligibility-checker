# 🎓 AI Loan Eligibility Checker

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Flask 3.0+](https://img.shields.io/badge/framework-Flask%203.0+-green.svg)](https://flask.palletsprojects.com/)
[![Database-SQLite](https://img.shields.io/badge/database-SQLite-lightgrey.svg)](https://www.sqlite.org/)
[![AI-Google_Gemini](https://img.shields.io/badge/AI-Google%20Gemini-orange.svg)](https://aistudio.google.com/)
[![License-Educational](https://img.shields.io/badge/license-Educational%20Project-purple.svg)](#disclaimer)

> **College Demonstration Project:** An end-to-end, full-stack AI web application designed to evaluate loan eligibility using transparent, viva-friendly banking mathematical models paired with **Google Gemini AI** for explainable, human-friendly financial advisory commentary.

---

## ⚠️ Important Educational Disclaimer

> **"This application provides an educational eligibility estimate only. It does not guarantee loan approval."**  
> *This system is built specifically for academic viva demonstration and technical showcase. It does not represent an actual regulated financial institution or binding underwriting policy.*

---

## 📋 Table of Contents
- [Project Overview](#-project-overview)
- [Key Features](#-key-features)
- [Viva Presentation Guide: How Scoring Works](#-viva-presentation-guide-how-scoring-works)
- [Technology Stack](#-technology-stack)
- [Project Directory Structure](#-project-directory-structure)
- [Installation & Setup](#-installation--setup)
- [Configuring Google Gemini API](#-configuring-google-gemini-api)
- [Running the Application](#-running-the-application)
- [Running Automated Tests](#-running-automated-tests)
- [Public Deployment Guide](#-public-deployment-guide)
- [Security Practices](#-security-practices)

---

## 🌟 Project Overview

Traditional loan underwriting engines can be opaque "black boxes." When applicants are turned down, they often receive cold rejections without understanding *why* or *how to fix it*.

The **AI Loan Eligibility Checker** addresses this by:
1. Evaluating seven foundational applicant variables against transparent banking benchmarks (FOIR, CIBIL credit scoring, and Loan-to-Income multiples).
2. Generating a clear **Eligibility Score (0 to 100)** and a definitive verdict: **Eligible**, **Needs Review**, or **Not Eligible**.
3. Highlighting specific **Positive Factors** (strengths) and **Risk Factors** (areas of concern).
4. Leveraging **Google Gemini AI** to produce an empathetic, personalized advisory summary with actionable tips to help applicants improve their profile.
5. Preserving every submission in a local **SQLite database** with an audit history log and interactive **Chart.js analytics dashboard**.

---

## 🚀 Key Features

| Feature | Description |
| :--- | :--- |
| **Professional Home Page** | Modern financial landing page with hero banner, key architectural pillars, live stats, and underwriting logic tables. |
| **Interactive Application Form** | Responsive form with real-time field validation, credit score range slider, and 3 quick pre-set demo profiles for viva presentations. |
| **Live Calculation Sidebar** | Dynamically calculates estimated monthly EMI and Debt-to-Income (FOIR) in real time as user slides or types numbers. |
| **100-Point Scoring Engine** | Transparent, mathematically sound scoring formula easy to explain to professors and examiners during project defense. |
| **3-Tier Decision Matrix** | Immediate classification into **Eligible** (>= 70), **Needs Review** (50-69), or **Not Eligible** (< 50). |
| **Visual Radial Score Meter** | Dynamic SVG semi-circle gauge animated with color-coded status indicator. |
| **Positive & Negative Factors** | Distinct itemized cards identifying credit strengths and financial leverage risks. |
| **Gemini AI Financial Advisor** | Natural language commentary explaining the outcome and offering actionable guidance to boost approval odds. |
| **Smart Fallback Engine** | Built-in heuristic advisor that automatically activates if no Gemini API key is configured or if offline. |
| **SQLite Audit Trail** | Every application is logged with full input metrics, outcome score, and AI advice. |
| **History & Search Filter** | Search previous applications by applicant name or ID, filter by verdict, or inspect detailed reports. |
| **Portfolio Dashboard** | Interactive Chart.js doughnut and bar charts visualizing approval rates and financial distributions. |
| **Print-Ready PDF Reports** | Built-in CSS print styling allowing students to generate clean one-page credit assessment PDFs. |

---

## 🧑‍🏫 Viva Presentation Guide: How Scoring Works

When examiners ask *"How is eligibility calculated?"*, here is the exact breakdown:

### Scoring Components (Total = 100 Points):

1. **Fixed Obligation to Income Ratio (FOIR) — 35 Points**
   - Standard Amortization Formula:
     $$\text{Estimated EMI} = P \times r \times \frac{(1+r)^n}{(1+r)^n - 1}$$
     *(Where $r = 10.5\% / 12$, $n = \text{tenure in months}$)*
   - $\text{FOIR} = \frac{\text{Existing Monthly EMI} + \text{Estimated New EMI}}{\text{Net Monthly Income}} \times 100\%$
   - $\le 35\%$: **35 Points** (Exceptional disposable surplus)
   - $35.1\% - 45\%$: **27 Points** (Healthy safety cushion)
   - $45.1\% - 55\%$: **16 Points** (Moderate debt strain)
   - $55.1\% - 65\%$: **7 Points** (High debt strain)
   - $> 65\%$: **0 Points** (Critical debt burden)

2. **Credit Score (CIBIL / FICO scale 300 to 900) — 30 Points**
   - $\ge 750$: **30 Points** (Prime credit tier)
   - $700 - 749$: **22 Points** (Good credit tier)
   - $650 - 699$: **15 Points** (Fair credit tier)
   - $550 - 649$: **8 Points** (Subprime risk)
   - $< 550$: **0 Points** (Severe default risk)

3. **Loan-to-Annual-Income (LTI) Multiplier — 15 Points**
   - $\text{LTI} = \frac{\text{Required Loan Amount}}{\text{Monthly Income} \times 12}$
   - $\le 2.5\times$: **15 Points** (Conservative request)
   - $2.51\times - 4.0\times$: **10 Points** (Standard request)
   - $4.01\times - 6.0\times$: **5 Points** (Aggressive leverage)
   - $> 6.0\times$: **0 Points** (Over-leveraged)

4. **Employment Experience & Stability — 10 Points**
   - Experience: $\ge 4$ years (+6 pts), $2-3.9$ years (+4 pts), $1-1.9$ years (+2 pts), $<1$ year (+0 pts).
   - Employment Type: Salaried (+4 pts), Business (+3 pts), Self-Employed (+3 pts), Freelancer (+2 pts).

5. **Age Bracket — 10 Points**
   - Ages $24 - 52$: **10 Points** (Prime earning years)
   - Ages $21 - 23$: **7 Points** (Early career)
   - Ages $53 - 60$: **6 Points** (Pre-retirement)
   - Ages $>60$ or $<21$: **2 - 3 Points** (Pension/co-borrower requirement)

### Final Verdict Classification:
- **70 - 100 Points**: **Eligible** (Green) — High pre-approval probability.
- **50 - 69 Points**: **Needs Review** (Amber) — Requires co-signer, lower amount, or longer tenure.
- **0 - 49 Points**: **Not Eligible** (Red) — Critical debt burden or subprime credit.

---

## 💻 Technology Stack

- **Backend:** Python 3.9+, Flask 3.0+
- **Database:** SQLite3 (standard library, zero installation overhead)
- **AI / LLM:** Google Gemini API (`google-genai` / `google-generativeai`)
- **Frontend:** HTML5, CSS3 (Custom Design System with responsive grid, glassmorphism), Vanilla JavaScript (ES6)
- **Visuals & Charts:** Chart.js, Font Awesome 6, Google Fonts (Plus Jakarta Sans)

---

## 📁 Project Directory Structure

```
AI-loan eligibility  checker/
│
├── app.py                     # Flask application routes, validation & API
├── eligibility_engine.py      # Transparent 100-point underwriting scoring logic
├── ai_advisor.py              # Gemini AI integration + smart heuristic fallback
├── database.py                # SQLite database initialization & CRUD queries
├── test_app.py                # Automated unit & integration test suite
├── requirements.txt           # Python dependencies
├── .env.example               # Template environment configuration
├── .gitignore                 # Security ignore file (.env, *.db, venv)
├── README.md                  # Complete documentation and viva guide
│
├── templates/                 # Jinja2 HTML Templates
│   ├── base.html              # Layout, navbar, educational banner & footer
│   ├── index.html             # Landing page with hero, features & scoring table
│   ├── apply.html             # Assessment form with real-time live preview
│   ├── result.html            # Result report with score meter & Gemini advice
│   ├── history.html           # Searchable SQLite application audit log
│   └── dashboard.html         # Portfolio analytics dashboard with Chart.js
│
└── static/                    # Static Assets
    ├── css/
    │   └── style.css          # Design system, cards, animations, print media
    └── js/
        ├── main.js            # Live EMI/FOIR calculations & demo profile loader
        └── dashboard.js       # Chart.js initialization logic
```

---

## ⚙️ Installation & Setup

### Prerequisites:
- Python 3.9 or higher installed ([Download Python](https://www.python.org/downloads/))
- Git installed (optional, for version control)

### Step-by-Step Instructions:

1. **Open your terminal or command prompt** in the project folder:
   ```bash
   cd "c:\Users\ADMIN\Documents\AI-loan eligibility  checker"
   ```

2. **(Recommended) Create a Python Virtual Environment:**
   ```bash
   # Windows:
   python -m venv venv
   .\venv\Scripts\activate

   # macOS / Linux:
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

---

## 🔑 Configuring Google Gemini API

The application has been engineered to work **both with or without a Gemini API Key**:
- **With API Key:** Generates real-time, dynamic insights using Google's Gemini models.
- **Without API Key (Demo Mode):** Automatically triggers the intelligent built-in financial heuristic advisor so your viva presentation never experiences an error.

### How to obtain a free Gemini API Key:
1. Visit [Google AI Studio](https://aistudio.google.com/).
2. Sign in with your Google account.
3. Click **"Get API key"** &rarr; **"Create API key in new project"**.
4. Copy your key.
5. Create a file named `.env` in the root project folder (or copy `.env.example`):
   ```env
   SECRET_KEY=college_demo_secure_key_2025
   FLASK_DEBUG=True
   PORT=5000
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

---

## 🚀 Running the Application

1. **Start the Flask server:**
   ```bash
   python app.py
   ```

2. **Access the application in your web browser:**
   Open: **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

3. **Try the Demo Features:**
   - On the **Apply Form**, click **"Prime Profile"**, **"Borderline Profile"**, or **"High Risk Profile"** to instantly populate realistic sample records.
   - Adjust the sliders and watch the **Live Calculation Preview** on the sidebar update EMI and FOIR in real time.
   - Click **"Evaluate Loan Eligibility"** to inspect the **Score Meter**, **Factor Lists**, and **Gemini AI Explanation**.
   - Check the **Audit History** to see all previous submissions logged in SQLite.
   - Open the **Dashboard** to view interactive Chart.js graphs.

---

## 🧪 Running Automated Tests

Run the built-in test suite to verify all business logic, database operations, and web routes:

```bash
python test_app.py
```

Expected output:
```
test_ai_advisor_fallback ... ok
test_crud_lifecycle ... ok
test_monthly_emi_calculation ... ok
test_prime_applicant_eligible ... ok
test_borderline_applicant_needs_review ... ok
test_high_risk_applicant_not_eligible ... ok
test_zero_income_edge_case ... ok
test_index_page ... ok
test_apply_get_page ... ok
test_apply_post_valid_submission ... ok
test_apply_post_invalid_inputs ... ok
test_history_page ... ok
test_dashboard_page ... ok
test_api_calculate_endpoint ... ok
test_api_stats_endpoint ... ok

----------------------------------------------------------------------
Ran 15 tests in 0.85s

OK
```

---

## 🌐 Public Deployment Guide

### Option 1: Deploy on Render.com (Recommended & Free)
1. Push your code to a GitHub repository:
   ```bash
   git init
   git add .
   git commit -m "Initial commit of AI Loan Eligibility Checker"
   git branch -M main
   git remote add origin https://github.com/your-username/ai-loan-eligibility-checker.git
   git push -u origin main
   ```
2. Go to [Render.com](https://render.com) and create a free account.
3. Click **New +** &rarr; **Web Service**.
4. Connect your GitHub repository.
5. Configure the deployment settings:
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app` (add `gunicorn` to `requirements.txt` for production)
6. Add Environment Variable:
   - `GEMINI_API_KEY`: Paste your key.
7. Click **Deploy Web Service**.

### Option 2: Deploy on PythonAnywhere
1. Create a free account on [PythonAnywhere](https://www.pythonanywhere.com/).
2. Open a Bash console and clone your repository or upload files.
3. Set up a virtual environment and run `pip install -r requirements.txt`.
4. Go to the **Web** tab, create a new Flask app pointing to `app.py`.
5. Add your `GEMINI_API_KEY` in the environment configuration.

---

## 🔒 Security Practices

- **Never Commit Secrets:** The `.gitignore` file is pre-configured to ignore `.env`, `*.db`, and cache directories.
- **Environment Isolation:** All secret keys and configuration flags are loaded dynamically via `python-dotenv`.
- **Input Sanitization:** Server-side type casting, range checking, and HTML escaping prevent injection and calculation overflow.

---

## 🎓 Academic Viva Questions & Answers

**Q1: Why did you choose FOIR instead of just looking at income?**  
*Answer:* Income alone doesn't show repayment capacity. A person earning ₹1,00,000 with ₹80,000 existing EMI is at higher risk of default than someone earning ₹40,000 with zero existing debt. FOIR calculates the real disposable surplus.

**Q2: How is Gemini AI utilized in this system?**  
*Answer:* Gemini AI provides explainability. It converts quantitative risk data into actionable qualitative advice, highlighting the applicant's financial strengths and explaining specifically what steps will improve eligibility.

**Q3: What happens if the Gemini API key runs out of quota during the viva?**  
*Answer:* The application implements a graceful fallback mechanism in `ai_advisor.py`. If the API key is missing or encounters a network error, a built-in heuristic advisor synthesizes customized markdown recommendations so the presentation is never interrupted.
