import pandas as pd


def calculate_scaleup_investment(
    target_supply_t,
    weighted_landed_cost_eur_t,
    industrial_scaleup_capex,
    supplier_onboarding_cost,
    working_capital_months,
):
    """
    Calculate modeled operating and scale-up capital requirements.

    All financial inputs are synthetic unless explicitly identified
    as public context elsewhere in the application.
    """

    annual_feedstock_spend = (
        target_supply_t * weighted_landed_cost_eur_t
    )

    monthly_feedstock_spend = annual_feedstock_spend / 12

    working_capital_requirement = (
        monthly_feedstock_spend * working_capital_months
    )

    total_scaleup_investment = (
        industrial_scaleup_capex
        + supplier_onboarding_cost
        + working_capital_requirement
    )

    return {
        "annual_feedstock_spend": annual_feedstock_spend,
        "monthly_feedstock_spend": monthly_feedstock_spend,
        "working_capital_requirement": working_capital_requirement,
        "industrial_scaleup_capex": industrial_scaleup_capex,
        "supplier_onboarding_cost": supplier_onboarding_cost,
        "total_scaleup_investment": total_scaleup_investment,
    }


def calculate_funding_position(
    starting_cash,
    public_grant,
    total_scaleup_investment,
    minimum_cash_buffer,
):
    """
    Estimate the funding position before a new private raise.

    Public grant is treated separately from synthetic financial inputs.
    """

    capital_available_before_raise = (
        starting_cash + public_grant
    )

    cash_after_scaleup = (
        capital_available_before_raise
        - total_scaleup_investment
    )

    immediate_funding_gap = max(
        minimum_cash_buffer - cash_after_scaleup,
        0,
    )

    return {
        "capital_available_before_raise":
            capital_available_before_raise,

        "cash_after_scaleup":
            cash_after_scaleup,

        "immediate_funding_gap":
            immediate_funding_gap,
    }


def simulate_cash_runway(
    starting_cash,
    monthly_revenue,
    monthly_revenue_growth,
    gross_margin,
    monthly_payroll,
    monthly_other_opex,
    monthly_base_capex,
    monthly_feedstock_spend,
    minimum_cash_buffer,
    horizon_months=36,
    post_scaleup_revenue_uplift=0.0,
    commercial_ramp_months=12,
):
    """
    Simulate monthly cash development after the modeled scale-up.

    Revenue combines:
    1. Organic monthly growth.
    2. A synthetic post-scale-up commercial uplift that is realized
       progressively over the selected ramp period.

    Runway is measured as the first month in which cash falls below
    the management minimum cash buffer.
    """

    cash = starting_cash
    base_revenue = monthly_revenue

    results = []
    runway_months = horizon_months
    buffer_breached = False

    for month in range(1, horizon_months + 1):

        # Organic revenue growth
        organic_revenue = (
            base_revenue
            * ((1 + monthly_revenue_growth) ** (month - 1))
        )

        # Progressive realization of post-scale-up commercial uplift
        ramp_progress = min(
            month / commercial_ramp_months,
            1.0,
        )

        realized_uplift = (
            post_scaleup_revenue_uplift
            * ramp_progress
        )

        revenue = organic_revenue * (
            1 + realized_uplift
        )

        gross_profit = revenue * gross_margin

        monthly_cash_flow = (
            gross_profit
            - monthly_payroll
            - monthly_other_opex
            - monthly_base_capex
            - monthly_feedstock_spend
        )

        cash += monthly_cash_flow

        results.append(
            {
                "month": month,
                "revenue": revenue,
                "organic_revenue": organic_revenue,
                "realized_uplift_pct": realized_uplift,
                "gross_profit": gross_profit,
                "monthly_cash_flow": monthly_cash_flow,
                "ending_cash": cash,
            }
        )

        if (
            cash < minimum_cash_buffer
            and not buffer_breached
        ):
            runway_months = month
            buffer_breached = True

    return pd.DataFrame(results), runway_months


def calculate_raise_scenario(
    cash_after_scaleup,
    raise_amount,
    transaction_cost_pct,
):
    """
    Calculate net proceeds and post-raise cash position.
    """

    transaction_cost = (
        raise_amount * transaction_cost_pct
    )

    net_proceeds = (
        raise_amount - transaction_cost
    )

    post_raise_cash = (
        cash_after_scaleup + net_proceeds
    )

    return {
        "raise_amount": raise_amount,
        "transaction_cost": transaction_cost,
        "net_proceeds": net_proceeds,
        "post_raise_cash": post_raise_cash,
    }
