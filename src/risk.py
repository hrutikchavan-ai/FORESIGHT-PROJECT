from pathlib import Path

import pandas as pd


# =========================================================
# PROJECT PATHS
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

PROCESSED_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
)

RISK_FILE = (
    PROCESSED_DIR
    / "risk_scored_data.csv"
)

OUTPUT_FILE = (
    PROCESSED_DIR
    / "risk_decisioned_data.csv"
)


# =========================================================
# REQUIRED COLUMNS
# =========================================================

REQUIRED_COLUMNS = [
    "sku_id",
    "stockout_risk",
    "overstock_risk",
    "stockout_units_at_risk",
    "sales_at_risk_rupees",
    "overstock_units_at_risk",
    "locked_capital_rupees",
]


# =========================================================
# LOAD RISK-SCORED DATA
# =========================================================

def load_risk_data(
    input_file=RISK_FILE
):
    """
    Load the existing risk-scored dataset.
    """

    if not input_file.exists():
        raise FileNotFoundError(
            f"Risk-scored dataset not found:\n"
            f"{input_file}"
        )

    df = pd.read_csv(
        input_file
    )

    return df


# =========================================================
# VALIDATE RISK DATA
# =========================================================

def validate_risk_data(df):
    """
    Validate that the risk-scored dataset contains
    all fields required by the decision layer.
    """

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            "Missing required risk columns: "
            + ", ".join(missing_columns)
        )

    if df.empty:
        raise ValueError(
            "Risk-scored dataset is empty."
        )

    return True


# =========================================================
# NORMALISE RISK FLAGS
# =========================================================

def normalise_risk_flags(df):
    """
    Convert stockout and overstock flags into
    consistent boolean values.
    """

    result = df.copy()

    result["stockout_risk"] = (
        result["stockout_risk"]
        .fillna(False)
        .astype(bool)
    )

    result["overstock_risk"] = (
        result["overstock_risk"]
        .fillna(False)
        .astype(bool)
    )

    return result


# =========================================================
# ACTION DECISION
# =========================================================

def determine_action(
    stockout_risk,
    overstock_risk
):
    """
    Convert risk flags into the operational action.

    Priority:
        Stockout  -> Reorder Now
        Overstock -> Markdown/Clear
        Neither   -> Healthy
    """

    if stockout_risk:
        return "Reorder Now"

    if overstock_risk:
        return "Markdown/Clear"

    return "Healthy"


# =========================================================
# APPLY ACTION LOGIC
# =========================================================

def apply_action_logic(df):
    """
    Add a transparent action column to the
    risk-scored dataset.
    """

    result = df.copy()

    result["action"] = [
        determine_action(
            stockout,
            overstock
        )
        for stockout, overstock
        in zip(
            result["stockout_risk"],
            result["overstock_risk"]
        )
    ]

    return result


# =========================================================
# VALIDATE RISK VALUES
# =========================================================

def validate_risk_values(df):
    """
    Check that risk impact fields contain
    valid non-negative numeric values.
    """

    numeric_columns = [
        "stockout_units_at_risk",
        "sales_at_risk_rupees",
        "overstock_units_at_risk",
        "locked_capital_rupees",
    ]

    result = df.copy()

    for column in numeric_columns:

        result[column] = pd.to_numeric(
            result[column],
            errors="coerce"
        )

        if result[column].isna().any():
            raise ValueError(
                f"Invalid numeric values found in {column}."
            )

        if (
            result[column] < 0
        ).any():

            raise ValueError(
                f"Negative values found in {column}."
            )

    return result


# =========================================================
# RISK SUMMARY
# =========================================================

