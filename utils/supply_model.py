import pandas as pd


def calculate_scenario_requirements(
    production_capacity,
    utilization_rate,
    conversion_ratio,
    supply_buffer,
):
    """
    Calculate modeled production and feedstock requirements.

    production_capacity: annual finished-output capacity in tonnes
    utilization_rate: expected facility utilization (decimal)
    conversion_ratio: synthetic tonnes of feedstock required per tonne of output
    supply_buffer: additional contracted supply buffer (decimal)
    """

    expected_output = production_capacity * utilization_rate

    feedstock_requirement = expected_output * conversion_ratio

    target_contracted_supply = feedstock_requirement * (1 + supply_buffer)

    return {
        "expected_output_t": expected_output,
        "feedstock_requirement_t": feedstock_requirement,
        "target_contracted_supply_t": target_contracted_supply,
    }


def calculate_supplier_metrics(suppliers):
    """
    Add commercial and supply-risk metrics to the supplier dataset.
    """

    df = suppliers.copy()

    # Total modeled cost of getting one tonne of feedstock to Leuna
    df["landed_cost_eur_t"] = (
        df["feedstock_cost_eur_t"] + df["transport_cost_eur_t"]
    )

    # Normalize selected variables to a 0-100 scale.
    # Higher normalized scores are always better.

    df["capacity_score"] = (
        df["annual_available_t"] / df["annual_available_t"].max()
    ) * 100

    df["cost_score"] = (
        1
        - (
            (df["landed_cost_eur_t"] - df["landed_cost_eur_t"].min())
            / (
                df["landed_cost_eur_t"].max()
                - df["landed_cost_eur_t"].min()
            )
        )
    ) * 100

    df["distance_score"] = (
        1
        - (
            (df["distance_to_leuna_km"] - df["distance_to_leuna_km"].min())
            / (
                df["distance_to_leuna_km"].max()
                - df["distance_to_leuna_km"].min()
            )
        )
    ) * 100

    df["reliability_score"] = df["reliability_pct"]

    df["quality_normalized"] = df["quality_score"]

    df["contract_score"] = df["contract_security_score"]

    df["risk_normalized"] = 100 - df["supply_risk_score"]

    return df


def calculate_weighted_supplier_score(
    suppliers,
    capacity_weight=0.20,
    cost_weight=0.20,
    distance_weight=0.10,
    reliability_weight=0.20,
    quality_weight=0.10,
    contract_weight=0.10,
    risk_weight=0.10,
):
    """
    Calculate a weighted supplier score.

    Default weights represent a balanced sourcing strategy.
    """

    df = calculate_supplier_metrics(suppliers)

    total_weight = (
        capacity_weight
        + cost_weight
        + distance_weight
        + reliability_weight
        + quality_weight
        + contract_weight
        + risk_weight
    )

    if round(total_weight, 6) != 1:
        raise ValueError("Supplier scoring weights must add up to 1.0")

    df["supplier_score"] = (
        df["capacity_score"] * capacity_weight
        + df["cost_score"] * cost_weight
        + df["distance_score"] * distance_weight
        + df["reliability_score"] * reliability_weight
        + df["quality_normalized"] * quality_weight
        + df["contract_score"] * contract_weight
        + df["risk_normalized"] * risk_weight
    )

    return df.sort_values(
        by="supplier_score",
        ascending=False,
    ).reset_index(drop=True)
