import streamlit as st
# streamlit run /home/alara/projects/lc_pipeline/streamlit_apps/01_hola_streamlit.py

# st.title() renders an H1 heading at the top of the page
st.title('Hello from Streamlit!')

# st.write() is the "universal" Streamlit function
# It renders text, dataframes, charts, almost anything you pass it
st.write('This is my first Streamlit app.')
st.write('Running on Python.')

# st.slider() returns the current slider value
# Argument 1: label, Argument 2: min, Argument 3: max, Argument 4: default
age = st.slider('Pick a number', 0, 100, 25 )

# This line re-renders every time the slider moves
st.write(f'You picked: {age}')

# Add a divider so we can see boundaries
st.divider()


# A counter to prove the script reran
import datetime
st.caption(f'Page rendered at {datetime.datetime.now().strftime("%H:%M:%S")}')