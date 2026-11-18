"""Data loading, simulation, and visualization."""
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf


def download_prices(ticker: str = "^NDX", period: str = "2y") -> pd.Series:
    """Download adjusted closing prices, handling yfinance's column formats."""
    data = yf.download(ticker, period=period, auto_adjust=True, progress=False)
    if data.empty or "Close" not in data.columns:
        raise ValueError(f"No closing prices returned for {ticker}. Check the ticker and network connection.")
    close = data["Close"]
    if isinstance(close, pd.DataFrame):
        if ticker not in close.columns:
            raise ValueError(f"No closing prices returned for {ticker}.")
        close = close[ticker]
    return close.dropna().rename("Close")


def simulate(prices, days=504, simulations=1000, seed=42):
    """Simulate geometric Brownian motion using historical daily log returns.

    The returned array includes the starting price at row zero.
    """
    prices = np.asarray(prices, dtype=float)
    if prices.ndim != 1 or len(prices) < 3 or not np.isfinite(prices).all() or (prices <= 0).any():
        raise ValueError("At least three finite, positive prices are required.")
    if days < 1 or simulations < 1:
        raise ValueError("Days and simulations must be positive.")
    returns = np.diff(np.log(prices))
    rng = np.random.default_rng(seed)
    changes = rng.normal(returns.mean(), returns.std(ddof=1), (days, simulations))
    paths = prices[-1] * np.exp(np.vstack([np.zeros(simulations), np.cumsum(changes, axis=0)]))
    return paths, returns


def plot_results(paths, output, ticker="^NDX"):
    """Save a chart showing sample paths and the terminal distribution."""
    paths = np.asarray(paths)
    final = paths[-1]
    median = np.median(final)
    fig, (ax, hist) = plt.subplots(1, 2, figsize=(14, 6), gridspec_kw={"width_ratios": [1.5, 1]})
    fig.patch.set_facecolor("#f6f8fc")
    for axis in (ax, hist):
        axis.set_facecolor("white")
        axis.grid(alpha=.15)
        axis.spines[["top", "right"]].set_visible(False)
    ax.plot(paths[:, :min(100, paths.shape[1])], color="#4361ee", alpha=.12, linewidth=.8)
    ax.plot(np.median(paths, axis=1), color="#172554", linewidth=2, label="Median path")
    ax.axhline(paths[0, 0], color="#e98a32", linestyle="--", label="Starting price")
    ax.set(title="Possible price paths", xlabel="Trading days", ylabel="Index level")
    ax.legend(frameon=False)
    hist.hist(final, bins=40, color="#4361ee", alpha=.8, edgecolor="white")
    hist.axvline(median, color="#172554", linewidth=2, label=f"Median: {median:,.0f}")
    hist.axvline(paths[0, 0], color="#e98a32", linestyle="--", label="Starting price")
    hist.set(title="Ending price distribution", xlabel="Index level", ylabel="Simulations")
    hist.legend(frameon=False)
    fig.suptitle(f"{ticker} Monte Carlo simulation", fontsize=17, fontweight="bold", x=.08, ha="left")
    fig.tight_layout(rect=(0, 0, 1, .94))
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=160, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
