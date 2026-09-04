import pandas as pd
import streamlit as st

from utils.supply_model import (
    calculate_scenario_requirements,
    calculate_weighted_supplier_score,
    allocate_suppliers,
)

from utils.financial_model import (
    calculate_scaleup_investment,
    calculate_funding_position,
    simulate_cash_runway,
    calculate_raise_scenario,
    calculate_required_raise,
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
# VISUAL THEME
# ---------------------------------------------------------

st.markdown(
    """
    <style>

    /* ---------- GLOBAL ---------- */

    .stApp {
        background-color: #FFFFFF;
        color: #0B0B0B;
    }

    .block-container {
        padding-top: 3rem;
        padding-bottom: 4rem;
        max-width: 1500px;
    }

    /* ---------- TYPOGRAPHY ---------- */

    h1 {
        color: #0B0B0B !important;
        font-weight: 700 !important;
        letter-spacing: -1.5px;
    }

    h2 {
        color: #0B0B0B !important;
        font-weight: 650 !important;
        letter-spacing: -0.7px;
        margin-top: 2.2rem !important;
    }

    h3 {
        color: #16E879 !important;
        font-weight: 650 !important;
    }

    h4 {
        color: #0B0B0B !important;
        font-weight: 600 !important;
    }

    p, label, span {
        color: #0B0B0B;
    }

    /* ---------- CAPTIONS ---------- */

    [data-testid="stCaptionContainer"] p {
        color: #777777 !important;
    }

    /* ---------- SIDEBAR ---------- */

    [data-testid="stSidebar"] {
        background-color: #F5F5F2;
        border-right: 1px solid #E6E6E2;
    }

    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #0B0B0B !important;
    }

    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label {
        color: #202020 !important;
    }

    /* ---------- METRICS ---------- */

    [data-testid="stMetricLabel"] {
        color: #666666 !important;
        font-weight: 500;
    }

    [data-testid="stMetricValue"] {
        color: #0B0B0B !important;
        font-weight: 500;
    }

    /* ---------- INFO BOX ---------- */

    [data-testid="stAlert"] {
        background-color: #F2FBFF;
        border: 1px solid #A9E4FF;
        border-radius: 4px;
        color: #0B0B0B;
    }

    /* ---------- TABLES ---------- */

    [data-testid="stDataFrame"] {
        border: 1px solid #E5E5E5;
        border-radius: 4px;
    }

    /* ---------- DIVIDERS ---------- */

    hr {
        border-color: #E5E5E5 !important;
    }

    /* ---------- LINKS ---------- */

    a {
        color: #009DDC !important;
    }

    /* ---------- SLIDERS ---------- */

    [data-testid="stSlider"] {
        accent-color: #16E879;
    }

    /* ---------- SELECT BOX ---------- */

    [data-baseweb="select"] > div {
        background-color: #FFFFFF;
        color: #0B0B0B;
        border-color: #D8D8D8;
    }

    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------

@st.cache_data
def load_data():
    suppliers = pd.read_csv("data/suppliers.csv")
    assumptions = pd.read_csv("data/production_assumptions.csv")
    scenarios = pd.read_csv("data/production_scenarios.csv")
    financial_assumptions = pd.read_csv(
        "data/financial_assumptions.csv"
    )

    return (
        suppliers,
        assumptions,
        scenarios,
        financial_assumptions,
    )


(
    suppliers,
    assumptions,
    scenarios,
    financial_assumptions,
) = load_data()


# ---------------------------------------------------------
# HELPER
# ---------------------------------------------------------

def get_assumption(name):
    return assumptions.loc[
        assumptions["assumption"] == name,
        "value"
    ].iloc[0]

def get_financial_assumption(name):
    return financial_assumptions.loc[
        financial_assumptions["assumption"] == name,
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
# FINANCIAL ASSUMPTIONS
# ---------------------------------------------------------

starting_cash = float(
    get_financial_assumption("starting_cash")
)

industrial_scaleup_capex = float(
    get_financial_assumption("industrial_scaleup_capex")
)

supplier_onboarding_cost = float(
    get_financial_assumption("supplier_onboarding_cost")
)

working_capital_months = float(
    get_financial_assumption("working_capital_months")
)

minimum_cash_buffer = float(
    get_financial_assumption("minimum_cash_buffer")
)

monthly_revenue = float(
    get_financial_assumption("monthly_revenue")
)

monthly_revenue_growth = float(
    get_financial_assumption("monthly_revenue_growth")
)

gross_margin = float(
    get_financial_assumption("gross_margin")
)

monthly_payroll = float(
    get_financial_assumption("monthly_payroll")
)

monthly_other_opex = float(
    get_financial_assumption("monthly_other_opex")
)

monthly_base_capex = float(
    get_financial_assumption("monthly_base_capex")
)

transaction_cost_pct = float(
    get_financial_assumption("fundraising_transaction_cost_pct")
)

model_horizon_months = int(
    get_financial_assumption("model_horizon_months")
)

post_scaleup_revenue_uplift = float(
    get_financial_assumption("post_scaleup_revenue_uplift")
)

commercial_ramp_months = int(
    get_financial_assumption("commercial_ramp_months")
)

# ---------------------------------------------------------
# SCALE-UP FINANCIAL IMPACT
# ---------------------------------------------------------

scaleup_financials = calculate_scaleup_investment(
    target_supply_t=requirements[
        "target_contracted_supply_t"
    ],
    weighted_landed_cost_eur_t=supply_summary[
        "weighted_landed_cost_eur_t"
    ],
    industrial_scaleup_capex=industrial_scaleup_capex,
    supplier_onboarding_cost=supplier_onboarding_cost,
    working_capital_months=working_capital_months,
)


funding_position = calculate_funding_position(
    starting_cash=starting_cash,
    public_grant=public_grant,
    total_scaleup_investment=scaleup_financials[
        "total_scaleup_investment"
    ],
    minimum_cash_buffer=minimum_cash_buffer,
)

# ---------------------------------------------------------
# BASE RUNWAY - NO PRIVATE RAISE
# ---------------------------------------------------------

base_runway_df, base_runway_months = simulate_cash_runway(
    starting_cash=funding_position["cash_after_scaleup"],
    monthly_revenue=monthly_revenue,
    monthly_revenue_growth=monthly_revenue_growth,
    gross_margin=gross_margin,
    monthly_payroll=monthly_payroll,
    monthly_other_opex=monthly_other_opex,
    monthly_base_capex=monthly_base_capex,
    monthly_feedstock_spend=scaleup_financials[
        "monthly_feedstock_spend"
    ],
    minimum_cash_buffer=minimum_cash_buffer,
    horizon_months=model_horizon_months,
    post_scaleup_revenue_uplift=post_scaleup_revenue_uplift,
    commercial_ramp_months=commercial_ramp_months,
)

# ---------------------------------------------------------
# REQUIRED PRIVATE FUNDING
# ---------------------------------------------------------

required_raise_18m = calculate_required_raise(
    runway_df=base_runway_df,
    minimum_cash_buffer=minimum_cash_buffer,
    target_month=18,
    transaction_cost_pct=transaction_cost_pct,
)

required_raise_24m = calculate_required_raise(
    runway_df=base_runway_df,
    minimum_cash_buffer=minimum_cash_buffer,
    target_month=24,
    transaction_cost_pct=transaction_cost_pct,
)

# ---------------------------------------------------------
# FUNDRAISING SCENARIOS
# ---------------------------------------------------------

raise_scenarios = {
    "No Raise": 0,
    "Lean Raise": 4_000_000,
    "Balanced Raise": 6_000_000,
    "Accelerated Raise": 8_000_000,
}

fundraising_results = []

for scenario_name, raise_amount in raise_scenarios.items():

    raise_result = calculate_raise_scenario(
        cash_after_scaleup=funding_position[
            "cash_after_scaleup"
        ],
        raise_amount=raise_amount,
        transaction_cost_pct=transaction_cost_pct,
    )

    runway_df, runway_months = simulate_cash_runway(
        starting_cash=raise_result["post_raise_cash"],
        monthly_revenue=monthly_revenue,
        monthly_revenue_growth=monthly_revenue_growth,
        gross_margin=gross_margin,
        monthly_payroll=monthly_payroll,
        monthly_other_opex=monthly_other_opex,
        monthly_base_capex=monthly_base_capex,
        monthly_feedstock_spend=scaleup_financials[
            "monthly_feedstock_spend"
        ],
        minimum_cash_buffer=minimum_cash_buffer,
        horizon_months=model_horizon_months,
        post_scaleup_revenue_uplift=post_scaleup_revenue_uplift,
        commercial_ramp_months=commercial_ramp_months,
    )

    cash_month_12 = runway_df.loc[
        runway_df["month"] == 12,
        "ending_cash"
    ].iloc[0]

    cash_month_24 = runway_df.loc[
        runway_df["month"] == 24,
        "ending_cash"
    ].iloc[0]

    cash_month_36 = runway_df.loc[
        runway_df["month"] == 36,
        "ending_cash"
    ].iloc[0]

    fundraising_results.append(
        {
            "scenario": scenario_name,
            "raise_amount": raise_amount,
            "net_proceeds": raise_result[
                "net_proceeds"
            ],
            "post_raise_cash": raise_result[
                "post_raise_cash"
            ],
            "runway_months": runway_months,
            "cash_month_12": cash_month_12,
            "cash_month_24": cash_month_24,
            "cash_month_36": cash_month_36,
        }
    )

fundraising_df = pd.DataFrame(fundraising_results)

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
# FINANCIAL IMPACT
# ---------------------------------------------------------

st.header("Financial Impact")

st.caption(
    "Illustrative financial impact of the selected supply and "
    "production scenario. Financial figures below are synthetic "
    "unless explicitly identified as public information."
)

f1, f2, f3, f4 = st.columns(4)

f1.metric(
    "Annual Feedstock Spend",
    f"€{scaleup_financials['annual_feedstock_spend'] / 1_000_000:.2f}M",
)

f2.metric(
    "Working Capital",
    f"€{scaleup_financials['working_capital_requirement'] / 1_000_000:.2f}M",
)

f3.metric(
    "Scale-Up Investment",
    f"€{scaleup_financials['total_scaleup_investment'] / 1_000_000:.2f}M",
)

f4.metric(
    "Cash After Scale-Up",
    f"€{funding_position['cash_after_scaleup'] / 1_000_000:.2f}M",
)

st.markdown("#### Capital Bridge")

capital_available = funding_position[
    "capital_available_before_raise"
]

st.write(
    f"**Synthetic starting cash:** "
    f"€{starting_cash / 1_000_000:.2f}M"
)

st.write(
    f"**Public grant:** "
    f"€{public_grant / 1_000_000:.2f}M"
)

st.write(
    f"**Capital available before private raise:** "
    f"€{capital_available / 1_000_000:.2f}M"
)

st.write(
    f"**Modeled scale-up investment:** "
    f"€{scaleup_financials['total_scaleup_investment'] / 1_000_000:.2f}M"
)

st.write(
    f"**Cash remaining after scale-up:** "
    f"€{funding_position['cash_after_scaleup'] / 1_000_000:.2f}M"
)

# ---------------------------------------------------------
# FUNDING REQUIREMENT
# ---------------------------------------------------------

st.header("Funding Requirement")

st.caption(
    "Estimated private capital required to maintain the modeled "
    "€1.5M minimum cash buffer through the selected planning horizon."
)

r1, r2 = st.columns(2)

r1.metric(
    "Required Raise — 18M",
    f"€{required_raise_18m['gross_raise_required'] / 1_000_000:.1f}M",
)

r2.metric(
    "Required Raise — 24M",
    f"€{required_raise_24m['gross_raise_required'] / 1_000_000:.1f}M",
)

st.caption(
    "Calculated from the lowest projected cash balance within each "
    "period and adjusted for the synthetic 3% fundraising transaction cost."
)

# ---------------------------------------------------------
# FUNDRAISING COMPARISON
# ---------------------------------------------------------

st.header("Fundraising Scenarios")

st.caption(
    "Illustrative private fundraising scenarios layered on top of "
    "the modeled scale-up plan and the publicly announced grant."
)

display_fundraising = fundraising_df.copy()

display_fundraising["Raise"] = (
    display_fundraising["raise_amount"] / 1_000_000
)

display_fundraising["Net Proceeds"] = (
    display_fundraising["net_proceeds"] / 1_000_000
)

display_fundraising["Post-Raise Cash"] = (
    display_fundraising["post_raise_cash"] / 1_000_000
)

display_fundraising["Cash @ 12M"] = (
    display_fundraising["cash_month_12"] / 1_000_000
)

display_fundraising["Cash @ 24M"] = (
    display_fundraising["cash_month_24"] / 1_000_000
)

display_fundraising["Cash @ 36M"] = (
    display_fundraising["cash_month_36"] / 1_000_000
)

display_fundraising = display_fundraising[
    [
        "scenario",
        "Raise",
        "Net Proceeds",
        "Post-Raise Cash",
        "runway_months",
        "Cash @ 12M",
        "Cash @ 24M",
        "Cash @ 36M",
    ]
]

display_fundraising.columns = [
    "Scenario",
    "Raise (€M)",
    "Net Proceeds (€M)",
    "Post-Raise Cash (€M)",
    "Runway (Months)",
    "Cash @ 12M (€M)",
    "Cash @ 24M (€M)",
    "Cash @ 36M (€M)",
]

st.dataframe(
    display_fundraising.style.format(
        {
            "Raise (€M)": "€{:.1f}",
            "Net Proceeds (€M)": "€{:.1f}",
            "Post-Raise Cash (€M)": "€{:.1f}",
            "Runway (Months)": "{:.0f}",
            "Cash @ 12M (€M)": "€{:.1f}",
            "Cash @ 24M (€M)": "€{:.1f}",
            "Cash @ 36M (€M)": "€{:.1f}",
        }
    ),
    use_container_width=True,
    hide_index=True,
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
