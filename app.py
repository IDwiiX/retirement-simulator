import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import simulator

st.set_page_config(page_title="Retirement Simulator", layout="wide")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Newsreader:ital,wght@0,400;0,500;0,600;0,700;1,400&family=IBM+Plex+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'Newsreader', Georgia, serif;
    }

    h1, h2, h3 {
        font-family: 'Newsreader', Georgia, serif !important;
        font-weight: 600 !important;
        letter-spacing: -0.01em;
    }

    [data-testid="stMetricValue"] {
        font-family: 'IBM Plex Mono', monospace;
        font-weight: 500;
    }

    [data-testid="stMetricLabel"] {
        font-family: 'Newsreader', Georgia, serif;
        font-style: italic;
    }

    .stCaption, [data-testid="stCaptionContainer"] {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.75rem;
    }

    section[data-testid="stSidebar"] label {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.85rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Monte Carlo Retirement Simulator")
st.markdown("Plan your future with confidence. Adjust the sliders and see the range of possible outcomes.")

st.sidebar.header("Your Details")
initial = st.sidebar.number_input("Current savings ($)", 0, 10_000_000, 100_000, step=10_000, format="%d")
monthly_contrib = st.sidebar.number_input("Monthly contribution ($)", 0, 20_000, 500, step=100, format="%d")
annual_ret = st.sidebar.slider("Expected annual return (%)", 0.0, 15.0, 7.0, 0.5) / 100
annual_vol = st.sidebar.slider("Annual volatility (%)", 1.0, 50.0, 15.0, 1.0) / 100
years_work = st.sidebar.slider("Years until retirement", 1, 50, 20)
years_retire = st.sidebar.slider("Years in retirement", 1, 50, 30)
withdrawal = st.sidebar.number_input("Annual withdrawal in retirement ($)", 0, 300_000, 40_000, step=5_000, format="%d")
n_sims = st.sidebar.slider("Number of simulations", 100, 10_000, 1_000, step=100)

percentiles, success_prob = simulator.simulate_retirement(
    initial, monthly_contrib, annual_ret, annual_vol,
    years_work, years_retire, withdrawal, n_sims
)

col1, col2, col3 = st.columns(3)
median_final = percentiles.iloc[-1]["50%"]
col1.metric("Median final portfolio", f"${median_final:,.0f}")
col2.metric("Probability of success", f"{success_prob:.1%}")
col3.metric("Worst-case (5th percentile)", f"${percentiles.iloc[-1]['5%']:,.0f}")

font_path = fm.findfont(fm.FontProperties(family="Georgia"))
plt.rcParams["font.family"] = "serif"
plt.rcParams["font.serif"] = ["Georgia", "Times New Roman", "DejaVu Serif"]
plt.rcParams["axes.edgecolor"] = "#2b2b2b"
plt.rcParams["axes.labelcolor"] = "#2b2b2b"
plt.rcParams["text.color"] = "#2b2b2b"
plt.rcParams["xtick.color"] = "#2b2b2b"
plt.rcParams["ytick.color"] = "#2b2b2b"

fig, ax = plt.subplots(figsize=(12, 6))
fig.patch.set_facecolor("#fdfcf9")
ax.set_facecolor("#fdfcf9")

ax.fill_between(percentiles.index, percentiles["5%"], percentiles["95%"],
                 alpha=0.20, color="#8a6d3b", label="5th–95th percentile", linewidth=0)
ax.fill_between(percentiles.index, percentiles["25%"], percentiles["75%"],
                 alpha=0.35, color="#8a6d3b", label="25th–75th percentile", linewidth=0)
ax.plot(percentiles.index, percentiles["50%"], color="#3d2c1f", linewidth=2.2, label="Median")
ax.axvline(x=percentiles.index[years_work * 12], color="#a13d3d", linestyle="--",
           linewidth=1.3, label="Retirement begins")

ax.set_ylabel("Portfolio value ($)", fontsize=11, style="italic")
ax.set_xlabel("Year", fontsize=11, style="italic")
ax.set_title("Projected Retirement Savings Over Time", fontsize=15, weight="bold", pad=14)
ax.legend(loc="upper left", frameon=False, fontsize=10)
ax.grid(True, alpha=0.15, color="#2b2b2b")
for spine in ["top", "right"]:
    ax.spines[spine].set_visible(False)

st.pyplot(fig)

st.markdown("---")
st.caption("This tool is for educational purposes only and does not constitute financial advice.")