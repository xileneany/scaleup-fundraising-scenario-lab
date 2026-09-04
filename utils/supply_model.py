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

def allocate_suppliers(
    suppliers,
    target_supply_t,
    max_supplier_dependency=0.35,
):
    """
    Allocate feedstock volume across suppliers based on supplier score,
    while respecting a maximum dependency per supplier.

    This is a simple greedy allocation model intended for scenario analysis,
    not a production procurement optimizer.
    """

    df = suppliers.copy()

    if "supplier_score" not in df.columns:
        df = calculate_weighted_supplier_score(df)

    max_volume_per_supplier = target_supply_t * max_supplier_dependency

    allocations = []
    remaining_supply = target_supply_t

    for _, row in df.iterrows():
        if remaining_supply <= 0:
            break

        supplier_available = row["annual_available_t"]

        allocated_volume = min(
            supplier_available,
            max_volume_per_supplier,
            remaining_supply,
        )

        if allocated_volume <= 0:
            continue

        allocation_share = allocated_volume / target_supply_t

        allocations.append(
            {
                "supplier_id": row["supplier_id"],
                "supplier_name": row["supplier_name"],
                "region": row["region"],
                "country": row["country"],
                "allocated_volume_t": allocated_volume,
                "allocation_share": allocation_share,
                "landed_cost_eur_t": row["landed_cost_eur_t"],
                "supplier_score": row["supplier_score"],
                "reliability_pct": row["reliability_pct"],
                "supply_risk_score": row["supply_risk_score"],
            }
        )

        remaining_supply -= allocated_volume

    allocation_df = pd.DataFrame(allocations)

    total_allocated = allocation_df["allocated_volume_t"].sum()

    supply_gap = max(
        target_supply_t - total_allocated,
        0,
    )

    coverage_pct = (
        total_allocated / target_supply_t
        if target_supply_t > 0
        else 0
    )

    if not allocation_df.empty:
        weighted_landed_cost = (
            (
                allocation_df["allocated_volume_t"]
                * allocation_df["landed_cost_eur_t"]
            ).sum()
            / total_allocated
        )

        weighted_reliability = (
            (
                allocation_df["allocated_volume_t"]
                * allocation_df["reliability_pct"]
            ).sum()
            / total_allocated
        )

        weighted_risk = (
            (
                allocation_df["allocated_volume_t"]
                * allocation_df["supply_risk_score"]
            ).sum()
            / total_allocated
        )

        largest_supplier_share = allocation_df[
            "allocation_share"
        ].max()

    else:
        weighted_landed_cost = 0
        weighted_reliability = 0
        weighted_risk = 0
        largest_supplier_share = 0

    summary = {
        "target_supply_t": target_supply_t,
        "total_allocated_t": total_allocated,
        "supply_gap_t": supply_gap,
        "coverage_pct": coverage_pct,
        "weighted_landed_cost_eur_t": weighted_landed_cost,
        "weighted_reliability_pct": weighted_reliability,
        "weighted_supply_risk": weighted_risk,
        "largest_supplier_share": largest_supplier_share,
        "supplier_count": len(allocation_df),
    }

    return allocation_df, summary
