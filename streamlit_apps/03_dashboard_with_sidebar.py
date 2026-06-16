# streamlit_apps/03_dashboard_with_sidebar.py — FINAL VERSION
# Now the widgets actually filter the data
# KPIs, table, everything reflects the active filter selection
import sys
from pathlib import Path
from matplotlib import pyplot as plt

# Add the project root (one level UP from streamlit_apps/) to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import streamlit as st
import pandas as pd
from services.dashboard_charts import build_pareto_chart, build_status_donut

st.set_page_config(
    page_title='LC Pipeline Dashboard',
    page_icon='📊',
    layout='wide'
)

# Load the data — same CSV from your notebook days
DATA_PATH = Path(__file__).parent.parent / 'data' / 'output' / 'validation_report.csv'


@st.cache_data
def load_data(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


df_full = load_data(DATA_PATH)

# === SIDEBAR ===
with st.sidebar:
    st.title('Filters')
    st.caption('Configure your view')
    st.divider()

    available_currencies = sorted(df_full['currency'].dropna().unique())
    selected_currency = st.selectbox(
        label='Currency',
        options=['All'] + list(available_currencies),
        index=0
    )

    available_severities = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']
    selected_severities = st.multiselect(
        label='Severity',
        options=available_severities,
        default=available_severities
    )

    selected_status = st.selectbox(
        label='Validation Status',
        options=['All', 'CLEAN', 'FLAGGED'],
        index=0
    )

    st.divider()
    st.caption(f'{len(df_full)} total LCs in dataset')

# === FILTER PIPELINE ===
# Start from full data, apply each filter step-by-step
# 'All' = skip that filter (don't narrow on this dimension)

df = df_full.copy()                          # Always start from clean copy

if selected_currency != 'All':
    df = df.query('currency == @selected_currency')

if selected_status != 'All':
    df = df.query('validation_status == @selected_status')

# Severity filter is trickier — it's stored in the 'severity' column
# but flagged rows can have multiple severities (one row = one transaction)
# The 'severity' field in your report = highest severity of all errors
if selected_severities:
    df = df[df['severity'].isin(selected_severities) | (df['severity'] == 'NONE')]
    # ↑ Keep rows where severity is in selected OR NaN (CLEAN rows have NaN)

# === MAIN AREA ===
st.title('LC Pipeline — Validation Dashboard')
st.markdown(f'*Showing {len(df)} of {len(df_full)} transactions*')

st.divider()

# KPIs — now reflect the FILTERED data
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric('Filtered LCs', len(df))

with col2:
    flagged = (df['validation_status'] == 'FLAGGED').sum()
    st.metric('Flagged', flagged)

with col3:
    clean = (df['validation_status'] == 'CLEAN').sum()
    st.metric('Clean', clean)

with col4:
    if len(df) > 0:
        flagged_pct = flagged / len(df) * 100
        st.metric('Flagged %', f'{flagged_pct:.0f}%')
    else:
        st.metric('Flagged %', '—')          # Avoid divide-by-zero

st.divider()

# Empty-state guard — show friendly message if nothing matches
if len(df) == 0:
    st.warning('⚠️ No transactions match the current filters. Try widening your selection.')
else:
    st.subheader(f'Validation Report ({len(df)} transactions)')
    st.dataframe(df, use_container_width=True, height=400)


# === Clean vs Flagged donut ===
from services.dashboard_charts import (
    build_pareto_chart,
    build_status_donut,
    build_severity_bars,
    build_country_bars,
    figure_to_png_bytes,    # NEW
)

st.divider()

if len(df) > 0:
    fig_donut = build_status_donut(df, figsize=(4, 3.5))
    donut_png = figure_to_png_bytes(fig_donut, dpi=100)
    st.image(donut_png, width=450)        # EXACT pixel width
    plt.close(fig_donut)                  # Free memory
else:
    st.info('ℹ️ No transactions match current filters.')

# === Errors by Validator Pareto ===
st.divider()

if len(df) > 0 and df['error_codes'].notna().any():
    fig_pareto = build_pareto_chart(df, figsize=(6, 3.5))
    pareto_png = figure_to_png_bytes(fig_pareto, dpi=100)
    st.image(pareto_png, width=600)       # EXACT pixel width
    plt.close(fig_pareto)
else:
    st.info('ℹ️ No errors to display with current filters.')

# === Errors by Severity — RAG breakdown ===
st.divider()

if len(df) > 0 and (df['severity'] != 'NONE').any():
    fig_severity = build_severity_bars(df)
    severity_png = figure_to_png_bytes(fig_severity, dpi=100)
    st.image(severity_png, width=500)
    plt.close(fig_severity)
else:
    st.info('ℹ️ No flagged transactions in current filter — no severity data.')


# === Top Countries — geographic concentration ===
st.divider()

flagged_count = (df['validation_status'] == 'FLAGGED').sum()
if flagged_count > 0:
    fig_countries = build_country_bars(df)
    countries_png = figure_to_png_bytes(fig_countries, dpi=100)
    st.image(countries_png, width=600)
    plt.close(fig_countries)
else:
    st.info('ℹ️ No flagged transactions — no country data to display.')









