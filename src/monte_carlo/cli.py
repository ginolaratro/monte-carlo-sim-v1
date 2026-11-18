"""Command-line interface for the simulation."""
import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from .simulation import download_prices, plot_results, simulate


def main():
    parser = argparse.ArgumentParser(description="Simulate possible index price paths from historical log returns.")
    parser.add_argument("--ticker", default="^NDX", help="Yahoo Finance ticker (default: ^NDX)")
    parser.add_argument("--period", default="2y", help="Yahoo Finance lookback period (default: 2y)")
    parser.add_argument("--csv", type=Path, help="Use a local CSV with a Close column instead of downloading")
    parser.add_argument("--days", type=int, default=504, help="Trading days to simulate (default: 504)")
    parser.add_argument("--simulations", type=int, default=1000, help="Number of paths (default: 1000)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed (default: 42)")
    parser.add_argument("--output", type=Path, default=Path("output/simulation.png"), help="Chart output path")
    args = parser.parse_args()
    try:
        prices = pd.read_csv(args.csv)["Close"].dropna() if args.csv else download_prices(args.ticker, args.period)
        paths, returns = simulate(prices, args.days, args.simulations, args.seed)
        plot_results(paths, args.output, args.ticker)
    except (ValueError, KeyError, OSError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    p5, median, p95 = np.percentile(paths[-1], [5, 50, 95])
    print(f"Starting level: {paths[0, 0]:,.2f}\nDaily log return: {returns.mean():.4%}; volatility: {returns.std(ddof=1):.4%}")
    print(f"Ending levels (5th / median / 95th percentile): {p5:,.2f} / {median:,.2f} / {p95:,.2f}")
    print(f"Chart saved to {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
