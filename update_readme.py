"""
update_readme.py
================
Auto-updates the GitHub profile README with:
- Latest project stats (stars, last updated)
- Current "working on" status from repo activity
- Last updated timestamp

Runs via GitHub Actions daily + on every push.
"""

import os
import re
import json
import requests
from datetime import datetime, timezone

# ── Config ────────────────────────────────────────────────────
USERNAME = os.environ.get("GITHUB_USERNAME", "gauravnikam777-vision")
TOKEN    = os.environ.get("GITHUB_TOKEN", "")

HEADERS = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# Projects to track — in display order
TRACKED_REPOS = [
    {
        "repo"       : "customer-churn-prediction",
        "emoji"      : "📉",
        "title"      : "Customer Churn Prediction",
        "subtitle"   : "End-to-end ML system — 1,769 of 7,043 customers flagged as High Risk",
        "live_link"  : "https://customer-churn-prediction-7dmchid9v9vkkyigyn3ivc.streamlit.app/",
        "badges"     : "![Python](https://img.shields.io/badge/-Python-3776AB?style=flat-square&logo=python&logoColor=white) ![Streamlit](https://img.shields.io/badge/-Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white) ![scikit-learn](https://img.shields.io/badge/-scikit--learn-F7931E?style=flat-square&logo=scikit-learn&logoColor=white)",
        "insight"    : "Month-to-month contract customers churn at **3× the rate** of annual customers. FastAPI backend + Streamlit dashboard with High/Medium/Low risk tiers."
    },
    {
        "repo"       : "diabetes-prediction-app",
        "emoji"      : "🩺",
        "title"      : "Diabetes Risk Predictor",
        "subtitle"   : "Live ML app — enter health metrics, get diabetes risk probability instantly",
        "live_link"  : "https://diabetes-prediction-app-pro.streamlit.app/",
        "badges"     : "![Python](https://img.shields.io/badge/-Python-3776AB?style=flat-square&logo=python&logoColor=white) ![XGBoost](https://img.shields.io/badge/-XGBoost-FF6600?style=flat-square) ![Streamlit](https://img.shields.io/badge/-Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)",
        "insight"    : "Blood glucose is the **strongest single predictor** — patients with glucose >140 mg/dL appear in the diabetic group at dramatically higher rates even controlling for BMI and age."
    },
    {
        "repo"       : "SuperStore-PowerBI-Sales-Forecast",
        "emoji"      : "⚡",
        "title"      : "SuperStore Sales Dashboard & Forecasting",
        "subtitle"   : "Power BI dashboard + Python EDA revealing profit leaks and 20-day forecast",
        "live_link"  : None,
        "badges"     : "![Power BI](https://img.shields.io/badge/-Power%20BI-F2C811?style=flat-square&logo=powerbi&logoColor=black) ![Python](https://img.shields.io/badge/-Python-3776AB?style=flat-square&logo=python&logoColor=white) ![DAX](https://img.shields.io/badge/-DAX-0078D4?style=flat-square)",
        "insight"    : "Tables sub-category was **losing money** on every sale despite appearing in revenue reports. Discounts above 20% consistently destroy margin."
    },
    {
        "repo"       : "Trader-Behavior-Insights",
        "emoji"      : "📈",
        "title"      : "Trader Behavior Insights",
        "subtitle"   : "Behavioral analysis of 90K+ crypto trades under Fear vs Greed conditions",
        "live_link"  : None,
        "badges"     : "![Python](https://img.shields.io/badge/-Python-3776AB?style=flat-square&logo=python&logoColor=white) ![Pandas](https://img.shields.io/badge/-Pandas-150458?style=flat-square&logo=pandas&logoColor=white)",
        "insight"    : "**Discipline, not market conditions**, separates profitable traders. High-frequency trading during Fear periods consistently predicts negative PnL."
    },
]

# ── Fetch repo stats from GitHub API ──────────────────────────
def get_repo_stats(repo_name):
    url = f"https://api.github.com/repos/{USERNAME}/{repo_name}"
    r = requests.get(url, headers=HEADERS)
    if r.status_code == 200:
        data = r.json()
        return {
            "stars"      : data.get("stargazers_count", 0),
            "forks"      : data.get("forks_count", 0),
            "updated_at" : data.get("pushed_at", ""),
            "language"   : data.get("language", ""),
        }
    return {"stars": 0, "forks": 0, "updated_at": "", "language": ""}


# ── Build PROJECTS section ─────────────────────────────────────
def build_projects_section():
    lines = []
    for proj in TRACKED_REPOS:
        stats = get_repo_stats(proj["repo"])
        repo_url = f"https://github.com/{USERNAME}/{proj['repo']}"

        # Parse last updated
        try:
            dt = datetime.fromisoformat(stats["updated_at"].replace("Z", "+00:00"))
            last_updated = dt.strftime("%b %Y")
        except:
            last_updated = ""

        # Stars badge
        stars_badge = ""
        if stats["stars"] > 0:
            stars_badge = f"![Stars](https://img.shields.io/github/stars/{USERNAME}/{proj['repo']}?style=flat-square&color=yellow)"

        # Live app badge
        live_badge = ""
        if proj.get("live_link"):
            live_badge = f"[![Live App](https://img.shields.io/badge/Live%20App-Online-brightgreen?style=flat-square)]({proj['live_link']})"

        lines.append(f"### {proj['emoji']} [{proj['title']}]({repo_url})")
        lines.append(f"> {proj['subtitle']}")
        lines.append("")
        if live_badge:
            lines.append(live_badge)
        lines.append(proj["badges"])
        if stars_badge:
            lines.append(stars_badge)
        lines.append("")
        lines.append(proj["insight"])
        if last_updated:
            lines.append(f"\n*Last updated: {last_updated}*")
        lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines).rstrip()


# ── Build STATUS section ───────────────────────────────────────
def build_status_section():
    now = datetime.now(timezone.utc).strftime("%d %B %Y")
    return f"""- 🔨 **Olist E-Commerce SQL Analysis** — 18 business queries, CTEs, window functions
- 🔨 **RFM Customer Segmentation** — 90K+ customers into Champions, At-Risk, Lost
- 📚 **Statistics & A/B Testing** — building foundations
- 🕐 *README last auto-updated: {now}*"""


# ── Update README ──────────────────────────────────────────────
def update_readme():
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()

    # Replace PROJECTS section
    projects_content = build_projects_section()
    content = re.sub(
        r"<!-- PROJECTS:START -->.*?<!-- PROJECTS:END -->",
        f"<!-- PROJECTS:START -->\n{projects_content}\n<!-- PROJECTS:END -->",
        content,
        flags=re.DOTALL
    )

    # Replace STATUS section
    status_content = build_status_section()
    content = re.sub(
        r"<!-- STATUS:START -->.*?<!-- STATUS:END -->",
        f"<!-- STATUS:START -->\n{status_content}\n<!-- STATUS:END -->",
        content,
        flags=re.DOTALL
    )

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(content)

    print("✅ README.md updated successfully!")


# ── Main ──────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"Fetching data for {USERNAME}...")
    update_readme()
