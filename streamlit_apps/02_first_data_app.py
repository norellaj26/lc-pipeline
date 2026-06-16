# streamlit_apps/02_first_data_app.py
# Display real pipeline data in Streamlit
# This becomes the foundation for our LC validation dashboard

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Page configuration — set ONCE at top of every Streamlit app
# This sets browser tab title, icon, and layout
st.set_page_config(
    page_title='LC Pipeline Dashboard',
    page_icon='📊',
    layout='wide'                    # 'wide' uses full browser width
)

# Title and subtitle for the app
st.title('LC Pipeline — Validation Dashboard')
st.markdown('*Interactive view of validation results*')

# Load the data — same CSV from your notebook days
DATA_PATH = Path(__file__).parent.parent / 'data' / 'output' / 'validation_report.csv'
df = pd.read_csv(DATA_PATH)

# st.metric() — KPI display widget (great for headline numbers)
# Three columns of metrics at the top — Streamlit handles the layout
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

# Show the raw data — st.dataframe() makes a sortable, scrollable table
st.subheader('Raw Validation Report')
st.dataframe(df.head(20), use_container_width=True)