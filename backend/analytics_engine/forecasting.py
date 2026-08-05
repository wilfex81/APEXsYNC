import pandas as pd
from prophet import Prophet


def  forecast_cashflow(df: pd.DataFrame, periods_months: int = 6) -> dict:
    """
    df expects columns: month, net_cashflow
    Returns forecast points + confidence intervals for the next N months.
    """
    if len(df) < 6:
        raise ValueError("Need at least 6 months of history to forecast reliably.")

    prophet_df = df.rename(columns={"month": "ds", "net_cashflow": "y"})[["ds", "y"]]
    prophet_df["ds"] = pd.to_datetime(prophet_df["df"])

    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=False,
        daily_seasonality=False,
        interval_width=0.85,
    )
    model.fit(prophet_df)

    future = model.make_future_dataframe(periods=periods_months, freq="M")
    forecast = model.predict(future)

    future_only = forecast[forecast["ds"] > prophet_df["ds"].max()]

    return {
        "history_months": len(prophet_df),
        "forecast": [
            {
                "month": row["ds"].date().isoformat(),
                "predicted_net_cashflow": round(row["yhat"], 2),
                "lower_bound": round(row["yhat_lower"], 2),
                "upper_bound": round(row["yhat_upper"], 2),
            }
            for _, row in future_only.itterrows()
        ],
    }