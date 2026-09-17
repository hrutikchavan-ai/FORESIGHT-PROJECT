from pathlib import Path
import pandas as pd


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent

RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

INPUT_FILE = RAW_DIR / "sales_transactions.csv"
OUTPUT_FILE = PROCESSED_DIR / "cleaned_sales.csv"


# ---------------------------------------------------------
# Load sales data
# ---------------------------------------------------------
def load_sales_data(
    input_file: Path = INPUT_FILE,
    nrows: int | None = 100000
) -> pd.DataFrame:
    """
    Load the sales transaction data.

    By default, the same 100,000-row validation sample used
    in the final notebook is loaded.
    """
    if not input_file.exists():
        raise FileNotFoundError(
            f"Input file not found: {input_file}"
        )

    df = pd.read_csv(input_file, nrows=nrows)

    return df


# ---------------------------------------------------------
# Clean sales data
# ---------------------------------------------------------
def clean_sales_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply the cleaning logic used in the final D1 notebook.
    """

    cleaned_sales = df.copy()

    # 1. Remove duplicate rows
    cleaned_sales = cleaned_sales.drop_duplicates()

    # 2. Convert date column to datetime
    cleaned_sales["date"] = pd.to_datetime(
        cleaned_sales["date"],
        errors="coerce"
    )

    # Remove rows where date could not be parsed
    cleaned_sales = cleaned_sales[
        cleaned_sales["date"].notna()
    ].copy()

    # 3. Remove invalid quantity values
    cleaned_sales = cleaned_sales[
        cleaned_sales["quantity"] > 0
    ].copy()

    # 4. Remove invalid unit prices
    cleaned_sales = cleaned_sales[
        cleaned_sales["unit_price"] > 0
    ].copy()

    # 5. Validate and correct total_value
    calculated_total = (
        cleaned_sales["quantity"]
        * cleaned_sales["unit_price"]
    ).round(2)

    total_value_difference = (
        cleaned_sales["total_value"]
        - calculated_total
    ).abs()

    invalid_total_mask = total_value_difference > 0.01

    # Correct total_value using quantity × unit_price
    cleaned_sales.loc[
        invalid_total_mask,
        "total_value"
    ] = calculated_total[invalid_total_mask]

    # 6. Fill missing promotion IDs
    cleaned_sales["promo_id"] = (
        cleaned_sales["promo_id"]
        .fillna("NO_PROMO")
    )

    return cleaned_sales


# ---------------------------------------------------------
# Final validation
# ---------------------------------------------------------
def validate_cleaned_data(
    df: pd.DataFrame
) -> dict:
    """
    Validate the cleaned dataset before saving.
    """

    calculated_total = (
        df["quantity"]
        * df["unit_price"]
    )

    total_difference = (
        df["total_value"]
        - calculated_total
    ).abs()

    validation = {
        "rows": len(df),
        "columns": len(df.columns),
        "missing_values": int(df.isna().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum()),
        "invalid_quantity_rows": int(
            (df["quantity"] <= 0).sum()
        ),
        "invalid_unit_price_rows": int(
            (df["unit_price"] <= 0).sum()
        ),
        "invalid_total_value_rows": int(
            (total_difference > 0.01).sum()
        ),
        "invalid_date_rows": int(
            df["date"].isna().sum()
        ),
        "missing_promo_id": int(
            df["promo_id"].isna().sum()
        ),
    }

    return validation


# ---------------------------------------------------------
# Save cleaned data
# ---------------------------------------------------------
def save_cleaned_data(
    df: pd.DataFrame,
    output_file: Path = OUTPUT_FILE
) -> None:
    """
    Save the cleaned dataset to data/processed.
    """

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        output_file,
        index=False
    )


# ---------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------
def run_pipeline() -> pd.DataFrame:
    """
    Run the complete sales-data cleaning pipeline.
    """

    print("=" * 60)
    print("FORESIGHT DATA PIPELINE")
    print("=" * 60)

    print("\nLoading sales data...")
    sales_df = load_sales_data()

    print(
        f"Loaded rows: {len(sales_df)}"
    )

    print("\nCleaning sales data...")
    cleaned_sales = clean_sales_data(
        sales_df
    )

    print(
        f"Cleaned rows: {len(cleaned_sales)}"
    )

    print("\nRunning final validation...")
    validation = validate_cleaned_data(
        cleaned_sales
    )

    for key, value in validation.items():
        print(f"{key}: {value}")

    # Basic validation guards
    assert validation["duplicate_rows"] == 0
    assert validation["invalid_quantity_rows"] == 0
    assert validation["invalid_unit_price_rows"] == 0
    assert validation["invalid_total_value_rows"] == 0
    assert validation["invalid_date_rows"] == 0
    assert validation["missing_promo_id"] == 0

    print("\nSaving cleaned dataset...")
    save_cleaned_data(
        cleaned_sales
    )

    print(
        f"Saved to: {OUTPUT_FILE}"
    )

    print("\nPipeline completed successfully.")

    return cleaned_sales


# ---------------------------------------------------------
# Run directly
# ---------------------------------------------------------
if __name__ == "__main__":
    run_pipeline()