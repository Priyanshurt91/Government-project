"""
╔══════════════════════════════════════════════════════════════╗
║              SEVA FORM AI — Admin Analytics Dashboard        ║
║  AI-Powered Government Service Form Filling Analytics Panel  ║
╚══════════════════════════════════════════════════════════════╝

Run:  streamlit run dashboard.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta
import uuid
import time
import json
import os
import random

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CONFIGURATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

st.set_page_config(
    page_title="Seva Form AI — Admin Dashboard",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Backend API base URL (for future live integration)
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CUSTOM CSS — Dark Premium Theme
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

st.markdown("""
<style>
    /* ---- Global ---- */
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #1a1a2e 50%, #16213e 100%);
    }

    /* ---- Sidebar ---- */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f0c29 0%, #1a1a2e 100%);
        border-right: 1px solid rgba(99, 102, 241, 0.2);
    }
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown li,
    section[data-testid="stSidebar"] label {
        color: #c7d2fe !important;
    }
    section[data-testid="stSidebar"] .stSelectbox label,
    section[data-testid="stSidebar"] .stRadio label {
        color: #a5b4fc !important;
    }

    /* ---- KPI Card ---- */
    .kpi-card {
        background: linear-gradient(135deg, rgba(30, 27, 75, 0.8), rgba(49, 46, 129, 0.4));
        border: 1px solid rgba(99, 102, 241, 0.25);
        border-radius: 16px;
        padding: 24px 20px;
        text-align: center;
        backdrop-filter: blur(12px);
        transition: transform 0.25s ease, box-shadow 0.25s ease;
    }
    .kpi-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 32px rgba(99, 102, 241, 0.25);
    }
    .kpi-icon { font-size: 2rem; margin-bottom: 6px; }
    .kpi-value {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2px;
    }
    .kpi-label { font-size: 0.85rem; color: #94a3b8; letter-spacing: 0.5px; }
    .kpi-delta { font-size: 0.75rem; margin-top: 4px; }
    .kpi-delta.up { color: #34d399; }
    .kpi-delta.down { color: #f87171; }

    /* ---- Section Header ---- */
    .section-header {
        font-size: 1.3rem;
        font-weight: 700;
        color: #e0e7ff;
        margin: 30px 0 10px 0;
        padding-bottom: 8px;
        border-bottom: 2px solid rgba(99, 102, 241, 0.3);
    }

    /* ---- Glass Panel ---- */
    .glass-panel {
        background: rgba(30, 27, 75, 0.5);
        border: 1px solid rgba(99, 102, 241, 0.15);
        border-radius: 14px;
        padding: 20px;
        backdrop-filter: blur(10px);
        margin-bottom: 16px;
    }

    /* ---- Status Badge ---- */
    .status-badge {
        display: inline-block;
        padding: 3px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .status-success { background: rgba(52, 211, 153, 0.2); color: #34d399; border: 1px solid rgba(52, 211, 153, 0.4); }
    .status-error { background: rgba(248, 113, 113, 0.2); color: #f87171; border: 1px solid rgba(248, 113, 113, 0.4); }
    .status-pending { background: rgba(251, 191, 36, 0.2); color: #fbbf24; border: 1px solid rgba(251, 191, 36, 0.4); }

    /* ---- Hide Streamlit branding ---- */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }

    /* ---- Title styling ---- */
    .dashboard-title {
        font-size: 1.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #818cf8 0%, #c084fc 50%, #f472b6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
    .dashboard-subtitle {
        font-size: 0.9rem;
        color: #64748b;
        margin-top: -5px;
    }
</style>
""", unsafe_allow_html=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MOCK DATA GENERATORS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@st.cache_data(ttl=300)
def generate_submissions_data(n=200):
    """Generate mock form submission data."""
    np.random.seed(42)
    services = [
        "Aadhaar Enrollment", "PAN Card Application", "Income Certificate",
        "Caste Certificate", "Domicile Certificate", "Birth Certificate",
        "Death Certificate", "Ration Card", "Passport Application",
        "Voter ID Registration", "Driving License", "Marriage Certificate",
    ]
    statuses = ["Completed", "Pending", "Failed"]
    status_weights = [0.75, 0.18, 0.07]
    names = [
        "Rahul Sharma", "Priya Patel", "Amit Kumar", "Sunita Devi",
        "Rajesh Singh", "Meena Kumari", "Vijay Verma", "Anjali Gupta",
        "Suresh Yadav", "Pooja Mishra", "Deepak Joshi", "Kavita Nair",
        "Arun Reddy", "Neha Chauhan", "Manoj Tiwari", "Suman Das",
        "Rakesh Pandey", "Geeta Bhat", "Ashok Mehta", "Divya Saxena",
    ]

    dates = [datetime.now() - timedelta(days=random.randint(0, 90)) for _ in range(n)]
    dates.sort()

    data = {
        "submission_id": [str(uuid.uuid4())[:8] for _ in range(n)],
        "applicant_name": [random.choice(names) for _ in range(n)],
        "service_name": [random.choice(services) for _ in range(n)],
        "timestamp": dates,
        "status": random.choices(statuses, weights=status_weights, k=n),
        "pdf_generated": [random.random() > 0.2 for _ in range(n)],
        "processing_time_s": np.round(np.random.exponential(2.5, n) + 0.5, 2),
    }
    return pd.DataFrame(data)


@st.cache_data(ttl=300)
def generate_document_data(n=300):
    """Generate mock document processing data.

    Produces n rows of realistic document-processing records including
    document type, randomly sampled extracted entities, confidence scores,
    processing times, and status labels.
    """
    np.random.seed(43)
    doc_types = ["Aadhaar", "PAN", "Birth Certificate", "Income Proof", "Address Proof", "Other"]
    doc_weights = [0.40, 0.25, 0.10, 0.08, 0.10, 0.07]
    statuses = ["Success", "Partial", "Failed"]
    status_weights = [0.78, 0.15, 0.07]

    entities_map = {
        "Aadhaar": ["name", "dob", "gender", "aadhaar", "address", "father_name"],
        "PAN": ["name", "dob", "pan", "father_name"],
        "Birth Certificate": ["name", "dob", "father_name", "mother_name", "place_of_birth"],
        "Income Proof": ["name", "income", "address"],
        "Address Proof": ["name", "address", "pincode", "state"],
        "Other": ["name"],
    }

    def _safe_sample(doc_type):
        """Safely sample a random subset of entities for a given doc type.

        FIX: The original code used random.randint(2, len(entities)) which
        crashes with ValueError when len(entities) < 2 (e.g. "Other" has
        only ["name"]). This helper ensures k is always in [1, len(entities)],
        and gracefully handles empty lists.
        """
        entities = entities_map.get(doc_type, [])
        if not entities:
            # Guard against empty entity lists — return placeholder
            return "unknown"
        # random.randint(a, b) is inclusive on both ends, so (1, len) is safe
        # even when len == 1 → randint(1, 1) always returns 1
        k = random.randint(1, len(entities))
        return ", ".join(random.sample(entities, k=k))

    dates = [datetime.now() - timedelta(days=random.randint(0, 90)) for _ in range(n)]
    dates.sort()
    types_list = random.choices(doc_types, weights=doc_weights, k=n)

    data = {
        "doc_id": [str(uuid.uuid4())[:8] for _ in range(n)],
        "document_type": types_list,
        "extracted_entities": [_safe_sample(t) for t in types_list],
        "confidence_score": np.round(np.clip(np.random.beta(8, 2, n) * 100, 30, 100), 1),
        "processing_time_ms": np.round(np.random.exponential(800, n) + 200, 0).astype(int),
        "status": random.choices(statuses, weights=status_weights, k=n),
        "timestamp": dates,
    }
    return pd.DataFrame(data)


@st.cache_data(ttl=300)
def generate_voice_data(n=150):
    """Generate mock voice processing data."""
    np.random.seed(44)
    languages = ["Hindi", "English", "Marathi", "Tamil", "Bengali", "Telugu", "Gujarati"]
    lang_weights = [0.40, 0.25, 0.10, 0.08, 0.07, 0.05, 0.05]
    modes = ["transcribe", "translate"]

    dates = [datetime.now() - timedelta(days=random.randint(0, 90)) for _ in range(n)]
    dates.sort()

    data = {
        "voice_id": [str(uuid.uuid4())[:8] for _ in range(n)],
        "language": random.choices(languages, weights=lang_weights, k=n),
        "mode": [random.choice(modes) for _ in range(n)],
        "duration_sec": np.round(np.random.uniform(3, 45, n), 1),
        "transcription_accuracy": np.round(np.clip(np.random.beta(9, 2, n) * 100, 50, 99.5), 1),
        "processing_time_ms": np.round(np.random.exponential(1200, n) + 500, 0).astype(int),
        "entities_extracted": np.random.randint(2, 10, n),
        "timestamp": dates,
    }
    return pd.DataFrame(data)


@st.cache_data(ttl=300)
def generate_service_data():
    """Generate mock service catalog data."""
    services = {
        "Aadhaar Enrollment": {"category": "Identity", "requests": 1247, "avg_time": 3.2, "success_rate": 94.5},
        "PAN Card Application": {"category": "Identity", "requests": 983, "avg_time": 2.8, "success_rate": 96.1},
        "Income Certificate": {"category": "Revenue", "requests": 756, "avg_time": 4.1, "success_rate": 91.3},
        "Caste Certificate": {"category": "Revenue", "requests": 634, "avg_time": 3.7, "success_rate": 89.8},
        "Domicile Certificate": {"category": "Revenue", "requests": 521, "avg_time": 3.5, "success_rate": 93.2},
        "Birth Certificate": {"category": "Civil Registration", "requests": 489, "avg_time": 2.9, "success_rate": 95.7},
        "Death Certificate": {"category": "Civil Registration", "requests": 234, "avg_time": 2.6, "success_rate": 97.1},
        "Ration Card": {"category": "Food & Supply", "requests": 412, "avg_time": 4.5, "success_rate": 88.4},
        "Passport Application": {"category": "External Affairs", "requests": 378, "avg_time": 5.2, "success_rate": 90.6},
        "Voter ID Registration": {"category": "Election", "requests": 345, "avg_time": 3.1, "success_rate": 92.8},
        "Driving License": {"category": "Transport", "requests": 298, "avg_time": 3.8, "success_rate": 91.5},
        "Marriage Certificate": {"category": "Civil Registration", "requests": 267, "avg_time": 3.0, "success_rate": 94.2},
    }
    rows = [{"service": k, **v} for k, v in services.items()]
    return pd.DataFrame(rows)


def generate_timeseries(days=90, base=15, trend=0.1, noise=5):
    """Generate a daily timeseries with trend + noise."""
    dates = pd.date_range(end=datetime.now().date(), periods=days, freq="D")
    values = base + np.arange(days) * trend + np.random.normal(0, noise, days)
    values = np.clip(values, 0, None).astype(int)
    return pd.DataFrame({"date": dates, "count": values})


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# HELPER FUNCTIONS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def kpi_card(icon, value, label, delta=None, delta_direction="up"):
    """Render a styled KPI card."""
    delta_html = ""
    if delta:
        cls = "up" if delta_direction == "up" else "down"
        arrow = "▲" if delta_direction == "up" else "▼"
        delta_html = f'<div class="kpi-delta {cls}">{arrow} {delta}</div>'

    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-icon">{icon}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-label">{label}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


def section_header(title, icon=""):
    """Render a styled section header."""
    st.markdown(f'<div class="section-header">{icon} {title}</div>', unsafe_allow_html=True)


def plotly_dark_layout(fig, height=400):
    """Apply consistent dark theme to plotly figures."""
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#c7d2fe", size=12),
        height=height,
        margin=dict(l=40, r=20, t=40, b=40),
        legend=dict(bgcolor="rgba(0,0,0,0)", borderwidth=0),
        xaxis=dict(gridcolor="rgba(99,102,241,0.1)", zerolinecolor="rgba(99,102,241,0.1)"),
        yaxis=dict(gridcolor="rgba(99,102,241,0.1)", zerolinecolor="rgba(99,102,241,0.1)"),
    )
    return fig


# Color palette
COLORS = ["#818cf8", "#c084fc", "#f472b6", "#34d399", "#fbbf24", "#60a5fa", "#fb923c", "#a78bfa"]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SIDEBAR NAVIGATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 20px 0 10px 0;">
        <div style="font-size: 2.5rem;">🏛️</div>
        <div class="dashboard-title">Seva Form AI</div>
        <div class="dashboard-subtitle">Admin Analytics Dashboard</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    page = st.radio(
        "Navigation",
        [
            "📊 Overview",
            "📄 Document Analytics",
            "🎤 Voice Analytics",
            "🏢 Service Usage",
            "📝 Recent Submissions",
            "🧠 AI Performance",
            "💚 System Health",
        ],
        label_visibility="collapsed",
    )

    st.markdown("---")

    # Date range filter (global)
    st.markdown('<p style="color:#a5b4fc; font-weight:600; font-size:0.85rem;">📅 Date Range</p>', unsafe_allow_html=True)
    date_range = st.date_input(
        "Select range",
        value=(datetime.now().date() - timedelta(days=30), datetime.now().date()),
        label_visibility="collapsed",
    )

    # Auto-refresh toggle
    auto_refresh = st.toggle("🔄 Auto Refresh (5 min)", value=False)
    if auto_refresh:
        st.markdown('<p style="color:#34d399; font-size:0.75rem;">● Live — refreshing every 5 min</p>', unsafe_allow_html=True)
        time.sleep(0.1)  # placeholder — actual refresh handled by ttl

    st.markdown("---")
    st.markdown(
        '<p style="color:#475569; font-size:0.7rem; text-align:center;">v1.0.0 • Seva Form AI © 2026</p>',
        unsafe_allow_html=True,
    )

# Load data
df_submissions = generate_submissions_data()
df_documents = generate_document_data()
df_voice = generate_voice_data()
df_services = generate_service_data()


# ╔══════════════════════════════════════════════════════╗
# ║                 PAGE 1: OVERVIEW                      ║
# ╚══════════════════════════════════════════════════════╝

if page == "📊 Overview":
    st.markdown('<div class="dashboard-title" style="font-size:1.6rem;">📊 Dashboard Overview</div>', unsafe_allow_html=True)
    st.markdown('<p style="color:#64748b; margin-bottom:20px;">Real-time system metrics and analytics at a glance</p>', unsafe_allow_html=True)

    # ---- KPI Row ----
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        kpi_card("📝", f"{len(df_submissions):,}", "Total Submissions", "+12.4% vs last month", "up")
    with c2:
        kpi_card("📄", f"{len(df_documents):,}", "Documents Processed", "+8.7% vs last month", "up")
    with c3:
        kpi_card("🎤", f"{len(df_voice):,}", "Voice Requests", "+15.2% vs last month", "up")
    with c4:
        success_rate = round(len(df_documents[df_documents["status"] == "Success"]) / len(df_documents) * 100, 1)
        kpi_card("🎯", f"{success_rate}%", "AI Success Rate", "+2.1% improvement", "up")
    with c5:
        kpi_card("👥", "1,847", "Active Users", "+5.3% vs last month", "up")
    with c6:
        pdfs = df_submissions["pdf_generated"].sum()
        kpi_card("📑", f"{int(pdfs):,}", "PDFs Generated", "+9.8% vs last month", "up")

    st.markdown("<br>", unsafe_allow_html=True)

    # ---- Charts Row 1 ----
    col_left, col_right = st.columns([3, 2])

    with col_left:
        section_header("Submissions Over Time", "📈")
        ts = generate_timeseries(90, base=12, trend=0.15, noise=4)
        fig = px.area(ts, x="date", y="count", color_discrete_sequence=["#818cf8"])
        fig.update_traces(fill="tozeroy", fillcolor="rgba(129,140,248,0.15)", line=dict(width=2.5))
        fig = plotly_dark_layout(fig, 350)
        fig.update_layout(xaxis_title="", yaxis_title="Submissions")
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        section_header("Document Type Distribution", "🗂️")
        doc_dist = df_documents["document_type"].value_counts().reset_index()
        doc_dist.columns = ["Document Type", "Count"]
        fig = px.pie(doc_dist, names="Document Type", values="Count", hole=0.55, color_discrete_sequence=COLORS)
        fig = plotly_dark_layout(fig, 350)
        fig.update_traces(textinfo="percent+label", textfont_size=11)
        st.plotly_chart(fig, use_container_width=True)

    # ---- Charts Row 2 ----
    col_left2, col_right2 = st.columns(2)

    with col_left2:
        section_header("Service Usage (Top 10)", "🏢")
        top_services = df_services.nlargest(10, "requests")
        fig = px.bar(top_services, x="requests", y="service", orientation="h", color="requests",
                     color_continuous_scale=["#312e81", "#818cf8", "#c084fc"])
        fig = plotly_dark_layout(fig, 380)
        fig.update_layout(yaxis=dict(autorange="reversed"), coloraxis_showscale=False, xaxis_title="Requests", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

    with col_right2:
        section_header("Processing Pipeline", "⚙️")
        pipeline_data = pd.DataFrame({
            "Stage": ["Documents Uploaded", "OCR Processed", "Entities Extracted", "Forms Filled", "PDFs Generated"],
            "Count": [300, 278, 264, 234, int(pdfs)],
        })
        fig = go.Figure(go.Funnel(
            y=pipeline_data["Stage"], x=pipeline_data["Count"],
            textinfo="value+percent initial",
            marker=dict(color=COLORS[:5]),
            connector=dict(line=dict(color="rgba(99,102,241,0.3)", width=1)),
        ))
        fig = plotly_dark_layout(fig, 380)
        st.plotly_chart(fig, use_container_width=True)


# ╔══════════════════════════════════════════════════════╗
# ║           PAGE 2: DOCUMENT ANALYTICS                  ║
# ╚══════════════════════════════════════════════════════╝

elif page == "📄 Document Analytics":
    st.markdown('<div class="dashboard-title" style="font-size:1.6rem;">📄 Document Processing Analytics</div>', unsafe_allow_html=True)
    st.markdown('<p style="color:#64748b; margin-bottom:20px;">OCR pipeline performance and extraction metrics</p>', unsafe_allow_html=True)

    # KPIs
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi_card("📄", f"{len(df_documents):,}", "Total Processed", "+8.7%", "up")
    with c2:
        avg_conf = round(df_documents["confidence_score"].mean(), 1)
        kpi_card("🎯", f"{avg_conf}%", "Avg Confidence", "+1.3%", "up")
    with c3:
        avg_time = round(df_documents["processing_time_ms"].mean())
        kpi_card("⚡", f"{avg_time} ms", "Avg Processing Time", "-12% faster", "up")
    with c4:
        fail_rate = round(len(df_documents[df_documents["status"] == "Failed"]) / len(df_documents) * 100, 1)
        kpi_card("❌", f"{fail_rate}%", "Failure Rate", "-0.5%", "up")

    st.markdown("<br>", unsafe_allow_html=True)

    # Charts
    col1, col2 = st.columns(2)

    with col1:
        section_header("Documents Processed Per Day", "📊")
        daily = df_documents.groupby(df_documents["timestamp"].dt.date).size().reset_index(name="count")
        daily.columns = ["date", "count"]
        fig = px.bar(daily, x="date", y="count", color_discrete_sequence=["#818cf8"])
        fig = plotly_dark_layout(fig, 350)
        fig.update_layout(xaxis_title="", yaxis_title="Documents")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        section_header("Success vs Failed Extractions", "✅")
        status_counts = df_documents["status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]
        color_map = {"Success": "#34d399", "Partial": "#fbbf24", "Failed": "#f87171"}
        fig = px.bar(status_counts, x="Status", y="Count", color="Status", color_discrete_map=color_map)
        fig = plotly_dark_layout(fig, 350)
        fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="Count")
        st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        section_header("OCR Confidence Distribution", "📈")
        fig = px.histogram(df_documents, x="confidence_score", nbins=25, color_discrete_sequence=["#c084fc"])
        fig = plotly_dark_layout(fig, 350)
        fig.update_layout(xaxis_title="Confidence Score (%)", yaxis_title="Frequency")
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        section_header("Processing Time by Doc Type", "⏱️")
        fig = px.box(df_documents, x="document_type", y="processing_time_ms", color="document_type",
                     color_discrete_sequence=COLORS)
        fig = plotly_dark_layout(fig, 350)
        fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="Time (ms)")
        st.plotly_chart(fig, use_container_width=True)

    # Data Table
    section_header("Recent Document Processing Logs", "📋")

    # Filters
    fc1, fc2 = st.columns(2)
    with fc1:
        type_filter = st.multiselect("Filter by Document Type", df_documents["document_type"].unique(), default=[])
    with fc2:
        status_filter = st.multiselect("Filter by Status", df_documents["status"].unique(), default=[])

    filtered = df_documents.copy()
    if type_filter:
        filtered = filtered[filtered["document_type"].isin(type_filter)]
    if status_filter:
        filtered = filtered[filtered["status"].isin(status_filter)]

    st.dataframe(
        filtered.sort_values("timestamp", ascending=False).head(50).reset_index(drop=True),
        use_container_width=True,
        height=400,
    )

    # Export
    csv = filtered.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Export to CSV", csv, "document_analytics.csv", "text/csv")


# ╔══════════════════════════════════════════════════════╗
# ║            PAGE 3: VOICE ANALYTICS                    ║
# ╚══════════════════════════════════════════════════════╝

elif page == "🎤 Voice Analytics":
    st.markdown('<div class="dashboard-title" style="font-size:1.6rem;">🎤 Voice Form Analytics</div>', unsafe_allow_html=True)
    st.markdown('<p style="color:#64748b; margin-bottom:20px;">Speech-to-text pipeline performance and language insights</p>', unsafe_allow_html=True)

    # KPIs
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi_card("🎤", f"{len(df_voice):,}", "Voice Recordings", "+15.2%", "up")
    with c2:
        n_langs = df_voice["language"].nunique()
        kpi_card("🌐", str(n_langs), "Languages Detected")
    with c3:
        avg_acc = round(df_voice["transcription_accuracy"].mean(), 1)
        kpi_card("🎯", f"{avg_acc}%", "Avg Accuracy", "+1.8%", "up")
    with c4:
        avg_proc = round(df_voice["processing_time_ms"].mean())
        kpi_card("⚡", f"{avg_proc} ms", "Avg Process Time", "-8% faster", "up")

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        section_header("Languages Used", "🌍")
        lang_counts = df_voice["language"].value_counts().reset_index()
        lang_counts.columns = ["Language", "Count"]
        fig = px.pie(lang_counts, names="Language", values="Count", hole=0.5, color_discrete_sequence=COLORS)
        fig = plotly_dark_layout(fig, 380)
        fig.update_traces(textinfo="percent+label", textfont_size=11)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        section_header("Voice Requests Per Day", "📊")
        daily_voice = df_voice.groupby(df_voice["timestamp"].dt.date).size().reset_index(name="count")
        daily_voice.columns = ["date", "count"]
        fig = px.area(daily_voice, x="date", y="count", color_discrete_sequence=["#c084fc"])
        fig.update_traces(fill="tozeroy", fillcolor="rgba(192,132,252,0.15)", line=dict(width=2.5))
        fig = plotly_dark_layout(fig, 380)
        fig.update_layout(xaxis_title="", yaxis_title="Requests")
        st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        section_header("Transcription Accuracy by Language", "📈")
        fig = px.box(df_voice, x="language", y="transcription_accuracy", color="language",
                     color_discrete_sequence=COLORS)
        fig = plotly_dark_layout(fig, 380)
        fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="Accuracy (%)")
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        section_header("Recording Duration Distribution", "⏱️")
        fig = px.histogram(df_voice, x="duration_sec", nbins=20, color_discrete_sequence=["#f472b6"])
        fig = plotly_dark_layout(fig, 380)
        fig.update_layout(xaxis_title="Duration (seconds)", yaxis_title="Frequency")
        st.plotly_chart(fig, use_container_width=True)

    section_header("Transcribe vs Translate Usage", "🔄")
    mode_lang = df_voice.groupby(["language", "mode"]).size().reset_index(name="count")
    fig = px.bar(mode_lang, x="language", y="count", color="mode", barmode="group",
                 color_discrete_map={"transcribe": "#818cf8", "translate": "#f472b6"})
    fig = plotly_dark_layout(fig, 350)
    fig.update_layout(xaxis_title="", yaxis_title="Count")
    st.plotly_chart(fig, use_container_width=True)


# ╔══════════════════════════════════════════════════════╗
# ║           PAGE 4: SERVICE USAGE                       ║
# ╚══════════════════════════════════════════════════════╝

elif page == "🏢 Service Usage":
    st.markdown('<div class="dashboard-title" style="font-size:1.6rem;">🏢 Service Usage Analytics</div>', unsafe_allow_html=True)
    st.markdown('<p style="color:#64748b; margin-bottom:20px;">Government service request distribution and trends</p>', unsafe_allow_html=True)

    # KPIs
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        total_req = df_services["requests"].sum()
        kpi_card("📊", f"{total_req:,}", "Total Requests")
    with c2:
        top_service = df_services.loc[df_services["requests"].idxmax(), "service"]
        kpi_card("🥇", top_service.split()[0], "Top Service")
    with c3:
        n_categories = df_services["category"].nunique()
        kpi_card("🏷️", str(n_categories), "Categories")
    with c4:
        avg_sr = round(df_services["success_rate"].mean(), 1)
        kpi_card("✅", f"{avg_sr}%", "Avg Success Rate")

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        section_header("Top Requested Services", "📊")
        sorted_services = df_services.sort_values("requests", ascending=True)
        fig = px.bar(sorted_services, x="requests", y="service", orientation="h",
                     color="success_rate", color_continuous_scale=["#f87171", "#fbbf24", "#34d399"])
        fig = plotly_dark_layout(fig, 450)
        fig.update_layout(coloraxis_colorbar=dict(title="Success %"), xaxis_title="Requests", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        section_header("Requests by Category", "🏷️")
        cat_data = df_services.groupby("category")["requests"].sum().reset_index()
        fig = px.pie(cat_data, names="category", values="requests", hole=0.5, color_discrete_sequence=COLORS)
        fig = plotly_dark_layout(fig, 450)
        fig.update_traces(textinfo="percent+label", textfont_size=11)
        st.plotly_chart(fig, use_container_width=True)

    section_header("Service Performance Table", "📋")
    display_df = df_services.copy()
    display_df["avg_time"] = display_df["avg_time"].apply(lambda x: f"{x:.1f}s")
    display_df["success_rate"] = display_df["success_rate"].apply(lambda x: f"{x}%")
    display_df.columns = ["Service", "Category", "Requests", "Avg Time", "Success Rate"]
    st.dataframe(display_df.sort_values("Requests", ascending=False).reset_index(drop=True), use_container_width=True)

    section_header("Request Distribution (Treemap)", "🗺️")
    fig = px.treemap(df_services, path=["category", "service"], values="requests",
                     color="success_rate", color_continuous_scale=["#f87171", "#fbbf24", "#34d399"])
    fig = plotly_dark_layout(fig, 450)
    st.plotly_chart(fig, use_container_width=True)


# ╔══════════════════════════════════════════════════════╗
# ║          PAGE 5: RECENT SUBMISSIONS                   ║
# ╚══════════════════════════════════════════════════════╝

elif page == "📝 Recent Submissions":
    st.markdown('<div class="dashboard-title" style="font-size:1.6rem;">📝 Recent Form Submissions</div>', unsafe_allow_html=True)
    st.markdown('<p style="color:#64748b; margin-bottom:20px;">Browse, search and filter submitted applications</p>', unsafe_allow_html=True)

    # Filters
    fc1, fc2, fc3, fc4 = st.columns(4)
    with fc1:
        search = st.text_input("🔍 Search by Name or ID", "")
    with fc2:
        svc_filter = st.multiselect("🏢 Service", df_submissions["service_name"].unique(), default=[])
    with fc3:
        sts_filter = st.multiselect("📌 Status", df_submissions["status"].unique(), default=[])
    with fc4:
        pdf_filter = st.selectbox("📑 PDF Generated", ["All", "Yes", "No"])

    filtered = df_submissions.copy()
    if search:
        search_lower = search.lower()
        filtered = filtered[
            filtered["applicant_name"].str.lower().str.contains(search_lower)
            | filtered["submission_id"].str.lower().str.contains(search_lower)
        ]
    if svc_filter:
        filtered = filtered[filtered["service_name"].isin(svc_filter)]
    if sts_filter:
        filtered = filtered[filtered["status"].isin(sts_filter)]
    if pdf_filter == "Yes":
        filtered = filtered[filtered["pdf_generated"] == True]
    elif pdf_filter == "No":
        filtered = filtered[filtered["pdf_generated"] == False]

    # Sort
    filtered = filtered.sort_values("timestamp", ascending=False)

    # Summary KPIs for filtered data
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi_card("📝", f"{len(filtered):,}", "Showing Results")
    with c2:
        completed = len(filtered[filtered["status"] == "Completed"])
        kpi_card("✅", f"{completed:,}", "Completed")
    with c3:
        pending = len(filtered[filtered["status"] == "Pending"])
        kpi_card("⏳", f"{pending:,}", "Pending")
    with c4:
        failed = len(filtered[filtered["status"] == "Failed"])
        kpi_card("❌", f"{failed:,}", "Failed")

    st.markdown("<br>", unsafe_allow_html=True)

    # Display as table
    display_cols = ["submission_id", "applicant_name", "service_name", "timestamp", "status", "pdf_generated", "processing_time_s"]
    display_df = filtered[display_cols].copy()
    display_df.columns = ["ID", "Applicant", "Service", "Timestamp", "Status", "PDF", "Time (s)"]
    display_df["PDF"] = display_df["PDF"].map({True: "✅", False: "❌"})
    display_df["Timestamp"] = display_df["Timestamp"].dt.strftime("%Y-%m-%d %H:%M")

    st.dataframe(display_df.reset_index(drop=True), use_container_width=True, height=500)

    # Export
    csv = filtered.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Export Results to CSV", csv, "submissions.csv", "text/csv")


# ╔══════════════════════════════════════════════════════╗
# ║         PAGE 6: AI PERFORMANCE MONITORING             ║
# ╚══════════════════════════════════════════════════════╝

elif page == "🧠 AI Performance":
    st.markdown('<div class="dashboard-title" style="font-size:1.6rem;">🧠 AI Performance Monitoring</div>', unsafe_allow_html=True)
    st.markdown('<p style="color:#64748b; margin-bottom:20px;">Model accuracy, extraction quality, and processing benchmarks</p>', unsafe_allow_html=True)

    # KPIs
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi_card("🎯", "92.4%", "OCR Accuracy", "+1.7% this month", "up")
    with c2:
        kpi_card("🧩", "88.6%", "Entity Extraction Rate", "+2.3%", "up")
    with c3:
        kpi_card("⚡", "1.8s", "Avg Processing Time", "-0.3s faster", "up")
    with c4:
        kpi_card("🔌", "124 ms", "API Response Time", "-8 ms faster", "up")

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        section_header("Accuracy Trend (Last 90 Days)", "📈")
        days = 90
        dates = pd.date_range(end=datetime.now().date(), periods=days, freq="D")
        ocr_acc = np.clip(85 + np.arange(days) * 0.08 + np.random.normal(0, 1.5, days), 75, 99)
        ent_acc = np.clip(80 + np.arange(days) * 0.1 + np.random.normal(0, 2, days), 70, 98)
        acc_df = pd.DataFrame({"Date": dates, "OCR Accuracy": ocr_acc, "Entity Extraction": ent_acc})

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=acc_df["Date"], y=acc_df["OCR Accuracy"], name="OCR Accuracy",
                                 line=dict(color="#818cf8", width=2.5), fill="tozeroy",
                                 fillcolor="rgba(129,140,248,0.1)"))
        fig.add_trace(go.Scatter(x=acc_df["Date"], y=acc_df["Entity Extraction"], name="Entity Extraction",
                                 line=dict(color="#c084fc", width=2.5), fill="tozeroy",
                                 fillcolor="rgba(192,132,252,0.1)"))
        fig = plotly_dark_layout(fig, 380)
        fig.update_layout(yaxis_title="Accuracy (%)", yaxis_range=[70, 100])
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        section_header("Model Performance Comparison", "🏆")
        models = ["Aadhaar OCR", "PAN OCR", "Generic OCR", "Whisper STT", "Entity NLP"]
        accuracy = [94.5, 96.1, 88.3, 91.7, 88.6]
        speed = [1.2, 0.9, 0.7, 2.8, 0.3]
        model_df = pd.DataFrame({"Model": models, "Accuracy (%)": accuracy, "Avg Time (s)": speed})

        fig = go.Figure()
        fig.add_trace(go.Bar(name="Accuracy (%)", x=models, y=accuracy,
                             marker_color="#818cf8", text=accuracy, textposition="outside"))
        fig.add_trace(go.Bar(name="Avg Time (s)", x=models, y=[s * 30 for s in speed],
                             marker_color="#f472b6", text=speed, textposition="outside"))
        fig = plotly_dark_layout(fig, 380)
        fig.update_layout(barmode="group", yaxis_title="Score", legend=dict(orientation="h", y=1.15))
        st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        section_header("Entity Extraction by Field", "🧩")
        fields = ["Name", "DOB", "Gender", "Aadhaar No.", "PAN No.", "Father Name", "Address", "Pincode", "Mobile"]
        extraction_rates = [96.2, 93.8, 98.1, 91.5, 95.7, 85.3, 82.4, 89.6, 78.2]
        field_df = pd.DataFrame({"Field": fields, "Success Rate (%)": extraction_rates})
        field_df = field_df.sort_values("Success Rate (%)", ascending=True)

        fig = px.bar(field_df, x="Success Rate (%)", y="Field", orientation="h",
                     color="Success Rate (%)", color_continuous_scale=["#f87171", "#fbbf24", "#34d399"])
        fig = plotly_dark_layout(fig, 380)
        fig.update_layout(coloraxis_showscale=False, xaxis_range=[60, 100], xaxis_title="Success Rate (%)", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        section_header("Processing Time Breakdown", "⏱️")
        stages = ["Image Preprocessing", "OCR Extraction", "Entity Parsing", "Form Mapping", "Response"]
        times = [320, 850, 180, 95, 45]
        stage_df = pd.DataFrame({"Stage": stages, "Time (ms)": times})

        fig = px.bar(stage_df, x="Stage", y="Time (ms)", color="Time (ms)",
                     color_continuous_scale=["#34d399", "#fbbf24", "#f87171"])
        fig = plotly_dark_layout(fig, 380)
        fig.update_layout(coloraxis_showscale=False, xaxis_title="", yaxis_title="Time (ms)")
        st.plotly_chart(fig, use_container_width=True)


# ╔══════════════════════════════════════════════════════╗
# ║           PAGE 7: SYSTEM HEALTH                       ║
# ╚══════════════════════════════════════════════════════╝

elif page == "💚 System Health":
    st.markdown('<div class="dashboard-title" style="font-size:1.6rem;">💚 System Health Monitor</div>', unsafe_allow_html=True)
    st.markdown('<p style="color:#64748b; margin-bottom:20px;">Backend infrastructure, API status, and resource utilization</p>', unsafe_allow_html=True)

    # API Status Cards
    section_header("API Endpoint Status", "🔌")

    endpoints = [
        {"name": "GET /", "status": "Healthy", "latency": "12 ms", "uptime": "99.97%"},
        {"name": "GET /services", "status": "Healthy", "latency": "18 ms", "uptime": "99.95%"},
        {"name": "POST /documents/upload", "status": "Healthy", "latency": "1,842 ms", "uptime": "99.89%"},
        {"name": "POST /api/voice-fill-form", "status": "Healthy", "latency": "2,945 ms", "uptime": "99.82%"},
        {"name": "POST /api/submit-form", "status": "Healthy", "latency": "45 ms", "uptime": "99.98%"},
        {"name": "POST /api/generate-pdf", "status": "Warning", "latency": "3,210 ms", "uptime": "98.45%"},
    ]

    cols = st.columns(3)
    for i, ep in enumerate(endpoints):
        with cols[i % 3]:
            if ep["status"] == "Healthy":
                badge = '<span class="status-badge status-success">● Healthy</span>'
            elif ep["status"] == "Warning":
                badge = '<span class="status-badge status-pending">● Warning</span>'
            else:
                badge = '<span class="status-badge status-error">● Down</span>'

            st.markdown(f"""
            <div class="glass-panel">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                    <strong style="color:#e0e7ff; font-size:0.9rem;">{ep['name']}</strong>
                    {badge}
                </div>
                <div style="display:flex; justify-content:space-between; color:#94a3b8; font-size:0.8rem;">
                    <span>⚡ {ep['latency']}</span>
                    <span>🕐 Uptime: {ep['uptime']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Resource Gauges
    section_header("Resource Utilization", "📊")

    c1, c2, c3, c4 = st.columns(4)
    cpu_usage = 34
    memory_usage = 62
    disk_usage = 45
    gpu_usage = 28

    for col, (label, value, color) in zip(
        [c1, c2, c3, c4],
        [("CPU Usage", cpu_usage, "#818cf8"), ("Memory Usage", memory_usage, "#c084fc"),
         ("Disk Usage", disk_usage, "#34d399"), ("GPU Usage", gpu_usage, "#f472b6")]
    ):
        with col:
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=value,
                number=dict(suffix="%", font=dict(color="#e0e7ff", size=36)),
                title=dict(text=label, font=dict(color="#94a3b8", size=14)),
                gauge=dict(
                    axis=dict(range=[0, 100], tickcolor="#475569", dtick=25),
                    bar=dict(color=color, thickness=0.8),
                    bgcolor="rgba(30,27,75,0.5)",
                    borderwidth=0,
                    steps=[
                        dict(range=[0, 60], color="rgba(30,27,75,0.3)"),
                        dict(range=[60, 85], color="rgba(251,191,36,0.1)"),
                        dict(range=[85, 100], color="rgba(248,113,113,0.1)"),
                    ],
                    threshold=dict(line=dict(color="#f87171", width=3), thickness=0.8, value=85),
                ),
            ))
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#c7d2fe"), height=220, margin=dict(l=30, r=30, t=50, b=10),
            )
            st.plotly_chart(fig, use_container_width=True)

    # Latency Over Time
    col1, col2 = st.columns(2)

    with col1:
        section_header("API Latency Over Time", "📈")
        days = 30
        dates = pd.date_range(end=datetime.now().date(), periods=days, freq="D")
        latency_df = pd.DataFrame({
            "Date": dates,
            "OCR Pipeline": np.clip(np.random.normal(1800, 200, days), 1200, 2800),
            "Voice Pipeline": np.clip(np.random.normal(2900, 350, days), 1800, 4200),
            "Form Submission": np.clip(np.random.normal(45, 10, days), 20, 100),
        })
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=latency_df["Date"], y=latency_df["OCR Pipeline"],
                                 name="OCR", line=dict(color="#818cf8", width=2)))
        fig.add_trace(go.Scatter(x=latency_df["Date"], y=latency_df["Voice Pipeline"],
                                 name="Voice", line=dict(color="#c084fc", width=2)))
        fig = plotly_dark_layout(fig, 350)
        fig.update_layout(yaxis_title="Latency (ms)")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        section_header("Requests Per Hour (Today)", "🕐")
        hours = list(range(24))
        # Simulate realistic daily pattern (peak at 10-14h)
        pattern = [2, 1, 1, 0, 0, 1, 3, 8, 15, 22, 28, 25, 30, 27, 20, 18, 14, 10, 8, 6, 4, 3, 3, 2]
        noise = np.random.randint(-2, 3, 24)
        reqs = np.clip(np.array(pattern) + noise, 0, None)
        hour_df = pd.DataFrame({"Hour": hours, "Requests": reqs})
        fig = px.bar(hour_df, x="Hour", y="Requests", color_discrete_sequence=["#818cf8"])
        fig = plotly_dark_layout(fig, 350)
        fig.update_layout(xaxis_title="Hour of Day", yaxis_title="Requests", xaxis_dtick=2)
        st.plotly_chart(fig, use_container_width=True)

    # System Info
    section_header("System Information", "ℹ️")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div class="glass-panel">
            <p style="color:#a5b4fc; font-weight:600; margin-bottom:8px;">🖥️ Backend</p>
            <p style="color:#94a3b8; font-size:0.85rem; margin:3px 0;">Framework: <span style="color:#e0e7ff;">FastAPI 0.100+</span></p>
            <p style="color:#94a3b8; font-size:0.85rem; margin:3px 0;">Server: <span style="color:#e0e7ff;">Uvicorn (ASGI)</span></p>
            <p style="color:#94a3b8; font-size:0.85rem; margin:3px 0;">Python: <span style="color:#e0e7ff;">3.10+</span></p>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="glass-panel">
            <p style="color:#a5b4fc; font-weight:600; margin-bottom:8px;">🤖 AI Models</p>
            <p style="color:#94a3b8; font-size:0.85rem; margin:3px 0;">OCR: <span style="color:#e0e7ff;">Tesseract 5 + OpenCV</span></p>
            <p style="color:#94a3b8; font-size:0.85rem; margin:3px 0;">STT: <span style="color:#e0e7ff;">Whisper (base)</span></p>
            <p style="color:#94a3b8; font-size:0.85rem; margin:3px 0;">NLP: <span style="color:#e0e7ff;">Regex Entity Extraction</span></p>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="glass-panel">
            <p style="color:#a5b4fc; font-weight:600; margin-bottom:8px;">🕐 Uptime</p>
            <p style="color:#94a3b8; font-size:0.85rem; margin:3px 0;">Started: <span style="color:#e0e7ff;">2026-03-01 06:00 IST</span></p>
            <p style="color:#94a3b8; font-size:0.85rem; margin:3px 0;">Uptime: <span style="color:#34d399;">3 days, 14 hours</span></p>
            <p style="color:#94a3b8; font-size:0.85rem; margin:3px 0;">Last check: <span style="color:#e0e7ff;">{datetime.now().strftime('%H:%M:%S IST')}</span></p>
        </div>
        """, unsafe_allow_html=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# AUTO-REFRESH LOGIC
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if auto_refresh:
    time.sleep(300)  # 5-minute interval
    st.rerun()
