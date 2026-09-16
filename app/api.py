from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


# ---------------------------------
# FastAPI App
# ---------------------------------

app = FastAPI(
    title="FORESIGHT Scoring API",
    description="Demand Forecast & Inventory Risk Scoring Service",
    version="1.0.0"
)


# ---------------------------------
# Load Risk Scored Data
# ---------------------------------

BASE_DIR = Path(__file__).resolve().parent

DATA_FILE = BASE_DIR / "data" / "processed" / "risk_scored_data.csv"

risk_df = pd.read_csv(DATA_FILE)


# ---------------------------------
# Input Models
# ---------------------------------

class SKURequest(BaseModel):
    sku_id: str


class BatchRequest(BaseModel):
    sku_ids: list[str]


# ---------------------------------
# Health Check
# ---------------------------------

@app.get("/")
def home():
    return {
        "service": "FORESIGHT Scoring API",
        "status": "running",
        "version": "1.0.0"
    }


# ---------------------------------
# Score Single SKU
# ---------------------------------

@app.post("/score")
def score_sku(request: SKURequest):

    sku_data = risk_df[
        risk_df["sku_id"].astype(str) == str(request.sku_id)
    ].copy()

    if sku_data.empty:
        raise HTTPException(
            status_code=404,
            detail=f"SKU {request.sku_id} not found"
        )

    # Forecast and actual demand
    actual_demand = float(
        sku_data["actual_demand"].sum()
    )

    forecast_demand = float(
        sku_data["forecast_demand"].sum()
    )

    # Risk flags
    stockout_risk = bool(
        sku_data["stockout_risk"].any()
    )

    overstock_risk = bool(
        sku_data["overstock_risk"].any()
    )

    # Action
    if stockout_risk:
        action = "Reorder Now"
    elif overstock_risk:
        action = "Markdown/Clear"
    else:
        action = "Healthy"

    # Optional risk metrics
    stockout_units = float(
        sku_data["stockout_units_at_risk"].sum()
    )

    sales_at_risk = float(
        sku_data["sales_at_risk_rupees"].sum()
    )

    overstock_units = float(
        sku_data["overstock_units_at_risk"].sum()
    )

    locked_capital = float(
        sku_data["locked_capital_rupees"].sum()
    )

    # Category
    category = (
        sku_data["category"].dropna().iloc[0]
        if "category" in sku_data.columns
        and not sku_data["category"].dropna().empty
        else None
    )

    return {
        "sku_id": request.sku_id,
        "category": category,

        "forecast": {
            "actual_demand": actual_demand,
            "forecast_demand": forecast_demand
        },

        "risk": {
            "stockout_risk": stockout_risk,
            "overstock_risk": overstock_risk,
            "stockout_units_at_risk": stockout_units,
            "sales_at_risk_rupees": sales_at_risk,
            "overstock_units_at_risk": overstock_units,
            "locked_capital_rupees": locked_capital
        },

        "action": action
    }


# ---------------------------------
# Score Batch of SKUs
# ---------------------------------

@app.post("/score/batch")
def score_batch(request: BatchRequest):

    results = []

    for sku_id in request.sku_ids:

        sku_data = risk_df[
            risk_df["sku_id"].astype(str) == str(sku_id)
        ].copy()

        if sku_data.empty:
            results.append({
                "sku_id": sku_id,
                "status": "not_found"
            })
            continue

        stockout_risk = bool(
            sku_data["stockout_risk"].any()
        )

        overstock_risk = bool(
            sku_data["overstock_risk"].any()
        )

        if stockout_risk:
            action = "Reorder Now"
        elif overstock_risk:
            action = "Markdown/Clear"
        else:
            action = "Healthy"

        results.append({
            "sku_id": sku_id,
            "actual_demand": float(
                sku_data["actual_demand"].sum()
            ),
            "forecast_demand": float(
                sku_data["forecast_demand"].sum()
            ),
            "stockout_risk": stockout_risk,
            "overstock_risk": overstock_risk,
            "action": action
        })

    return {
        "count": len(results),
        "results": results
    }