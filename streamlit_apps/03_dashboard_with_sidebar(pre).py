# streamlit_apps/03_dashboard_with_sidebar(pre).py — UPGRADED
# Add real filter widgets to the sidebar
# We don't FILTER the data yet — that's Chunk 7
# Today we just READ the user's selections and show them back as text
# (Helps verify widgets work before plugging into data logic)

import streamlit as st
import pandas as pd
from pathlib import Path
from streamlit.source_util import page_icon_and_name

# Page config — must be FIRST st.* call in any app
st.set_page_config(
    page_title='LC Pipeline Dashboard',
    page_icon='📊',
    layout='wide'
)

# Load the data — same CSV from your notebook days
DATA_PATH = Path(__file__).parent.parent / 'data' / 'output' / 'validation_report.csv'
df = pd.read_csv(DATA_PATH)

# === SIDEBAR: All filters live here ===
with st.sidebar:
    st.title('Filters')
    st.caption('Configure your view')
    st.divider()

    # Widget 1: Currency selector (single choice)
    # We get the unique currencies FROM THE DATA — never hardcode
    available_currencies = sorted(df['currency'].dropna().unique())

    selected_currency = st.selectbox(
        label='Currency',                       # The label shown above
        options=['All'] + list(available_currencies),  # 'All' = no filter
        index=0                                  # Default: first option ('All')
    )

    # Widget 2: Severity multi-select
    # User can pick zero, one, or multiple severities at once
    available_severities = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']

    selected_severities = st.multiselect(
        label='Severity',
        options=available_severities,
        default=available_severities             # Default: all selected
    )

    # Widget 3: Validation status selector
    selected_status = st.selectbox(
        label='Validation Status',
        options=['All', 'CLEAN', 'FLAGGED'],
        index=0
    )

    st.divider()
    st.caption('Filters update the dashboard live (data filtering in next step)')

# === MAIN AREA ===
st.title('LC Pipeline — Validation Dashboard')
st.markdown('*Interactive view of validation results*')

# DEBUG block — show what user selected
# This is for OUR sanity check — we want to see widget values flow correctly
# We'll remove this in Chunk 7 once filtering works
st.subheader('🔍 Debug: Current filter state')
st.write(f'**Currency:** {selected_currency}')
st.write(f'**Severities selected:** {selected_severities}')
st.write(f'**Status:** {selected_status}')
st.divider()

# Original KPIs (unfiltered for now — Chunk 7 will fix this)
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric('Total LCs', len(df))
with col2:
    flagged = (df['validation_status'] == 'FLAGGED').sum()
    st.metric('Flagged', flagged)
with col3:
    clean = (df['validation_status'] == 'CLEAN').sum()
    st.metric('Clean', clean)
with col4:
    flagged_pct = flagged / len(df) * 100
    st.metric('Flagged %', f'{flagged_pct:.0f}%')

st.divider()
st.subheader('Raw Validation Report')
st.dataframe(df.head(20), use_container_width=True)

