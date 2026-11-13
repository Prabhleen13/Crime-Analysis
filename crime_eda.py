import streamlit as st
import pandas as pd
import plotly.express as px
import os
import plotly.graph_objects as go
from datetime import datetime
import mysql.connector
from scipy.stats import chi2_contingency
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import pydeck as pdk
from sklearn.ensemble import IsolationForest
from io import BytesIO
from html import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak
)


# ============================================================
# CRIME ANALYSIS | REDESIGNED INTELLIGENCE WORKSPACE
# Requirements: streamlit, pandas, plotly
# ============================================================

st.set_page_config(
    page_title="Crime Analysis | Intelligence Workspace",
    page_icon="⌁",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ----------------------------- THEMES -----------------------
THEMES = {
    "Obsidian / Cyan": {
        "bg": "#080D18", "surface": "#111B2B", "surface2": "#17253A",
        "text": "#EDF5FF", "muted": "#91A4BC", "line": "#263750",
        "primary": "#38E0D0", "secondary": "#9B8CFF", "accent": "#55B8FF",
        "danger": "#FF6B83", "warning": "#FFC766",
        "palette": ["#38E0D0", "#9B8CFF", "#55B8FF", "#FF6B83",
                    "#FFC766", "#8CE99A", "#F78FB3", "#A5B4FC"]
    },
    "Ocean / Ice": {
        "bg": "#071923", "surface": "#102B3A", "surface2": "#17394A",
        "text": "#ECFAFF", "muted": "#A1C2D0", "line": "#285064",
        "primary": "#5DE2E7", "secondary": "#A6F0D2", "accent": "#75B9FF",
        "danger": "#FF829D", "warning": "#FFD37A",
        "palette": ["#5DE2E7", "#A6F0D2", "#75B9FF", "#FF829D",
                    "#FFD37A", "#C4B5FD", "#F9A8D4", "#A7F3D0"]
    },
    "Emerald / Gold": {
        "bg": "#101812", "surface": "#1A2A20", "surface2": "#24392C",
        "text": "#F0F8F1", "muted": "#A9BDAE", "line": "#354D3D",
        "primary": "#78E0A3", "secondary": "#E7C879", "accent": "#69CBB8",
        "danger": "#F28B82", "warning": "#F4D06F",
        "palette": ["#78E0A3", "#E7C879", "#69CBB8", "#F28B82",
                    "#F4D06F", "#A7C7E7", "#D6A6E8", "#B7E4C7"]
    },
    "Sunset / Rose": {
        "bg": "#1B1020", "surface": "#2D1B32", "surface2": "#402544",
        "text": "#FFF2F5", "muted": "#D2B6C7", "line": "#57344F",
        "primary": "#FF9671", "secondary": "#D6A3FF", "accent": "#FFD166",
        "danger": "#FF6685", "warning": "#FFC857",
        "palette": ["#FF9671", "#D6A3FF", "#FFD166", "#FF6685",
                    "#8BE0C2", "#83B9FF", "#F7A8C8", "#C4B5FD"]
    },
    "Paper / Indigo": {
        "bg": "#F2F5FA", "surface": "#FFFFFF", "surface2": "#E8EDF6",
        "text": "#182238", "muted": "#65738A", "line": "#D7DFEA",
        "primary": "#3D5AFE", "secondary": "#8B5CF6", "accent": "#0891B2",
        "danger": "#E54865", "warning": "#D97706",
        "palette": ["#3D5AFE", "#8B5CF6", "#0891B2", "#E54865",
                    "#D97706", "#059669", "#DB2777", "#64748B"]
    },
        "Espresso / Champagne": {
        "bg": "#17120F", "surface": "#251C17", "surface2": "#35271F",
        "text": "#F8F0E7", "muted": "#C1AD9B", "line": "#574234",
        "primary": "#D6A875", "secondary": "#B98B68", "accent": "#E8C9A5",
        "danger": "#D98272", "warning": "#E8C477",
        "palette": ["#D6A875", "#B98B68", "#E8C9A5", "#D98272",
                    "#E8C477", "#A8B89A", "#C99A9A", "#A9B9C9"]
    },
        "Netflix / Crimson": {
        "bg": "#080808", "surface": "#171717", "surface2": "#242424",
        "text": "#FFFFFF", "muted": "#B3B3B3", "line": "#383838",
        "primary": "#E50914", "secondary": "#B20710", "accent": "#FF3344",
        "danger": "#FF5A5F", "warning": "#F5C518",
        "palette": ["#E50914", "#FF3344", "#B20710", "#F5C518",
                    "#FFFFFF", "#A3A3A3", "#8B0000", "#D9D9D9"]
    }

}
#-------------------------------CSS-----------------------------------------------------
def inject_style(t):
    st.markdown(f"""
    <style>

    @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;500;600;700;800&display=swap');

    :root {{
        --bg: {t["bg"]};
        --surface: {t["surface"]};
        --surface2: {t["surface2"]};
        --text: {t["text"]};
        --muted: {t["muted"]};
        --line: {t["line"]};
        --primary: {t["primary"]};
        --secondary: {t["secondary"]};
        --accent: {t["accent"]};
        --danger: {t["danger"]};
        --warning: {t["warning"]};
    }}

    /* ---------------- GLOBAL APP ---------------- */

    html, body, [class*="css"] {{
        font-family: 'Manrope', sans-serif;
    }}

    .stApp {{
        background: var(--bg);
        color: var(--text);
    }}

    .block-container {{
        max-width: 1500px;
        width: 100%;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }}

    h1, h2, h3, h4, h5, h6 {{
        font-family: 'Manrope', sans-serif;
        color: var(--text);
        font-weight: 800;
    }}

    p, label, span, div {{
        font-family: 'Manrope', sans-serif;
    }}

    /* ---------------- SIDEBAR ---------------- */

    section[data-testid="stSidebar"] {{
        background: var(--surface);
        border-right: 1px solid var(--line);
    }}

    section[data-testid="stSidebar"] * {{
        color: var(--text);
    }}

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {{
        color: var(--primary);
    }}

    /* ---------------- WELCOME SECTION ---------------- */

    .welcome-box {{
        padding: 38px;
        border-radius: 22px;
        background: linear-gradient(
            120deg,
            var(--surface),
            var(--surface2)
        );
        border: 1px solid var(--line);
        margin-bottom: 28px;
        box-shadow: 0 10px 35px rgba(0,0,0,0.12);
    }}

    .welcome-box h1 {{
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 10px;
        color: var(--text);
    }}

    .welcome-box p {{
        color: var(--muted);
        font-size: 1rem;
        line-height: 1.8;
    }}

    /* ---------------- HERO SECTION ---------------- */

    .hero {{
        padding: 28px 32px;
        border-radius: 18px;
        background: var(--surface);
        border: 1px solid var(--line);
        margin: 20px 0 25px 0;
        box-shadow: 0 8px 25px rgba(0,0,0,0.10);
    }}

    .hero .eyebrow,
    .eyebrow {{
        color: var(--primary);
        font-family: 'DM Mono', monospace;
        font-size: 0.75rem;
        letter-spacing: 2px;
        text-transform: uppercase;
        font-weight: 500;
    }}

    .hero h1 {{
        font-size: 2.2rem;
        margin: 8px 0;
        color: var(--text);
    }}

    .hero p {{
        color: var(--muted);
        font-size: 0.95rem;
        margin-bottom: 0;
    }}

    /* ---------------- WORKSPACE HEADING ---------------- */

    .workspace-heading {{
        padding: 24px 4px 18px 4px;
    }}

    .workspace-heading h2 {{
        font-size: 2rem;
        font-weight: 800;
        margin: 8px 0;
        color: var(--text);
    }}

    .workspace-heading p {{
        color: var(--muted);
        font-size: 1rem;
    }}

    /* ---------------- NAVIGATION CARDS - FULL WIDTH ---------------- */

    div[data-testid="stRadio"] {{
        width: 100% !important;
        max-width: 100% !important;
    }}

    div[data-testid="stRadio"] > div {{
        width: 100% !important;
        max-width: 100% !important;
    }}

    div[data-testid="stRadio"] div[role="radiogroup"] {{
        display: grid !important;
        grid-template-columns: repeat(4, minmax(0, 1fr)) !important;
        gap: 16px;
        width: 100% !important;
        max-width: 100% !important;
    }}

    div[data-testid="stRadio"] div[role="radiogroup"] label {{
        width: 100% !important;
        min-width: 0 !important;
        min-height: 125px;
        box-sizing: border-box;
        margin: 0 !important;
        padding: 22px 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
        background: var(--surface);
        border: 1px solid var(--line);
        border-radius: 17px;
        cursor: pointer;
        transition: all 0.22s ease;
    }}

    div[data-testid="stRadio"] div[role="radiogroup"] label:hover {{
        background: var(--surface2);
        border-color: var(--primary);
        box-shadow: 0 8px 22px rgba(0,0,0,0.22);
        transform: translateY(-5px);
    }}

    div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) {{
        background: var(--surface2);
        border: 2px solid var(--primary);
        box-shadow: 0 5px 18px rgba(0,0,0,0.18);
    }}

    div[data-testid="stRadio"] div[role="radiogroup"] label p {{
        color: var(--text);
        font-weight: 700;
        font-size: 0.9rem;
    }}

    div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) p {{
        color: var(--primary);
    }}

    /* ---------------- METRIC CARDS ---------------- */

    [data-testid="stMetric"] {{
        background: var(--surface);
        border: 1px solid var(--line);
        border-radius: 16px;
        padding: 18px 20px;
        transition: all 0.2s ease;
    }}

    [data-testid="stMetric"]:hover {{
        border-color: var(--primary);
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.12);
    }}

    [data-testid="stMetricLabel"] {{
        color: var(--muted);
        font-weight: 600;
    }}

    [data-testid="stMetricValue"] {{
        color: var(--primary);
        font-weight: 800;
    }}

    [data-testid="stMetricDelta"] {{
        font-family: 'DM Mono', monospace;
    }}

    /* ---------------- TABS ---------------- */

    .stTabs [data-baseweb="tab-list"] {{
        gap: 10px;
        border-bottom: 1px solid var(--line);
    }}

    .stTabs [data-baseweb="tab"] {{
        background: var(--surface);
        border-radius: 10px 10px 0 0;
        padding: 12px 18px;
        color: var(--muted);
        font-weight: 700;
    }}

    .stTabs [aria-selected="true"] {{
        color: var(--primary) !important;
        border-bottom: 3px solid var(--primary);
    }}

    /* ---------------- INPUTS AND FILTERS ---------------- */

    .stSelectbox > div > div,
    .stMultiSelect > div > div,
    .stTextInput > div > div,
    .stNumberInput > div > div,
    .stDateInput > div > div {{
        background: var(--surface);
        border-color: var(--line);
        border-radius: 10px;
        color: var(--text);
    }}

    div[data-baseweb="select"] {{
        background: var(--surface);
    }}

    div[data-baseweb="select"] * {{
        color: var(--text);
    }}

    .stSlider [data-baseweb="slider"] {{
        color: var(--primary);
    }}

    /* ---------------- BUTTONS ---------------- */

    .stButton button,
    .stDownloadButton button,
    .stLinkButton a {{
        border-radius: 11px;
        border: 1px solid var(--line);
        background: var(--surface);
        color: var(--text);
        font-weight: 700;
        padding: 9px 18px;
        transition: all 0.22s ease;
    }}

    .stButton button:hover,
    .stDownloadButton button:hover,
    .stLinkButton a:hover {{
        border-color: var(--primary);
        color: var(--primary);
        background: var(--surface2);
        transform: translateY(-2px);
        box-shadow: 0 5px 16px rgba(0,0,0,0.16);
    }}

    .stButton button[kind="primary"] {{
        background: var(--primary);
        color: #111111;
        border: 1px solid var(--primary);
        font-weight: 800;
    }}

    .stButton button[kind="primary"]:hover {{
        filter: brightness(1.12);
        box-shadow: 0 0 18px var(--primary);
        transform: translateY(-3px);
    }}

    /* ---------------- VIDEO BUTTON ---------------- */

    .video-button {{
        border-radius: 14px;
        padding: 15px 25px;
        font-weight: 800;
        background: var(--primary);
        color: #111111;
        transition: all 0.25s ease;
    }}

    .video-button:hover {{
        transform: scale(1.04);
        box-shadow: 0 0 22px var(--primary);
    }}

    /* ---------------- DATA TABLES ---------------- */

    [data-testid="stDataFrame"],
    [data-testid="stTable"] {{
        border: 1px solid var(--line);
        border-radius: 12px;
        overflow: hidden;
    }}

    [data-testid="stDataFrame"] {{
        background: var(--surface);
    }}

    /* ---------------- EXPANDERS ---------------- */

    [data-testid="stExpander"] {{
        background: var(--surface);
        border: 1px solid var(--line);
        border-radius: 12px;
    }}

    [data-testid="stExpander"] summary {{
        color: var(--text);
        font-weight: 700;
    }}

    /* ---------------- ALERTS AND INFO BOXES ---------------- */

    [data-testid="stAlert"] {{
        border-radius: 12px;
        border: 1px solid var(--line);
    }}

    .stAlert p {{
        color: var(--text);
    }}

    /* ---------------- DIVIDERS ---------------- */

    hr {{
        border-color: var(--line);
        opacity: 0.7;
        margin-top: 25px;
        margin-bottom: 25px;
    }}

    /* ---------------- CAPTIONS AND NOTES ---------------- */

    .stCaption,
    [data-testid="stCaptionContainer"] {{
        color: var(--muted);
    }}

    .note {{
        background: var(--surface);
        border-left: 4px solid var(--primary);
        border-radius: 9px;
        padding: 14px 18px;
        color: var(--muted);
        margin: 12px 0;
    }}

    /* ---------------- FOOTER ---------------- */

    .footer {{
        text-align: center;
        padding: 25px 10px;
        margin-top: 40px;
        border-top: 1px solid var(--line);
        color: var(--muted);
        font-size: 0.82rem;
    }}

    /* ---------------- SCROLLBAR ---------------- */

    ::-webkit-scrollbar {{
        width: 9px;
        height: 9px;
    }}

    ::-webkit-scrollbar-track {{
        background: var(--bg);
    }}

    ::-webkit-scrollbar-thumb {{
        background: var(--secondary);
        border-radius: 10px;
    }}

    ::-webkit-scrollbar-thumb:hover {{
        background: var(--primary);
    }}

    /* ---------------- RESPONSIVE LAYOUT ---------------- */

    @media (max-width: 900px) {{
        div[data-testid="stRadio"] div[role="radiogroup"] {{
            grid-template-columns: repeat(3, minmax(0, 1fr)) !important;
        }}

        .welcome-box h1 {{
            font-size: 2rem;
        }}

        .hero h1 {{
            font-size: 1.8rem;
        }}
    }}

    @media (max-width: 600px) {{
        div[data-testid="stRadio"] div[role="radiogroup"] {{
            grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
        }}

        div[data-testid="stRadio"] div[role="radiogroup"] label {{
            min-height: 90px;
            padding: 14px 8px;
        }}

        .welcome-box {{
            padding: 22px;
        }}

        .welcome-box h1 {{
            font-size: 1.7rem;
        }}

        .hero {{
            padding: 20px;
        }}

        .hero h1 {{
            font-size: 1.5rem;
        }}

        .workspace-heading h2 {{
            font-size: 1.5rem;
        }}
    }}

    </style>
    """, unsafe_allow_html=True)
# ----------------------------- DATA -------------------------
@st.cache_data
def load_data():
    # Database credentials are read from local environment variables or
    # .streamlit/secrets.toml. Never commit real credentials to GitHub.
    try:
        mysql_secrets = st.secrets.get("mysql", {})
    except Exception:
        mysql_secrets = {}

    connection = mysql.connector.connect(
        host=os.getenv("MYSQL_HOST") or mysql_secrets.get("host", "localhost"),
        user=os.getenv("MYSQL_USER") or mysql_secrets.get("user", "root"),
        password=os.getenv("MYSQL_PASSWORD") or mysql_secrets.get("password", ""),
        database=os.getenv("MYSQL_DATABASE") or mysql_secrets.get("database", "")
    )

    query = "SELECT * FROM crime_records"
    data = pd.read_sql(query, connection)
    connection.close()

    data.columns = [
        "Report Number", "Date Reported", "Date of Occurance",
        "Time of Occurrence", "City", "Crime Code", "Crime Description",
        "Victim Age", "Victim Gender", "Weapon Used", "Crime Domain",
        "Police Deployed", "Case Closed", "Date and Time of Case Closed",
        "Case Status", "Crime Occurred", "Age Group"
    ]

    for c in ["Date Reported", "Date of Occurance", "Date and Time of Case Closed"]:
        data[c] = pd.to_datetime(data[c], errors="coerce")

    data["Year"] = data["Date of Occurance"].dt.year
    data["Month"] = data["Date of Occurance"].dt.month
    data["Month Name"] = data["Date of Occurance"].dt.month_name()
    data["Weekday"] = data["Date of Occurance"].dt.day_name()

    data["Hour"] = pd.to_datetime(
        data["Time of Occurrence"].astype(str), errors="coerce"
    ).dt.hour

    data["Reporting Delay Days"] = (
        data["Date Reported"] - data["Date of Occurance"]
    ).dt.total_seconds() / 86400

    data["Closure Duration Days"] = (
        data["Date and Time of Case Closed"].dt.normalize()
        - data["Date Reported"].dt.normalize()
    ).dt.total_seconds() / 86400

    return data

try:
    df = load_data()
except Exception as e:
    st.error(f"Could not load crime_dataset_cleaned.csv: {e}")
    st.info("Keep this CSV in the same folder as your dashboard Python file.")
    st.stop()

if df["Year"].notna().sum() == 0:
    st.error("Occurrence dates could not be read. Check the Date of Occurance column.")
    st.stop()

# ----------------------------- HELPERS ----------------------
def heading(kicker, title, description=None):
    st.markdown(f'<div class="section-kicker">{kicker}</div><div class="section-title">{title}</div>', unsafe_allow_html=True)
    if description:
        st.caption(description)

def chart_layout(fig, t, height=390):
    fig.update_layout(
        height=height, paper_bgcolor=t["surface"], plot_bgcolor=t["surface"],
        font=dict(color=t["text"], family="Manrope"),
        title_font=dict(size=17), margin=dict(l=24, r=24, t=55, b=35),
        legend_title_text="", hoverlabel=dict(bgcolor=t["surface2"], font_color=t["text"]),
        colorway=t["palette"]
    )
    fig.update_xaxes(showgrid=False, zeroline=False, linecolor=t["line"])
    fig.update_yaxes(gridcolor=t["line"], zeroline=False)
    return fig

def chart(fig, t, key, height=390):
    st.plotly_chart(chart_layout(fig, t, height), use_container_width=True,
                    key=key, config={"displaylogo": False, "scrollZoom": True})

def no_data(data):
    if data.empty:
        st.warning("No records match these filters. Widen your filters to continue.")
        st.stop()

def metric_strip(data):
    total = len(data)
    open_n = int((data["Case Status"].astype(str).str.lower() == "open").sum())
    closed_n = int((data["Case Status"].astype(str).str.lower() == "closed").sum())
    a, b, c, d = st.columns(4)
    a.metric("RECORDS IN VIEW", f"{total:,}")
    b.metric("CITIES COVERED", f"{data['City'].nunique():,}")
    c.metric("OPEN CASES", f"{open_n:,}")
    d.metric("CLOSED CASES", f"{closed_n:,}")

def count_table(data, col, label="Records"):
    out = data[col].fillna("Not Recorded").value_counts().rename_axis(col).reset_index(name=label)
    return out

def top_insight(data, col, label):
    s = data[col].dropna()
    return f"{label}: **{s.value_counts().idxmax()}** ({s.value_counts().max():,} records)" if not s.empty else f"{label}: unavailable"


# ---------------------- EXTENDED ANALYTICS TOOLKIT ----------------------
# These helpers support the additional modules below and are intentionally
# kept separate so the project is easier to explain during the MSc viva.

def safe_percentage(part, whole):
    """Return a percentage safely, including when the denominator is zero."""
    return round((part / whole) * 100, 2) if whole else 0.0


def grouped_summary(data, group_columns, value_name="Records"):
    """Create a count summary for one or more categorical columns."""
    if isinstance(group_columns, str):
        group_columns = [group_columns]
    valid_columns = [c for c in group_columns if c in data.columns]
    if not valid_columns:
        return pd.DataFrame(columns=list(group_columns) + [value_name])
    return (
        data.groupby(valid_columns, dropna=False)
        .size()
        .reset_index(name=value_name)
        .sort_values(value_name, ascending=False)
    )


def numeric_summary(data, column):
    """Return a compact numeric summary without assuming values exist."""
    if column not in data.columns:
        return pd.Series(dtype="float64")
    values = pd.to_numeric(data[column], errors="coerce").dropna()
    if values.empty:
        return pd.Series(dtype="float64")
    return values.describe()


def missing_value_report(data):
    """Report missing and non-missing values for every column."""
    report = pd.DataFrame({
        "Column": data.columns,
        "Missing": data.isna().sum().values,
        "Present": data.notna().sum().values,
        "Missing %": [
            safe_percentage(data[c].isna().sum(), len(data))
            for c in data.columns
        ]
    })
    return report.sort_values("Missing", ascending=False)


def category_profile(data, column):
    """Build count and percentage statistics for a categorical variable."""
    if column not in data.columns:
        return pd.DataFrame(columns=[column, "Records", "Percentage"])
    counts = data[column].fillna("Not Recorded").value_counts(dropna=False)
    result = counts.rename_axis(column).reset_index(name="Records")
    result["Percentage"] = result["Records"].apply(
        lambda n: safe_percentage(n, len(data))
    )
    return result


def date_range_profile(data, column):
    """Describe the valid date span for a date column."""
    if column not in data.columns:
        return {"valid": 0, "earliest": None, "latest": None}
    values = pd.to_datetime(data[column], errors="coerce").dropna()
    if values.empty:
        return {"valid": 0, "earliest": None, "latest": None}
    return {
        "valid": int(values.count()),
        "earliest": values.min(),
        "latest": values.max()
    }


def make_bar(data, x, y, title, theme, color=None, orientation="v"):
    """Reusable bar chart with the active theme."""
    kwargs = {"color": color, "orientation": orientation} if color else {
        "orientation": orientation
    }
    fig = px.bar(
        data, x=x, y=y, title=title,
        color=color,
        color_discrete_sequence=theme["palette"],
        **({"orientation": orientation} if not color else {})
    )
    return chart_layout(fig, theme)


def make_donut(data, names, values, title, theme):
    """Reusable donut chart."""
    fig = px.pie(
        data, names=names, values=values, title=title, hole=0.58,
        color_discrete_sequence=theme["palette"]
    )
    fig.update_traces(textposition="inside", textinfo="percent")
    return chart_layout(fig, theme)


def make_line(data, x, y, title, theme):
    """Reusable line chart with visible point markers."""
    fig = px.line(
        data, x=x, y=y, title=title, markers=True,
        color_discrete_sequence=[theme["primary"]]
    )
    fig.update_traces(line_width=3)
    return chart_layout(fig, theme)


def make_heatmap(matrix, title, theme, height=500):
    """Reusable heatmap with readable hover values."""
    fig = px.imshow(
        matrix, title=title, aspect="auto",
        color_continuous_scale=[theme["surface"], theme["primary"]]
    )
    return chart_layout(fig, theme, height)


def add_download_button(data, filename, label):
    """Offer a UTF-8 CSV download for the supplied dataframe."""
    payload = data.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label=label,
        data=payload,
        file_name=filename,
        mime="text/csv",
        use_container_width=False
    )


