import pandas as pd
from pathlib import Path

BASE_DIR = Path("/Users/dhanistha/mutual-fund-analytics")
PROCESSED_DIR = BASE_DIR / "data" / "processed"


def recommend_funds(risk_appetite):
    risk_appetite = risk_appetite.strip().lower()

    risk_map = {
        "low": ["Low"],
        "moderate": ["Moderate", "Moderately High"],
        "high": ["High", "Very High"],
    }

    if risk_appetite not in risk_map:
        raise ValueError("Risk appetite must be Low, Moderate, or High")

    scorecard = pd.read_csv(PROCESSED_DIR / "fund_scorecard.csv")
    performance = pd.read_csv(PROCESSED_DIR / "07_scheme_performance_clean.csv")

    data = scorecard.merge(
        performance[["amfi_code", "risk_grade"]],
        on="amfi_code",
        how="left"
    )

    filtered = data[data["risk_grade"].isin(risk_map[risk_appetite])].copy()

    recommendations = (
        filtered.sort_values("sharpe_ratio", ascending=False)
        .head(3)
        [[
            "amfi_code",
            "scheme_name",
            "fund_house",
            "risk_grade",
            "sharpe_ratio",
            "cagr_3yr",
            "fund_score",
        ]]
    )

    return recommendations


if __name__ == "__main__":
    risk = input("Enter risk appetite (Low / Moderate / High): ")
    result = recommend_funds(risk)
    print("\nTop 3 Recommended Funds:")
    print(result.to_string(index=False))
