import numpy as np
import pandas as pd


def simulate_retirement(
    initial_savings: float,
    monthly_contribution: float,
    annual_return: float,
    annual_volatility: float,
    years_to_retirement: int,
    years_in_retirement: int,
    annual_withdrawal: float,
    n_simulations: int = 1000,
    random_seed: int = 42,
) -> tuple[pd.DataFrame, float]:
    rng = np.random.default_rng(random_seed)
    total_years = years_to_retirement + years_in_retirement
    months = total_years * 12

    monthly_return = (1 + annual_return) ** (1 / 12) - 1
    monthly_vol = annual_volatility / np.sqrt(12)

    portfolio = np.zeros((n_simulations, months + 1))
    portfolio[:, 0] = initial_savings
    failed = np.zeros(n_simulations, dtype=bool)

    shocks = rng.normal(monthly_return, monthly_vol, size=(n_simulations, months))

    for month in range(1, months + 1):
        portfolio[:, month] = portfolio[:, month - 1] * (1 + shocks[:, month - 1])

        if month <= years_to_retirement * 12:
            portfolio[:, month] += monthly_contribution
        else:
            portfolio[:, month] -= annual_withdrawal / 12
            failed[portfolio[:, month] <= 0] = True
            portfolio[failed & (portfolio[:, month] < 0), month] = 0

    success_prob = 1 - failed.mean()

    dates = pd.date_range(start="2024-01-01", periods=months + 1, freq="ME")
    df = pd.DataFrame(portfolio.T, index=dates)
    percentile_df = df.quantile([0.05, 0.25, 0.5, 0.75, 0.95], axis=1).T
    percentile_df.columns = ["5%", "25%", "50%", "75%", "95%"]

    return percentile_df, success_prob