def filtered_top_n(data, column, n=10):
    """Return the n most common values for a selected field."""
    if column not in data.columns:
        return pd.DataFrame(columns=[column, "Records"])
    return data[column].fillna("Not Recorded").value_counts().head(n).rename_axis(
        column
    ).reset_index(name="Records")


def calculate_case_rates(data):
    """Calculate open/closed shares from the current filtered records."""
    total = len(data)
    status = data["Case Status"].astype(str).str.strip().str.lower()
    open_count = int((status == "open").sum())
    closed_count = int((status == "closed").sum())
    unknown_count = total - open_count - closed_count
    return {
        "total": total,
        "open": open_count,
        "closed": closed_count,
        "unknown": unknown_count,
        "open_pct": safe_percentage(open_count, total),
        "closed_pct": safe_percentage(closed_count, total)
    }


def create_city_crime_matrix(data, minimum_city_records=1):
    """Return city-by-crime counts for heatmap and export use."""
    if data.empty:
        return pd.DataFrame()
    city_totals = data["City"].value_counts()
    included = city_totals[city_totals >= minimum_city_records].index
    subset = data[data["City"].isin(included)]
    return pd.crosstab(subset["City"], subset["Crime Description"])


def create_age_gender_matrix(data):
    """Return age-group by gender counts."""
    return pd.crosstab(
        data["Age Group"].fillna("Not Recorded"),
        data["Victim Gender"].fillna("Not Recorded")
    )


def get_peak_period(data, column):
    """Return the most frequent non-empty category and its count."""
    if column not in data.columns or data[column].dropna().empty:
        return "Unavailable", 0
    counts = data[column].value_counts()
    return str(counts.index[0]), int(counts.iloc[0])


def build_insight_text(data):
    """Create concise observations that describe the current filtered data."""
    if data.empty:
        return []
    observations = []
    for column, label in [
        ("City", "City with most records"),
        ("Crime Description", "Most frequent crime label"),
        ("Age Group", "Most represented age group"),
        ("Weapon Used", "Most frequently recorded weapon label"),
        ("Crime Occurred", "Most common occurrence period")
    ]:
        value, count = get_peak_period(data, column)
        observations.append(f"{label}: {value} ({count:,} records)")
    rates = calculate_case_rates(data)
    observations.append(
        f"Closed case share: {rates['closed_pct']:.2f}% of current records"
    )
    return observations


def data_quality_flags(data):
    """Flag records with missing or unusual values for review."""
    flags = pd.DataFrame(index=data.index)
    flags["Missing occurrence date"] = data["Date of Occurance"].isna()
    flags["Missing report date"] = data["Date Reported"].isna()
    flags["Report before occurrence"] = (
        data["Date Reported"] < data["Date of Occurance"]
    )
    flags["Age outside 0-110"] = (
        (pd.to_numeric(data["Victim Age"], errors="coerce") < 0)
        | (pd.to_numeric(data["Victim Age"], errors="coerce") > 110)
    )
    flags["Negative reporting delay"] = data["Reporting Delay Days"] < 0
    flags["Negative closure duration"] = data["Closure Duration Days"] < 0
    flags = flags.fillna(False)
    return flags


def make_monthly_city_table(data):
    """Build a year/month/city aggregate table."""
    valid = data.dropna(subset=["Year", "Month"])
    if valid.empty:
        return pd.DataFrame()
    return (
        valid.groupby(["Year", "Month", "City"])
        .size()
        .reset_index(name="Records")
        .sort_values(["Year", "Month", "Records"], ascending=[True, True, False])
    )


def make_crime_domain_summary(data):
    """Summarise records by crime domain and crime description."""
    return grouped_summary(data, ["Crime Domain", "Crime Description"])


def make_weapon_summary(data):
    """Summarise weapon labels with percentages."""
    return category_profile(data, "Weapon Used")


def make_gender_crime_summary(data):
    """Summarise crime categories by victim gender."""
    return grouped_summary(data, ["Crime Description", "Victim Gender"])


def make_city_status_summary(data):
    """Summarise case status for each city."""
    return grouped_summary(data, ["City", "Case Status"])


def make_weekday_hour_matrix(data):
    """Return weekday/hour counts in calendar order."""
    weekdays = [
        "Monday", "Tuesday", "Wednesday", "Thursday",
        "Friday", "Saturday", "Sunday"
    ]
    matrix = pd.crosstab(data["Weekday"], data["Hour"])
    return matrix.reindex(weekdays).reindex(columns=range(24), fill_value=0)


def format_value(value):
    """Format a value for record inspection."""
    if pd.isna(value):
        return "Not recorded"
    if isinstance(value, (pd.Timestamp, datetime)):
        return value.strftime("%Y-%m-%d")
    if isinstance(value, float):
        return f"{value:,.2f}"
    return str(value)


def render_table(data, height=420):
    """Render a dataframe consistently across analytical modules."""
    st.dataframe(
        data,
        use_container_width=True,
        hide_index=True,
        height=height
    )


def render_export(data, stem):
    """Render an export button using a predictable filename."""
    add_download_button(
        data,
        f"{stem}.csv",
        f"↓ Download {stem.replace('_', ' ').title()} CSV"
    )


def render_info_panel(title, body, theme):
    """Render a compact explanatory panel."""
    st.markdown(
        f'<div class="note"><strong>{title}</strong><br>{body}</div>',
        unsafe_allow_html=True
    )


def render_kpi_row(items):
    """Render a variable number of KPI metrics."""
    columns = st.columns(len(items))
    for column, (label, value) in zip(columns, items):
        column.metric(label, value)


def get_valid_numeric_columns(data):
    """Return numeric fields suitable for basic exploratory analysis."""
    return [
        c for c in data.select_dtypes(include="number").columns
        if data[c].notna().any()
    ]


def get_valid_categorical_columns(data):
    """Return categorical fields suitable for grouping."""
    return [
        c for c in data.columns
        if data[c].dtype == "object" or str(data[c].dtype) == "category"
    ]


def export_summary_bundle(data):
    """Create a compact multi-section summary table for the current view."""
    sections = []
    for col in [
        "City", "Crime Description", "Crime Domain", "Victim Gender",
        "Age Group", "Weapon Used", "Case Status", "Crime Occurred"
    ]:
        part = category_profile(data, col)
        if not part.empty:
            part.insert(0, "Field", col)
            part = part.rename(columns={col: "Category"})
            sections.append(part[["Field", "Category", "Records", "Percentage"]])
    return pd.concat(sections, ignore_index=True) if sections else pd.DataFrame()


def make_case_duration_by_city(data):
    """Calculate median closure duration by city where closure data exists."""
    valid = data.dropna(subset=["Closure Duration Days"])
    if valid.empty:
        return pd.DataFrame(columns=["City", "Median closure days", "Closed records"])
    return (
        valid.groupby("City")
        .agg(
            **{
                "Median closure days": ("Closure Duration Days", "median"),
                "Closed records": ("Report Number", "count")
            }
        )
        .reset_index()
        .sort_values("Median closure days", ascending=False)
    )


def make_reporting_delay_by_crime(data):
    """Calculate mean reporting delay by crime label."""
    valid = data.dropna(subset=["Reporting Delay Days"])
    if valid.empty:
        return pd.DataFrame(columns=["Crime Description", "Mean delay days", "Records"])
    return (
        valid.groupby("Crime Description")
        .agg(
            **{
                "Mean delay days": ("Reporting Delay Days", "mean"),
                "Records": ("Report Number", "count")
            }
        )
        .reset_index()
        .sort_values("Mean delay days", ascending=False)
    )


def make_police_deployment_by_domain(data):
    """Calculate average police deployment by domain."""
    return (
        data.groupby("Crime Domain")["Police Deployed"]
        .agg(["mean", "median", "count"])
        .reset_index()
        .rename(columns={
            "mean": "Average deployment",
            "median": "Median deployment",
            "count": "Records"
        })
    )


def make_age_statistics_by_crime(data):
    """Calculate age statistics by crime description."""
    return (
        data.groupby("Crime Description")["Victim Age"]
        .agg(["mean", "median", "min", "max", "count"])
        .reset_index()
        .rename(columns={
            "mean": "Mean age", "median": "Median age",
            "min": "Minimum age", "max": "Maximum age",
            "count": "Records with age"
        })
    )


def make_open_case_city_table(data):
    """Summarise open case records by city."""
    open_data = data[
        data["Case Status"].astype(str).str.strip().str.lower() == "open"
    ]
    return count_table(open_data, "City")


def make_closed_case_city_table(data):
    """Summarise closed case records by city."""
    closed_data = data[
        data["Case Status"].astype(str).str.strip().str.lower() == "closed"
    ]
    return count_table(closed_data, "City")


def make_crime_time_table(data):
    """Summarise crime category and supplied day-part labels."""
    return grouped_summary(data, ["Crime Description", "Crime Occurred"])


def make_victim_city_table(data):
    """Summarise age group and gender by city."""
    return grouped_summary(data, ["City", "Age Group", "Victim Gender"])


def make_weapon_domain_table(data):
    """Summarise recorded weapon and domain combinations."""
    return grouped_summary(data, ["Weapon Used", "Crime Domain"])


def make_monthly_trend(data):
    """Aggregate records by occurrence month."""
    valid = data.dropna(subset=["Date of Occurance"]).copy()
    if valid.empty:
        return pd.DataFrame(columns=["Month", "Records"])
    valid["Occurrence month"] = valid["Date of Occurance"].dt.to_period("M").astype(str)
    return valid.groupby("Occurrence month").size().reset_index(name="Records").rename(
        columns={"Occurrence month": "Month"}
    )


def make_year_city_table(data):
    """Aggregate occurrence records by year and city."""
    valid = data.dropna(subset=["Year"])
    return grouped_summary(valid, ["Year", "City"])


def make_hour_crime_table(data):
    """Aggregate records by hour and crime label."""
    return grouped_summary(data.dropna(subset=["Hour"]), ["Hour", "Crime Description"])


def make_gender_age_percentages(data):
    """Return within-age-group gender percentages."""
    matrix = create_age_gender_matrix(data)
    if matrix.empty:
        return matrix
    denominator = matrix.sum(axis=1).replace(0, pd.NA)
    return matrix.div(denominator, axis=0).mul(100).fillna(0).round(2)


def make_city_share_table(data):
    """Calculate city share of all records in the current view."""
    result = count_table(data, "City")
    if not result.empty:
        result["Share %"] = result["Records"].apply(
            lambda n: safe_percentage(n, len(data))
        )
    return result


def make_category_share_table(data, column):
    """Calculate percentage share for any categorical field."""
    return category_profile(data, column)


def validate_case_status(data):
    """Compare Case Status and Case Closed indicators if both are available."""
    if "Case Closed" not in data.columns:
        return {"available": False, "matches": None, "checked": 0}
    status = data["Case Status"].astype(str).str.strip().str.lower()
    closed = data["Case Closed"].astype(str).str.strip().str.lower()
    status_closed = status.eq("closed")
    closed_true = closed.isin(["yes", "true", "1", "closed"])
    checked = status.notna() & closed.notna()
    matches = int((status_closed[checked] == closed_true[checked]).sum())
    return {
        "available": True,
        "matches": matches,
        "checked": int(checked.sum())
    }


def get_data_dictionary():
    """Explain the meaning of the supplied dataset fields."""
    return pd.DataFrame([
        ("Report Number", "Identifier assigned to a report record."),
        ("Date Reported", "Date the report was recorded."),
        ("Date of Occurance", "Occurrence date; spelling follows source dataset."),
        ("Time of Occurrence", "Time value supplied for the occurrence."),
        ("City", "City label associated with the record."),
        ("Crime Code", "Crime code supplied by the dataset."),
        ("Crime Description", "Crime category label supplied by the dataset."),
        ("Victim Age", "Age value recorded for the victim."),
        ("Victim Gender", "Gender code supplied for the victim."),
        ("Weapon Used", "Weapon label; missing values may be marked Not Recorded."),
        ("Crime Domain", "Broad crime domain label."),
        ("Police Deployed", "Police deployment value supplied by the dataset."),
        ("Case Closed", "Closure indicator supplied by the dataset."),
        ("Date and Time of Case Closed", "Closure timestamp where available."),
        ("Case Status", "Open/Closed status label."),
        ("Crime Occurred", "Dataset-provided time-of-day category."),
        ("Age Group", "Age band label supplied by the dataset.")
    ], columns=["Field", "Description"])


