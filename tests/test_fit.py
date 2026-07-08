import numpy as np
import pandas as pd
import pytest

from datakit.fit import fit, parse_model
from datakit.io import DatakitError


def test_linear_exact(linear_df):
    result = fit(linear_df, "x", "y", "linear")
    assert result.coefficients["slope"] == pytest.approx(2.0)
    assert result.coefficients["intercept"] == pytest.approx(1.0)
    assert result.r_squared == pytest.approx(1.0)
    assert result.predict(np.array([100.0]))[0] == pytest.approx(201.0)
    assert result.n_points == 10


def test_poly_exact():
    x = np.linspace(-3, 3, 25)
    df = pd.DataFrame({"x": x, "y": 3 * x**2 - 2 * x + 5})
    result = fit(df, "x", "y", "poly:2")
    assert result.coefficients["c2"] == pytest.approx(3.0)
    assert result.coefficients["c1"] == pytest.approx(-2.0)
    assert result.coefficients["c0"] == pytest.approx(5.0)
    assert result.r_squared == pytest.approx(1.0)
    assert "x^2" in result.equation


def test_exp_exact():
    x = np.linspace(0, 4, 30)
    df = pd.DataFrame({"x": x, "y": 2.0 * np.exp(0.5 * x)})
    result = fit(df, "x", "y", "exp")
    assert result.coefficients["a"] == pytest.approx(2.0)
    assert result.coefficients["b"] == pytest.approx(0.5)
    assert result.r_squared == pytest.approx(1.0)


def test_exp_ignores_nonpositive_y():
    x = [0.0, 1.0, 2.0, 3.0]
    y = [-1.0, 2 * np.exp(0.5), 2 * np.exp(1.0), 2 * np.exp(1.5)]
    result = fit(pd.DataFrame({"x": x, "y": y}), "x", "y", "exp")
    assert result.n_points == 3
    assert any("non-positive" in w for w in result.warnings)


def test_missing_rows_ignored():
    df = pd.DataFrame({"x": [0.0, 1.0, 2.0, None], "y": [1.0, 3.0, 5.0, 7.0]})
    result = fit(df, "x", "y", "linear")
    assert result.n_points == 3
    assert result.coefficients["slope"] == pytest.approx(2.0)
    assert any("missing" in w for w in result.warnings)


@pytest.mark.parametrize("spec", ["cubic", "poly:0", "poly:x", "poly:-2"])
def test_bad_model_spec(linear_df, spec):
    with pytest.raises(DatakitError):
        fit(linear_df, "x", "y", spec)


def test_parse_model():
    assert parse_model("linear") == ("poly", 1)
    assert parse_model("poly:3") == ("poly", 3)
    assert parse_model("EXP") == ("exp", 0)


def test_too_few_points():
    df = pd.DataFrame({"x": [1.0, 2.0], "y": [1.0, 2.0]})
    with pytest.raises(DatakitError):
        fit(df, "x", "y", "poly:3")


def test_unknown_column(linear_df):
    with pytest.raises(DatakitError):
        fit(linear_df, "x", "nope")
