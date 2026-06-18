import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import json
import time
import datetime

# Import our helper modules
import database as db
import ai_engine as ai
import pdf_generator as pdf

# -------------------------------------------------------------
# App Initialization & Page Config
# -------------------------------------------------------------
st.set_page_config(
    page_title="LaunchLens AI — GTM Intelligence Platform",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
db.init_db()

# Load custom CSS for premium styling
st.markdown("""
<style>
    /* Global style overrides */
    .stApp {
        background-color: #0F172A; /* Slate 900 background */
        color: #F8FAFC; /* Slate 50 text */
    }
    
    /* Header typography */
    h1, h2, h3 {
        color: #F8FAFC !important;
        font-family: 'Outfit', 'Inter', sans-serif;
    }
    
    /* Dashboard metrics container */
    .dashboard-metrics-container {
        display: flex;
        justify-content: space-between;
        gap: 15px;
        margin-bottom: 25px;
    }
    
    /* Stylized UI Cards */
    .premium-card {
        background-color: #1E293B; /* Slate 800 */
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    
    .metric-card {
        flex: 1;
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        border: 1px solid #334155;
        border-top: 4px solid #3B82F6; /* Accent color */
        border-radius: 10px;
        padding: 15px 20px;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    .metric-value {
        font-size: 28px;
        font-weight: 700;
        color: #3B82F6;
        margin: 5px 0;
    }
    
    .metric-label {
        font-size: 11px;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        font-weight: 600;
    }

    /* Score Indicator Rings/Badges */
    .score-badge-green {
        background-color: #065F46;
        color: #34D399;
        padding: 4px 10px;
        border-radius: 12px;
        font-weight: bold;
        font-size: 14px;
        border: 1px solid #059669;
    }
    .score-badge-orange {
        background-color: #78350F;
        color: #FBBF24;
        padding: 4px 10px;
        border-radius: 12px;
        font-weight: bold;
        font-size: 14px;
        border: 1px solid #D97706;
    }
    .score-badge-red {
        background-color: #7F1D1D;
        color: #F87171;
        padding: 4px 10px;
        border-radius: 12px;
        font-weight: bold;
        font-size: 14px;
        border: 1px solid #DC2626;
    }
    
    /* Persona Card */
    .persona-card {
        background-color: #1E293B;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 18px;
        margin-bottom: 15px;
        border-top: 4px solid #2563EB;
        height: 100%;
    }
    
    .persona-name {
        font-size: 18px;
        font-weight: 700;
        color: #F8FAFC;
        margin-bottom: 2px;
    }
    
    .persona-role {
        font-size: 12px;
        font-weight: 600;
        color: #94A3B8;
        margin-bottom: 12px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Competitor Card */
    .competitor-card {
        background-color: #1E293B;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 18px;
        margin-bottom: 15px;
        border-left: 4px solid #3B82F6;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# Sidebar Configuration (API Key & Navigation)
# -------------------------------------------------------------
st.sidebar.markdown("""
<div style="text-align: center; padding: 10px 0;">
    <h1 style="color: #3B82F6 !important; font-size: 26px; font-weight: 800; margin-bottom: 0;">LaunchLens AI</h1>
    <p style="color: #94A3B8; font-size: 11px; margin-top: 4px; text-transform: uppercase; letter-spacing: 1.2px;">GTM Intelligence Platform</p>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")

# Navigation Selection
nav_choice = st.sidebar.radio(
    "Navigate",
    ["Dashboard", "GTM Intelligence Engine", "Saved Reports Archive"],
    label_visibility="collapsed"
)

st.sidebar.markdown("---")

# API Configuration
st.sidebar.markdown("### Configuration")

# Check Environment or secrets for Groq API key
env_key = os.environ.get("GROQ_API_KEY")
if not env_key:
    try:
        env_key = st.secrets.get("GROQ_API_KEY", "")
    except Exception:
        env_key = ""


# Sidebar API Key Input
api_key = st.sidebar.text_input(
    "Groq API Key",
    value=env_key if env_key else "",
    type="password",
    help="Enter your Groq API Key. Get one at console.groq.com."
)

# Sidebar Model Selection
groq_model = st.sidebar.selectbox(
    "Select AI Model",
    ["llama-3.3-70b-versatile", "llama3-70b-8192", "mixtral-8x7b-32768"],
    help="llama-3.3-70b-versatile is recommended for complex reasoning and GTM strategy planning."
)

st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style="font-size: 11px; color: #64748B; text-align: center;">
    LaunchLens AI v1.0.0 (MVP)<br/>
    Powered by Groq Llama Models<br/>
    Local Storage: SQLite3
</div>
""", unsafe_allow_html=True)

# Helper function for rendering progress bars in UI
def render_ui_progress_bar(label, score, rationale):
    color = "#34D399" if score >= 70 else ("#FBBF24" if score >= 50 else "#F87171")
    st.markdown(f"""
    <div style="margin-bottom: 16px; background-color: #1E293B; padding: 15px; border-radius: 8px; border: 1px solid #334155;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
            <span style="font-weight: 700; color: #F8FAFC; font-size: 14px;">{label}</span>
            <span style="font-weight: 700; color: {color}; font-size: 15px;">{score}/100</span>
        </div>
        <div style="background-color: #334155; border-radius: 10px; height: 10px; width: 100%; overflow: hidden; margin-bottom: 10px;">
            <div style="background-color: {color}; height: 100%; width: {score}%; border-radius: 10px;"></div>
        </div>
        <p style="font-size: 13px; color: #CBD5E1; margin: 0; line-height: 1.4;"><b>Rationale:</b> {rationale}</p>
    </div>
    """, unsafe_allow_html=True)


# Helper function to render a formatted report view
def render_full_report_tabs(report_dict, project_meta_dict, show_delete_button=False):
    """
    Renders the beautiful tab-based report interface in Streamlit.
    'report_dict' is the raw deserialized JSON report data.
    'project_meta_dict' has keys: id, name, industry, problem, target_customer, country
    """
    # Quick header
    st.markdown(f"## GTM Intelligence Report: {project_meta_dict['name']}")
    st.markdown(f"**Industry:** {project_meta_dict['industry']} | **Region:** {project_meta_dict['country']} | **Target Customer:** {project_meta_dict['target_customer']}")
    
    # Render PDF Download Button and deletion if requested
    col_dl, col_space, col_del = st.columns([1.5, 4, 1])
    with col_dl:
        # Prepare PDF data
        full_project_data = {
            "name": project_meta_dict["name"],
            "industry": project_meta_dict["industry"],
            "problem": project_meta_dict["problem"],
            "target_customer": project_meta_dict["target_customer"],
            "country": project_meta_dict["country"],
            "validation_score": project_meta_dict["validation_score"],
            "opportunity_score": project_meta_dict["opportunity_score"],
            "risk_score": project_meta_dict["risk_score"],
            "data": report_dict,
            "created_at": project_meta_dict.get("created_at", datetime.datetime.now().strftime("%Y-%m-%d")) if "created_at" in project_meta_dict else time.strftime("%Y-%m-%d")
        }
        try:
            pdf_bytes = pdf.create_gtm_pdf(full_project_data)
            st.download_button(
                label="Download Executive PDF Report",
                data=pdf_bytes,
                file_name=f"LaunchLens_AI_GTM_Report_{project_meta_dict['name'].replace(' ', '_')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Error compiling PDF: {str(e)}")
            
    with col_del:
        if show_delete_button and "id" in project_meta_dict:
            if st.button("Delete Report", use_container_width=True, type="secondary"):
                db.delete_project(project_meta_dict["id"])
                st.success("Project deleted successfully!")
                time.sleep(1)
                st.rerun()

    st.markdown("---")

    # Score rendering function
    def score_badge_html(score, label, is_risk=False):
        badge_class = "score-badge-green"
        if is_risk:
            if score >= 70: badge_class = "score-badge-red"
            elif score >= 40: badge_class = "score-badge-orange"
        else:
            if score < 50: badge_class = "score-badge-red"
            elif score < 70: badge_class = "score-badge-orange"
            
        return f"""
        <div style="text-align: center; background-color: #1E293B; border: 1px solid #334155; padding: 12px; border-radius: 8px;">
            <div style="font-size: 11px; font-weight: bold; color: #94A3B8; letter-spacing: 0.5px; text-transform: uppercase;">{label}</div>
            <div style="margin: 8px 0;"><span class="{badge_class}">{score}/100</span></div>
        </div>
        """

    # Layout for 3 main scores
    s_col1, s_col2, s_col3 = st.columns(3)
    with s_col1:
        st.markdown(score_badge_html(project_meta_dict["validation_score"], "Validator Score"), unsafe_allow_html=True)
    with s_col2:
        st.markdown(score_badge_html(project_meta_dict["opportunity_score"], "Opportunity Score"), unsafe_allow_html=True)
    with s_col3:
        st.markdown(score_badge_html(project_meta_dict["risk_score"], "Risk Score (Lower is Safer)", is_risk=True), unsafe_allow_html=True)

    st.markdown("<br/>", unsafe_allow_html=True)

    # Tabs definition
    tab_overview, tab_market, tab_gaps, tab_competitors, tab_personas, tab_gtm, tab_investor = st.tabs([
        "Overview", "Market Trends", "Market Gap Finder", "Competitors", "Personas", "GTM Strategy", "Investor Assessment"
    ])

    # 1. Overview Tab
    with tab_overview:
        st.markdown("### Executive Summary")
        st.markdown(f"<div style='font-size: 15px; line-height: 1.6; color: #CBD5E1;'>{report_dict.get('summary')}</div>", unsafe_allow_html=True)
        st.markdown("---")
        
        st.markdown("### SWOT Analysis Matrix")
        swot = report_dict.get("swot", {})
        
        swot_s = "".join([f"<li>{x}</li>" for x in swot.get("strengths", [])])
        swot_w = "".join([f"<li>{x}</li>" for x in swot.get("weaknesses", [])])
        swot_o = "".join([f"<li>{x}</li>" for x in swot.get("opportunities", [])])
        swot_t = "".join([f"<li>{x}</li>" for x in swot.get("threats", [])])
        
        st.markdown(f"""
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 20px;">
            <div style="background-color: #064E3B; border: 1px solid #059669; border-radius: 8px; padding: 18px;">
                <h4 style="color: #34D399; margin-top: 0; margin-bottom: 8px;">Strengths (Internal)</h4>
                <ul style="font-size: 13.5px; margin: 0; padding-left: 20px; color: #A7F3D0; line-height: 1.5;">
                    {swot_s if swot_s else "<li>None identified</li>"}
                </ul>
            </div>
            <div style="background-color: #7F1D1D; border: 1px solid #DC2626; border-radius: 8px; padding: 18px;">
                <h4 style="color: #F87171; margin-top: 0; margin-bottom: 8px;">Weaknesses (Internal)</h4>
                <ul style="font-size: 13.5px; margin: 0; padding-left: 20px; color: #FCA5A5; line-height: 1.5;">
                    {swot_w if swot_w else "<li>None identified</li>"}
                </ul>
            </div>
            <div style="background-color: #1E3A8A; border: 1px solid #3B82F6; border-radius: 8px; padding: 18px;">
                <h4 style="color: #60A5FA; margin-top: 0; margin-bottom: 8px;">Opportunities (External)</h4>
                <ul style="font-size: 13.5px; margin: 0; padding-left: 20px; color: #93C5FD; line-height: 1.5;">
                    {swot_o if swot_o else "<li>None identified</li>"}
                </ul>
            </div>
            <div style="background-color: #7C2D12; border: 1px solid #EA580C; border-radius: 8px; padding: 18px;">
                <h4 style="color: #FDBA74; margin-top: 0; margin-bottom: 8px;">Threats (External)</h4>
                <ul style="font-size: 13.5px; margin: 0; padding-left: 20px; color: #FED7AA; line-height: 1.5;">
                    {swot_t if swot_t else "<li>None identified</li>"}
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 2. Market Tab
    with tab_market:
        st.markdown("### Market Analysis")
        st.markdown(f"<div style='font-size: 14.5px; line-height: 1.6; color: #E2E8F0; margin-bottom: 20px;'>{report_dict.get('industry_overview')}</div>", unsafe_allow_html=True)
        
        st.markdown("### Key Trends & Opportunities")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("""
            <div style="background-color: #1E293B; border: 1px solid #334155; padding: 15px; border-radius: 8px; height: 100%;">
                <h4 style="color: #3B82F6; margin-top:0;">Industry Trends</h4>
            """, unsafe_allow_html=True)
            for t in report_dict.get("market_trends", []):
                st.markdown(f"- {t}")
            st.markdown("</div>", unsafe_allow_html=True)
            
        with c2:
            st.markdown("""
            <div style="background-color: #1E293B; border: 1px solid #334155; padding: 15px; border-radius: 8px; height: 100%;">
                <h4 style="color: #10B981; margin-top:0;">Emerging Opportunities</h4>
            """, unsafe_allow_html=True)
            for o in report_dict.get("emerging_opportunities", []):
                st.markdown(f"- {o}")
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<br/>", unsafe_allow_html=True)
        st.markdown("### Key Industry Challenges")
        for ch in report_dict.get("key_challenges", []):
            st.markdown(f"Challenge: {ch}")

    # 3. Market Gap Finder Tab
    with tab_gaps:
        st.markdown("### White Space & Gap Finder")
        
        gap_score = report_dict.get("market_gap_opportunity_score", 0)
        
        st.markdown(f"""
        <div style="background-color: #1E293B; border: 1px solid #334155; padding: 20px; border-radius: 12px; margin-bottom: 20px;">
            <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 12px;">
                <div style="font-size: 28px; font-weight:bold; color: #10B981;">{gap_score}/100</div>
                <div>
                    <h4 style="margin: 0; color:#F8FAFC;">White Space Opportunity Score</h4>
                    <p style="margin: 0; font-size: 12px; color: #94A3B8;">A higher score indicates a large, unaddressed market opportunity with minimal direct competitor features.</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        g1, g2, g3 = st.columns(3)
        with g1:
            st.markdown(f"""
            <div class="premium-card" style="height: 100%; border-top: 4px solid #F59E0B;">
                <h4 style="color: #F59E0B; margin-top:0;">Underserved Customer Segments</h4>
                <p style="font-size: 13.5px; color: #CBD5E1; line-height: 1.5;">{report_dict.get('market_gap_underserved_segments')}</p>
            </div>
            """, unsafe_allow_html=True)
        with g2:
            st.markdown(f"""
            <div class="premium-card" style="height: 100%; border-top: 4px solid #EF4444;">
                <h4 style="color: #EF4444; margin-top:0;">Competitor Feature Gaps</h4>
                <p style="font-size: 13.5px; color: #CBD5E1; line-height: 1.5;">{report_dict.get('market_gap_missing_features')}</p>
            </div>
            """, unsafe_allow_html=True)
        with g3:
            st.markdown(f"""
            <div class="premium-card" style="height: 100%; border-top: 4px solid #10B981;">
                <h4 style="color: #10B981; margin-top:0;">White Space Product Opportunities</h4>
                <p style="font-size: 13.5px; color: #CBD5E1; line-height: 1.5;">{report_dict.get('market_gap_product_opportunities')}</p>
            </div>
            """, unsafe_allow_html=True)

    # 4. Competitors Tab
    with tab_competitors:
        st.markdown("### Competitor Intelligence")
        
        c_dir, c_ind = st.columns(2)
        with c_dir:
            st.markdown("<h3 style='color: #3B82F6 !important;'>Direct Competitors</h3>", unsafe_allow_html=True)
            for c in report_dict.get("direct_competitors", []):
                st.markdown(f"""
                <div class="competitor-card">
                    <h4 style="margin-top:0; color: #3B82F6;">{c.get('name')}</h4>
                    <p style="font-size: 13px; color: #E2E8F0;">{c.get('description')}</p>
                    <div style="font-size: 12.5px; margin-top: 8px;">
                        <span style="color: #34D399;"><b>Strengths:</b></span> {c.get('strengths')}<br/>
                        <span style="color: #F87171;"><b>Weaknesses:</b></span> {c.get('weaknesses')}<br/>
                        <span style="color: #60A5FA;"><b>Positioning:</b></span> {c.get('positioning')}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
        with c_ind:
            st.markdown("<h3 style='color: #A7F3D0 !important;'>Indirect Competitors</h3>", unsafe_allow_html=True)
            for c in report_dict.get("indirect_competitors", []):
                st.markdown(f"""
                <div class="competitor-card" style="border-left-color: #34D399;">
                    <h4 style="margin-top:0; color: #34D399;">{c.get('name')}</h4>
                    <p style="font-size: 13px; color: #E2E8F0;">{c.get('description')}</p>
                    <div style="font-size: 12.5px; margin-top: 8px;">
                        <span style="color: #34D399;"><b>Strengths:</b></span> {c.get('strengths')}<br/>
                        <span style="color: #F87171;"><b>Weaknesses:</b></span> {c.get('weaknesses')}<br/>
                        <span style="color: #60A5FA;"><b>Positioning:</b></span> {c.get('positioning')}
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # 5. Personas Tab
    with tab_personas:
        st.markdown("### Target Customer Personas")
        st.markdown("AI has identified three distinct target user profiles based on goals, challenges, and buying behaviors:")
        
        p1, p2, p3 = st.columns(3)
        cols = [p1, p2, p3]
        
        # Draw each persona in a separate column
        for idx, pers in enumerate(report_dict.get("personas", [])):
            with cols[idx]:
                st.markdown(f"""
                <div class="persona-card">
                    <div class="persona-name">{pers.get('name')}</div>
                    <div class="persona-role">{pers.get('role')}</div>
                    <p style="font-size: 13px; color: #E2E8F0; margin-bottom: 8px;"><b>Persona Goals:</b><br/>{pers.get('goals')}</p>
                    <p style="font-size: 13px; color: #E2E8F0; margin-bottom: 8px;"><b>Pain Points:</b><br/>{pers.get('pain_points')}</p>
                    <p style="font-size: 13px; color: #E2E8F0; margin-bottom: 0;"><b>Buying Motivation:</b><br/>{pers.get('buying_motivation')}</p>
                </div>
                """, unsafe_allow_html=True)

    # 6. GTM Strategy Tab
    with tab_gtm:
        st.markdown("### Go-To-Market (GTM) Strategy")
        
        st.markdown("#### Ideal Customer Profile (ICP)")
        st.markdown(f"<div style='background-color: #1E293B; border: 1px solid #334155; padding: 15px; border-radius: 8px; margin-bottom: 20px;'>{report_dict.get('gtm', {}).get('icp')}</div>", unsafe_allow_html=True)
        
        st.markdown("#### Value Proposition & Positioning")
        st.markdown(f"<div style='background-color: #1E293B; border: 1px solid #334155; padding: 15px; border-radius: 8px; margin-bottom: 20px;'>{report_dict.get('gtm', {}).get('positioning')}</div>", unsafe_allow_html=True)
        
        st.markdown("#### Pricing & Commercial Strategy Recommendation")
        st.markdown(f"<div style='background-color: #1E293B; border: 1px solid #334155; padding: 15px; border-radius: 8px; margin-bottom: 20px;'>{report_dict.get('gtm', {}).get('pricing_recommendation')}</div>", unsafe_allow_html=True)
        
        gtm_c1, gtm_c2 = st.columns(2)
        with gtm_c1:
            st.markdown("#### Marketing Channels & Execution")
            for chan in report_dict.get("gtm", {}).get("marketing_channels", []):
                st.markdown(f"- **{chan}**")
            
            st.markdown("<br/>", unsafe_allow_html=True)
            st.markdown("#### Sales & Lead Conversion Strategy")
            st.markdown(report_dict.get("gtm", {}).get("sales_strategy"))
            
        with gtm_c2:
            st.markdown("#### 30-Day Launch Roadmap")
            for step in report_dict.get("gtm", {}).get("launch_roadmap_30_day", []):
                st.markdown(f"- {step}")

    # 7. Investor Assessment Tab
    with tab_investor:
        st.markdown("### Investor Readiness Scorecard")
        st.markdown("AI has evaluated your idea on core criteria used by Venture Capitalists:")
        st.markdown("<br/>", unsafe_allow_html=True)
        
        ir = report_dict.get("investor_readiness", {})
        
        render_ui_progress_bar("Market Attractiveness", ir.get("market_attractiveness_score", 0), ir.get("market_attractiveness_rationale"))
        render_ui_progress_bar("Business Viability", ir.get("business_viability_score", 0), ir.get("business_viability_rationale"))
        render_ui_progress_bar("Scalability Potential", ir.get("scalability_score", 0), ir.get("scalability_rationale"))
        render_ui_progress_bar("Funding Readiness", ir.get("funding_readiness_score", 0), ir.get("funding_readiness_rationale"))


# -------------------------------------------------------------
# Navigation View Handler
# -------------------------------------------------------------

# 1. DASHBOARD VIEW
if nav_choice == "Dashboard":
    st.markdown("# LaunchLens AI Dashboard")
    st.markdown("Overview of all validated startup ideas, market research benchmarks, and portfolio statistics.")
    st.markdown("---")

    # Get data from SQLite
    all_projects = db.get_all_projects()

    if not all_projects:
        st.info("No projects found in your local database yet. Go to the **GTM Intelligence Engine** tab to analyze your first startup idea!")
        
        # Nice big button to go to GTM Engine
        st.markdown("<br/><br/>", unsafe_allow_html=True)
        col_btn_l, col_btn_c, col_btn_r = st.columns([1, 1, 1])
        with col_btn_c:
            if st.button("Analyze Startup Idea Now", type="primary", use_container_width=True):
                # Redirect session state
                st.info("Please select 'GTM Intelligence Engine' in the sidebar.")
    else:
        df = pd.DataFrame(all_projects)
        
        # Calculate summary metrics
        total_projects = len(df)
        unique_industries = df['industry'].nunique()
        avg_val_score = round(df['validation_score'].mean(), 1)
        avg_opp_score = round(df['opportunity_score'].mean(), 1)
        
        # Show metric row
        st.markdown(f"""
        <div class="dashboard-metrics-container">
            <div class="metric-card">
                <div class="metric-label">Total Projects</div>
                <div class="metric-value">{total_projects}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Industries Analyzed</div>
                <div class="metric-value" style="color: #10B981;">{unique_industries}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Avg Validation Score</div>
                <div class="metric-value" style="color: #F59E0B;">{avg_val_score}/100</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Avg Opportunity Score</div>
                <div class="metric-value" style="color: #EC4899;">{avg_opp_score}/100</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### Analytics Insights")
        
        # Plotly layout columns
        ch_col1, ch_col2 = st.columns(2)
        
        with ch_col1:
            # 1. Opportunity vs Validation score comparison
            fig_bar = px.bar(
                df,
                x='name',
                y=['opportunity_score', 'validation_score'],
                barmode='group',
                title='Validation vs Opportunity Scores by Startup',
                labels={'value': 'Score', 'variable': 'Metric', 'name': 'Startup'},
                color_discrete_sequence=['#3B82F6', '#10B981'] # Blue and Green
            )
            fig_bar.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='#F8FAFC',
                legend_title_text=''
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        with ch_col2:
            # 2. Donut chart of industry distribution
            fig_pie = px.pie(
                df,
                names='industry',
                title='Projects by Industry Sector',
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig_pie.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='#F8FAFC'
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        st.markdown("### Project History")
        
        # Convert created_at to clean date strings for presentation
        df_display = df.copy()
        df_display['date'] = pd.to_datetime(df_display['created_at']).dt.date
        df_display = df_display[['id', 'name', 'industry', 'country', 'validation_score', 'opportunity_score', 'risk_score', 'date']]
        
        st.dataframe(
            df_display.rename(columns={
                'name': 'Startup Name',
                'industry': 'Industry',
                'country': 'Country',
                'validation_score': 'Validation',
                'opportunity_score': 'Opportunity',
                'risk_score': 'Risk',
                'date': 'Date Created'
            }),
            hide_index=True,
            use_container_width=True
        )


# 2. GTM INTELLIGENCE ENGINE VIEW
elif nav_choice == "GTM Intelligence Engine":
    st.markdown("# GTM Intelligence Engine")
    st.markdown("Enter details about your startup idea. Our AI will analyze the market, competitors, customer segments, and build a full GTM Launch Plan.")
    st.markdown("---")

    # If API key is not configured, show warning
    if not api_key:
        st.warning("API Key not configured. Please enter your Groq API Key in the left sidebar to generate GTM reports.")
    else:
        # Form Container
        with st.form("gtm_form"):
            st.markdown("### Startup Profile Settings")
            
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                startup_name = st.text_input("Startup Name", placeholder="e.g. CalAI", help="Name of your product or idea")
                industry = st.text_input("Industry", placeholder="e.g. SaaS / Productivity", help="Which industry category does it target?")
                target_customer = st.text_input("Target Customer / ICP", placeholder="e.g. Busy professionals, remote teams", help="Who are your target buyers?")
                
            with col_f2:
                country = st.text_input("Country / Target Region", placeholder="e.g. US & Europe, Global", help="Main region you are launching in")
                problem = st.text_area("Problem Statement", placeholder="e.g. Busy professionals struggle to find time for focused work due to back-to-back meetings and inefficient calendar scheduling.", height=120, help="What specific customer pain point are you solving?")

            submitted = st.form_submit_button("Generate GTM Report", type="primary", use_container_width=True)

            if submitted:
                # Validation checks
                if not startup_name or not industry or not problem or not target_customer or not country:
                    st.error("Please fill out all fields before submitting.")
                else:
                    # Setup progress bar
                    progress_placeholder = st.empty()
                    status_placeholder = st.empty()
                    
                    with progress_placeholder.container():
                        st.info("Initializing Groq Llama GTM Intelligence analysis...")
                        progress_bar = st.progress(0)
                        
                    steps = [
                        ("Analyzing startup feasibility and problem statement...", 15),
                        ("Conducting market research and scoping emerging trends...", 35),
                        ("Evaluating direct and indirect competitor landscapes...", 55),
                        ("Modeling target customer personas and buying motivations...", 75),
                        ("Synthesizing SWOT matrix and 30-Day Launch Roadmap...", 90),
                        ("Performing VC Investor Readiness Assessment...", 95)
                    ]
                    
                    # Store generated data in session state
                    try:
                        # Call Groq API (this handles JSON output formatting and validation)
                        # We run it synchronously, it takes about 10-15s
                        start_time = time.time()
                        
                        # Background loading simulation alongside API call
                        with st.spinner("Groq AI is analyzing. Please wait..."):
                            # Threaded status indicator updates
                            for status_lbl, val in steps:
                                status_placeholder.text(f"{status_lbl}")
                                progress_bar.progress(val)
                                time.sleep(0.5) # simple step simulation
                                
                            report = ai.generate_gtm_report(
                                name=startup_name,
                                industry=industry,
                                problem=problem,
                                target_customer=target_customer,
                                country=country,
                                api_key=api_key,
                                model=groq_model
                            )
                            
                        duration = time.time() - start_time
                        
                        progress_bar.progress(100)
                        progress_placeholder.empty()
                        status_placeholder.empty()
                        
                        st.success(f"GTM Report generated successfully in {round(duration, 1)} seconds!")
                        
                        # Save to SQLite database
                        report_data = report.model_dump()
                        project_id = db.save_project(
                            name=startup_name,
                            industry=industry,
                            problem=problem,
                            target_customer=target_customer,
                            country=country,
                            validation_score=report.validation_score,
                            opportunity_score=report.opportunity_score,
                            risk_score=report.risk_score,
                            data_dict=report_data
                        )
                        
                        # Store in session state for instant view
                        st.session_state["last_report"] = report_data
                        st.session_state["last_meta"] = {
                            "id": project_id,
                            "name": startup_name,
                            "industry": industry,
                            "problem": problem,
                            "target_customer": target_customer,
                            "country": country,
                            "validation_score": report.validation_score,
                            "opportunity_score": report.opportunity_score,
                            "risk_score": report.risk_score
                        }
                        
                    except Exception as e:
                        progress_placeholder.empty()
                        status_placeholder.empty()
                        st.error(f"Generation Failed: {str(e)}")
                        
        # Display session state last report if it exists
        if "last_report" in st.session_state:
            st.markdown("---")
            render_full_report_tabs(st.session_state["last_report"], st.session_state["last_meta"])


# 3. SAVED REPORTS ARCHIVE VIEW
elif nav_choice == "Saved Reports Archive":
    st.markdown("# Saved Reports Archive")
    st.markdown("Load and view any historical validation runs saved in your local database.")
    st.markdown("---")

    # Fetch list
    all_projects = db.get_all_projects()

    if not all_projects:
        st.info("No reports saved yet. Create a report in the **GTM Intelligence Engine** first!")
    else:
        # Create selectbox mapping Name - Industry (ID)
        report_options = {f"{p['name']} — {p['industry']} (Created: {p['created_at'][:10]})": p['id'] for p in all_projects}
        
        selected_label = st.selectbox("Select Report to Load", list(report_options.keys()))
        selected_id = report_options[selected_label]
        
        # Load project details
        project = db.get_project_by_id(selected_id)
        
        if project:
            # Prepare metadata dict
            meta_dict = {
                "id": project["id"],
                "name": project["name"],
                "industry": project["industry"],
                "problem": project["problem"],
                "target_customer": project["target_customer"],
                "country": project["country"],
                "validation_score": project["validation_score"],
                "opportunity_score": project["opportunity_score"],
                "risk_score": project["risk_score"],
                "created_at": project["created_at"]
            }
            
            render_full_report_tabs(project["data"], meta_dict, show_delete_button=True)
        else:
            st.error("Error loading selected report.")
