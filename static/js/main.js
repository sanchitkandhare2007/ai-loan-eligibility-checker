/**
 * main.js - Core interactive logic for AI Loan Eligibility Checker
 * Handles live calculations, form synchronization, demo profile loading, and UI enhancements.
 */

document.addEventListener("DOMContentLoaded", function () {
    initMobileNav();
    initCreditScoreSync();
    initLiveEstimator();
    initFormLoadingState();
});

/* ----------------------------------------------------
   1. Mobile Navigation Toggle
---------------------------------------------------- */
function initMobileNav() {
    const mobileBtn = document.getElementById("mobileMenuBtn");
    const mobileDrawer = document.getElementById("mobileDrawer");

    if (mobileBtn && mobileDrawer) {
        mobileBtn.addEventListener("click", function () {
            mobileDrawer.classList.toggle("open");
            const icon = mobileBtn.querySelector("i");
            if (icon) {
                icon.classList.toggle("fa-bars");
                icon.classList.toggle("fa-xmark");
            }
        });
    }
}

/* ----------------------------------------------------
   2. Credit Score Input & Slider Synchronization
---------------------------------------------------- */
function initCreditScoreSync() {
    const slider = document.getElementById("credit_score_range");
    const input = document.getElementById("credit_score");
    const badge = document.getElementById("creditScoreBadge");

    if (!slider || !input) return;

    function updateScoreDisplay(val) {
        const score = parseInt(val, 10) || 300;
        slider.value = score;
        input.value = score;

        if (badge) {
            if (score >= 750) {
                badge.className = "badge badge-success font-bold text-sm";
                badge.innerText = `${score} - Prime Tier`;
            } else if (score >= 650) {
                badge.className = "badge badge-warning font-bold text-sm";
                badge.innerText = `${score} - Good Tier`;
            } else if (score >= 550) {
                badge.className = "badge badge-warning font-bold text-sm";
                badge.innerText = `${score} - Fair Tier`;
            } else {
                badge.className = "badge badge-danger font-bold text-sm";
                badge.innerText = `${score} - High Risk`;
            }
        }
    }

    slider.addEventListener("input", (e) => {
        updateScoreDisplay(e.target.value);
        triggerLiveCalculation();
    });

    input.addEventListener("input", (e) => {
        let val = parseInt(e.target.value, 10);
        if (isNaN(val)) val = 300;
        if (val > 900) val = 900;
        if (val < 300) val = 300;
        updateScoreDisplay(val);
        triggerLiveCalculation();
    });

    // Initial update
    updateScoreDisplay(input.value || 760);
}

/* ----------------------------------------------------
   3. Live Dynamic Estimator (Calculates EMI, FOIR, LTI)
---------------------------------------------------- */
function calculateEMI(principal, annualRate, tenureYears) {
    if (principal <= 0 || tenureYears <= 0) return 0;
    const monthlyRate = annualRate / 12 / 100;
    const months = tenureYears * 12;
    try {
        const emi = (principal * monthlyRate * Math.pow(1 + monthlyRate, months)) / (Math.pow(1 + monthlyRate, months) - 1);
        return isNaN(emi) ? 0 : emi;
    } catch (e) {
        return principal / months;
    }
}

function formatCurrencyINR(val) {
    return "₹" + Math.round(val).toLocaleString("en-IN") + ".00";
}

function triggerLiveCalculation() {
    const loanAmountInput = document.getElementById("required_loan_amount");
    const incomeInput = document.getElementById("monthly_income");
    const existingEmiInput = document.getElementById("existing_emi");
    const tenureSelect = document.getElementById("loan_tenure_years");

    if (!loanAmountInput || !incomeInput) return;

    const loanAmount = parseFloat(loanAmountInput.value) || 0;
    const income = parseFloat(incomeInput.value) || 0;
    const existingEmi = parseFloat(existingEmiInput.value) || 0;
    const tenure = parseInt(tenureSelect ? tenureSelect.value : 5, 10) || 5;

    // Calculate Estimated New EMI at standard 10.5% rate
    const estimatedNewEmi = calculateEMI(loanAmount, 10.5, tenure);
    const totalObligation = existingEmi + estimatedNewEmi;
    const foir = income > 0 ? (totalObligation / income) * 100 : 100;
    const annualIncome = income * 12;
    const lti = annualIncome > 0 ? (loanAmount / annualIncome).toFixed(1) : "0.0";

    // Update Sidebar Elements
    const emiEl = document.getElementById("previewEmi");
    const totalObligEl = document.getElementById("previewTotalObligation");
    const foirTextEl = document.getElementById("previewFoirText");
    const foirBarEl = document.getElementById("previewFoirBar");
    const foirVerdictEl = document.getElementById("previewFoirVerdict");
    const ltiEl = document.getElementById("previewLti");

    if (emiEl) emiEl.innerText = formatCurrencyINR(estimatedNewEmi);
    if (totalObligEl) totalObligEl.innerText = formatCurrencyINR(totalObligation);
    if (foirTextEl) foirTextEl.innerText = foir.toFixed(1) + "%";
    if (ltiEl) ltiEl.innerText = lti + "x";

    if (foirBarEl) {
        const visualWidth = Math.min(100, Math.max(5, foir));
        foirBarEl.style.width = visualWidth + "%";

        if (foir <= 35) {
            foirBarEl.className = "progress-bar-fill bg-emerald-500";
            if (foirVerdictEl) {
                foirVerdictEl.innerHTML = `<span class="text-emerald-600"><i class="fa-solid fa-circle-check"></i> Low Debt Burden (&le; 35%)</span>`;
            }
        } else if (foir <= 45) {
            foirBarEl.className = "progress-bar-fill bg-emerald-400";
            if (foirVerdictEl) {
                foirVerdictEl.innerHTML = `<span class="text-emerald-600"><i class="fa-solid fa-circle-check"></i> Manageable Repayment Buffer</span>`;
            }
        } else if (foir <= 55) {
            foirBarEl.className = "progress-bar-fill bg-amber-500";
            if (foirVerdictEl) {
                foirVerdictEl.innerHTML = `<span class="text-amber-600"><i class="fa-solid fa-triangle-exclamation"></i> Moderate Debt Commitment</span>`;
            }
        } else {
            foirBarEl.className = "progress-bar-fill bg-red-500";
            if (foirVerdictEl) {
                foirVerdictEl.innerHTML = `<span class="text-red-600"><i class="fa-solid fa-circle-xmark"></i> Critical Debt-to-Income Strain</span>`;
            }
        }
    }
}

