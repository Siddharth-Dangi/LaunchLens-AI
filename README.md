# LaunchLens AI — Go-To-Market (GTM) Intelligence Platform

<p align="center">
  <strong>Validate startup ideas, analyze competitors, uncover market white spaces, and generate investor-ready GTM strategies in seconds.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/Framework-Streamlit-FF4B4B.svg" alt="Streamlit">
  <img src="https://img.shields.io/badge/AI%20Engine-Groq%20Llama%203.3-orange.svg" alt="Groq Llama 3.3">
  <img src="https://img.shields.io/badge/Database-SQLite-003B57.svg" alt="SQLite">
</p>

---

## 🚀 Overview

**LaunchLens AI** is an AI-powered Go-To-Market (GTM) intelligence and startup validation platform. Built for founders, product builders, and venture capital analysts, it takes a raw startup profile and generates a comprehensive, VC-grade market research report, competitor analysis, customer persona profiles, white space gap mapping, strategic launch roadmaps, and an investor-readiness assessment.

All generated reports can be exported as publication-quality executive PDFs and are saved locally in a SQLite database for future analysis.

---

## ✨ Features

- **💡 GTM Intelligence Engine**: Instantly generates comprehensive startup reports from a simple input form (Name, Industry, Target Region, Target Customer, and Problem Statement).
- **📊 Interactive Analytics Dashboard**: Track average validation, opportunity, and risk scores across all saved projects with beautiful, interactive Plotly visualizations.
- **🔎 Competitor Intelligence**: Automatically maps direct and indirect competitors, highlighting their strengths, weaknesses, and market positioning.
- **🎯 AI Customer Personas**: Models three distinct buyer personas complete with roles, goals, specific pain points, and buying motivations.
- **🕳️ White Space & Gap Finder**: Scopes underserved customer segments, missing competitor features, and specific product opportunities, calculating a *Gap Opportunity Score*.
- **⚡ SWOT Matrix**: Synthesizes a structured matrix highlighting internal Strengths & Weaknesses and external Opportunities & Threats.
- **📅 Strategic GTM & 30-Day Launch Roadmap**: Outlines Ideal Customer Profile (ICP), product positioning, suggested pricing models (SaaS, Freemium, etc.), targeted marketing channels, sales strategy, and a weekly step-by-step launch timeline.
- **🛡️ Investor Readiness Scorecard**: Grades the business on VCs' core criteria (Market Attractiveness, Business Viability, Scalability, and Funding Readiness) with accompanying analytical rationales.
- **📁 Saved Reports Archive**: Re-load, view, or delete past research runs from the local SQLite database.
- **📄 Executive PDF Generation**: Generates professionally styled, multi-page PDFs using ReportLab, complete with a clean layout, tables, colored indicators, and dynamic page numbering.

---

## 🛠️ Technology Stack

- **Frontend / UI**: [Streamlit](https://streamlit.io/) (with a custom dark Slate theme)
- **AI Model Orchestration**: [Groq API](https://groq.com/) using Llama models (`llama-3.3-70b-versatile` recommended)
- **Data Validation**: [Pydantic v2](https://docs.pydantic.dev/) for strict structured JSON output validation
- **Database**: [SQLite3](https://www.sqlite.org/index.html) for light local storage
- **Data Viz**: [Plotly Express](https://plotly.com/python/) for interactive charts
- **PDF Generation**: [ReportLab](https://www.reportlab.com/) for page-budgeted PDF report compilation

---

## 📂 Project Structure

```
├── app.py                # Main Streamlit web application & routing logic
├── ai_engine.py          # Pydantic validation schemas & Groq API client orchestration
├── database.py           # SQLite database helper functions for project CRUD operations
├── pdf_generator.py      # ReportLab canvas styles and document layout builders
├── requirements.txt      # Project Python dependencies
└── launchlens.db         # Local SQLite database (auto-generated)
```

---

## ⚙️ Setup & Installation

### Prerequisites
- Python 3.9 or higher
- A **Groq API Key** (obtainable from the [Groq Console](https://console.groq.com/))

### 1. Clone the Repository
```bash
git clone https://github.com/Siddharth-Dangi/LaunchLens-AI.git
cd LaunchLens-AI
```

### 2. Create and Activate a Virtual Environment
```bash
# macOS/Linux
python -m venv .venv
source .venv/bin/activate

# Windows
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables (Optional)
You can set your Groq API key as an environment variable, or enter it directly in the Streamlit application's sidebar:
```bash
export GROQ_API_KEY="your-groq-api-key-here"
```

### 5. Run the Application
```bash
streamlit run app.py
```

The app will open automatically in your browser at `http://localhost:8501`.

---

## 🛡️ License

This project is licensed under the MIT License. See the LICENSE file for details.
