# streamlit_apps/05_dashboard.py — FINAL VERSION
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
from datetime import datetime


# Project-internal imports — chart functions live in services/
from services.dashboard_charts import (
    build_pareto_chart,
    build_status_donut,
    build_severity_bars,
    build_country_bars,
    figure_to_png_bytes,
)

st.set_page_config(
    page_title='LC Pipeline Dashboard',
    page_icon='📊',
    layout='wide'
)

# Load the data — same CSV from your notebook days
DATA_PATH = project_root / 'data' / 'output' / 'validation_report.csv'


@st.cache_data
def load_data(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)



df_full = load_data(DATA_PATH)

# === SIDEBAR ===
with st.sidebar:
    st.title('Filters')
    st.caption('Configure your view')
    st.divider()

    # Currency selector (unchanged)
    available_currencies = sorted(df_full['currency'].dropna().unique())
    selected_currency = st.selectbox(
        label='Currency',
        options=['All'] + list(available_currencies),
        index=0,
    )

    # Status selector — NOW APPEARS BEFORE severity because it drives it
    selected_status = st.selectbox(
        label='Validation Status',
        options=['All', 'CLEAN', 'FLAGGED'],
        index=0,
    )

    # CONDITIONAL severity filter — only shown when relevant
    # If user picks Status=CLEAN, severity is meaningless (clean LCs have no severity)
    # If user picks Status=ALL or FLAGGED, show severity filter normally
    if selected_status == 'CLEAN':
        selected_severities = []  # Empty = no filter applied
        st.caption('ℹ️ Severity filter hidden — clean LCs have no severity')
    else:
        available_severities = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']
        selected_severities = st.multiselect(
            label='Severity',
            options=available_severities,
            default=available_severities,
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



# === Tabbed dashboard layout ===

st.title('LC Pipeline — Validation Dashboard')

tab_overview, tab_data, tab_about = st.tabs([
    '📊 Overview',
    '📋 Raw Data',
    'ℹ️ About',
])

# ── TAB 1: Overview (KPIs + 2x2 chart grid) ──
with tab_overview:
    # KPIs row
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
            st.metric('Flagged %', f'{flagged / len(df) * 100:.0f}%')
        else:
            st.metric('Flagged %', '—')

    st.divider()

    st.subheader('📊 Validation Dashboard — 4-panel view')

    with st.expander('💡 How to read this dashboard'):
        st.markdown("""
        This dashboard answers four questions about your LC pipeline:

        - **Top-left (Pareto):** WHICH validator produces the most errors?
        - **Top-right (Donut):** HOW BAD is the overall failure rate?
        - **Bottom-left (Severity):** HOW URGENT are the flagged LCs?
        - **Bottom-right (Countries):** WHERE geographically should we focus?

        Read the dashboard top-to-bottom, left-to-right (the F-pattern).
        Each filter on the left narrows ALL four panels simultaneously.
        """)

    # ── ROW 1: Pareto (left) + Donut (right) ──
    row1_col1, row1_col2 = st.columns(2)

    with row1_col1:
        if len(df) > 0 and df['error_codes'].notna().any():
            fig_pareto = build_pareto_chart(df, figsize=(5, 3))
            st.image(figure_to_png_bytes(fig_pareto, dpi=100), width=500)
            plt.close(fig_pareto)

            with st.expander('ℹ️ About this chart'):
                st.markdown("""
                **Errors by Validator** shows how many errors each validator
                detected across the filtered LCs. Each bar = one validator.

                **What to look for:** A heavily skewed distribution (one
                or two tall bars) suggests a SYSTEMIC issue. A flat
                distribution suggests random data quality problems.
                """)
        else:
            st.info('ℹ️ No errors to display.')

    with row1_col2:
        if len(df) > 0:
            fig_donut = build_status_donut(df, figsize=(4, 3))
            st.image(figure_to_png_bytes(fig_donut, dpi=100), width=400)
            plt.close(fig_donut)

            with st.expander('ℹ️ About this chart'):
                st.markdown("""
                **Clean vs Flagged** shows the proportion of LCs that
                passed (CLEAN) vs. failed (FLAGGED) validation.

                **What to look for:** A bank should target <30% flagged
                rate for incoming LCs. Higher rates suggest upstream
                data quality issues at counterparty branches.
                """)
        else:
            st.info('ℹ️ No transactions.')

    # ── ROW 2: Severity (left) + Countries (right) ──
    row2_col1, row2_col2 = st.columns(2)

    with row2_col1:
        if len(df) > 0 and (df['severity'] != 'NONE').any():
            fig_severity = build_severity_bars(df, figsize=(5, 3))
            st.image(figure_to_png_bytes(fig_severity, dpi=100), width=500)
            plt.close(fig_severity)

            with st.expander('ℹ️ About this chart'):
                st.markdown("""
                **Errors by Severity** ranks flagged LCs by urgency.
                CRITICAL = must-fix today. LOW = address when capacity.

                **What to look for:** A high CRITICAL bar signals
                immediate attention required. A normal distribution
                across severities is healthier than concentration in
                one bucket.
                """)
        else:
            st.info('ℹ️ No flagged transactions.')

    with row2_col2:
        flagged_count = (df['validation_status'] == 'FLAGGED').sum()
        if flagged_count > 0:
            fig_countries = build_country_bars(df, figsize=(5, 3.5))
            st.image(figure_to_png_bytes(fig_countries, dpi=100), width=500)
            plt.close(fig_countries)

            with st.expander('ℹ️ About this chart'):
                st.markdown("""
                **Top Countries — Flagged LCs** shows which applicant
                countries contribute the most flagged transactions.

                **What to look for:** Concentration in one or two
                countries suggests a specific branch needs training.
                Dispersed distribution suggests systemic process issues.
                """)
        else:
            st.info('ℹ️ No country data.')

# ── TAB 2: Raw Data (the dataframe) ──
with tab_data:
    if len(df) == 0:
        st.warning('⚠️ No transactions match the current filters.')
    else:
        st.subheader(f'Validation Report ({len(df)} transactions)')
        st.dataframe(df, use_container_width=True, height=500)


# ── TAB 3: About (methodology + footer) ──
with tab_about:
    st.subheader('About this dashboard')

    st.markdown("""
    **Source:** `validation_report.csv`
    **Pipeline:** LC Pipeline — MT700 SWIFT validation
    **Severity:** Highest severity per LC

    This dashboard provides interactive exploration of Letter of Credit
    (LC) validation results. Each transaction is validated against eight
    rule sets (LEI, SHIP, AMT, XVAL, DATE, LC, BIC, PTY). Severity is
    assigned based on the highest-severity error found per LC.

    **How to use:**
    - Use the sidebar filters to narrow by currency, severity, or status
    - The Overview tab shows KPIs and 4-panel chart breakdown
    - The Raw Data tab shows all filtered transactions in tabular form
    - All views update live as filters change
    """)

    st.divider()

    st.caption(
        f'**Dashboard rendered:** {datetime.now().strftime("%Y-%m-%d %H:%M")}  ·  '
        f'**Showing:** {len(df)} of {len(df_full)} transactions  ·  '
        f'**Filters active:** Currency={selected_currency}, '
        f'Severities={", ".join(selected_severities) if selected_severities else "none"}, '
        f'Status={selected_status}'
    )





