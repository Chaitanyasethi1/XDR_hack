"""
AI Adaptive XDR – Civic Cyber Shield
Main Streamlit Dashboard
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import datetime

from simulator import (
    generate_normal_activity,
    simulate_phishing_attack,
    simulate_credential_breach,
    simulate_insider_threat,
)
from anomaly import AnomalyDetector
from phishing import PhishingDetector
from risk_engine import compute_risk_scores
from incident_response import process_incidents

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Adaptive XDR – Civic Cyber Shield",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Professional Slate UI CSS ────────────────────────────────────────────────
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">

<style>
    /* Global Styles */
    .stApp {
        background-color: #0f172a;
        color: #f8fafc;
        font-family: 'Inter', sans-serif;
    }
    
    [data-testid="stHeader"] {
        background: #0f172a !important;
    }

    .main-title {
        text-align: center;
        font-size: 2.2rem;
        font-weight: 700;
        color: #ffffff;
        padding: 1.5rem 0 0.5rem 0;
    }
    
    .sub-title {
        text-align: center;
        font-size: 0.85rem;
        color: #94a3b8;
        margin-bottom: 2rem;
        text-transform: uppercase;
        font-weight: 500;
        letter-spacing: 1px;
    }

    /* Professional Metric Cards */
    .kpi-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 1.2rem;
        text-align: center;
    }
    
    .kpi-value {
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0px;
    }

    .kpi-label {
        font-size: 0.7rem;
        color: #94a3b8;
        text-transform: uppercase;
        font-weight: 600;
    }

    /* Signal Colors */
    .kpi-critical { color: #ef4444; }
    .kpi-warn { color: #f59e0b; }
    .kpi-ok { color: #10b981; }
    .kpi-cyan { color: #3b82f6; }

    /* Section Headers */
    .section-header {
        font-size: 1rem;
        font-weight: 600;
        color: #f8fafc;
        border-bottom: 1px solid #334155;
        padding-bottom: 0.5rem;
        margin: 2rem 0 1rem 0;
    }

    /* Buttons */
    div.stButton > button {
        background-color: #1e293b;
        color: #f1f5f9;
        border: 1px solid #334155;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-weight: 500;
    }

    div.stButton > button:hover {
        background-color: #334155;
        color: #ffffff;
    }

    /* Containers */
    div[data-testid="stExpander"] { background: #1e293b; border: 1px solid #334155; }
    div[data-testid="stDataFrame"] { background: #1e293b; border: 1px solid #334155; }
</style>
""", unsafe_allow_html=True)

# ── Initialize Models (cached) ──────────────────────────────────────────────
@st.cache_resource
def load_models():
    anomaly_detector = AnomalyDetector()
    phishing_detector = PhishingDetector()
    phishing_detector.train()
    baseline = generate_normal_activity(200)
    anomaly_detector.fit(baseline)
    return anomaly_detector, phishing_detector

anomaly_detector, phishing_detector = load_models()

# ── Session State ────────────────────────────────────────────────────────────
if "event_log" not in st.session_state:
    baseline = generate_normal_activity(80)
    baseline = anomaly_detector.predict(baseline)
    baseline = phishing_detector.predict(baseline)
    baseline = compute_risk_scores(baseline)
    st.session_state.event_log = baseline
    st.session_state.incidents = process_incidents(baseline)
    st.session_state.attack_history = []

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown('<div class="main-title">AI Adaptive XDR – Civic Cyber Shield</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Municipal Extended Detection & Response • Real-Time AI Threat Intelligence</div>', unsafe_allow_html=True)

df = st.session_state.event_log

# ── KPI Row ──────────────────────────────────────────────────────────────────
active_threats = int((df["risk_level"].isin(["HIGH", "CRITICAL"])).sum())
avg_risk = float(df["risk_score"].mean())
incidents_today = len(st.session_state.incidents)
max_risk = float(df["risk_score"].max())

risk_color = "kpi-critical" if avg_risk > 60 else ("kpi-warn" if avg_risk > 35 else "kpi-ok")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"""<div class="kpi-card">
        <div class="kpi-value kpi-critical">{active_threats}</div>
        <div class="kpi-label">Active Threats</div>
    </div>""", unsafe_allow_html=True)
with col2:
    st.markdown(f"""<div class="kpi-card">
        <div class="kpi-value {risk_color}">{avg_risk:.1f}</div>
        <div class="kpi-label">Avg Risk Score</div>
    </div>""", unsafe_allow_html=True)