def add_chart_note(text):
    """Show a short note directly below a chart."""
    st.caption(text)


def make_comparison_delta(data, group_column, value_column):
    """Create grouped count and share values for comparison."""
    result = grouped_summary(data, group_column)
    if not result.empty:
        result["Share %"] = result["Records"].apply(
            lambda value: safe_percentage(value, len(data))
        )
    return result


def get_top_and_bottom(data, column, count=5):
    """Return top and bottom categories for a categorical column."""
    counts = data[column].fillna("Not Recorded").value_counts()
    return counts.head(count), counts.tail(count).sort_values()


def make_age_band_gender_pivot(data):
    """Return a pivot table suitable for age/gender comparison."""
    return pd.pivot_table(
        data, index="Age Group", columns="Victim Gender",
        values="Report Number", aggfunc="count", fill_value=0
    )


def make_domain_city_pivot(data):
    """Return a pivot table suitable for domain/city comparison."""
    return pd.pivot_table(
        data, index="Crime Domain", columns="City",
        values="Report Number", aggfunc="count", fill_value=0
    )


def make_weapon_city_pivot(data):
    """Return a pivot table suitable for weapon/city comparison."""
    return pd.pivot_table(
        data, index="Weapon Used", columns="City",
        values="Report Number", aggfunc="count", fill_value=0
    )


def make_case_status_crime_pivot(data):
    """Return a crime/status cross-tabulation."""
    return pd.crosstab(data["Crime Description"], data["Case Status"])


def make_crime_age_pivot(data):
    """Return a crime/age-group cross-tabulation."""
    return pd.crosstab(data["Crime Description"], data["Age Group"])


def make_crime_gender_pivot(data):
    """Return a crime/gender cross-tabulation."""
    return pd.crosstab(data["Crime Description"], data["Victim Gender"])


def make_crime_weekday_pivot(data):
    """Return a crime/weekday cross-tabulation."""
    return pd.crosstab(data["Crime Description"], data["Weekday"])


def make_domain_weapon_pivot(data):
    """Return a domain/weapon cross-tabulation."""
    return pd.crosstab(data["Crime Domain"], data["Weapon Used"])


def make_city_age_pivot(data):
    """Return a city/age-group cross-tabulation."""
    return pd.crosstab(data["City"], data["Age Group"])


def make_city_gender_pivot(data):
    """Return a city/gender cross-tabulation."""
    return pd.crosstab(data["City"], data["Victim Gender"])


def make_month_daypart_pivot(data):
    """Return a month/day-part cross-tabulation."""
    return pd.crosstab(data["Month Name"], data["Crime Occurred"])


def make_status_domain_pivot(data):
    """Return a case-status/domain cross-tabulation."""
    return pd.crosstab(data["Crime Domain"], data["Case Status"])


def make_city_weapon_pivot(data):
    """Return a city/weapon cross-tabulation."""
    return pd.crosstab(data["City"], data["Weapon Used"])


def make_year_domain_pivot(data):
    """Return a year/domain cross-tabulation."""
    return pd.crosstab(data["Year"], data["Crime Domain"])


def make_year_gender_pivot(data):
    """Return a year/gender cross-tabulation."""
    return pd.crosstab(data["Year"], data["Victim Gender"])


def make_year_status_pivot(data):
    """Return a year/status cross-tabulation."""
    return pd.crosstab(data["Year"], data["Case Status"])


def make_city_month_pivot(data):
    """Return a city/month cross-tabulation."""
    return pd.crosstab(data["City"], data["Month Name"])


def make_hour_domain_pivot(data):
    """Return an hour/domain cross-tabulation."""
    return pd.crosstab(data["Hour"], data["Crime Domain"])


def make_hour_weapon_pivot(data):
    """Return an hour/weapon cross-tabulation."""
    return pd.crosstab(data["Hour"], data["Weapon Used"])


def make_age_weapon_pivot(data):
    """Return an age group/weapon cross-tabulation."""
    return pd.crosstab(data["Age Group"], data["Weapon Used"])


def make_age_domain_pivot(data):
    """Return an age group/domain cross-tabulation."""
    return pd.crosstab(data["Age Group"], data["Crime Domain"])


def make_gender_domain_pivot(data):
    """Return a gender/domain cross-tabulation."""
    return pd.crosstab(data["Victim Gender"], data["Crime Domain"])


def make_gender_weapon_pivot(data):
    """Return a gender/weapon cross-tabulation."""
    return pd.crosstab(data["Victim Gender"], data["Weapon Used"])


def make_status_weapon_pivot(data):
    """Return a status/weapon cross-tabulation."""
    return pd.crosstab(data["Case Status"], data["Weapon Used"])


def make_status_gender_pivot(data):
    """Return a status/gender cross-tabulation."""
    return pd.crosstab(data["Case Status"], data["Victim Gender"])


def make_status_age_pivot(data):
    """Return a status/age-group cross-tabulation."""
    return pd.crosstab(data["Case Status"], data["Age Group"])


def make_domain_age_pivot(data):
    """Return a domain/age-group cross-tabulation."""
    return pd.crosstab(data["Crime Domain"], data["Age Group"])


def make_domain_gender_pivot(data):
    """Return a domain/gender cross-tabulation."""
    return pd.crosstab(data["Crime Domain"], data["Victim Gender"])


def make_crime_hour_pivot(data):
    """Return a crime/hour cross-tabulation."""
    return pd.crosstab(data["Crime Description"], data["Hour"])


def make_crime_month_pivot(data):
    """Return a crime/month cross-tabulation."""
    return pd.crosstab(data["Crime Description"], data["Month Name"])


def make_crime_city_pivot(data):
    """Return a crime/city cross-tabulation."""
    return pd.crosstab(data["Crime Description"], data["City"])


def make_domain_weekday_pivot(data):
    """Return a domain/weekday cross-tabulation."""
    return pd.crosstab(data["Crime Domain"], data["Weekday"])


def make_weapon_weekday_pivot(data):
    """Return a weapon/weekday cross-tabulation."""
    return pd.crosstab(data["Weapon Used"], data["Weekday"])


def make_weapon_hour_pivot(data):
    """Return a weapon/hour cross-tabulation."""
    return pd.crosstab(data["Weapon Used"], data["Hour"])


def make_age_weekday_pivot(data):
    """Return an age group/weekday cross-tabulation."""
    return pd.crosstab(data["Age Group"], data["Weekday"])


def make_gender_weekday_pivot(data):
    """Return a gender/weekday cross-tabulation."""
    return pd.crosstab(data["Victim Gender"], data["Weekday"])


def make_city_weekday_pivot(data):
    """Return a city/weekday cross-tabulation."""
    return pd.crosstab(data["City"], data["Weekday"])


def make_status_weekday_pivot(data):
    """Return a status/weekday cross-tabulation."""
    return pd.crosstab(data["Case Status"], data["Weekday"])


def make_status_hour_pivot(data):
    """Return a status/hour cross-tabulation."""
    return pd.crosstab(data["Case Status"], data["Hour"])


def make_domain_hour_pivot(data):
    """Return a domain/hour cross-tabulation."""
    return pd.crosstab(data["Crime Domain"], data["Hour"])


def make_domain_month_pivot(data):
    """Return a domain/month cross-tabulation."""
    return pd.crosstab(data["Crime Domain"], data["Month Name"])


def make_weapon_month_pivot(data):
    """Return a weapon/month cross-tabulation."""
    return pd.crosstab(data["Weapon Used"], data["Month Name"])


def make_age_month_pivot(data):
    """Return an age group/month cross-tabulation."""
    return pd.crosstab(data["Age Group"], data["Month Name"])


def make_gender_month_pivot(data):
    """Return a gender/month cross-tabulation."""
    return pd.crosstab(data["Victim Gender"], data["Month Name"])


def make_status_month_pivot(data):
    """Return a status/month cross-tabulation."""
    return pd.crosstab(data["Case Status"], data["Month Name"])


def make_city_hour_pivot(data):
    """Return a city/hour cross-tabulation."""
    return pd.crosstab(data["City"], data["Hour"])


def make_city_domain_pivot(data):
    """Return a city/domain cross-tabulation."""
    return pd.crosstab(data["City"], data["Crime Domain"])


def make_city_status_pivot(data):
    """Return a city/status cross-tabulation."""
    return pd.crosstab(data["City"], data["Case Status"])


def make_city_crime_domain_pivot(data):
    """Return a city/crime-domain cross-tabulation."""
    return pd.crosstab(data["City"], data["Crime Domain"])


def make_crime_status_pivot(data):
    """Return a crime/status cross-tabulation."""
    return pd.crosstab(data["Crime Description"], data["Case Status"])


def make_crime_weapon_pivot(data):
    """Return a crime/weapon cross-tabulation."""
    return pd.crosstab(data["Crime Description"], data["Weapon Used"])


def make_crime_agegroup_pivot(data):
    """Return a crime/age-group cross-tabulation."""
    return pd.crosstab(data["Crime Description"], data["Age Group"])


def make_crime_gender_pivot(data):
    """Return a crime/gender cross-tabulation."""
    return pd.crosstab(data["Crime Description"], data["Victim Gender"])


def make_crime_domain_pivot(data):
    """Return a crime/domain cross-tabulation."""
    return pd.crosstab(data["Crime Description"], data["Crime Domain"])


def make_city_occurrence_period_pivot(data):
    """Return a city/day-part cross-tabulation."""
    return pd.crosstab(data["City"], data["Crime Occurred"])


def make_age_occurrence_period_pivot(data):
    """Return an age/day-part cross-tabulation."""
    return pd.crosstab(data["Age Group"], data["Crime Occurred"])


def make_gender_occurrence_period_pivot(data):
    """Return a gender/day-part cross-tabulation."""
    return pd.crosstab(data["Victim Gender"], data["Crime Occurred"])


def make_weapon_occurrence_period_pivot(data):
    """Return a weapon/day-part cross-tabulation."""
    return pd.crosstab(data["Weapon Used"], data["Crime Occurred"])


def make_domain_occurrence_period_pivot(data):
    """Return a domain/day-part cross-tabulation."""
    return pd.crosstab(data["Crime Domain"], data["Crime Occurred"])


def make_status_occurrence_period_pivot(data):
    """Return a status/day-part cross-tabulation."""
    return pd.crosstab(data["Case Status"], data["Crime Occurred"])


def make_crime_occurrence_period_pivot(data):
    """Return a crime/day-part cross-tabulation."""
    return pd.crosstab(data["Crime Description"], data["Crime Occurred"])


def make_city_age_gender_pivot(data):
    """Return a city/age/gender cross-tabulation."""
    return pd.pivot_table(
        data, index=["City", "Age Group"], columns="Victim Gender",
        values="Report Number", aggfunc="count", fill_value=0
    )


def make_crime_age_gender_pivot(data):
    """Return a crime/age/gender cross-tabulation."""
    return pd.pivot_table(
        data, index=["Crime Description", "Age Group"],
        columns="Victim Gender", values="Report Number",
        aggfunc="count", fill_value=0
    )


def make_city_crime_status_pivot(data):
    """Return a city/crime/status cross-tabulation."""
    return pd.pivot_table(
        data, index=["City", "Crime Description"], columns="Case Status",
        values="Report Number", aggfunc="count", fill_value=0
    )


def make_city_weapon_domain_pivot(data):
    """Return a city/weapon/domain cross-tabulation."""
    return pd.pivot_table(
        data, index=["City", "Weapon Used"], columns="Crime Domain",
        values="Report Number", aggfunc="count", fill_value=0
    )


def make_age_gender_domain_pivot(data):
    """Return an age/gender/domain cross-tabulation."""
    return pd.pivot_table(
        data, index=["Age Group", "Victim Gender"], columns="Crime Domain",
        values="Report Number", aggfunc="count", fill_value=0
    )


def make_crime_weekday_hour_pivot(data):
    """Return a crime/weekday/hour cross-tabulation."""
    return pd.pivot_table(
        data, index=["Crime Description", "Weekday"], columns="Hour",
        values="Report Number", aggfunc="count", fill_value=0
    )


def make_city_month_crime_pivot(data):
    """Return a city/month/crime cross-tabulation."""
    return pd.pivot_table(
        data, index=["City", "Month Name"], columns="Crime Description",
        values="Report Number", aggfunc="count", fill_value=0
    )


def make_year_month_city_pivot(data):
    """Return a year/month/city cross-tabulation."""
    return pd.pivot_table(
        data, index=["Year", "Month"], columns="City",
        values="Report Number", aggfunc="count", fill_value=0
    )


def make_year_month_crime_pivot(data):
    """Return a year/month/crime cross-tabulation."""
    return pd.pivot_table(
        data, index=["Year", "Month"], columns="Crime Description",
        values="Report Number", aggfunc="count", fill_value=0
    )


def make_year_month_domain_pivot(data):
    """Return a year/month/domain cross-tabulation."""
    return pd.pivot_table(
        data, index=["Year", "Month"], columns="Crime Domain",
        values="Report Number", aggfunc="count", fill_value=0
    )


def make_year_month_status_pivot(data):
    """Return a year/month/status cross-tabulation."""
    return pd.pivot_table(
        data, index=["Year", "Month"], columns="Case Status",
        values="Report Number", aggfunc="count", fill_value=0
    )


def make_year_month_gender_pivot(data):
    """Return a year/month/gender cross-tabulation."""
    return pd.pivot_table(
        data, index=["Year", "Month"], columns="Victim Gender",
        values="Report Number", aggfunc="count", fill_value=0
    )


def make_year_month_age_pivot(data):
    """Return a year/month/age-group cross-tabulation."""
    return pd.pivot_table(
        data, index=["Year", "Month"], columns="Age Group",
        values="Report Number", aggfunc="count", fill_value=0
    )


def make_year_month_weapon_pivot(data):
    """Return a year/month/weapon cross-tabulation."""
    return pd.pivot_table(
        data, index=["Year", "Month"], columns="Weapon Used",
        values="Report Number", aggfunc="count", fill_value=0
    )


def make_year_month_daypart_pivot(data):
    """Return a year/month/day-part cross-tabulation."""
    return pd.pivot_table(
        data, index=["Year", "Month"], columns="Crime Occurred",
        values="Report Number", aggfunc="count", fill_value=0
    )


def make_year_month_city_crime_pivot(data):
    """Return a year/month/city/crime grouped count table."""
    return grouped_summary(data, ["Year", "Month", "City", "Crime Description"])


def make_full_data_profile(data):
    """Return high-level data profile metrics for the selected view."""
    return {
        "rows": int(data.shape[0]),
        "columns": int(data.shape[1]),
        "duplicate_rows": int(data.duplicated().sum()),
        "duplicate_report_numbers": int(data["Report Number"].duplicated().sum()),
        "missing_cells": int(data.isna().sum().sum()),
        "cities": int(data["City"].nunique()),
        "crime_labels": int(data["Crime Description"].nunique()),
        "first_occurrence": data["Date of Occurance"].min(),
        "last_occurrence": data["Date of Occurance"].max()
    }


def create_monthly_summary(data):
    """Create monthly totals plus year and month numeric fields."""
    valid = data.dropna(subset=["Date of Occurance"]).copy()
    if valid.empty:
        return pd.DataFrame()
    valid["Month start"] = valid["Date of Occurance"].dt.to_period("M").dt.to_timestamp()
    result = valid.groupby("Month start").size().reset_index(name="Records")
    result["Year"] = result["Month start"].dt.year
    result["Month"] = result["Month start"].dt.month_name()
    return result


def create_homicide_profile(data):
    """Summarise only records whose crime description contains Homicide."""
    subset = data[
        data["Crime Description"].astype(str).str.contains(
            "Homicide", case=False, na=False
        )
    ].copy()
    return subset


def create_open_case_profile(data):
    """Return records marked open using the Case Status field."""
    return data[
        data["Case Status"].astype(str).str.strip().str.lower() == "open"
    ].copy()


def create_closed_case_profile(data):
    """Return records marked closed using the Case Status field."""
    return data[
        data["Case Status"].astype(str).str.strip().str.lower() == "closed"
    ].copy()


def add_percentage_column(summary, denominator):
    """Add a percentage column to a count summary."""
    result = summary.copy()
    if "Records" in result.columns:
        result["Percentage"] = result["Records"].apply(
            lambda value: safe_percentage(value, denominator)
        )
    return result


def top_category_label(data, column):
    """Return the most frequent category label for a field."""
    if column not in data.columns:
        return "Unavailable"
    values = data[column].dropna()
    if values.empty:
        return "Unavailable"
    return str(values.value_counts().index[0])


def top_category_count(data, column):
    """Return the count of the most frequent category."""
    if column not in data.columns:
        return 0
    values = data[column].dropna().value_counts()
    return int(values.iloc[0]) if not values.empty else 0


def get_date_filter_bounds(data):
    """Return minimum and maximum valid occurrence dates."""
    dates = data["Date of Occurance"].dropna()
    if dates.empty:
        return None, None
    return dates.min().date(), dates.max().date()


def apply_date_range(data, start_date, end_date):
    """Apply an inclusive occurrence date filter."""
    if start_date is None or end_date is None:
        return data.copy()
    dates = data["Date of Occurance"].dt.date
    return data[(dates >= start_date) & (dates <= end_date)].copy()


def display_source_caveat():
    """Display the dataset provenance and interpretation warning."""
    st.caption(
        "Academic analysis only. The supplied dataset's provenance and "
        "representativeness have not been independently verified. "
        "Counts are records, not population-adjusted crime rates."
    )


def display_homicide_caveat():
    """Display the interpretation limit for homicide-labelled rows."""
    st.warning(
        "A Homicide crime-description label is not, by itself, a verified "
        "cause-of-death record. This dataset does not provide a dedicated "
        "confirmed cause-of-death field or incident narrative."
    )


