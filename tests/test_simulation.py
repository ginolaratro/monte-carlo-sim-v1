import numpy as np
import pandas as pd
import pytest

from monte_carlo.simulation import download_prices, plot_results, simulate


def test_simulation_is_reproducible_and_starts_at_last_price():
    paths, returns = simulate([100, 101, 99, 102], days=10, simulations=5, seed=7)
    again, _ = simulate([100, 101, 99, 102], days=10, simulations=5, seed=7)
    assert paths.shape == (11, 5)
    assert np.all(paths[0] == 102)
    assert np.all(paths > 0)
    np.testing.assert_array_equal(paths, again)
    assert len(returns) == 3


@pytest.mark.parametrize("prices", [[1, 2], [1, 0, 2], [1, float('nan'), 2]])
def test_invalid_prices_rejected(prices):
    with pytest.raises(ValueError):
        simulate(prices)


def test_download_handles_multiindex(monkeypatch):
    frame = pd.DataFrame({("Close", "^NDX"): [100., 101., 102.]})
    monkeypatch.setattr("monte_carlo.simulation.yf.download", lambda *a, **kw: frame)
    assert download_prices().tolist() == [100., 101., 102.]


def test_plot_writes_file(tmp_path):
    paths, _ = simulate([100, 101, 99], days=5, simulations=3)
    output = tmp_path / "nested" / "chart.png"
    plot_results(paths, output)
    assert output.stat().st_size > 0