with col3:
    st.markdown(f"""<div class="kpi-card">
        <div class="kpi-value kpi-warn">{incidents_today}</div>
        <div class="kpi-label">Incidents Today</div>
    </div>""", unsafe_allow_html=True)
with col4:
    st.markdown(f"""<div class="kpi-card">
        <div class="kpi-value kpi-critical">{max_risk:.0f}</div>
        <div class="kpi-label">Peak Risk Score</div>
    </div>""", unsafe_allow_html=True)

st.markdown("")

# ── Charts Row ───────────────────────────────────────────────────────────────
chart_left, chart_right = st.columns([1, 1])

with chart_left:
    st.markdown('<div class="section-header">Risk Gauge</div>', unsafe_allow_html=True)
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=avg_risk,
        delta={"reference": 35, "increasing": {"color": "#ff2d55"}, "decreasing": {"color": "#00e676"}},
        title={"text": "System Risk Level", "font": {"color": "#8892a0", "size": 14}},
        number={"font": {"color": "#e0e6ed", "size": 40}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": "#3a4a5a", "tickfont": {"color": "#6b7b8d"}},
            "bar": {"color": "#00d4ff"},
            "bgcolor": "#121929",
            "bordercolor": "#1e2d3d",
            "steps": [
                {"range": [0, 30], "color": "#0a2e1a"},
                {"range": [30, 55], "color": "#2e2a0a"},
                {"range": [55, 75], "color": "#2e1a0a"},
                {"range": [75, 100], "color": "#2e0a0f"},
            ],
            "threshold": {
                "line": {"color": "#ff2d55", "width": 3},
                "thickness": 0.8,
                "value": 75,
            },
        },
    ))
    fig_gauge.update_layout(
        height=280,
        margin=dict(t=50, b=20, l=30, r=30),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#e0e6ed"},
    )
    st.plotly_chart(fig_gauge, use_container_width=True)

