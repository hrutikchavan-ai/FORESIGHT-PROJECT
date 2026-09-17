# FORESIGHT — Demand Forecasting & Inventory Risk

## 1. Project Overview

FORESIGHT is a demand forecasting and inventory-risk decision-support solution for NorthBay Living.

The solution converts historical sales and inventory information into:

- Weekly SKU-level demand forecasts
- Stockout and overstock risk signals
- Recommended business actions
- Rupee value at stake
- An interactive Streamlit planning dashboard
- A FastAPI scoring service

The objective is to help Operations and Finance prioritize replenishment and excess-inventory decisions using a repeatable, data-driven workflow.

---

## 2. Business Problem

The project addresses two practical inventory questions:

1. Which SKUs are at risk of stocking out?
2. Which SKUs are carrying too much inventory?

The solution connects forecasting with inventory-risk scoring so that users can move from a demand signal to an operational action.

The main recommended actions are:

- **Reorder Now**
- **Markdown/Clear**
- **Watch / Healthy**

The system is a decision-support tool. It does not automatically place purchase orders.

---

## 3. Project Workflow

```text
Raw Data
   |
   v
Data Cleaning & Validation
   |
   v
Analysis-Ready Data
   |
   v
Weekly SKU Demand
   |
   v
Forecasting
   |
   v
Risk Scoring
   |
   v
Rupee Impact + Recommended Action
   |
   +-----------------------+
   |                       |
   v                       v
Streamlit Dashboard    FastAPI Scoring Service
```

---

## 4. Repository Structure

```text
FORESIGHT-PROJECT/
├── app/
│   └── app.py
├── data/
│   ├── raw/
│   └── processed/
├── notebooks/
│   ├── 01_data_quality_eda.ipynb
│   ├── 02_baseline_forecast.ipynb
│   └── 03_model_risk.ipynb
├── reports/
│   ├── EDA memo.pdf
│   └── Executive readout.pdf
├── service/
│   └── api.py
├── src/
│   ├── pipeline.py
│   ├── forecast.py
│   └── risk.py
├── .gitignore
├── README.md
└── requirements.txt
```

---

## 5. Data

The project uses retail data covering sales, products/SKUs, stores, inventory, promotions, and customers.

### Main data sources

- Sales transactions
- SKU master
- Store master
- Inventory snapshot
- SKU inventory flags
- Promotions
- Customer master

The original sales transaction source contains **10M+ transactions**.

For the validation work documented in this repository, a **100,000-row transaction sample** was used because the complete transaction file was too large to upload during development.

> The 100K sample is a validation subset of the original transaction source. Forecast metrics may change when the complete transaction history is processed.

---

## 6. Data Preparation

The data-preparation workflow includes:

- Data ingestion
- Data type fixes
- Missing-value checks
- Duplicate checks
- Data validation
- Feature preparation
- Creation of analysis-ready data

The cleaning logic is implemented in code rather than being performed manually.

---

## 7. Forecasting Methodology

Weekly demand is created at SKU level from transaction-level sales.

The forecasting workflow includes:

- Historical demand features
- Lag features
- Rolling-demand features
- Time/calendar features
- Chronological train/test splitting
- Seasonal-Naive baseline
- Random Forest forecasting model
- Rolling-origin validation

The model is evaluated against the Seasonal-Naive reference rather than being evaluated in isolation.

---

## 8. Forecast Evaluation

The primary forecast metric is **WAPE (Weighted Absolute Percentage Error)**.

On the supplied 100K transaction validation sample:

| Model | Test WAPE |
|---|---:|
| Random Forest | 155.05% |
| Seasonal Naive | 156.65% |

Difference:

**1.60 percentage points**

The model result is reported as observed on the validation sample and should not be interpreted as a guarantee of future demand.

Rolling-origin validation was also used to evaluate the forecasting approach over multiple historical folds.

---

## 9. Inventory Risk Scoring

Forecast and inventory information are converted into transparent risk signals:

