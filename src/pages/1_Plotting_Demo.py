import time
from itertools import chain

import numpy as np
import streamlit as st

st.set_page_config(page_title="Plotting Demo", page_icon="📈")

st.markdown("# Plotting Demo")
st.sidebar.header("Plotting Demo")
st.write(
    """This demo illustrates a combination of plotting and animation with
Streamlit. We're generating a bunch of random numbers in a loop for around
5 seconds. Enjoy!"""
)

progress_bar = st.sidebar.progress(0)
status_text = st.sidebar.empty()
last_rows = np.random.randn(1, 1)
chart = st.line_chart(last_rows)

st.button("Re-run")
i = 1
while True:
    new_rows = last_rows[-1, :] + np.random.randn(5, 1).cumsum(axis=0)
    status_text.text("%i%% Complete" % i)
    chart.add_rows(new_rows)
    progress_bar.progress(i)
    last_rows = new_rows
    time.sleep(0.05)
    i += 1
    if i == 101:
        progress_bar.empty()
        time.sleep(1.05)
        i = 1

# Streamlit widgets automatically run the script from top to bottom. Since
# this button is not connected to any other logic, it just causes a plain
# rerun.
