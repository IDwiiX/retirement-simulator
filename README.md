# Monte Carlo Retirement Simulator

### Stochastic Retirement Planning Tool


![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-2.x-013243?style=for-the-badge&logo=numpy&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2.x-150458?style=for-the-badge&logo=pandas&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

A Monte Carlo simulator for retirement savings: thousands of stochastic portfolio paths, run through an accumulation and withdrawal phase, summarized into percentile bands and a probability of not running out of money — with an interactive Streamlit front end.

**Core capabilities:** vectorized Monte Carlo engine (NumPy) · lognormal-return portfolio simulation · contribution and withdrawal phase modeling · percentile-band projection · probability-of-success estimation · interactive Streamlit dashboard with live parameter controls.

---

## How It Works

```text
                Monte Carlo Retirement Engine
                            │
       ┌────────────────────┼────────────────────┐
       ▼                    ▼                     ▼
  Accumulation         Simulation Core        Withdrawal
  Phase                                       Phase
  monthly contrib.     N random paths         fixed annual
  compounding growth   monthly return shocks  drawdown
                        (μ, σ from sliders)    ruin tracking
       └────────────────────┼────────────────────┘
                             ▼
                  Percentile Aggregation
                  (5 / 25 / 50 / 75 / 95%)
                             │
                             ▼
                  Streamlit Dashboard
```

```text
retirement-simulator/
├── assets/
│   └── dashboard.png
├── app.py
├── simulator.py
├── requirements.txt
├── LICENSE
└── README.md
```

---

## The Model

Each of the `n_simulations` paths evolves month by month. Monthly return is drawn from a normal distribution around the compounded monthly equivalent of the annual expected return:

$$
r_m = (1+r_a)^{1/12} - 1, \qquad \sigma_m = \frac{\sigma_a}{\sqrt{12}}
$$

$$
\varepsilon_t \sim \mathcal{N}(r_m,\ \sigma_m^2)
$$

**Accumulation phase** (months `1` to `years_to_retirement × 12`):

$$
V_t = V_{t-1}(1+\varepsilon_t) + C
$$

where $C$ is the fixed monthly contribution.

**Withdrawal phase** (remaining months):

$$
V_t = V_{t-1}(1+\varepsilon_t) - \frac{W}{12}
$$

where $W$ is the fixed annual withdrawal. A path that hits zero is marked as failed and held at zero for the rest of the simulation — it does not go negative or recover.

**Probability of success** is the share of paths that never fail:

$$
P(\text{success}) = 1 - \frac{1}{N}\sum_{i=1}^{N} \mathbb{1}[\text{path } i \text{ fails}]
$$

**Output percentiles.** At every month, the 5th/25th/50th/75th/95th percentile is taken across all simulated paths, giving the fan-chart bands shown on the dashboard rather than a single deterministic projection.

All `N` paths and all months are simulated in pre-allocated NumPy arrays with the random shocks drawn in a single vectorized call, rather than looping in Python per-simulation.

---

## Dashboard


Adjustable in the sidebar: current savings, monthly contribution, expected annual return, annual volatility, years to retirement, years in retirement, annual withdrawal, and number of simulations. The main panel updates live with three headline metrics (median final portfolio, probability of success, 5th-percentile worst case) and a percentile fan chart with a marker at the retirement-start date.

---

## Usage

```bash
# Clone
git clone git@github.com:IDwiiX/retirement-simulator.git
cd retirement-simulator

# Environment
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# Install
pip install -r requirements.txt

# Run
streamlit run app.py
```

The dashboard opens at:

```text
http://localhost:8501
```

### Using it as a library

```python
import simulator

percentiles, success_prob = simulator.simulate_retirement(
    initial_savings=100_000,
    monthly_contribution=500,
    annual_return=0.07,
    annual_volatility=0.15,
    years_to_retirement=20,
    years_in_retirement=30,
    annual_withdrawal=40_000,
    n_simulations=5_000,
)

print(f"Success probability: {success_prob:.1%}")
print(percentiles.tail())
```

---

## Publishing This Repo

```bash
git init
git add .
git commit -m "Initial commit: Monte Carlo retirement simulator"
git branch -M main
git remote add origin git@github.com:IDwiiX/retirement-simulator.git
git push -u origin main
```

Subsequent changes:

```bash
git add .
git commit -m "Describe the change"
git push
```

---

## Design Notes

- **Vectorized core** — all `N` simulations and all months are computed as NumPy array operations; the only Python-level loop is over months, not over simulations.
- **Percentile bands over point estimates** — the model deliberately surfaces the full distribution of outcomes (5–95% and 25–75% bands) instead of a single "expected" trajectory, since retirement planning is a tail-risk problem as much as an average-case one.
- **Ruin tracking, not just endpoint value** — a path is marked failed the moment it hits zero during withdrawal, so `success_prob` reflects the probability of never running out of money, not just the final balance.
- **Deterministic by default** — a fixed random seed makes runs reproducible; pass a different `random_seed` for fresh draws.

---


## Author

**Mohamed Ali** — CS student focused on quantitative finance, financial mathematics, and machine learning.

MIT License.