- **Stockout**
- **Overstock**
- **Healthy**

The risk layer also produces a recommended action and financial impact.

### Example actions

| Risk situation | Recommended action |
|---|---|
| Stockout risk | Reorder Now |
| Overstock risk | Markdown/Clear |
| No immediate risk | Watch / Healthy |

The risk output includes financial-impact fields such as:

- `sales_at_risk_rupees`
- `locked_capital_rupees`
- `rupee_value_at_stake`

These fields help Operations and Finance prioritize items by potential business impact.

---

## 10. Streamlit Planning Dashboard

The dashboard provides a stakeholder-facing view of the forecasting and inventory-risk outputs.

### Main capabilities

- Category filter
- SKU filter
- Actual vs Forecast visualization
- Stockout / Overstock / Healthy risk overview
- Reorder Now priority list
- Markdown/Clear priority list
- Watch SKU information
- Financial impact information
- Action summary

### Live Dashboard

https://foresight-project-cs3i.onrender.com

---

## 11. FastAPI Scoring Service

FORESIGHT also provides a FastAPI scoring service for programmatic SKU scoring.

### Live Scoring Service

https://foresight-scoring-api-6nec.onrender.com

### API Documentation

https://foresight-scoring-api-6nec.onrender.com/docs

### Single SKU Scoring

```text
POST /score
```

Example input:

```json
{
  "sku_id": "SKU003633"
}
```

The response provides the requested SKU's forecast information, risk information, recommended action, and relevant financial-impact fields.

### Batch Scoring

```text
POST /score/batch
```

The batch endpoint accepts multiple SKU IDs and returns scoring results for the requested SKUs.

### Invalid Input

The service validates incoming requests and returns an HTTP error response for an unknown SKU instead of silently returning an incorrect result.

---

## 12. Running the Project Locally

### Clone the repository

```bash
git clone https://github.com/hrutikchavan-ai/FORESIGHT-PROJECT.git
cd FORESIGHT-PROJECT
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Run the Streamlit dashboard

```bash
streamlit run app/app.py
```

### Run the FastAPI service

```bash
uvicorn service.api:app --reload
```

The FastAPI documentation will then be available at:

```text
http://127.0.0.1:8000/docs
```

---

## 13. Limitations & Assumptions

- Forecast validation documented here uses the supplied 100K transaction sample rather than the complete 10M+ transaction source.
- Forecast performance may change when the complete transaction history is processed.
- New or sparse SKUs may have less reliable forecasts.
- Risk results depend on the available forecast, inventory, price, and cost inputs.
- Promotions and other external demand drivers can affect actual demand.
- WAPE should be monitored over time as new data becomes available.
- Risk outputs are decision-support signals and should be reviewed with business context.
- The system does not automatically place purchase orders.

---

## 14. Business Usage

### Operations

Operations can use the dashboard to:

1. Identify high-risk SKUs.
2. Review **Reorder Now** items.
3. Review **Markdown/Clear** items.
4. Compare actual demand with forecast demand.
5. Prioritize items using financial impact.

### Finance

Finance can use the financial-impact outputs to understand:

- Potential sales exposure from stockout risk
- Capital tied up in excess inventory
- Which SKU risks require further business review

---

## 15. Project Deliverables

The FORESIGHT project includes:

- Data pipeline and data-quality validation
- Data-quality and EDA analysis
- Seasonal-Naive forecasting baseline
- SKU-level demand forecasting
- Rolling-origin forecast validation
- Stockout and overstock risk scoring
- Rupee impact and recommended actions
- Streamlit planning dashboard
- FastAPI scoring service
- Executive readout

---

## 16. Reproducibility

The project is organized so that the analysis and modelling workflow can be reproduced from the repository code and documented dependencies.

For final submission, the repository should contain the pipeline, notebooks, model code, dashboard/service code, and required reports.

Do not commit large raw data dumps, credentials, API keys, or other secrets to the repository.
