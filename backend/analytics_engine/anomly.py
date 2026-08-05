import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest


def detect_cashflow_anomalies(df: pd.DataFrame, contamination: float = 0.1) -> list:
    """Flags month with unusual net cash flow relative to the trend."""
    if len(df) < 6:
        return []

    features = df[["net_cashflow"]].copy()
    model = IsolationForest(contamination=contamination, random_state=42)
    df = df.copy()
    df["anomaly_score"] = model.fit_predict(features)
    df["is_anomaly"] = df["anomaly_score"] == -1

    anomalies = df[df["is_anomaly"]]
    return [
        {
            "month" : row["month"].isoformat() if hasattr(row["month"], "isoformat") else str(row["month"]),
            "net_cashflow": round(row["net_cashflow"], 2),
            "reason": "Unusual net cash flow relative to historical pattern",
        }
        for _, row in anomalies.iterrows()
    ]


def detect_slow_moving_inventory(df: pd.DataFrame, turnover_threshold: float = 0.4):
    """
    Flags SKUs whos average turnover rate is persistently below threshold- 
    this is the direct 'muda' (waste) signal for inventory: capital tied up
    in stock that isn't moving.
    """
    if df.empty:
        return []

    summary = df.groupby("sku").agg(
        avg_turnover_rate=("avg_turnover_rate", "mean"),
        avg_value = ("inventory_value", "mean"),
        months_tracked = ("month", "count"), 
    ).reset_index()

    flagged = summary[
        (summary["avg_turnover_rate"] < turnover_threshold) & (summary["months_tracked"] > 0)
    ]

    return [
        {
            "sku": row["sku"],
            "avg_turnover_rate": round(row["avg_turnover_rate"], 3),
            "avg_inventory_value": round(row["avg_value"], 2),
            "reason": f"Turnover rate {row['avg_turnover_rate']:.3f} below threshold {turnover_threshold} — capital tied up in slow-moving stock",
        }
        for _, row in flagged.iterrows()
    ]