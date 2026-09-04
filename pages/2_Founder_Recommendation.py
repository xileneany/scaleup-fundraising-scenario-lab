import streamlit as st

st.set_page_config(
    page_title="Founder Recommendation",
    page_icon="→",
    layout="wide",
)

# ---------------------------------------------------------
# MICROHARVEST-INSPIRED VISUAL SYSTEM
# ---------------------------------------------------------

st.markdown(
    """
    <style>

    /* Main background */
    .stApp {
        background-color: #FFFFFF;
        color: #0B0B0B;
    }

    /* Main content */
    [data-testid="stMain"] {
        background-color: #FFFFFF;
    }

    [data-testid="stMainBlockContainer"] {
        background-color: #FFFFFF;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #F5F5F2;
        border-right: 1px solid #E5E5E5;
    }

    /* Text */
    h1, h2, h3, h4, p, label {
        color: #0B0B0B !important;
    }

    h1 {
        font-weight: 700 !important;
        letter-spacing: -1.5px;
    }

    h2, h3 {
        font-weight: 650 !important;
        letter-spacing: -0.5px;
    }

    /* Captions */
    [data-testid="stCaptionContainer"] {
        color: #777777 !important;
    }

    /* Buttons / page links */
    [data-testid="stPageLink"] a {
        background-color: #16E879;
        color: #0B0B0B !important;
        border-radius: 12px;
        padding: 10px 16px;
        text-decoration: none;
        font-weight: 600;
    }

    /* Divider */
    hr {
        border-color: #E5E5E5 !important;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# NAVIGATION
# ---------------------------------------------------------

st.page_link(
    "app.py",
    label="← Back to Scenario Lab",
)


# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------

st.title("Founder Recommendation")

st.caption(
    "Executive decision view connecting industrial scale-up, "
    "supply resilience and capital requirements."
)

st.info(
    "Portfolio case inspired by MicroHarvest's publicly announced "
    "Leuna scale-up. Recommendations are derived from synthetic "
    "scenario assumptions and are not company forecasts."
)
