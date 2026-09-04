import pandas as pd
import streamlit as st

from utils.supply_model import (
    calculate_scenario_requirements,
    calculate_weighted_supplier_score,
    allocate_suppliers,
)


# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------

st.set_page_config(
    page_title="Industrial Scale-Up Scenario Lab",
    page_icon="🏭",
    layout="wide",
)


# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------

@st.cache_data
def load_data():
    suppliers = pd.read_csv("data/suppliers.csv")
    assumptions = pd.read_csv("data/production_assumptions.csv")
    scenarios = pd.read_csv("data/production_scenarios.csv")

    return suppliers, assumptions, scenarios


suppliers, assumptions, scenarios = load_data()


# ---------------------------------------------------------
# HELPER
# ---------------------------------------------------------

def get_assumption(name):
    return assumptions.loc[
        assumptions["assumption"] == name,
        "value"
    ].iloc[0]


# ---------------------------------------------------------
# PUBLIC CONTEXT
# ---------------------------------------------------------

production_capacity = float(
    get_assumption("planned_production_capacity")
)

public_grant = float(
    get_assumption("public_grant")
)

max_supplier_dependency = float(
    get_assumption("maximum_supplier_dependency")
)


# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------

st.title("Industrial Scale-Up Scenario Lab")

st.caption(
    "Supply resilience, capacity planning and capital scenarios "
    "for industrial biotech scale-up"
)

st.info(
    "Portfolio case inspired by MicroHarvest's publicly announced "
    "Leuna scale-up. Public company context is separated from "
    "synthetic model assumptions."
)


# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------

st.sidebar.header("Scenario Controls")

selected_scenario = st.sidebar.selectbox(
    "Production scenario",
    scenarios["scenario"].tolist(),
    index=1,
)

scenario = scenarios.loc[
    scenarios["scenario"] == selected_scenario
].iloc[0]


st.sidebar.markdown("### Model Assumptions")

utilization_pct = st.sidebar.slider(
    "Capacity utilization",
    min_value=40,
    max_value=100,
    value=int(float(scenario["utilization_rate"]) * 100),
    step=5,
    format="%d%%",
)

utilization_rate = utilization_pct / 100

conversion_ratio = st.sidebar.slider(
    "Feedstock conversion ratio",
    min_value=1.0,
    max_value=3.0,
    value=float(scenario["feedstock_conversion_ratio"]),
    step=0.1,
)

supply_buffer_pct = st.sidebar.slider(
    "Supply resilience buffer",
    min_value=0,
    max_value=40,
    value=int(float(scenario["supply_buffer"]) * 100),
    step=5,
    format="%d%%",
)

supply_buffer = supply_buffer_pct / 100

max_dependency_pct = st.sidebar.slider(
    "Maximum supplier dependency",
    min_value=20,
    max_value=60,
    value=int(max_supplier_dependency * 100),
    step=5,
    format="%d%%",
)

max_dependency = max_dependency_pct / 100


st.sidebar.caption(
    "Conversion ratio, utilization, resilience buffer and supplier "
    "dependency are scenario assumptions and are not company-reported data."
)


# ---------------------------------------------------------
# SCENARIO CALCULATION
# ---------------------------------------------------------

requirements = calculate_scenario_requirements(
    production_capacity=production_capacity,
    utilization_rate=utilization_rate,
    conversion_ratio=conversion_ratio,
    supply_buffer=supply_buffer,
)


# ---------------------------------------------------------
# SUPPLIER SCORING
# ---------------------------------------------------------

scored_suppliers = calculate_weighted_supplier_score(
    suppliers
)


allocation, supply_summary = allocate_suppliers(
    suppliers=scored_suppliers,
    target_supply_t=requirements[
        "target_contracted_supply_t"
    ],
    max_supplier_dependency=max_dependency,
)


# ---------------------------------------------------------
# EXECUTIVE OVERVIEW
# ---------------------------------------------------------

st.header("Executive Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Planned Capacity",
    f"{production_capacity:,.0f} t/year",
)

col2.metric(
    "Modeled Output",
    f"{requirements['expected_output_t']:,.0f} t/year",
)

col3.metric(
    "Target Feedstock Coverage",
    f"{requirements['target_contracted_supply_t']:,.0f} t/year",
)