def display_geography_caveat():
    """Display the geographic resolution limit."""
    st.info(
        "The source contains city names only. City comparisons are possible, "
        "but street-level locations and incident hotspots cannot be inferred "
        "without verified coordinates."
    )


def display_correlation_caveat():
    """Display the statistical interpretation limit."""
    st.caption(
        "Correlation describes association between numeric fields. "
        "It does not demonstrate causation or explain why an event occurred."
    )


def display_record_count_caveat():
    """Display a short reminder about the unit of analysis."""
    st.caption("All totals on this page count rows in the selected dataset view.")

# ---------------------- END EXTENDED ANALYTICS TOOLKIT ------------------

# ----------------------------- TOP BAR ----------------------
top_left, top_mid, top_right = st.columns([5, 2, 2])
with top_left:
    st.markdown('<div class="eyebrow">MSc IT • DATA INTELLIGENCE PROJECT</div>', unsafe_allow_html=True)
    st.markdown("## CRIME ANALYSIS <span style='color:#38E0D0'>/</span> INTELLIGENCE WORKSPACE", unsafe_allow_html=True)
with top_mid:
    theme_name = st.selectbox("INTERFACE PALETTE", list(THEMES.keys()), index=0)
T = THEMES[theme_name]
with top_right:
    st.markdown("<div style='height:26px'></div>", unsafe_allow_html=True)
    with st.popover("ⓘ About this workspace"):
        st.markdown("**Crime Analysis**")
        st.write("Interactive academic exploration of the supplied crime dataset.")
        st.write("All counts represent dataset records, not verified crime rates.")
inject_style(T)

# ----------------------------- FILTER DRAWER ----------------
with st.expander("⌄  DATA CONTROLS  |  Refine the records shown throughout the workspace", expanded=False):
    f1, f2, f3, f4 = st.columns(4)
    years = sorted(df["Year"].dropna().astype(int).unique().tolist())
    cities = sorted(df["City"].dropna().astype(str).unique().tolist())
    crimes = sorted(df["Crime Description"].dropna().astype(str).unique().tolist())
    genders = sorted(df["Victim Gender"].dropna().astype(str).unique().tolist())
    with f1:
        chosen_years = st.multiselect("Occurrence year", years, default=years, key="filter_years")
    with f2:
        chosen_cities = st.multiselect("City", cities, default=cities, key="filter_cities")
    with f3:
        chosen_crimes = st.multiselect("Crime category", crimes, default=crimes, key="filter_crimes")
    with f4:
        chosen_genders = st.multiselect("Victim gender", genders, default=genders, key="filter_genders")

    with st.expander("Occurrence date range", expanded=False):
        min_date, max_date = get_date_filter_bounds(df)
        if min_date and max_date:
            chosen_date_range = st.date_input(
                "Limit records to occurrence dates",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date,
                key="filter_date_range"
            )
        else:
            chosen_date_range = None

    if st.button("↺ Reset all filters", key="reset_filters"):
        for k in ["filter_years", "filter_cities", "filter_crimes", "filter_genders"]:
            st.session_state.pop(k, None)
        st.rerun()

# Defaults if controls have not been rendered/initialized yet
chosen_years = st.session_state.get("filter_years", years)
chosen_cities = st.session_state.get("filter_cities", cities)
chosen_crimes = st.session_state.get("filter_crimes", crimes)
chosen_genders = st.session_state.get("filter_genders", genders)

filtered = df[
    df["Year"].isin(chosen_years)
    & df["City"].isin(chosen_cities)
    & df["Crime Description"].isin(chosen_crimes)
    & df["Victim Gender"].isin(chosen_genders)
].copy()

if "filter_date_range" in st.session_state:
    _range = st.session_state.get("filter_date_range")
    if isinstance(_range, (tuple, list)) and len(_range) == 2:
        filtered = apply_date_range(filtered, _range[0], _range[1])

        # ----------------------------- PROJECT WELCOME -------------------

