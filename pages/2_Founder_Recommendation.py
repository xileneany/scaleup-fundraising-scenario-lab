import pandas as pd
import streamlit as st

from utils.financial_model import (
    calculate_scaleup_investment,
    calculate_funding_position,
    simulate_cash_runway,
    calculate_required_raise,
)

from utils.supply_model import (
    calculate_scenario_requirements,
    calculate_weighted_supplier_score,
    allocate_suppliers,
)


# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------

st.set_page_config(
    page_title="Founder Recommendation",
    page_icon="→",
    layout="wide",
)


# ---------------------------------------------------------
# VISUAL SYSTEM
# ---------------------------------------------------------

st.markdown(
    """
    <style>

    .stApp {
        background-color: #FFFFFF;
        color: #0B0B0B;
    }

    [data-testid="stMain"],
    [data-testid="stMainBlockContainer"] {
        background-color: #FFFFFF;
    }

    [data-testid="stSidebar"] {
        background-color: #F5F5F2;
        border-right: 1px solid #E5E5E5;
    }

    h1, h2, h3, h4, p, label {
        color: #0B0B0B !important;
    }

    h1 {
        font-weight: 700 !important;
        letter-spacing: -1.5px;
    }

    h2, h3 {
        font-weight: 650 !important;
    }

    [data-testid="stCaptionContainer"] {
        color: #777777 !important;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# KPI CARD
# ---------------------------------------------------------

def kpi_card(label, value):
    html = f"""
<div style="background-color:#16E879; border-radius:18px; padding:24px 26px;">
    <div style="font-size:16px; font-weight:600; color:#111111; margin-bottom:14px;">
        {label}
    </div>
    <div style="font-size:34px; font-weight:700; color:#111111; line-height:1.1;">
        {value}
    </div>
</div>
"""
    st.markdown(html, unsafe_allow_html=True)


# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------

@st.cache_data
def load_data():
    suppliers = pd.read_csv("data/suppliers.csv")
    assumptions = pd.read_csv("data/production_assumptions.csv")
    scenarios = pd.read_csv("data/production_scenarios.csv")
    financial = pd.read_csv("data/financial_assumptions.csv")

    return suppliers, assumptions, scenarios, financial


suppliers, assumptions, scenarios, financial = load_data()


def get_assumption(name):
    return assumptions.loc[
        assumptions["assumption"] == name,
        "value"
    ].iloc[0]


def get_financial_assumption(name):
    return financial.loc[
        financial["assumption"] == name,
        "value"
    ].iloc[0]


# ---------------------------------------------------------
# MODEL INPUTS
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

# Use Base Scale-Up scenario
scenario = scenarios.loc[
    scenarios["scenario"] == "Base Scale-Up"
].iloc[0]

utilization_rate = float(scenario["utilization_rate"])
conversion_ratio = float(
    scenario["feedstock_conversion_ratio"]
)
supply_buffer = float(scenario["supply_buffer"])


# ---------------------------------------------------------
# PRODUCTION + SUPPLY MODEL
# ---------------------------------------------------------

requirements = calculate_scenario_requirements(
    production_capacity=production_capacity,
    utilization_rate=utilization_rate,
    conversion_ratio=conversion_ratio,
    supply_buffer=supply_buffer,
)

scored_suppliers = calculate_weighted_supplier_score(
    suppliers
)

allocation, supply_summary = allocate_suppliers(
    suppliers=scored_suppliers,
    target_supply_t=requirements[
        "target_contracted_supply_t"
    ],
    max_supplier_dependency=max_supplier_dependency,
)


# ---------------------------------------------------------
# FINANCIAL INPUTS
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
    get_financial_assumption(
        "fundraising_transaction_cost_pct"
    )
)

model_horizon_months = int(
    get_financial_assumption("model_horizon_months")
)

post_scaleup_revenue_uplift = float(
    get_financial_assumption(
        "post_scaleup_revenue_uplift"
    )
)

commercial_ramp_months = int(
    get_financial_assumption(
        "commercial_ramp_months"
    )
)


# ---------------------------------------------------------
# SCALE-UP FINANCIALS
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

runway_df, runway_months = simulate_cash_runway(
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

required_raise_24m = calculate_required_raise(
    runway_df=runway_df,
    minimum_cash_buffer=minimum_cash_buffer,
    target_month=24,
    transaction_cost_pct=transaction_cost_pct,
)

required_24m = required_raise_24m[
    "gross_raise_required"
]


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
    "Leuna scale-up. Recommendations below are derived from synthetic "
    "scenario assumptions and are not company forecasts."
)


# ---------------------------------------------------------
# DECISION SNAPSHOT
# ---------------------------------------------------------

st.header("Decision Snapshot")

c1, c2, c3 = st.columns(3)

with c1:
    kpi_card(
        "24M Funding Requirement",
        f"€{required_24m / 1_000_000:.1f}M"
    )

with c2:
    kpi_card(
        "Supply Coverage",
        f"{supply_summary['coverage_pct']:.0%}"
    )

with c3:
    kpi_card(
        "Largest Supplier Share",
        f"{supply_summary['largest_supplier_share']:.0%}"
    )


# ---------------------------------------------------------
# MANAGEMENT VIEW
# ---------------------------------------------------------

st.header("Management View")

if required_24m > 8_000_000:

    st.warning(
        f"The modeled €8M accelerated fundraising scenario does not "
        f"fully support the 24-month liquidity objective. The model "
        f"indicates approximately €{required_24m / 1_000_000:.1f}M "
        f"of private capital would be required to maintain the "
        f"€{minimum_cash_buffer / 1_000_000:.1f}M minimum cash buffer."
    )

    st.markdown(
        """
### Recommended course of action

**1. Reassess financing size.**  
Evaluate a financing package above the modeled €8M accelerated case.

**2. Protect execution flexibility.**  
Consider phasing non-critical scale-up investment rather than committing
all modeled capital simultaneously.

**3. Preserve supply resilience.**  
Maintain a diversified supplier structure while protecting the modeled
supplier concentration limit.

**4. Track commercial ramp-up closely.**  
Use revenue realization and cash development as decision gates for
subsequent investment commitments.
"""
    )

else:

    st.success(
        "The modeled financing requirement can be covered within the "
        "fundraising scenarios currently evaluated."
    )

    st.markdown(
        """
### Recommended course of action

Proceed with fundraising preparation while maintaining supplier
diversification and monitoring commercial ramp-up against the cash plan.
"""
    )


# ---------------------------------------------------------
# DECISION LOGIC
# ---------------------------------------------------------

st.header("Why This Recommendation")

st.write(
    f"The modeled production plan targets "
    f"{requirements['expected_output_t']:,.0f} tonnes of annual output "
    f"and requires approximately "
    f"{requirements['target_contracted_supply_t']:,.0f} tonnes of "
    f"contracted feedstock coverage."
)

st.write(
    f"The supplier allocation achieves "
    f"{supply_summary['coverage_pct']:.0%} modeled coverage while the "
    f"largest supplier represents "
    f"{supply_summary['largest_supplier_share']:.0%} of allocated volume."
)

st.write(
    f"After incorporating the publicly announced €{public_grant / 1_000_000:.1f}M "
    f"grant into the synthetic capital bridge, the model estimates that "
    f"approximately €{required_24m / 1_000_000:.1f}M of additional private "
    f"capital would be required to protect the modeled liquidity buffer "
    f"through month 24."
)


# ---------------------------------------------------------
# NOTE
# ---------------------------------------------------------

st.divider()

st.caption(
    "Decision-support prototype. Supplier relationships, operating costs, "
    "cash balances, revenue assumptions and financing requirements are "
    "synthetic. Publicly announced company information is presented "
    "separately for context."
)