function initLiveEstimator() {
    const inputs = [
        "required_loan_amount",
        "monthly_income",
        "existing_emi",
        "loan_tenure_years"
    ];

    inputs.forEach((id) => {
        const el = document.getElementById(id);
        if (el) {
            el.addEventListener("input", triggerLiveCalculation);
            el.addEventListener("change", triggerLiveCalculation);
        }
    });

    // Run once on load
    triggerLiveCalculation();
}

/* ----------------------------------------------------
   4. Quick Demo Profiles for College Presentation (Viva)
---------------------------------------------------- */
function loadSampleProfile(type) {
    const form = document.getElementById("loanApplicationForm");
    if (!form) return;

    if (type === "prime") {
        document.getElementById("applicant_name").value = "Rahul Sharma (Prime)";
        document.getElementById("age").value = "29";
        document.getElementById("employment_type").value = "Salaried";
        document.getElementById("employment_experience").value = "5.5";
        document.getElementById("monthly_income").value = "90000";
        document.getElementById("existing_emi").value = "6000";
        document.getElementById("required_loan_amount").value = "550000";
        document.getElementById("loan_tenure_years").value = "5";
        document.getElementById("credit_score").value = "785";
        document.getElementById("credit_score_range").value = "785";
    } else if (type === "moderate") {
        document.getElementById("applicant_name").value = "Priya Patel (Review)";
        document.getElementById("age").value = "34";
        document.getElementById("employment_type").value = "Self-Employed";
        document.getElementById("employment_experience").value = "3.0";
        document.getElementById("monthly_income").value = "52000";
        document.getElementById("existing_emi").value = "14500";
        document.getElementById("required_loan_amount").value = "600000";
        document.getElementById("loan_tenure_years").value = "5";
        document.getElementById("credit_score").value = "665";
        document.getElementById("credit_score_range").value = "665";
    } else if (type === "high_risk") {
        document.getElementById("applicant_name").value = "Amit Verma (High Risk)";
        document.getElementById("age").value = "22";
        document.getElementById("employment_type").value = "Freelancer";
        document.getElementById("employment_experience").value = "0.5";
        document.getElementById("monthly_income").value = "28000";
        document.getElementById("existing_emi").value = "15000";
        document.getElementById("required_loan_amount").value = "750000";
        document.getElementById("loan_tenure_years").value = "3";
        document.getElementById("credit_score").value = "510";
        document.getElementById("credit_score_range").value = "510";
    }

    // Trigger UI updates
    const scoreVal = document.getElementById("credit_score").value;
    const slider = document.getElementById("credit_score_range");
    const badge = document.getElementById("creditScoreBadge");
    if (slider) slider.value = scoreVal;
    if (badge) {
        const s = parseInt(scoreVal, 10);
        if (s >= 750) {
            badge.className = "badge badge-success font-bold text-sm";
            badge.innerText = `${s} - Prime Tier`;
        } else if (s >= 650) {
            badge.className = "badge badge-warning font-bold text-sm";
            badge.innerText = `${s} - Good Tier`;
        } else {
            badge.className = "badge badge-danger font-bold text-sm";
            badge.innerText = `${s} - High Risk`;
        }
    }

    triggerLiveCalculation();
}

/* ----------------------------------------------------
   5. Form Submit Loading Spinner
---------------------------------------------------- */
function initFormLoadingState() {
    const form = document.getElementById("loanApplicationForm");
    const submitBtn = document.getElementById("submitBtn");

    if (form && submitBtn) {
        form.addEventListener("submit", function () {
            submitBtn.disabled = true;
            submitBtn.innerHTML = `
                <i class="fa-solid fa-spinner fa-spin"></i> Analyzing with AI Model...
            `;
        });
    }
}