col4.metric(
    "Supply Coverage",
    f"{supply_summary['coverage_pct']:.0%}",
)


# ---------------------------------------------------------
# PUBLIC VS SYNTHETIC CONTEXT
# ---------------------------------------------------------

st.subheader("Planning Context")

context_col1, context_col2 = st.columns(2)

with context_col1:
    st.markdown("#### Public Context")

    st.write(
        f"**Announced production capacity:** "
        f"{production_capacity:,.0f} t/year"
    )

    st.write(
        f"**Announced public grant:** "
        f"€{public_grant / 1_000_000:.1f}M"
    )

    st.write("**Location:** Leuna, Germany")
    st.write("**Primary announced feedstock:** Molasses")


with context_col2:
    st.markdown("#### Synthetic Scenario Inputs")

    st.write(
        f"**Capacity utilization:** "
        f"{utilization_rate:.0%}"
    )

    st.write(
        f"**Feedstock conversion:** "
        f"{conversion_ratio:.1f}x"
    )

    st.write(
        f"**Supply resilience buffer:** "
        f"{supply_buffer:.0%}"
    )

    st.write(
        f"**Maximum supplier dependency:** "
        f"{max_dependency:.0%}"
    )


# ---------------------------------------------------------
# PRODUCTION & FEEDSTOCK
# ---------------------------------------------------------

st.header("Production & Feedstock Planning")

p1, p2, p3 = st.columns(3)

p1.metric(
    "Expected Production",
    f"{requirements['expected_output_t']:,.0f} t",
)

p2.metric(
    "Feedstock Requirement",
    f"{requirements['feedstock_requirement_t']:,.0f} t",
)

p3.metric(
    "Contracted Supply Target",
    f"{requirements['target_contracted_supply_t']:,.0f} t",
)


# ---------------------------------------------------------
# SUPPLY NETWORK
# ---------------------------------------------------------

st.header("Recommended Supply Network")

s1, s2, s3, s4 = st.columns(4)

s1.metric(
    "Suppliers",
    supply_summary["supplier_count"],
)

s2.metric(
    "Weighted Landed Cost",
    f"€{supply_summary['weighted_landed_cost_eur_t']:,.1f}/t",
)

s3.metric(
    "Weighted Reliability",
    f"{supply_summary['weighted_reliability_pct']:.1f}%",
)

s4.metric(
    "Largest Supplier Share",
    f"{supply_summary['largest_supplier_share']:.0%}",
)


# ---------------------------------------------------------
# ALLOCATION TABLE
# ---------------------------------------------------------

if not allocation.empty:

    display_allocation = allocation[
        [
            "supplier_name",
            "region",
            "allocated_volume_t",
            "allocation_share",
            "landed_cost_eur_t",
            "supplier_score",
            "reliability_pct",
            "supply_risk_score",
        ]
    ].copy()

    display_allocation.columns = [
        "Supplier",
        "Region",
        "Allocated Volume (t)",
        "Share",
        "Landed Cost (€/t)",
        "Supplier Score",
        "Reliability (%)",
        "Supply Risk",
    ]

    st.dataframe(
        display_allocation.style.format(
            {
                "Allocated Volume (t)": "{:,.0f}",
                "Share": "{:.1%}",
                "Landed Cost (€/t)": "€{:,.1f}",
                "Supplier Score": "{:.1f}",
                "Reliability (%)": "{:.1f}",
                "Supply Risk": "{:.0f}",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )


# ---------------------------------------------------------
# SUPPLY GAP WARNING
# ---------------------------------------------------------

if supply_summary["supply_gap_t"] > 0:

    st.error(
        f"Supply gap detected: "
        f"{supply_summary['supply_gap_t']:,.0f} tonnes "
        f"remain uncovered under the selected constraints."
    )

else:

    st.success(
        "The modeled supplier network provides full coverage "
        "under the selected scenario and concentration constraint."
    )


# ---------------------------------------------------------
# MODEL NOTE
# ---------------------------------------------------------

st.divider()

st.caption(
    "Decision-support prototype using synthetic supplier, cost, "
    "conversion and financial assumptions. Publicly announced "
    "company information is shown separately and should not be "
    "interpreted as evidence of actual supplier relationships, "
    "cost structures or financing requirements."
)