def create_risk_summary(df):
    """
    Create an operational summary of risk states
    and financial exposure.
    """

    summary = {
        "total_rows": len(df),

        "stockout_rows": int(
            df["stockout_risk"]
            .sum()
        ),

        "overstock_rows": int(
            df["overstock_risk"]
            .sum()
        ),

        "healthy_rows": int(
            (
                ~df["stockout_risk"]
                & ~df["overstock_risk"]
            ).sum()
        ),

        "stockout_units_at_risk": float(
            df["stockout_units_at_risk"]
            .sum()
        ),

        "sales_at_risk_rupees": float(
            df["sales_at_risk_rupees"]
            .sum()
        ),

        "overstock_units_at_risk": float(
            df["overstock_units_at_risk"]
            .sum()
        ),

        "locked_capital_rupees": float(
            df["locked_capital_rupees"]
            .sum()
        ),
    }

    return summary


# =========================================================
# ACTION SUMMARY
# =========================================================

def create_action_summary(df):
    """
    Count records by operational action.
    """

    return (
        df["action"]
        .value_counts()
        .rename_axis("action")
        .reset_index(
            name="count"
        )
    )


# =========================================================
# SAVE DECISION DATA
# =========================================================

def save_risk_decisions(
    df,
    output_file=OUTPUT_FILE
):
    """
    Save the final risk decision dataset.
    """

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        output_file,
        index=False
    )


# =========================================================
# MAIN RISK PIPELINE
# =========================================================

def run_risk_pipeline():

    print("=" * 60)
    print("FORESIGHT RISK DECISION PIPELINE")
    print("=" * 60)

    # -----------------------------------------------------
    # 1. Load data
    # -----------------------------------------------------

    print(
        "\n1. Loading risk-scored data..."
    )

    df = load_risk_data()

    print(
        f"Loaded rows: {len(df)}"
    )

    # -----------------------------------------------------
    # 2. Validate structure
    # -----------------------------------------------------

    print(
        "\n2. Validating risk columns..."
    )

    validate_risk_data(
        df
    )

    print(
        "Risk columns: PASS"
    )

    # -----------------------------------------------------
    # 3. Normalise flags
    # -----------------------------------------------------

    print(
        "\n3. Normalising risk flags..."
    )

    df = normalise_risk_flags(
        df
    )

    print(
        "Risk flags: PASS"
    )

    # -----------------------------------------------------
    # 4. Validate numerical impact fields
    # -----------------------------------------------------

    print(
        "\n4. Validating risk impact values..."
    )

    df = validate_risk_values(
        df
    )

    print(
        "Risk values: PASS"
    )

    # -----------------------------------------------------
    # 5. Apply action logic
    # -----------------------------------------------------

    print(
        "\n5. Applying operational action logic..."
    )

    df = apply_action_logic(
        df
    )

    print(
        "Action logic: PASS"
    )

    # -----------------------------------------------------
    # 6. Create summary
    # -----------------------------------------------------

    print(
        "\n6. Creating risk summary..."
    )

    summary = create_risk_summary(
        df
    )

    for key, value in summary.items():

        print(
            f"{key}: {value}"
        )

    # -----------------------------------------------------
    # 7. Action summary
    # -----------------------------------------------------

    print(
        "\n7. Action summary..."
    )

    action_summary = create_action_summary(
        df
    )

    print(
        action_summary.to_string(
            index=False
        )
    )

    # -----------------------------------------------------
    # 8. Save final output
    # -----------------------------------------------------

    print(
        "\n8. Saving risk decision dataset..."
    )

    save_risk_decisions(
        df
    )

    print(
        f"Saved to:\n{OUTPUT_FILE}"
    )

    # -----------------------------------------------------
    # Final checks
    # -----------------------------------------------------

    print(
        "\n9. Final checks..."
    )

    valid_actions = {
        "Reorder Now",
        "Markdown/Clear",
        "Healthy"
    }

    assert (
        set(df["action"].unique())
        .issubset(valid_actions)
    )

    assert (
        df["stockout_risk"]
        .notna()
        .all()
    )

    assert (
        df["overstock_risk"]
        .notna()
        .all()
    )

    print(
        "Risk decision validation: PASS"
    )

    print(
        "\nRISK PIPELINE: PASS"
    )

    print("=" * 60)

    return df


# =========================================================
# RUN DIRECTLY
# =========================================================

if __name__ == "__main__":
    run_risk_pipeline()