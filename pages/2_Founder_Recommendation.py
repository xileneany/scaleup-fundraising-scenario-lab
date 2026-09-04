import streamlit as st

st.set_page_config(
    page_title="Founder Recommendation",
    page_icon="→",
    layout="wide",
)

st.title("Founder Recommendation")

st.write(
    "Executive recommendation based on the modeled scale-up, "
    "supply network and fundraising scenarios."
)

st.page_link(
    "app.py",
    label="← Back to Scenario Lab",
)
