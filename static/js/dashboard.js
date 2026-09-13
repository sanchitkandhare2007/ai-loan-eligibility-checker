/**
 * dashboard.js - Chart.js visualization for Credit Risk Analytics Dashboard
 */

document.addEventListener("DOMContentLoaded", function () {
    if (typeof Chart === "undefined" || typeof dashboardStats === "undefined") {
        return;
    }

    initOutcomeDoughnutChart();
    initFinancialComparisonChart();
});

function initOutcomeDoughnutChart() {
    const ctx = document.getElementById("outcomeDoughnutChart");
    if (!ctx) return;

    const total = dashboardStats.eligible + dashboardStats.needs_review + dashboardStats.not_eligible;

    // Handle empty state gracefully
    if (total === 0) {
        new Chart(ctx, {
            type: "doughnut",
            data: {
                labels: ["No Applications Yet"],
                datasets: [{
                    data: [1],
                    backgroundColor: ["#e2e8f0"],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: { enabled: false }
                }
            }
        });
        return;
    }

    new Chart(ctx, {
        type: "doughnut",
        data: {
            labels: ["Eligible", "Needs Review", "Not Eligible"],
            datasets: [{
                data: [
                    dashboardStats.eligible,
                    dashboardStats.needs_review,
                    dashboardStats.not_eligible
                ],
                backgroundColor: [
                    "#10b981", // Emerald
                    "#f59e0b", // Amber
                    "#ef4444"  // Rose/Red
                ],
                borderColor: "#ffffff",
                borderWidth: 3,
                hoverOffset: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: "68%",
            plugins: {
                legend: {
                    position: "bottom",
                    labels: {
                        boxWidth: 12,
                        padding: 15,
                        font: {
                            family: "'Plus Jakarta Sans', sans-serif",
                            size: 12,
                            weight: "600"
                        }
                    }
                }
            }
        }
    });
}

function initFinancialComparisonChart() {
    const ctx = document.getElementById("financialComparisonChart");
    if (!ctx) return;

    const incomeK = Math.round(dashboardStats.avg_income / 1000);
    const loanK = Math.round(dashboardStats.avg_loan / 1000);

    new Chart(ctx, {
        type: "bar",
        data: {
            labels: ["Avg Monthly Income", "Avg Loan Principal Demand"],
            datasets: [{
                label: "Amount (₹ Thousands)",
                data: [incomeK, loanK],
                backgroundColor: [
                    "rgba(79, 70, 229, 0.85)", // Indigo
                    "rgba(6, 182, 212, 0.85)"   // Cyan
                ],
                borderRadius: 8,
                borderSkipped: false
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function (value) {
                            return "₹" + value + "k";
                        },
                        font: {
                            family: "'Plus Jakarta Sans', sans-serif",
                            size: 11
                        }
                    },
                    grid: {
                        color: "#f1f5f9"
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        font: {
                            family: "'Plus Jakarta Sans', sans-serif",
                            size: 12,
                            weight: "600"
                        }
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            return "₹" + (context.raw * 1000).toLocaleString("en-IN");
                        }
                    }
                }
            }
        }
    });
}