st.markdown("""
<div style="
    padding: 30px;
    border-radius: 18px;
    background: linear-gradient(120deg, #172B3A, #234B5C);
    color: white;
    margin-bottom: 25px;
">
    <div style="font-size:13px; letter-spacing:3px; color:#9DD9E8;">
        CRIME ANALYSIS & INTELLIGENCE
    </div>
    <h1 style="color:white; margin-bottom:8px;">
        Explore. Analyse. Understand.
    </h1>
    <p style="font-size:16px; color:#E2EDF2;">
        An interactive academic dashboard to explore crime records,
        investigate patterns, study case trends and understand
        crime-related data through analytics and visualisation.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("### Welcome to the Crime Intelligence Workspace")
st.caption("Select a module below to begin exploring the dashboard.")

# ----------------------------- CRIME INTRO VIDEO -------------------

st.markdown("### Discover Crime Scene Investigation")

st.caption(
    "Understand how crime scenes are examined, evidence is collected "
    "and investigations are conducted."
)

VIDEO_URL = "https://youtu.be/wWX3V2c_mLM"

@st.dialog("Crime Scene Investigation", width="large")
def show_crime_video():
    st.video(VIDEO_URL)
    st.link_button(
        "▶ Open on YouTube",
        VIDEO_URL,
        use_container_width=True
    )

if st.button("▶ WATCH CRIME INTRO", key="crime_intro_btn"):
    show_crime_video()

st.markdown("---")

# ----------------------------- NAVIGATION -------------------

pages = [
    "Overview",
    "Geography",
    "Time Patterns",
    "Victim Profiles",
    "Case Investigations",
    "Anomaly Detection",
    "Weapons & Deployment",
    "Analytics Lab",
    "Crime Forecasting",
    "Data Studio",
    "Data Quality",
    "City Profiles",
    "Comparative Analysis",
    "Homicide Review",
    "Summary Reports"
]

page_icons = {
    "Overview": "📊",
    "Geography": "🌍",
    "Time Patterns": "🕒",
    "Victim Profiles": "👥",
    "Case Investigations": "🔎",
    "Anomaly Detection": "🚨",
    "Weapons & Deployment": "🛡️",
    "Analytics Lab": "📈",
    "Crime Forecasting": "🔮",
    "Data Studio": "🗄️",
    "Data Quality": "✅",
    "City Profiles": "🏙️",
    "Comparative Analysis": "⚖️",
    "Homicide Review": "🔬",
    "Summary Reports": "📑"
}

st.markdown("""
<div class="workspace-heading">
    <div class="eyebrow">YOUR INVESTIGATION WORKSPACE</div>
    <h2>Explore Intelligence Modules</h2>
    <p>Select a module to investigate crime records, patterns and insights.</p>
</div>
""", unsafe_allow_html=True)

page = st.radio(
    "WORKSPACE MODULES",
    pages,
    format_func=lambda x: f"{page_icons[x]}   {x}",
    horizontal=False,
    label_visibility="collapsed"
)

st.markdown(f"""
<div class="hero">
    <div class="eyebrow">LIVE FILTERED VIEW / {page.upper()}</div>
    <h1>{page}</h1>
    <p>Explore patterns, compare segments and inspect the records behind each chart.</p>
</div>
""", unsafe_allow_html=True)

if filtered.empty:
    st.warning(
        "Your current filter combination returns no records. "
        "Open Data Controls and change the selection."
    )
    st.stop()

# ----------------------------- END NAVIGATION -------------------


# ----------------------------- OVERVIEW ---------------------
if page == "Overview":
    metric_strip(filtered)
    st.markdown("---")
    l, r = st.columns([1.25, 1])
    with l:
        heading("01 / TREND SIGNAL", "Occurrence records by year")
        yearly = filtered.groupby("Year").size().reset_index(name="Records")
        fig = px.area(yearly, x="Year", y="Records", markers=True,
                      color_discrete_sequence=[T["primary"]])
        fig.update_traces(line_width=3, fillcolor=T["primary"], opacity=.72)
        chart(fig, T, "overview_year")
    with r:
        heading("02 / CATEGORY MIX", "Crime description distribution")
        cat = count_table(filtered, "Crime Description")
        fig = px.pie(cat, names="Crime Description", values="Records", hole=.62,
                     color_discrete_sequence=T["palette"])
        fig.update_traces(textposition="inside", textinfo="percent",
                          hovertemplate="<b>%{label}</b><br>Records: %{value:,}<br>Share: %{percent}<extra></extra>")
        chart(fig, T, "overview_category")
    l, r = st.columns(2)
    with l:
        heading("03 / CITY LEADERBOARD", "Highest record counts")
        city = count_table(filtered, "City").head(12).sort_values("Records")
        fig = px.bar(city, x="Records", y="City", orientation="h", text="Records",
                     color="Records", color_continuous_scale=[[0, T["surface2"]], [1, T["primary"]]])
        fig.update_traces(texttemplate="%{text:,}", textposition="outside", cliponaxis=False)
        chart(fig, T, "overview_city", 480)
    with r:
        heading("04 / VICTIM PROFILE", "Age group × gender")
        ag = filtered.groupby(["Age Group", "Victim Gender"]).size().reset_index(name="Records")
        fig = px.bar(ag, x="Age Group", y="Records", color="Victim Gender",
                     barmode="group", color_discrete_sequence=T["palette"], text_auto=".2s")
        chart(fig, T, "overview_age_gender", 480)
    heading("SIGNALS FROM THE CURRENT FILTER", "Quick dataset observations")
    i1, i2, i3 = st.columns(3)
    i1.markdown(f'<div class="note">{top_insight(filtered, "City", "Largest city record count")}</div>', unsafe_allow_html=True)
    i2.markdown(f'<div class="note">{top_insight(filtered, "Crime Description", "Most frequent category")}</div>', unsafe_allow_html=True)
    i3.markdown(f'<div class="note">{top_insight(filtered, "Age Group", "Most represented age group")}</div>', unsafe_allow_html=True)

# ----------------------------- GEOGRAPHY --------------------
elif page == "Geography":
    heading("MODULE 02", "Geographic intelligence", "City-level comparisons from the city field in the supplied dataset.")
    city = count_table(filtered, "City").sort_values("Records", ascending=False)
    st.metric("Cities represented in current view", city["City"].nunique())
    l, r = st.columns([1.1, 1])
    with l:
        heading("CITY RANKING", "Records by city")
        fig = px.bar(city.sort_values("Records").tail(20), x="Records", y="City",
                     orientation="h", color="Records",
                     color_continuous_scale=[[0, T["surface2"]], [1, T["primary"]]],
                     text="Records")
        fig.update_traces(textposition="outside", cliponaxis=False)
        chart(fig, T, "geo_city_rank", 650)
    with r:
        heading("CITY × CRIME TYPE", "Compare category composition")
        options = city["City"].head(min(8, len(city))).tolist()
        selected = st.multiselect("Choose cities to compare", options,
                                  default=options[:min(4, len(options))], key="geo_compare")
        comp = filtered[filtered["City"].isin(selected)]
        comp_data = comp.groupby(["City", "Crime Description"]).size().reset_index(name="Records")
        fig = px.bar(comp_data, x="City", y="Records", color="Crime Description",
                     barmode="stack", color_discrete_sequence=T["palette"])
        chart(fig, T, "geo_mix", 650)
    st.markdown('<div class="note">Location limitation: the supplied file contains city names, not incident latitude/longitude. This version therefore compares cities and does not claim to show street-level hotspots. A map should only be added after attaching a checked city-coordinate reference table.</div>', unsafe_allow_html=True)
    heading("CITY COMPARISON TABLE", "Sort and inspect city totals")
    st.dataframe(city, use_container_width=True, hide_index=True)

# ----------------------------- TIME PATTERNS ----------------
elif page == "Time Patterns":
    heading("MODULE 03", "Temporal intelligence", "Occurrence dates and times are used for these patterns.")
    l, r = st.columns(2)
    with l:
        heading("YEARLY", "Records by occurrence year")
        yearly = filtered.groupby("Year").size().reset_index(name="Records")
        chart(px.line(yearly, x="Year", y="Records", markers=True,
                      color_discrete_sequence=[T["primary"]]), T, "time_year")
    with r:
        heading("MONTHLY", "Records by calendar month")
        order = ["January","February","March","April","May","June","July","August","September","October","November","December"]
        monthly = filtered["Month Name"].value_counts().reindex(order).fillna(0).rename_axis("Month").reset_index(name="Records")
        fig = px.bar(monthly, x="Month", y="Records", color="Records",
                     color_continuous_scale=[[0, T["surface2"]], [1, T["secondary"]]])
        fig.update_xaxes(tickangle=-35)
        chart(fig, T, "time_month")
    heading("YEAR × MONTH", "Occurrence volume heatmap")
    heat = pd.pivot_table(filtered, index="Month", columns="Year",
                          values="Report Number", aggfunc="count", fill_value=0).reindex(range(1,13))
    chart(px.imshow(heat, labels=dict(x="Year", y="Month number", color="Records"),
                    color_continuous_scale=[T["surface"], T["primary"]], aspect="auto"),
          T, "time_heat", 480)
    l, r = st.columns(2)
    with l:
        heading("WEEKDAY", "Records by day of week")
        order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        wd = filtered["Weekday"].value_counts().reindex(order).fillna(0).rename_axis("Weekday").reset_index(name="Records")
        chart(px.bar(wd, x="Weekday", y="Records", text="Records",
                     color_discrete_sequence=[T["accent"]]), T, "time_weekday")
    with r:
        heading("HOUR OF DAY", "Records by hour")
        hr = filtered.groupby("Hour").size().reindex(range(24), fill_value=0).rename_axis("Hour").reset_index(name="Records")
        chart(px.bar(hr, x="Hour", y="Records", color="Records",
                     color_continuous_scale=[T["surface2"], T["primary"]]), T, "time_hour")
    heading("DAY PART", "Dataset-provided occurrence period")
    parts = count_table(filtered, "Crime Occurred")
    chart(px.funnel(parts, x="Records", y="Crime Occurred",
                    color_discrete_sequence=[T["secondary"]]), T, "time_daypart", 430)

# ----------------------------- VICTIMS -----------------------
elif page == "Victim Profiles":
    heading("MODULE 04", "Victim intelligence", "Descriptive comparisons of age and gender fields.")
    l, r, q = st.columns(3)
    l.metric("Mean victim age", f"{filtered['Victim Age'].mean():.1f}" if filtered["Victim Age"].notna().any() else "N/A")
    r.metric("Median victim age", f"{filtered['Victim Age'].median():.1f}" if filtered["Victim Age"].notna().any() else "N/A")
    q.metric("Age groups", filtered["Age Group"].nunique())
    a, b = st.columns(2)
    with a:
        heading("GENDER MIX", "Victim gender records")
        g = count_table(filtered, "Victim Gender")
        chart(px.pie(g, names="Victim Gender", values="Records", hole=.58,
                     color_discrete_sequence=T["palette"]), T, "victim_gender")
    with b:
        heading("AGE PROFILE", "Distribution of victim ages")
        fig = px.histogram(filtered, x="Victim Age", nbins=25,
                           color_discrete_sequence=[T["secondary"]])
        chart(fig, T, "victim_age")
    a, b = st.columns(2)
    with a:
        heading("AGE BANDS", "Records by supplied age group")
        ag = count_table(filtered, "Age Group")
        chart(px.bar(ag, x="Age Group", y="Records", color="Age Group",
                     color_discrete_sequence=T["palette"], text="Records"), T, "victim_bands")
    with b:
        heading("AGE × GENDER", "Grouped comparison")
        ag = filtered.groupby(["Age Group", "Victim Gender"]).size().reset_index(name="Records")
        chart(px.bar(ag, x="Age Group", y="Records", color="Victim Gender",
                     barmode="group", color_discrete_sequence=T["palette"]), T, "victim_age_gender")
    heading("GENDER × CRIME", "Category comparison")
    gc = filtered.groupby(["Crime Description", "Victim Gender"]).size().reset_index(name="Records")
    fig = px.bar(gc, x="Crime Description", y="Records", color="Victim Gender",
                 barmode="group", color_discrete_sequence=T["palette"])
    fig.update_xaxes(tickangle=-50)
    chart(fig, T, "victim_gender_crime", 620)
    st.markdown("---")
    heading("HOMICIDE-LABELLED RECORDS", "A focused look at records labelled Homicide")
    hom = filtered[filtered["Crime Description"].astype(str).str.contains("Homicide", case=False, na=False)]
    if hom.empty:
        st.info("No homicide-labelled records match the current filters.")
    else:
        x, y, z = st.columns(3)
        x.metric("Homicide-labelled records", f"{len(hom):,}")
        y.metric("Female-coded records", f"{(hom['Victim Gender'] == 'F').sum():,}")
        z.metric("Male-coded records", f"{(hom['Victim Gender'] == 'M').sum():,}")
        hh = hom.groupby(["Age Group", "Victim Gender"]).size().reset_index(name="Records")
        chart(px.bar(hh, x="Age Group", y="Records", color="Victim Gender",
                     barmode="group", color_discrete_sequence=T["palette"]), T, "victim_homicide")
    st.warning("The dataset has no dedicated confirmed cause-of-death field or incident narrative. Homicide-labelled records must not be treated as independently verified deaths or used to explain why a person died.")

# ----------------------------- INVESTIGATIONS ----------------

# ----------------------------- CASE INVESTIGATIONS ----------------
elif page == "Case Investigations":

    heading(
        "MODULE 05",
        "Advanced case investigation",
        "Search, filter and inspect individual case records alongside investigation analytics."
    )

    # ============================================================
    # 1. ADVANCED CASE SEARCH
    # ============================================================

    heading(
        "CASE SEARCH",
        "Find an individual case",
        "Search using a Report Number or narrow the records using the available filters."
    )

    investigation_view = filtered.copy()

    # Search and filter controls
    col1, col2 = st.columns(2)

    with col1:
        report_search = st.text_input(
            "Search Report Number",
            placeholder="Enter full or partial Report Number...",
            key="investigation_report_search"
        )

    with col2:
        city_filter = st.selectbox(
            "Filter by City",
            ["All Cities"] + sorted(
                investigation_view["City"].dropna().astype(str).unique().tolist()
            ),
            key="investigation_city_filter"
        )

    col3, col4 = st.columns(2)

    with col3:
        crime_filter = st.selectbox(
            "Filter by Crime Category",
            ["All Categories"] + sorted(
                investigation_view["Crime Description"]
                .dropna().astype(str).unique().tolist()
            ),
            key="investigation_crime_filter"
        )

    with col4:
        status_filter = st.selectbox(
            "Filter by Case Status",
            ["All Statuses"] + sorted(
                investigation_view["Case Status"]
                .dropna().astype(str).unique().tolist()
            ),
            key="investigation_status_filter"
        )

    # Apply search
    if report_search.strip():
        investigation_view = investigation_view[
            investigation_view["Report Number"]
            .astype(str)
            .str.contains(
                report_search.strip(),
                case=False,
                regex=False,
                na=False
            )
        ]

    # Apply city filter
    if city_filter != "All Cities":
        investigation_view = investigation_view[
            investigation_view["City"].astype(str) == city_filter
        ]

    # Apply crime filter
    if crime_filter != "All Categories":
        investigation_view = investigation_view[
            investigation_view["Crime Description"].astype(str) == crime_filter
        ]

    # Apply case status filter
    if status_filter != "All Statuses":
        investigation_view = investigation_view[
            investigation_view["Case Status"].astype(str) == status_filter
        ]

    # Search result summary
    st.markdown("---")

    result_col1, result_col2 = st.columns(2)

    with result_col1:
        st.metric(
            "Matching Case Records",
            f"{len(investigation_view):,}"
        )

    with result_col2:
        st.metric(
            "Unique Report Numbers",
            f"{investigation_view['Report Number'].nunique():,}"
        )

    if investigation_view.empty:

        st.warning(
            "No case records match your search. "
            "Try another Report Number or change the filters."
        )

    else:

        # ========================================================
        # 2. SELECT AN INDIVIDUAL CASE
        # ========================================================

        heading(
            "CASE SELECTION",
            "Choose a case to investigate"
        )

        case_options = (
            investigation_view["Report Number"]
            .dropna()
            .astype(str)
            .drop_duplicates()
            .tolist()
        )

        if case_options:

            selected_report = st.selectbox(
                "Select Report Number",
                case_options,
                key="investigation_selected_report"
            )

            case_record = investigation_view[
                investigation_view["Report Number"].astype(str)
                == selected_report
            ].copy()

            # Use the first matching record for the individual profile
            case = case_record.iloc[0]

            # ====================================================
            # 3. INDIVIDUAL CASE PROFILE
            # ====================================================

            st.markdown("---")

            heading(
                "INVESTIGATION PROFILE",
                f"Report #{selected_report}",
                "Detailed information available in the supplied dataset."
            )

            # Main case information
            p1, p2, p3 = st.columns(3)

            with p1:
                st.metric(
                    "City",
                    str(case["City"])
                )

            with p2:
                st.metric(
                    "Crime Category",
                    str(case["Crime Description"])
                )

            with p3:
                current_status = str(case["Case Status"])
                st.metric(
                    "Case Status",
                    current_status
                )

            st.markdown("---")

            # Date and reporting information
            heading(
                "TIMELINE INFORMATION",
                "Occurrence and reporting details"
            )

            t1, t2, t3 = st.columns(3)

            with t1:
                st.write("**Date of Occurrence**")
                st.write(str(case["Date of Occurance"]))

            with t2:
                st.write("**Date Reported**")
                st.write(str(case["Date Reported"]))

            with t3:
                st.write("**Time of Occurrence**")
                st.write(str(case["Time of Occurrence"]))

            # Reporting delay
            delay = case.get("Reporting Delay Days")

            if pd.notna(delay):
                st.metric(
                    "Reporting Delay",
                    f"{float(delay):.2f} days"
                )
            else:
                st.info("Reporting delay is unavailable for this record.")

            st.markdown("---")

            # Victim and crime information
            heading(
                "VICTIM AND CRIME DETAILS",
                "Available record information"
            )

            v1, v2, v3 = st.columns(3)

            with v1:
                st.write("**Victim Age**")
                st.write(str(case["Victim Age"]))

            with v2:
                st.write("**Victim Gender**")
                st.write(str(case["Victim Gender"]))

            with v3:
                st.write("**Age Group**")
                st.write(str(case["Age Group"]))

            v1, v2, v3 = st.columns(3)

            with v1:
                st.write("**Crime Code**")
                st.write(str(case["Crime Code"]))

            with v2:
                st.write("**Crime Domain**")
                st.write(str(case["Crime Domain"]))

            with v3:
                st.write("**Weapon Used**")
                st.write(str(case["Weapon Used"]))

            st.markdown("---")

            # Police deployment and closure information
            heading(
                "INVESTIGATION STATUS",
                "Police deployment and case closure details"
            )

            i1, i2, i3 = st.columns(3)

            with i1:
                st.metric(
                    "Police Deployed",
                    str(case["Police Deployed"])
                )

            with i2:
                st.write("**Case Closed**")
                st.write(str(case["Case Closed"]))

            with i3:
                st.write("**Closure Date**")
                st.write(str(case["Date and Time of Case Closed"]))

            closure_duration = case.get("Closure Duration Days")

            if pd.notna(closure_duration):
                st.metric(
                    "Closure Duration",
                    f"{float(closure_duration):.2f} days"
                )
            else:
                st.info(
                    "Closure duration is unavailable for this record."
                )

            st.markdown("---")

            # ====================================================
            # 4. COMPLETE RECORD
            # ====================================================

            heading(
                "COMPLETE CASE RECORD",
                "Underlying database information"
            )

            render_table(case_record, 350)

            # ====================================================
            # 5. INDIVIDUAL CASE EXPORT
            # ====================================================

            heading(
                "CASE EXPORT",
                "Download individual case information"
            )

            render_export(
                case_record,
                f"case_report_{selected_report}"
            )

        else:
            st.warning(
                "No valid Report Numbers are available in these results."
            )

    # ============================================================
    # 6. ORIGINAL CASE ANALYTICS
    # ============================================================

    st.markdown("---")

    heading(
        "INVESTIGATION ANALYTICS",
        "Overall case status and investigation timelines",
        "These charts describe the records in the current dashboard selection."
    )

    status = count_table(filtered, "Case Status")

    a, b = st.columns(2)

    with a:
        heading(
            "CASE STATUS",
            "Open versus closed records"
        )

        chart(
            px.pie(
                status,
                names="Case Status",
                values="Records",
                hole=.58,
                color="Case Status",
                color_discrete_map={
                    "Open": T["danger"],
                    "Closed": T["primary"]
                }
            ),
            T,
            "case_status"
        )

    with b:
        heading(
            "STATUS BY CITY",
            "Open and closed record counts"
        )

        cs = (
            filtered.groupby(["City", "Case Status"])
            .size()
            .reset_index(name="Records")
        )

        chart(
            px.bar(
                cs,
                x="City",
                y="Records",
                color="Case Status",
                barmode="group",
                color_discrete_sequence=[
                    T["danger"],
                    T["primary"]
                ]
            ),
            T,
            "case_city",
            470
        )

    a, b = st.columns(2)

    with a:
        heading(
            "REPORTING DELAY",
            "Occurrence to report (days)"
        )

        d = filtered.dropna(
            subset=["Reporting Delay Days"]
        )

        chart(
            px.histogram(
                d,
                x="Reporting Delay Days",
                nbins=25,
                color_discrete_sequence=[T["accent"]]
            ),
            T,
            "case_delay"
        )

        if not d.empty:
            st.metric(
                "Average reporting delay",
                f"{d['Reporting Delay Days'].mean():.2f} days"
            )

    with b:
        heading(
            "CLOSURE DURATION",
            "Report to closure date (days)"
        )

        d = filtered.dropna(
            subset=["Closure Duration Days"]
        )

        chart(
            px.histogram(
                d,
                x="Closure Duration Days",
                nbins=25,
                color_discrete_sequence=[T["secondary"]]
            ),
            T,
            "case_duration"
        )

        if not d.empty:
            st.metric(
                "Average closure duration",
                f"{d['Closure Duration Days'].mean():.2f} days"
            )

    st.caption(
        "These are date differences calculated from the supplied fields. "
        "They are not official investigation-performance measures. "
        "The individual case profile displays only information available "
        "in the supplied dataset."
    )

    
# ----------------------------- ANOMALY DETECTION ----------------
elif page == "Anomaly Detection":

    heading(
        "MODULE 15",
        "Crime anomaly detection",
        "Identify unusual records using the Isolation Forest machine-learning algorithm."
    )

    st.info(
        "This module identifies statistically unusual records in the supplied "
        "dataset. An anomaly does not mean that a crime is suspicious or that "
        "any person has committed wrongdoing."
    )

    # ------------------------------------------------------------
    # 1. AVAILABLE FEATURES
    # ------------------------------------------------------------

    heading(
        "MODEL CONFIGURATION",
        "Select analytical features",
        "Choose numerical variables for the anomaly detection model."
    )

    available_features = [
        "Victim Age",
        "Police Deployed",
        "Hour",
        "Reporting Delay Days",
        "Closure Duration Days"
    ]

    available_features = [
        col for col in available_features
        if col in filtered.columns
        and pd.api.types.is_numeric_dtype(filtered[col])
    ]

    if len(available_features) < 2:

        st.warning(
            "At least two numerical features are required for anomaly detection."
        )

    else:

        selected_features = st.multiselect(
            "Select features for the model",
            available_features,
            default=available_features,
            key="anomaly_features"
        )

        contamination = st.slider(
            "Expected proportion of anomalies",
            min_value=0.01,
            max_value=0.15,
            value=0.05,
            step=0.01,
            format="%.2f",
            help="This controls the model's expected proportion of unusual records."
        )

        random_state = 42

        # --------------------------------------------------------
        # 2. PREPARE DATA
        # --------------------------------------------------------

        if len(selected_features) < 2:

            st.warning(
                "Please select at least two numerical features."
            )

        else:

            model_data = filtered[
                selected_features
            ].copy()

            model_data = model_data.replace(
                [float("inf"), float("-inf")],
                float("nan")
            )

            valid_mask = model_data.notna().all(axis=1)

            model_data = model_data.loc[valid_mask]

            source_records = filtered.loc[
                valid_mask
            ].copy()

            st.markdown("---")

            st.metric(
                "Records available for modelling",
                f"{len(model_data):,}"
            )

            # ----------------------------------------------------
            # 3. TRAIN ISOLATION FOREST
            # ----------------------------------------------------

            if len(model_data) < 20:

                st.warning(
                    "At least 20 complete records are recommended "
                    "for this analysis."
                )

            else:

                with st.spinner(
                    "Training Isolation Forest model..."
                ):

                    anomaly_model = IsolationForest(
                        n_estimators=150,
                        contamination=contamination,
                        random_state=random_state,
                        n_jobs=-1
                    )

                    predictions = anomaly_model.fit_predict(
                        model_data
                    )

                    anomaly_scores = anomaly_model.decision_function(
                        model_data
                    )

                results = source_records.copy()

                results["Anomaly Status"] = [
                    "Anomaly" if value == -1 else "Normal"
                    for value in predictions
                ]

                results["Anomaly Score"] = anomaly_scores

                results["Anomaly Score"] = (
                    results["Anomaly Score"].round(5)
                )

                anomaly_records = results[
                    results["Anomaly Status"] == "Anomaly"
                ].copy()

                normal_records = results[
                    results["Anomaly Status"] == "Normal"
                ].copy()

                # ------------------------------------------------
                # 4. MODEL SUMMARY
                # ------------------------------------------------

                st.markdown("---")

                heading(
                    "MODEL RESULTS",
                    "Anomaly detection summary"
                )

                m1, m2, m3, m4 = st.columns(4)

                with m1:
                    st.metric(
                        "Total Analysed",
                        f"{len(results):,}"
                    )

                with m2:
                    st.metric(
                        "Anomalies Detected",
                        f"{len(anomaly_records):,}"
                    )

                with m3:
                    st.metric(
                        "Normal Records",
                        f"{len(normal_records):,}"
                    )

                with m4:
                    anomaly_percentage = (
                        len(anomaly_records) / len(results) * 100
                    )

                    st.metric(
                        "Anomaly Percentage",
                        f"{anomaly_percentage:.2f}%"
                    )

                # ------------------------------------------------
                # 5. ANOMALY DISTRIBUTION
                # ------------------------------------------------

                heading(
                    "ANOMALY DISTRIBUTION",
                    "Normal versus unusual records"
                )

                distribution = (
                    results["Anomaly Status"]
                    .value_counts()
                    .rename_axis("Status")
                    .reset_index(name="Records")
                )

                a, b = st.columns(2)

                with a:

                    chart(
                        px.pie(
                            distribution,
                            names="Status",
                            values="Records",
                            hole=0.58,
                            color="Status",
                            color_discrete_map={
                                "Normal": T["primary"],
                                "Anomaly": T["danger"]
                            }
                        ),
                        T,
                        "anomaly_distribution"
                    )

                with b:

                    chart(
                        px.bar(
                            distribution,
                            x="Status",
                            y="Records",
                            color="Status",
                            color_discrete_map={
                                "Normal": T["primary"],
                                "Anomaly": T["danger"]
                            },
                            text="Records"
                        ),
                        T,
                        "anomaly_bar"
                    )

                # ------------------------------------------------
                # 6. FEATURE COMPARISON
                # ------------------------------------------------

                st.markdown("---")

                heading(
                    "FEATURE COMPARISON",
                    "Normal records versus detected anomalies"
                )

                comparison_feature = st.selectbox(
                    "Choose a feature to compare",
                    selected_features,
                    key="anomaly_comparison_feature"
                )

                comparison_data = results[
                    ["Anomaly Status", comparison_feature]
                ].copy()

                chart(
                    px.box(
                        comparison_data,
                        x="Anomaly Status",
                        y=comparison_feature,
                        color="Anomaly Status",
                        color_discrete_map={
                            "Normal": T["primary"],
                            "Anomaly": T["danger"]
                        },
                        points="outliers"
                    ),
                    T,
                    "anomaly_feature_box"
                )

                # ------------------------------------------------
                # 7. TWO-DIMENSIONAL ANOMALY VISUALIZATION
                # ------------------------------------------------

                heading(
                    "ANOMALY SCATTER ANALYSIS",
                    "Explore unusual observations"
                )

                if len(selected_features) >= 2:

                    x_feature = st.selectbox(
                        "Horizontal axis",
                        selected_features,
                        index=0,
                        key="anomaly_x"
                    )

                    y_index = (
                        1 if selected_features[1] != x_feature else 0
                    )

                    y_feature = st.selectbox(
                        "Vertical axis",
                        selected_features,
                        index=y_index,
                        key="anomaly_y"
                    )

                    if x_feature == y_feature:

                        st.warning(
                            "Choose two different features for the scatter plot."
                        )

                    else:

                        scatter_fig = px.scatter(
                            results,
                            x=x_feature,
                            y=y_feature,
                            color="Anomaly Status",
                            hover_data=[
                                col for col in [
                                    "Report Number",
                                    "City",
                                    "Crime Description",
                                    "Anomaly Score"
                                ]
                                if col in results.columns
                            ],
                            color_discrete_map={
                                "Normal": T["primary"],
                                "Anomaly": T["danger"]
                            },
                            title="Normal and anomalous records"
                        )

                        chart(
                            scatter_fig,
                            T,
                            "anomaly_scatter",
                            480
                        )

                # ------------------------------------------------
                # 8. ANOMALY RECORD TABLE
                # ------------------------------------------------

                st.markdown("---")

                heading(
                    "DETECTED ANOMALIES",
                    "Records identified as unusual"
                )

                if anomaly_records.empty:

                    st.info(
                        "No anomalies were identified with the current settings."
                    )

                else:

                    display_columns = [
                        col for col in [
                            "Report Number",
                            "City",
                            "Crime Description",
                            "Victim Age",
                            "Victim Gender",
                            "Police Deployed",
                            "Hour",
                            "Reporting Delay Days",
                            "Closure Duration Days",
                            "Anomaly Score"
                        ]
                        if col in anomaly_records.columns
                    ]

                    st.dataframe(
                        anomaly_records[display_columns]
                        .sort_values("Anomaly Score"),
                        use_container_width=True,
                        hide_index=True
                    )

                    render_export(
                        anomaly_records,
                        "crime_anomaly_detection_results"
                    )

                # ------------------------------------------------
                # 9. FEATURE IMPORTANCE CONTEXT
                # ------------------------------------------------

                st.markdown("---")

                heading(
                    "FEATURE PROFILE",
                    "Average feature values by detection group"
                )

                profile = (
                    results.groupby("Anomaly Status")[selected_features]
                    .mean()
                    .round(2)
                    .reset_index()
                )

                st.dataframe(
                    profile,
                    use_container_width=True,
                    hide_index=True
                )

                # ------------------------------------------------
                # 10. INTERPRETATION
                # ------------------------------------------------

                heading(
                    "ANALYTICAL INTERPRETATION",
                    "Understanding the model output"
                )

                st.write(
                    f"The Isolation Forest model analysed "
                    f"{len(results):,} complete records using "
                    f"{len(selected_features)} selected numerical features."
                )

                st.write(
                    f"It identified {len(anomaly_records):,} records "
                    f"({anomaly_percentage:.2f}%) as unusual relative "
                    f"to the patterns learned from the supplied data."
                )

                st.caption(
                    "Isolation Forest anomaly scores are model-specific. "
                    "More negative scores generally indicate more unusual "
                    "observations. This model does not establish criminal "
                    "intent, causation, risk, or suspicious behaviour. "
                    "Results depend on feature selection, missing values, "
                    "the contamination setting and dataset characteristics."
                )



# ----------------------------- WEAPONS ----------------------
elif page == "Weapons & Deployment":
    heading("MODULE 06", "Weapons & police deployment", "Explore recorded weapon categories, crime domains and deployment values.")
    a, b = st.columns(2)
    with a:
        heading("WEAPON PROFILE", "Records by weapon category")
        w = count_table(filtered, "Weapon Used")
        chart(px.bar(w.sort_values("Records"), x="Records", y="Weapon Used",
                     orientation="h", color="Records",
                     color_continuous_scale=[T["surface2"], T["primary"]]), T, "weapon_dist", 480)
    with b:
        heading("CRIME DOMAIN", "Distribution by domain")
        dom = count_table(filtered, "Crime Domain")
        chart(px.treemap(dom, path=["Crime Domain"], values="Records",
                         color="Records", color_continuous_scale=[T["surface2"], T["secondary"]]), T, "weapon_domain", 480)
    heading("WEAPON × CRIME", "Which weapon labels appear alongside each crime category?")
    wc = filtered.groupby(["Crime Description", "Weapon Used"]).size().reset_index(name="Records")
    fig = px.bar(wc, x="Crime Description", y="Records", color="Weapon Used",
                 barmode="stack", color_discrete_sequence=T["palette"])
    fig.update_xaxes(tickangle=-45)
    chart(fig, T, "weapon_crime", 610)
    a, b = st.columns(2)
    with a:
        heading("POLICE DEPLOYMENT", "Average deployment by city")
        p = filtered.groupby("City")["Police Deployed"].mean().reset_index().sort_values("Police Deployed", ascending=False)
        chart(px.bar(p.head(20).sort_values("Police Deployed"), x="Police Deployed", y="City",
                     orientation="h", color="Police Deployed",
                     color_continuous_scale=[T["surface2"], T["accent"]]), T, "police_city", 540)
    with b:
        heading("DEPLOYMENT × STATUS", "Average deployment by case status")
        ps = filtered.groupby("Case Status")["Police Deployed"].mean().reset_index()
        chart(px.bar(ps, x="Case Status", y="Police Deployed", color="Case Status",
                     color_discrete_sequence=[T["danger"], T["primary"]]), T, "police_status")


# ----------------------------- ADVANCED ANALYTICS ------------
elif page == "Analytics Lab":
    heading(
        "MODULE 07",
        "Advanced statistical analytics",
        "Explore categorical associations using Chi-square tests and Cramer's V."
    )

    st.info(
        "These tests identify statistical associations in the supplied dataset. "
        "They do not establish causation or real-world crime risk."
    )

    # Existing numeric correlation analysis
    numeric = [
        "Victim Age", "Police Deployed", "Year", "Month",
        "Hour", "Reporting Delay Days", "Closure Duration Days"
    ]

    corr = filtered[numeric].corr(numeric_only=True)

    heading("CORRELATION MATRIX", "Numeric-field relationships")

    chart(
        px.imshow(
            corr,
            text_auto=".2f",
            zmin=-1,
            zmax=1,
            color_continuous_scale="RdBu_r",
            aspect="auto"
        ),
        T,
        "analytics_corr",
        570
    )

    # New categorical association analysis
    heading(
        "CHI-SQUARE ASSOCIATION TEST",
        "Test relationships between categorical variables"
    )

    categorical_columns = [
        "Victim Gender",
        "Crime Domain",
        "Case Status",
        "Weapon Used",
        "Crime Description",
        "City"
    ]

    c1, c2 = st.columns(2)

    with c1:
        variable_1 = st.selectbox(
            "Select first variable",
            categorical_columns,
            index=0,
            key="chi_variable_1"
        )

    with c2:
        variable_2 = st.selectbox(
            "Select second variable",
            categorical_columns,
            index=1,
            key="chi_variable_2"
        )

    if variable_1 == variable_2:
        st.warning("Please select two different variables.")

    else:
        analysis_data = filtered[[variable_1, variable_2]].dropna()

        # Group very rare categories to avoid an excessively sparse table.
        def group_rare_categories(series, minimum=20):
            counts = series.value_counts()
            rare = counts[counts < minimum].index
            return series.where(~series.isin(rare), "Other / Rare")

        first = group_rare_categories(analysis_data[variable_1])
        second = group_rare_categories(analysis_data[variable_2])

        contingency = pd.crosstab(first, second)

        if (
            len(contingency) < 2
            or contingency.shape[1] < 2
            or contingency.values.sum() == 0
        ):
            st.warning(
                "Not enough distinct categories to perform this test."
            )

        else:
            chi2, p_value, dof, expected = chi2_contingency(contingency)

            n = contingency.to_numpy().sum()
            rows, cols = contingency.shape

            denominator = n * min(rows - 1, cols - 1)

            cramers_v = (
                (chi2 / denominator) ** 0.5
                if denominator > 0 else 0
            )

            m1, m2, m3, m4 = st.columns(4)

            m1.metric("Chi-square statistic", f"{chi2:,.2f}")
            m2.metric("P-value", f"{p_value:.6g}")
            m3.metric("Degrees of freedom", f"{dof:,}")
            m4.metric("Cramer's V", f"{cramers_v:.3f}")

            if p_value < 0.05:
                st.success(
                    "The test indicates evidence of an association "
                    "between the selected variables."
                )
            else:
                st.info(
                    "The test does not provide sufficient evidence "
                    "of an association at the 5% significance level."
                )

            heading(
                "CONTINGENCY TABLE",
                "Observed record counts"
            )

            st.dataframe(
                contingency,
                use_container_width=True
            )

            heading(
                "EXPECTED FREQUENCIES",
                "Counts expected if the variables were independent"
            )

            expected_df = pd.DataFrame(
                expected,
                index=contingency.index,
                columns=contingency.columns
            )

            st.dataframe(
                expected_df.round(2),
                use_container_width=True
            )

            st.caption(
                "Important: Chi-square assumptions should be checked. "
                "Sparse expected cell counts can make the approximation "
                "unreliable. Categories grouped as Other / Rare are "
                "combined only for this analysis."
            )

    # Existing city-crime heatmap
    heading("CITY × CRIME", "Cross-tabulation heatmap")

    pivot = pd.pivot_table(
        filtered,
        index="Crime Description",
        columns="City",
        values="Report Number",
        aggfunc="count",
        fill_value=0
    )

    chart(
        px.imshow(
            pivot,
            aspect="auto",
            color_continuous_scale=[T["surface"], T["primary"]],
            labels=dict(color="Records")
        ),
        T,
        "analytics_city_crime",
        700
    )

    # Existing weekday-hour heatmap
    heading("WEEKDAY × HOUR", "When records occur in the supplied data")

    wh = pd.pivot_table(
        filtered,
        index="Weekday",
        columns="Hour",
        values="Report Number",
        aggfunc="count",
        fill_value=0
    )

    wh = wh.reindex([
        "Monday", "Tuesday", "Wednesday", "Thursday",
        "Friday", "Saturday", "Sunday"
    ])

    chart(
        px.imshow(
            wh,
            aspect="auto",
            color_continuous_scale=[T["surface"], T["secondary"]],
            labels=dict(color="Records")
        ),
        T,
        "analytics_week_hour",
        500
    )

    st.info(
        "The dataset has an unusually regular date/category distribution. "
        "Treat findings as descriptive of this file until its provenance "
        "and representativeness are independently established."
    )
    # ---------------- K-MEANS CLUSTERING ----------------
    
    st.markdown("---")
    heading(
        "MACHINE LEARNING",
        "Crime Pattern Clustering",
        "Discover groups of similar records using K-Means clustering."
    )
    
    cluster_features = [
        "Victim Age",
        "Police Deployed",
        "Hour",
        "Reporting Delay Days",
        "Closure Duration Days"
    ]
    
    available_features = [
        col for col in cluster_features if col in filtered.columns
    ]
    
    if len(available_features) < 2:
        st.warning("Not enough numerical features are available for clustering.")
    
    else:
        cluster_data = filtered[available_features].copy()
    
        cluster_data = cluster_data.replace(
            [float("inf"), float("-inf")], float("nan")
        ).dropna()
    
        if len(cluster_data) < 10:
            st.warning("At least 10 complete records are required.")
    
        else:
            max_clusters = min(8, len(cluster_data) - 1)
    
            col1, col2 = st.columns(2)
    
            with col1:
                n_clusters = st.slider(
                    "Number of clusters",
                    min_value=2,
                    max_value=max_clusters,
                    value=min(3, max_clusters)
                )
    
            with col2:
                st.metric("Records analysed", f"{len(cluster_data):,}")
    
            scaler = StandardScaler()
            scaled_data = scaler.fit_transform(cluster_data)
    
            kmeans = KMeans(
                n_clusters=n_clusters,
                random_state=42,
                n_init=10
            )
    
            cluster_labels = kmeans.fit_predict(scaled_data)
    
            cluster_data["Cluster"] = (
                cluster_labels.astype(str)
            )
    
            score = silhouette_score(
                scaled_data,
                cluster_labels
            )
    
            st.markdown("### Clustering performance")
    
            c1, c2 = st.columns(2)
    
            c1.metric("Clusters created", n_clusters)
            c2.metric("Silhouette score", f"{score:.3f}")
    
            st.caption(
                "Silhouette scores range from -1 to 1. "
                "Higher values generally indicate better-separated clusters. "
                "Interpret cautiously when clusters are small or overlapping."
            )
    
            st.markdown("### Cluster visualisation")
    
            x_feature = st.selectbox(
                "X-axis",
                available_features,
                index=0,
                key="cluster_x"
            )
    
            y_feature = st.selectbox(
                "Y-axis",
                available_features,
                index=1,
                key="cluster_y"
            )
    
            fig = px.scatter(
                cluster_data,
                x=x_feature,
                y=y_feature,
                color="Cluster",
                title="K-Means Cluster Distribution",
                opacity=0.7
            )
    
            chart(fig, T, "kmeans_cluster_chart", height=480)
    
            st.markdown("### Cluster profiles")
    
            profile = cluster_data.groupby("Cluster")[
                available_features
            ].mean().round(2)
    
            st.dataframe(profile, use_container_width=True)
    
            st.markdown("### Cluster sizes")
    
            sizes = (
                cluster_data["Cluster"]
                .value_counts()
                .sort_index()
                .rename_axis("Cluster")
                .reset_index(name="Records")
            )
    
            fig = px.bar(
                sizes,
                x="Cluster",
                y="Records",
                color="Cluster",
                title="Number of records in each cluster"
            )
    
            chart(fig, T, "kmeans_cluster_sizes")
    
            st.info(
                "These clusters represent similarities among records in "
                "the supplied dataset. They do not predict crime, identify "
                "criminals, or establish real-world crime-risk levels."
            )

    

    
# ----------------------------- DATA STUDIO -------------------


elif page == "Crime Forecasting":

    heading(
        "MODULE 08",
        "Crime Forecasting & Prediction",
        "Interactive time-series analysis, model comparison and future projections."
    )

    st.info(
        "This module forecasts monthly records in the supplied dataset. "
        "It does not predict actual future crime in India."
    )

    date_column = "Date of Occurance"

    if date_column not in filtered.columns:

        st.error("Occurrence date column is not available.")

    else:

        forecast_data = filtered.copy()

        forecast_data[date_column] = pd.to_datetime(
            forecast_data[date_column],
            errors="coerce"
        )

        forecast_data = forecast_data.dropna(
            subset=[date_column]
        )

        monthly = (
            forecast_data
            .set_index(date_column)
            .resample("MS")
            .size()
            .asfreq("MS", fill_value=0)
        )

        if len(monthly) < 30:

            st.warning(
                "At least 30 months of historical records are required. "
                "Please expand the dashboard date filter."
            )

        else:

            # -------------------------------------------------
            # 1. HISTORICAL OVERVIEW
            # -------------------------------------------------

            heading(
                "01 | HISTORICAL ANALYSIS",
                "Monthly crime-record distribution"
            )

            total_records = int(monthly.sum())
            average_records = monthly.mean()
            highest_month = monthly.idxmax().strftime("%B %Y")
            highest_count = int(monthly.max())

            c1, c2, c3 = st.columns(3)

            c1.metric("Total Records", f"{total_records:,}")
            c2.metric("Monthly Average", f"{average_records:,.1f}")
            c3.metric("Highest Month", highest_month)

            historical = monthly.rename(
                "Records"
            ).reset_index()

            historical.columns = ["Month", "Records"]

            fig_history = px.area(
                historical,
                x="Month",
                y="Records",
                markers=True,
                title="Historical Monthly Records"
            )

            chart(
                fig_history,
                T,
                "forecast_history",
                420
            )

            st.caption(
                f"The highest monthly count was {highest_count:,} "
                f"records in {highest_month}."
            )

            # -------------------------------------------------
            # 2. FORECAST SETTINGS
            # -------------------------------------------------

            heading(
                "02 | FORECAST CONTROLS",
                "Configure your prediction"
            )

            forecast_months = st.selectbox(
                "Select forecast duration",
                [3, 6, 12],
                index=1,
                format_func=lambda x: f"Next {x} months"
            )

            st.caption(
                "Both forecasting models use the same historical "
                "monthly record series."
            )

            # Last six months reserved for testing.
            train = monthly.iloc[:-6]
            test = monthly.iloc[-6:]

            # -------------------------------------------------
            # 3. MODEL COMPARISON
            # -------------------------------------------------

            heading(
                "03 | MODEL COMPARISON",
                "Holt-Winters vs Seasonal Naive"
            )

            try:

                # Holt-Winters validation
                hw_model = ExponentialSmoothing(
                    train,
                    trend="add",
                    seasonal="add",
                    seasonal_periods=12,
                    initialization_method="estimated"
                ).fit()

                hw_predictions = hw_model.forecast(6)

                # Seasonal Naive validation
                naive_predictions = train.iloc[-12:-6].copy()
                naive_predictions.index = test.index

                # Calculate errors
                hw_errors = test - hw_predictions
                naive_errors = test - naive_predictions

                hw_mae = hw_errors.abs().mean()
                hw_rmse = (hw_errors.pow(2).mean()) ** 0.5

                naive_mae = naive_errors.abs().mean()
                naive_rmse = (naive_errors.pow(2).mean()) ** 0.5

                comparison = pd.DataFrame({
                    "Model": [
                        "Holt-Winters",
                        "Seasonal Naive"
                    ],
                    "MAE": [
                        hw_mae,
                        naive_mae
                    ],
                    "RMSE": [
                        hw_rmse,
                        naive_rmse
                    ]
                })

                st.dataframe(
                    comparison.round(2),
                    use_container_width=True,
                    hide_index=True
                )

                fig_compare = px.bar(
                    comparison.melt(
                        id_vars="Model",
                        var_name="Metric",
                        value_name="Error"
                    ),
                    x="Model",
                    y="Error",
                    color="Metric",
                    barmode="group",
                    title="Forecast Error Comparison"
                )

                chart(
                    fig_compare,
                    T,
                    "forecast_comparison",
                    400
                )

                st.caption(
                    "MAE measures average absolute error. RMSE gives "
                    "greater weight to larger errors. Lower values are better."
                )

                # -------------------------------------------------
                # 4. ACTUAL VS PREDICTED
                # -------------------------------------------------

                heading(
                    "04 | VALIDATION",
                    "Actual records vs model predictions"
                )

                validation_df = pd.DataFrame({
                    "Month": test.index,
                    "Actual": test.values,
                    "Holt-Winters": hw_predictions.values,
                    "Seasonal Naive": naive_predictions.values
                })

                validation_long = validation_df.melt(
                    id_vars="Month",
                    var_name="Series",
                    value_name="Records"
                )

                fig_validation = px.line(
                    validation_long,
                    x="Month",
                    y="Records",
                    color="Series",
                    markers=True,
                    title="Six-Month Model Validation"
                )

                chart(
                    fig_validation,
                    T,
                    "forecast_validation",
                    430
                )

                # -------------------------------------------------
                # 5. FINAL FUTURE FORECAST
                # -------------------------------------------------

                heading(
                    "05 | FUTURE PROJECTIONS",
                    "Predicted monthly records"
                )

                final_hw_model = ExponentialSmoothing(
                    monthly,
                    trend="add",
                    seasonal="add",
                    seasonal_periods=12,
                    initialization_method="estimated"
                ).fit()

                future_hw = final_hw_model.forecast(
                    forecast_months
                )

                # Seasonal Naive future prediction:
                # Repeat the last 12-month seasonal pattern.
                last_year = monthly.iloc[-12:].values

                future_naive_values = [
                    last_year[i % 12]
                    for i in range(forecast_months)
                ]

                future_naive = pd.Series(
                    future_naive_values,
                    index=future_hw.index
                )

                future_df = pd.DataFrame({
                    "Month": future_hw.index,
                    "Holt-Winters": future_hw.values,
                    "Seasonal Naive": future_naive.values
                })

                future_df["Holt-Winters"] = (
                    future_df["Holt-Winters"]
                    .clip(lower=0)
                    .round(0)
                )

                future_df["Seasonal Naive"] = (
                    future_df["Seasonal Naive"]
                    .clip(lower=0)
                    .round(0)
                )

                st.dataframe(
                    future_df,
                    use_container_width=True,
                    hide_index=True
                )

                # -------------------------------------------------
                # 6. INTERACTIVE FORECAST CHART
                # -------------------------------------------------

                history_plot = historical.copy()

                history_plot["Series"] = "Historical"

                hw_plot = pd.DataFrame({
                    "Month": future_hw.index,
                    "Records": future_df["Holt-Winters"],
                    "Series": "Holt-Winters Forecast"
                })

                naive_plot = pd.DataFrame({
                    "Month": future_hw.index,
                    "Records": future_df["Seasonal Naive"],
                    "Series": "Seasonal Naive Forecast"
                })

                combined_plot = pd.concat(
                    [
                        history_plot,
                        hw_plot,
                        naive_plot
                    ],
                    ignore_index=True
                )

                heading(
                    "06 | FORECAST VISUALISATION",
                    "Historical and future records"
                )

                fig_forecast = px.line(
                    combined_plot,
                    x="Month",
                    y="Records",
                    color="Series",
                    markers=True,
                    title="Historical vs Future Forecast"
                )

                chart(
                    fig_forecast,
                    T,
                    "forecast_final_chart",
                    480
                )

                # -------------------------------------------------
                # 7. AUTOMATIC INSIGHTS
                # -------------------------------------------------

                heading(
                    "07 | AUTOMATED INSIGHTS",
                    "Understanding the forecast"
                )

                avg_hw = future_df["Holt-Winters"].mean()
                avg_naive = future_df["Seasonal Naive"].mean()

                if hw_mae < naive_mae:
                    model_result = "Holt-Winters performed better on the test period."
                elif hw_mae > naive_mae:
                    model_result = "Seasonal Naive performed better on the test period."
                else:
                    model_result = "Both models had equal MAE on the test period."

                st.write(
                    f"**Model comparison:** {model_result}"
                )

                st.write(
                    f"**Holt-Winters forecast average:** "
                    f"{avg_hw:,.1f} records per month."
                )

                st.write(
                    f"**Seasonal Naive forecast average:** "
                    f"{avg_naive:,.1f} records per month."
                )

                st.write(
                    f"**Historical highest month:** "
                    f"{highest_month} ({highest_count:,} records)."
                )

                st.caption(
                    "These insights describe patterns in the supplied "
                    "dataset. They do not establish real-world crime trends."
                )

                # -------------------------------------------------
                # 8. DOWNLOAD REPORT
                # -------------------------------------------------

                heading(
                    "08 | EXPORT",
                    "Download forecasting results"
                )

                csv_forecast = future_df.to_csv(
                    index=False
                ).encode("utf-8")

                st.download_button(
                    "Download Forecast CSV",
                    csv_forecast,
                    "crime_forecast_results.csv",
                    "text/csv"
                )

                csv_comparison = comparison.to_csv(
                    index=False
                ).encode("utf-8")

                st.download_button(
                    "Download Model Comparison CSV",
                    csv_comparison,
                    "crime_model_comparison.csv",
                    "text/csv"
                )

                st.info(
                    "Forecasts are experimental projections based on "
                    "historical records. They are not actual crime predictions."
                )

            except Exception as e:

                st.error(
                    f"Forecasting could not be completed: {e}"
                )


elif page == "Data Studio":
    heading("MODULE 08", "Data studio", "Search, inspect, filter and export the records currently in view.")
    search = st.text_input("⌕ Search across visible fields", placeholder="Try a city, weapon, crime category, report number...")
    view = filtered.copy()
    if search.strip():
        mask = view.astype(str).apply(lambda col: col.str.contains(search.strip(), case=False, na=False, regex=False)).any(axis=1)
        view = view[mask]
    a, b, c = st.columns(3)
    a.metric("Rows matching search", f"{len(view):,}")
    b.metric("Columns", f"{view.shape[1]:,}")
    c.metric("Missing cells in view", f"{int(view.isna().sum().sum()):,}")
    st.dataframe(view, use_container_width=True, hide_index=True, height=510)
    csv_bytes = view.to_csv(index=False).encode("utf-8")
    st.download_button("↓ Export current view as CSV", csv_bytes,
                       "crime_analysis_filtered.csv", "text/csv")
    st.markdown("---")
    heading("RECORD INSPECTOR", "Open one report record")
    if not view.empty:
        report_ids = view["Report Number"].astype(str).tolist()
        selected_id = st.selectbox("Report number", report_ids)
        selected = view[view["Report Number"].astype(str) == selected_id].iloc[0]
        left, right = st.columns(2)
        items = list(selected.items())
        midpoint = (len(items) + 1) // 2
        with left:
            for k, v in items[:midpoint]:
                st.write(f"**{k}:** {v if pd.notna(v) else 'Not recorded'}")
        with right:
            for k, v in items[midpoint:]:
                st.write(f"**{k}:** {v if pd.notna(v) else 'Not recorded'}")
    else:
        st.info("No records match the search phrase.")


# ----------------------------- DATA QUALITY -----------------
elif page == "Data Quality":
    heading("MODULE 09", "Data quality & validation",
            "Inspect missing values, duplicate identifiers, date consistency and unusual values.")
    profile = make_full_data_profile(filtered)
    render_kpi_row([
        ("Rows in current view", f"{profile['rows']:,}"),
        ("Columns", f"{profile['columns']:,}"),
        ("Missing cells", f"{profile['missing_cells']:,}"),
        ("Duplicate report IDs", f"{profile['duplicate_report_numbers']:,}")
    ])
    st.markdown("---")
    heading("MISSING VALUE AUDIT", "Missing values by column")
    missing = missing_value_report(filtered)
    render_table(missing, 430)
    render_export(missing, "crime_analysis_missing_value_audit")
    heading("DATE RANGE AUDIT", "Coverage of date fields")
    date_rows = []
    for col in ["Date Reported", "Date of Occurance", "Date and Time of Case Closed"]:
        result = date_range_profile(filtered, col)
        date_rows.append({
            "Field": col,
            "Valid values": result["valid"],
            "Earliest": result["earliest"],
            "Latest": result["latest"]
        })
    render_table(pd.DataFrame(date_rows), 220)
    heading("VALIDATION FLAGS", "Records requiring closer inspection")
    flags = data_quality_flags(filtered)
    flag_summary = flags.sum().rename_axis("Validation check").reset_index(name="Flagged records")
    flag_summary["Flagged %"] = flag_summary["Flagged records"].apply(
        lambda n: safe_percentage(n, len(filtered))
    )
    render_table(flag_summary, 300)
    flagged_rows = filtered.loc[flags.any(axis=1)].copy()
    st.metric("Records with at least one flag", f"{len(flagged_rows):,}")
    if not flagged_rows.empty:
        with st.expander("Inspect flagged records"):
            render_table(flagged_rows, 420)
            render_export(flagged_rows, "crime_analysis_flagged_records")
    else:
        st.success("No records were flagged by these selected checks.")
    status_check = validate_case_status(filtered)
    if status_check["available"]:
        st.write(
            f"Case status consistency: {status_check['matches']:,} matching "
            f"records out of {status_check['checked']:,} checked."
        )
    display_source_caveat()

# ----------------------------- CITY PROFILES ----------------


# ----------------------------- CITY PROFILES ----------------
elif page == "City Profiles":

    heading(
        "MODULE 10",
        "City intelligence profiles",
        "Explore Indian cities through an interactive geographical intelligence map."
    )

    # Approximate city-centre coordinates
    # These are reference locations, NOT individual crime incident locations.

    city_coordinates = {
        "Agra": (27.1767, 78.0081),
        "Ahmedabad": (23.0225, 72.5714),
        "Bangalore": (12.9716, 77.5946),
        "Bhopal": (23.2599, 77.4126),
        "Chennai": (13.0827, 80.2707),
        "Delhi": (28.6139, 77.2090),
        "Faridabad": (28.4089, 77.3178),
        "Ghaziabad": (28.6692, 77.4538),
        "Hyderabad": (17.3850, 78.4867),
        "Indore": (22.7196, 75.8577),
        "Jaipur": (26.9124, 75.7873),
        "Kalyan": (19.2437, 73.1355),
        "Kanpur": (26.4499, 80.3319),
        "Kolkata": (22.5726, 88.3639),
        "Lucknow": (26.8467, 80.9462),
        "Ludhiana": (30.9010, 75.8573),
        "Meerut": (28.9845, 77.7064),
        "Mumbai": (19.0760, 72.8777),
        "Nagpur": (21.1458, 79.0882),
        "Nashik": (19.9975, 73.7898),
        "Patna": (25.5941, 85.1376),
        "Pune": (18.5204, 73.8567),
        "Rajkot": (22.3039, 70.8022),
        "Srinagar": (34.0837, 74.7973),
        "Surat": (21.1702, 72.8311),
        "Thane": (19.2183, 72.9781),
        "Varanasi": (25.3176, 82.9739),
        "Vasai": (19.3919, 72.8397),
        "Visakhapatnam": (17.6868, 83.2185)
    }

    city_options = sorted(
        filtered["City"].dropna().unique().tolist()
    )

    if not city_options:

        st.info("No city values are available in the current selection.")

    else:

        # ---------------- CITY MAP DATA ----------------

        map_data = (
            filtered.groupby("City")
            .size()
            .reset_index(name="Records")
        )

        map_data["Latitude"] = map_data["City"].map(
            lambda city: city_coordinates.get(city, (None, None))[0]
        )

        map_data["Longitude"] = map_data["City"].map(
            lambda city: city_coordinates.get(city, (None, None))[1]
        )

        map_data = map_data.dropna(
            subset=["Latitude", "Longitude"]
        ).copy()

        # ---------------- INTERACTIVE MAP ----------------

        heading(
            "INTERACTIVE INDIA MAP",
            "Explore crime records geographically",
            "Zoom, drag, hover over and click city markers to explore city profiles."
        )

        # Read selected city from a previous map click
        clicked_city = None

        if "city_profiles_map" in st.session_state:

            previous_event = st.session_state["city_profiles_map"]

            try:
                selected_objects = previous_event.selection.objects

                if selected_objects:
                    for layer_objects in selected_objects.values():
                        if layer_objects:
                            clicked_city = layer_objects[0].get("City")
                            break

            except (AttributeError, TypeError, KeyError):
                clicked_city = None

        # Keep only valid selected cities
        if clicked_city not in city_options:
            clicked_city = None

        # Dropdown remains available as an alternative to clicking
        default_city = (
            clicked_city
            if clicked_city
            else city_options[0]
        )

        selected_city = st.selectbox(
            "Or choose a city manually",
            city_options,
            index=city_options.index(default_city),
            key="city_profiles_dropdown"
        )

        # The manually selected city is used unless a map click
        # has selected another city in the current session.
        if clicked_city:
            selected_city = clicked_city

        # Highlight the selected city
        map_data["Selected"] = (
            map_data["City"] == selected_city
        )

        map_data["Point Color"] = map_data["Selected"].apply(
            lambda selected:
                [255, 190, 60, 255]
                if selected
                else [40, 170, 230, 210]
        )

        map_data["Point Radius"] = map_data["Selected"].apply(
            lambda selected: 12500 if selected else 8000
        )

        # Interactive marker layer
        city_layer = pdk.Layer(
            "ScatterplotLayer",
            data=map_data,
            id="city_layer",
            get_position="[Longitude, Latitude]",
            get_fill_color="Point Color",
            get_line_color=[255, 255, 255, 220],
            get_radius="Point Radius",
            radius_units="meters",
            radius_min_pixels=6,
            radius_max_pixels=25,
            line_width_min_pixels=1,
            stroked=True,
            filled=True,
            pickable=True,
            auto_highlight=True
        )

        # Optional text labels
        label_layer = pdk.Layer(
            "TextLayer",
            data=map_data,
            get_position="[Longitude, Latitude]",
            get_text="City",
            get_size=12,
            get_color=[255, 255, 255, 230],
            get_pixel_offset=[0, -18],
            get_text_anchor="middle",
            get_alignment_baseline="bottom",
            pickable=False
        )

        view_state = pdk.ViewState(
            latitude=22.5,
            longitude=79.0,
            zoom=3.5,
            pitch=35,
            bearing=0
        )

        tooltip = {
            "html": """
                <div style="padding:8px">
                    <b style="font-size:16px">{City}</b>
                    <br/>
                    Records: <b>{Records}</b>
                    <br/>
                    <span>Click marker to view city profile</span>
                </div>
            """,
            "style": {
                "backgroundColor": "#172033",
                "color": "white"
            }
        }

        deck = pdk.Deck(
            layers=[city_layer, label_layer],
            initial_view_state=view_state,
            map_style="https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json",
            tooltip=tooltip
        )

        map_event = st.pydeck_chart(
            deck,
            key="city_profiles_map",
            on_select="rerun",
            selection_mode="single-object",
            height=600
        )

        # Get city clicked on the current map interaction
        try:
            current_objects = map_event.selection.objects

            if current_objects:
                for layer_objects in current_objects.values():
                    if layer_objects:
                        map_clicked_city = layer_objects[0].get("City")

                        if map_clicked_city in city_options:
                            selected_city = map_clicked_city

                        break

        except (AttributeError, TypeError, KeyError):
            pass

        st.caption(
            "Blue markers represent other cities. The golden marker represents "
            "the selected city. Marker size is based on the number of records "
            "in the current filtered dataset. Locations are approximate city "
            "centres, not actual crime incident coordinates."
        )

        # ---------------- SELECTED CITY SUMMARY ----------------

        city_view = filtered[
            filtered["City"] == selected_city
        ].copy()

        st.markdown("---")

        heading(
            "SELECTED CITY",
            f"City intelligence: {selected_city}"
        )

        metric_strip(city_view)

        # ---------------- CRIME MIX AND CASE STATUS ----------------

        left, right = st.columns(2)

        with left:

            heading(
                "CRIME MIX",
                f"Crime categories in {selected_city}"
            )

            crime_mix = count_table(
                city_view,
                "Crime Description"
            )

            chart(
                make_donut(
                    crime_mix,
                    "Crime Description",
                    "Records",
                    "Crime category mix",
                    T
                ),
                T,
                "city_profile_crime"
            )

        with right:

            heading(
                "CASE STATUS",
                "Open and closed records"
            )

            status_mix = count_table(
                city_view,
                "Case Status"
            )

            chart(
                make_donut(
                    status_mix,
                    "Case Status",
                    "Records",
                    "Case status mix",
                    T
                ),
                T,
                "city_profile_status"
            )

        # ---------------- AGE AND WEAPON ANALYSIS ----------------

        left, right = st.columns(2)

        with left:

            heading(
                "VICTIM AGE GROUP",
                "Age group distribution"
            )

            age_mix = count_table(
                city_view,
                "Age Group"
            )

            chart(
                px.bar(
                    age_mix,
                    x="Age Group",
                    y="Records",
                    color="Age Group",
                    color_discrete_sequence=T["palette"]
                ),
                T,
                "city_profile_age"
            )

        with right:

            heading(
                "WEAPON LABELS",
                "Recorded weapon categories"
            )

            weapon_mix = count_table(
                city_view,
                "Weapon Used"
            )

            chart(
                px.bar(
                    weapon_mix,
                    x="Weapon Used",
                    y="Records",
                    color="Weapon Used",
                    color_discrete_sequence=T["palette"]
                ),
                T,
                "city_profile_weapon"
            )

        # ---------------- YEARLY TREND ----------------

        heading(
            "YEARLY CITY TREND",
            "Occurrence records by year"
        )

        city_year = (
            city_view.groupby("Year")
            .size()
            .reset_index(name="Records")
        )

        chart(
            make_line(
                city_year,
                "Year",
                "Records",
                "City records by year",
                T
            ),
            T,
            "city_profile_year"
        )

        # ---------------- CITY RECORDS ----------------

        heading(
            "CITY RECORDS",
            "Underlying records for the selected city"
        )

        render_table(city_view, 420)

        render_export(
            city_view,
            f"crime_analysis_{selected_city.lower().replace(' ', '_')}_profile"
        )

    display_geography_caveat()

# ----------------------------- COMPARATIVE ANALYSIS ----------
elif page == "Comparative Analysis":
    heading("MODULE 11", "Comparative analysis studio",
            "Choose two segments and compare their record distributions.")
    cities_available = sorted(filtered["City"].dropna().unique().tolist())
    if len(cities_available) >= 2:
        c1, c2 = st.columns(2)
        city_a = c1.selectbox("First city", cities_available, key="compare_city_a")
        city_b = c2.selectbox("Second city", cities_available,
                              index=1, key="compare_city_b")
        if city_a == city_b:
            st.warning("Choose two different cities to make a comparison.")
        else:
            compare_data = filtered[filtered["City"].isin([city_a, city_b])]
            totals = compare_data.groupby("City").size().reset_index(name="Records")
            chart(px.bar(totals, x="City", y="Records", color="City",
                         color_discrete_sequence=T["palette"], text="Records"),
                  T, "compare_city_totals")
            crime_compare = compare_data.groupby(
                ["City", "Crime Description"]
            ).size().reset_index(name="Records")
            heading("CATEGORY COMPARISON", "Crime descriptions across both cities")
            chart(px.bar(crime_compare, x="Crime Description", y="Records",
                         color="City", barmode="group",
                         color_discrete_sequence=T["palette"]),
                  T, "compare_city_crime", 600)
            status_compare = compare_data.groupby(
                ["City", "Case Status"]
            ).size().reset_index(name="Records")
            heading("CASE STATUS COMPARISON", "Open and closed records")
            chart(px.bar(status_compare, x="City", y="Records",
                         color="Case Status", barmode="group",
                         color_discrete_sequence=[T["danger"], T["primary"]]),
                  T, "compare_city_status")
            render_table(crime_compare, 420)
            render_export(crime_compare, "crime_analysis_two_city_comparison")
    else:
        st.info("At least two cities are required for comparison.")
    st.markdown("---")
    heading("ADDITIONAL COMPARISON", "Select a field to compare by category")
    compare_field = st.selectbox(
        "Choose a categorical field",
        ["Crime Domain", "Weapon Used", "Age Group", "Victim Gender",
         "Case Status", "Crime Occurred"]
    )
    compare_summary = count_table(filtered, compare_field)
    compare_summary["Share %"] = compare_summary["Records"].apply(
        lambda n: safe_percentage(n, len(filtered))
    )
    chart(px.bar(compare_summary, x=compare_field, y="Records",
                 color=compare_field, color_discrete_sequence=T["palette"]),
          T, "compare_selected_field")
    render_table(compare_summary, 360)

# ----------------------------- HOMICIDE REVIEW ----------------
elif page == "Homicide Review":
    heading("MODULE 12", "Homicide-labelled record review",
            "A careful descriptive review of records carrying the Homicide label.")
    homicide_data = create_homicide_profile(filtered)
    if homicide_data.empty:
        st.info("No Homicide-labelled records match the current filters.")
    else:
        gender_counts = homicide_data["Victim Gender"].value_counts()
        female_count = int(gender_counts.get("F", 0))
        male_count = int(gender_counts.get("M", 0))
        other_count = int(len(homicide_data) - female_count - male_count)
        render_kpi_row([
            ("Homicide-labelled rows", f"{len(homicide_data):,}"),
            ("Female-coded rows", f"{female_count:,}"),
            ("Male-coded rows", f"{male_count:,}"),
            ("Other / unclassified codes", f"{other_count:,}")
        ])
        left, right = st.columns(2)
        with left:
            heading("GENDER", "Gender codes in homicide-labelled rows")
            g = count_table(homicide_data, "Victim Gender")
            chart(make_donut(g, "Victim Gender", "Records",
                             "Gender code distribution", T), T, "hom_review_gender")
        with right:
            heading("AGE GROUP", "Age-group distribution")
            a = count_table(homicide_data, "Age Group")
            chart(px.bar(a, x="Age Group", y="Records",
                         color="Age Group", color_discrete_sequence=T["palette"]),
                  T, "hom_review_age")
        left, right = st.columns(2)
        with left:
            heading("WEAPON LABEL", "Recorded weapon categories")
            w = count_table(homicide_data, "Weapon Used")
            chart(px.bar(w, x="Weapon Used", y="Records",
                         color="Weapon Used", color_discrete_sequence=T["palette"]),
                  T, "hom_review_weapon")
        with right:
            heading("CITY", "Cities represented in these records")
            c = count_table(homicide_data, "City").head(15)
            chart(px.bar(c.sort_values("Records"), x="Records", y="City",
                         orientation="h", color="Records",
                         color_continuous_scale=[T["surface2"], T["danger"]]),
                  T, "hom_review_city", 500)
        heading("HOMICIDE-LABELLED ROWS BY YEAR", "Occurrence year distribution")
        hy = homicide_data.groupby("Year").size().reset_index(name="Records")
        chart(make_line(hy, "Year", "Records", "Homicide-labelled records by year", T),
              T, "hom_review_year")
        heading("RECORD INSPECTION", "Underlying homicide-labelled rows")
        render_table(homicide_data, 420)
        render_export(homicide_data, "crime_analysis_homicide_labelled_records")
    display_homicide_caveat()

# ----------------------------- SUMMARY REPORTS ---------------

elif page == "Summary Reports":
    heading(
        "MODULE 13",
        "Summary report builder",
        "Generate downloadable intelligence reports and individual case PDFs."
    )

    # --------------------------------------------------
    # PDF GENERATOR FUNCTION
    # --------------------------------------------------
    def create_intelligence_pdf(title, subtitle, sections):
        buffer = BytesIO()

        doc = SimpleDocTemplate(
            buffer,
            pagesize=landscape(A4),
            rightMargin=15 * mm,
            leftMargin=15 * mm,
            topMargin=15 * mm,
            bottomMargin=15 * mm
        )

        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            "CustomTitle",
            parent=styles["Title"],
            fontSize=19,
            leading=24,
            textColor=colors.HexColor("#17365D"),
            alignment=TA_CENTER,
            spaceAfter=8
        )

        subtitle_style = ParagraphStyle(
            "CustomSubtitle",
            parent=styles["Normal"],
            fontSize=9,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#64748B"),
            spaceAfter=18
        )

        section_style = ParagraphStyle(
            "SectionHeading",
            parent=styles["Heading2"],
            fontSize=12,
            leading=16,
            textColor=colors.HexColor("#1D4ED8"),
            spaceBefore=12,
            spaceAfter=7
        )

        cell_style = ParagraphStyle(
            "TableCell",
            parent=styles["Normal"],
            fontSize=7,
            leading=9,
            wordWrap="CJK"
        )

        header_style = ParagraphStyle(
            "TableHeader",
            parent=cell_style,
            textColor=colors.white,
            fontName="Helvetica-Bold"
        )

        story = [
            Paragraph(escape(title), title_style),
            Paragraph(escape(subtitle), subtitle_style)
        ]

        for section_title, content in sections:
            story.append(Paragraph(escape(str(section_title)), section_style))

            if isinstance(content, pd.DataFrame):
                if content.empty:
                    story.append(Paragraph("No records available.", styles["Normal"]))
                    continue

                pdf_data = [
                    [
                        Paragraph(escape(str(col)), header_style)
                        for col in content.columns
                    ]
                ]

                # Keep PDF tables manageable
                display_data = content.head(100)

                for _, row in display_data.iterrows():
                    pdf_row = []

                    for value in row:
                        if pd.isna(value):
                            value = "Not Available"

                        text_value = str(value)

                        if len(text_value) > 120:
                            text_value = text_value[:117] + "..."

                        pdf_row.append(
                            Paragraph(escape(text_value), cell_style)
                        )

                    pdf_data.append(pdf_row)

                available_width = landscape(A4)[0] - 30 * mm
                col_width = available_width / max(len(content.columns), 1)

                pdf_table = Table(
                    pdf_data,
                    colWidths=[col_width] * len(content.columns),
                    repeatRows=1,
                    hAlign="LEFT"
                )

                pdf_table.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0),
                     colors.HexColor("#17365D")),
                    ("GRID", (0, 0), (-1, -1), 0.35,
                     colors.HexColor("#CBD5E1")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 5),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1),
                     [colors.white, colors.HexColor("#F1F5F9")])
                ]))

                story.append(pdf_table)

                if len(content) > 100:
                    story.append(Spacer(1, 5))
                    story.append(Paragraph(
                        "Note: The PDF displays the first 100 rows of this table.",
                        styles["Italic"]
                    ))

            elif isinstance(content, (list, tuple)):
                for item in content:
                    story.append(
                        Paragraph(escape(str(item)), styles["Normal"])
                    )
                    story.append(Spacer(1, 4))

            else:
                story.append(
                    Paragraph(escape(str(content)), styles["Normal"])
                )

            story.append(Spacer(1, 8))

        def add_page_number(canvas, document):
            canvas.saveState()
            canvas.setFont("Helvetica", 8)
            canvas.setFillColor(colors.HexColor("#64748B"))
            canvas.drawRightString(
                landscape(A4)[0] - 15 * mm,
                8 * mm,
                f"Page {document.page}"
            )
            canvas.restoreState()

        doc.build(
            story,
            onFirstPage=add_page_number,
            onLaterPages=add_page_number
        )

        buffer.seek(0)
        return buffer.getvalue()

    # --------------------------------------------------
    # DATASET OVERVIEW
    # --------------------------------------------------
    profile = make_full_data_profile(filtered)

    render_kpi_row([
        ("Records", f"{profile['rows']:,}"),
        ("Cities", f"{profile['cities']:,}"),
        ("Crime labels", f"{profile['crime_labels']:,}"),
        ("Missing cells", f"{profile['missing_cells']:,}")
    ])

    # --------------------------------------------------
    # REPORT TYPE SELECTION
    # --------------------------------------------------
    report_type = st.selectbox(
        "Choose report",
        [
            "Executive overview",
            "City summary",
            "Crime category summary",
            "Victim demographics",
            "Case status summary",
            "Weapon summary",
            "Crime domain summary",
            "Occurrence time summary",
            "Police deployment summary"
        ]
    )

    if report_type == "Executive overview":
        report = pd.DataFrame({
            "Observation": build_insight_text(filtered)
        })

        st.subheader("Executive observations")
        render_table(report, 300)

    elif report_type == "City summary":
        report = make_city_share_table(filtered)

    elif report_type == "Crime category summary":
        report = make_category_share_table(filtered, "Crime Description")

    elif report_type == "Victim demographics":
        report = make_gender_crime_summary(filtered)

    elif report_type == "Case status summary":
        report = count_table(filtered, "Case Status")

    elif report_type == "Weapon summary":
        report = make_weapon_summary(filtered)

    elif report_type == "Crime domain summary":
        report = make_crime_domain_summary(filtered)

    elif report_type == "Occurrence time summary":
        report = make_crime_time_table(filtered)

    else:
        report = make_police_deployment_by_domain(filtered)

    if report_type != "Executive overview":
        st.subheader(report_type)
        render_table(report, 460)

        render_export(
            report,
            "crime_analysis_" + report_type.lower().replace(" ", "_")
        )

    # --------------------------------------------------
    # DOWNLOAD SELECTED REPORT AS PDF
    # --------------------------------------------------
    st.markdown("---")
    heading(
        "PDF REPORT",
        "Download intelligence report",
        "Export the currently selected report as a professionally formatted PDF."
    )

    summary_sections = [
        ("Dataset overview", pd.DataFrame({
            "Metric": ["Total records", "Cities", "Crime labels", "Missing cells"],
            "Value": [
                profile["rows"],
                profile["cities"],
                profile["crime_labels"],
                profile["missing_cells"]
            ]
        })),
        (report_type, report)
    ]

    summary_pdf = create_intelligence_pdf(
        "CRIME ANALYSIS & INTELLIGENCE REPORT",
        f"{report_type} | Generated on {pd.Timestamp.now():%d %B %Y}",
        summary_sections
    )

    st.download_button(
        label="Download Summary Report (PDF)",
        data=summary_pdf,
        file_name="Crime_Intelligence_Summary_Report.pdf",
        mime="application/pdf",
        use_container_width=True,
        key="summary_pdf_download"
    )

    # --------------------------------------------------
    # INDIVIDUAL CASE PDF GENERATOR
    # --------------------------------------------------
    st.markdown("---")

    heading(
        "INDIVIDUAL CASE REPORT",
        "Generate a case-specific PDF",
        "Select a Report Number to generate a detailed summary of its recorded information."
    )

    if "Report Number" in filtered.columns and not filtered.empty:

        report_numbers = sorted(
            filtered["Report Number"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        if report_numbers:

            selected_report_number = st.selectbox(
                "Select Report Number",
                report_numbers,
                key="individual_case_report_number"
            )

            selected_case = filtered[
                filtered["Report Number"].astype(str)
                == selected_report_number
            ].copy()

            st.success(
                f"{len(selected_case)} matching record(s) found."
            )

            case = selected_case.iloc[0]

            case_fields = [
                "Report Number",
                "City",
                "Crime Code",
                "Crime Description",
                "Crime Domain",
                "Date of Occurance",
                "Time of Occurrence",
                "Date Reported",
                "Victim Age",
                "Victim Gender",
                "Age Group",
                "Weapon Used",
                "Police Deployed",
                "Case Closed",
                "Case Status",
                "Date and Time of Case Closed",
                "Reporting Delay Days",
                "Closure Duration Days"
            ]

            case_details = []

            for field in case_fields:
                if field in selected_case.columns:
                    value = case[field]

                    if pd.isna(value):
                        value = "Not Available"

                    case_details.append({
                        "Field": field,
                        "Recorded Information": str(value)
                    })

            case_details_df = pd.DataFrame(case_details)

            st.subheader("Selected case details")
            render_table(case_details_df, 450)

            if len(selected_case) > 1:
                st.info(
                    "This Report Number appears in multiple records. "
                    "The PDF includes the first record's case details "
                    "and a table of all matching records."
                )

            individual_sections = [
                ("Case information", case_details_df)
            ]

            if len(selected_case) > 1:
                individual_sections.append(
                    ("All matching records", selected_case)
                )

            individual_pdf = create_intelligence_pdf(
                "INDIVIDUAL CASE SUMMARY",
                f"Report Number: {selected_report_number}",
                individual_sections
            )

            safe_filename = "".join(
                char if char.isalnum() or char in "-_" else "_"
                for char in selected_report_number
            )

            st.download_button(
                label="Download Individual Case PDF",
                data=individual_pdf,
                file_name=f"Case_Summary_{safe_filename}.pdf",
                mime="application/pdf",
                use_container_width=True,
                key="individual_case_pdf_download"
            )

        else:
            st.warning("No Report Numbers are available in the filtered dataset.")

    else:
        st.warning("No case records are available in the current filters.")

    # --------------------------------------------------
    # DATA DICTIONARY
    # --------------------------------------------------
    st.markdown("---")

    heading("DATA DICTIONARY", "Understand the dataset columns")

    dictionary = get_data_dictionary()

    render_table(dictionary, 420)
    render_export(dictionary, "crime_analysis_data_dictionary")

    heading("PROJECT INTERPRETATION", "Important limitations")

    display_source_caveat()
    display_geography_caveat()
    display_homicide_caveat()
    display_correlation_caveat()


    
# -------------------------------------------------------------------------
# NOTABLE CRIME CASES IN INDIA (2019–2024)
# -------------------------------------------------------------------------

st.markdown("---")

st.markdown("""
<div style="text-align:center; padding:22px 10px;">
    <p style="color:#C49A45; letter-spacing:4px; font-size:12px;">
        SPECIAL CASE STUDIES • 2019–2024
    </p>
    <h1 style="margin-bottom:8px;">
        Notable Crime Cases in India
    </h1>
    <p style="color:gray; font-size:14px;">
        A visual review of high-profile deaths and criminal investigations
        involving prominent public figures.
    </p>
</div>
""", unsafe_allow_html=True)

notable_cases = [
    {
        "name": "Sidhu Moose Wala",
        "year": "2022",
        "date": "29 May 2022",
        "place": "Jawaharke village, Mansa, Punjab",
        "crime": "Murder by shooting",
        "description": (
            "Punjabi singer Sidhu Moose Wala was shot dead by armed "
            "assailants while travelling in his vehicle. "
            "The incident led to a major murder investigation."
        ),
        "image": r"C:\Users\DELL\OneDrive\Desktop\Crime Analysis\images\Sidhu moose vala image.jpg",
        "source": "https://indianexpress.com/article/cities/amritsar/punjabi-singer-congress-leader-sidhu-moose-wala-shot-dead-7942590/"
    },
    {
        "name": "Sushant Singh Rajput",
        "year": "2020",
        "date": "14 June 2020",
        "place": "Bandra, Mumbai, Maharashtra",
        "crime": "Death by suicide (CBI closure report)",
        "description": (
            "Actor Sushant Singh Rajput was found dead at his Bandra "
            "residence. The CBI filed a closure report in March 2025, "
            "describing the death as a suicide."
        ),
        "image": r"C:\Users\DELL\OneDrive\Desktop\Crime Analysis\images\Sushant Singh Rajput.jpg",
        "source": "https://indianexpress.com/article/cities/mumbai/cbi-files-closure-report-in-sushant-singh-rajput-death-case-9900499/"
    },
    {
        "name": "Sonali Phogat",
        "year": "2022",
        "date": "23 August 2022",
        "place": "Anjuna, Goa",
        "crime": "Death followed by murder investigation",
        "description": (
            "Actor and politician Sonali Phogat died after being "
            "taken to a hospital in Goa. Police initially registered "
            "an unnatural death case, followed by a murder investigation."
        ),
        "image": r"C:\Users\DELL\OneDrive\Desktop\Crime Analysis\images\Sonali_phogat.jpg",
        "source": "https://www.indiatoday.in/india/story/sonali-phogat-death-goa-police-registers-murder-case-1992420-2022-08-25"
    },
    {
        "name": "Baba Siddique",
        "year": "2024",
        "date": "12 October 2024",
        "place": "Kherwadi, Bandra, Mumbai",
        "crime": "Murder by shooting",
        "description": (
            "Former Maharashtra minister Baba Siddique was shot "
            "outside his son's office in Mumbai and later died "
            "from his firearm injuries."
        ),
        "image": r"C:\Users\DELL\OneDrive\Desktop\Crime Analysis\images\baba siddiqui.jpg",
        "source": "https://www.mid-day.com/mumbai/mumbai-news/article/baba-siddique-shot-dead-post-mortem-confirms-he-died-of-gun-wounds-23410194"
    }
]

for i in range(0, len(notable_cases), 2):

    left, right = st.columns(2, gap="large")

    for col, case in zip([left, right], notable_cases[i:i + 2]):

        with col:

            with st.container(border=True):

                if os.path.exists(case["image"]):
                    st.image(
                        case["image"],
                        use_container_width=True
                    )
                else:
                    st.warning(
                        f"Image not found: {case['image']}"
                    )

                st.markdown(f"### {case['name']}")

                st.caption(
                    f"{case['year']}  •  {case['place']}"
                )

                st.markdown(
                    f"**Date of death:** {case['date']}"
                )

                st.markdown(
                    f"**Case classification:** {case['crime']}"
                )

                st.write(case["description"])

                with st.expander("Read case information and source"):
                    st.write(case["description"])
                    st.write(f"**Location:** {case['place']}")
                    st.write(f"**Date:** {case['date']}")
                    st.markdown(
                        f"[Read source article]({case['source']})"
                    )

st.markdown("""
<div style="
    text-align:center;
    padding:18px;
    color:gray;
    font-size:12px;
">
    These are independently curated academic case studies.
    They are separate from the supplied crime dataset.
    Investigation details and legal status should be interpreted
    using reliable reporting and court records.
</div>
""", unsafe_allow_html=True)

# -------------------------------------------------------------------------
# END OF NOTABLE CRIME CASES
# -------------------------------------------------------------------------



# ----------------------------- FOOTER / EXIT -----------------

st.markdown("---")
left, right = st.columns([5, 1])
with left:
    st.markdown('<div class="footer">CRIME ANALYSIS  •  ACADEMIC DATA ANALYTICS  •  RECORD COUNTS FROM THE SUPPLIED DATASET</div>', unsafe_allow_html=True)
with right:
    with st.popover("Exit / Help"):
        st.write("To close the dashboard, stop the Streamlit process in the terminal using **Ctrl + C**.")
        st.write("This button cannot close your browser or shut down the server by itself.")


# -------------------------------------------------------------------------
# END OF CRIME ANALYSIS INTELLIGENCE WORKSPACE
#
# Recommended project execution:
#   python -m pip install streamlit pandas plotly
#   python -m streamlit run crime_analysis_redesigned.py
#
# Keep crime_dataset_cleaned.csv in the same folder as this script.
# The app is a descriptive academic analytics tool. It is not an official
# law-enforcement system, a crime-rate calculator, or a predictive policing
# product. Model development and SQL connectivity can be integrated as
# separate validated project stages after the exploratory analysis.