with chart_right:
    st.markdown('<div class="section-header">Threat Trend</div>', unsafe_allow_html=True)
    # Build time series from event log
    trend_df = df.copy()
    trend_df["timestamp"] = pd.to_datetime(trend_df["timestamp"])
    trend_df = trend_df.sort_values("timestamp")
    trend_df["cumulative_risk"] = trend_df["risk_score"].expanding().mean()

    fig_trend = go.Figure()
    fig_trend.add_trace(go.Scatter(
        x=trend_df["timestamp"].tolist(),
        y=trend_df["risk_score"].tolist(),
        mode="markers",
        marker=dict(
            size=6,
            color=trend_df["risk_score"].tolist(),
            colorscale=[[0, "#00e676"], [0.4, "#ffaa00"], [0.7, "#ff6b35"], [1, "#ff2d55"]],
            opacity=0.7,
        ),
        name="Event Risk",
    ))
    fig_trend.add_trace(go.Scatter(
        x=trend_df["timestamp"].tolist(),
        y=trend_df["cumulative_risk"].tolist(),
        mode="lines",
        line=dict(color="#00d4ff", width=2),
        name="Avg Trend",
    ))
    fig_trend.add_hline(y=75, line_dash="dash", line_color="#ff2d55", opacity=0.5,
                         annotation_text="CRITICAL", annotation_font_color="#ff2d55")
    fig_trend.update_layout(
        height=280,
        margin=dict(t=20, b=40, l=40, r=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(gridcolor="#1e2d3d", tickfont={"color": "#6b7b8d"}),
        yaxis=dict(gridcolor="#1e2d3d", tickfont={"color": "#6b7b8d"}, title="Risk Score"),
        legend=dict(font={"color": "#8892a0"}, bgcolor="rgba(0,0,0,0)"),
        font={"color": "#e0e6ed"},
    )
    st.plotly_chart(fig_trend, use_container_width=True)

# ── Department Risk Breakdown ────────────────────────────────────────────────
st.markdown('<div class="section-header">Risk by Department</div>', unsafe_allow_html=True)
dept_risk = df.groupby("department")["risk_score"].mean().sort_values(ascending=True)
fig_dept = go.Figure(go.Bar(
    x=dept_risk.values.tolist(),
    y=dept_risk.index.tolist(),
    orientation="h",
    marker=dict(
        color=dept_risk.values.tolist(),
        colorscale=[[0, "#00e676"], [0.5, "#ffaa00"], [1, "#ff2d55"]],
    ),
))
fig_dept.update_layout(
    height=300,
    margin=dict(t=10, b=30, l=100, r=20),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=dict(gridcolor="#1e2d3d", tickfont={"color": "#6b7b8d"}, title="Avg Risk Score"),
    yaxis=dict(tickfont={"color": "#8892a0"}),
    font={"color": "#e0e6ed"},
)
st.plotly_chart(fig_dept, use_container_width=True)

# ── Attack Simulation ────────────────────────────────────────────────────────
st.markdown('<div class="section-header">Attack Simulation Console</div>', unsafe_allow_html=True)
sim_col1, sim_col2, sim_col3 = st.columns(3)

def run_simulation(attack_fn, attack_name):
    """Run an attack simulation and update state."""
    new_events = attack_fn()
    new_events = anomaly_detector.predict(new_events)
    new_events = phishing_detector.predict(new_events)
    new_events = compute_risk_scores(new_events)
    st.session_state.event_log = pd.concat([st.session_state.event_log, new_events], ignore_index=True)
    new_incidents = process_incidents(new_events)
    st.session_state.incidents.extend(new_incidents)
    st.session_state.attack_history.append({
        "type": attack_name,
        "time": datetime.datetime.now().strftime("%H:%M:%S"),
        "events": len(new_events),
        "incidents": len(new_incidents),
    })

with sim_col1:
    if st.button("⚡ Simulate Phishing Attack", use_container_width=True):
        run_simulation(simulate_phishing_attack, "Phishing")
        st.rerun()

with sim_col2:
    if st.button("🔓 Simulate Credential Breach", use_container_width=True):
        run_simulation(simulate_credential_breach, "Credential Breach")
        st.rerun()

with sim_col3:
    if st.button("👤 Simulate Insider Threat", use_container_width=True):
        run_simulation(simulate_insider_threat, "Insider Threat")
        st.rerun()

if st.session_state.attack_history:
    st.markdown("")
    for atk in reversed(st.session_state.attack_history[-5:]):
        st.markdown(
            f"<span style='color:#6b7b8d'>[{atk['time']}]</span> "
            f"<span style='color:#ff6b35'>{atk['type']}</span> — "
            f"{atk['events']} events, {atk['incidents']} incidents generated",
            unsafe_allow_html=True,
        )

# ── Alert / Incident Table ──────────────────────────────────────────────────
st.markdown('<div class="section-header">Active Alerts & Incidents</div>', unsafe_allow_html=True)

if st.session_state.incidents:
    inc_df = pd.DataFrame(st.session_state.incidents)
    inc_df = inc_df.sort_values("risk_score", ascending=False)

    display_df = inc_df[["timestamp", "user_id", "department", "event_type", "risk_score", "risk_level", "action"]].copy()
    display_df.columns = ["Timestamp", "User", "Department", "Threat Type", "Risk Score", "Severity", "Action"]

    def color_severity(val):
        colors = {"CRITICAL": "#ff2d55", "HIGH": "#ff6b35", "MEDIUM": "#ffaa00", "LOW": "#00e676"}
        return f"color: {colors.get(val, '#e0e6ed')}"

    st.dataframe(
        display_df.head(20).style.applymap(color_severity, subset=["Severity"]),
        use_container_width=True,
        height=350,
    )
else:
    st.info("No incidents detected. System operating within normal parameters.")

# ── Incident Detail Panel ───────────────────────────────────────────────────
st.markdown('<div class="section-header">Incident Reports</div>', unsafe_allow_html=True)

if st.session_state.incidents:
    for i, inc in enumerate(reversed(st.session_state.incidents[-10:])):
        severity_emoji = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🟢"}.get(inc["risk_level"], "⚪")
        with st.expander(
            f"{severity_emoji} {inc['risk_level']} — {inc['user_id']} — {inc['event_type']} (Risk: {inc['risk_score']:.0f})"
        ):
            st.code(inc["summary"], language=None)
else:
    st.info("No incident reports to display.")

# ── Footer ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:#3a4a5a; font-size:0.8rem;'>"
    "AI Adaptive XDR – Civic Cyber Shield • Powered by Isolation Forest & TF-IDF/LR • "
    f"Events Processed: {len(df)} • {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    "</div>",
    unsafe_allow_html=True,
)
