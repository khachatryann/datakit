import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def linear_df():
    """Perfect line y = 2x + 1 over x = 0..9."""
    x = np.arange(10, dtype=float)
    return pd.DataFrame({"x": x, "y": 2.0 * x + 1.0})


@pytest.fixture
def messy_df():
    """20 rows: values tight around 10, one extreme outlier (100), one NaN."""
    value = [
        10.0, 10.1, 9.9, 10.2, 9.8, 10.0, 10.1, 9.9, 10.3, 9.7,
        10.0, 10.2, 9.8, 10.1, 9.9, 10.0, 100.0, 10.1, None, 9.9,
    ]
    return pd.DataFrame(
        {"group": ["a", "b"] * 10, "value": value, "t": np.arange(20, dtype=float)}
    )


@pytest.fixture
def linear_csv(tmp_path, linear_df):
    path = tmp_path / "linear.csv"
    linear_df.to_csv(path, index=False)
    return str(path)


@pytest.fixture
def messy_csv(tmp_path, messy_df):
    path = tmp_path / "messy.csv"
    messy_df.to_csv(path, index=False)
    return str(path)
