import pytest

from datakit.io import DatakitError
from datakit.stats import summary_stats


def test_basic_stats(linear_df):
    table = summary_stats(linear_df)
    assert table.loc["x", "mean"] == pytest.approx(4.5)
    assert table.loc["y", "mean"] == pytest.approx(10.0)
    assert table.loc["x", "count"] == 10
    assert {"count", "mean", "std", "min", "25%", "50%", "75%", "max"} <= set(table.columns)


def test_column_selection(linear_df):
    table = summary_stats(linear_df, columns=["y"])
    assert list(table.index) == ["y"]


def test_nan_excluded_from_count(messy_df):
    table = summary_stats(messy_df, columns=["value"])
    assert table.loc["value", "count"] == 19


def test_group_by(messy_df):
    table = summary_stats(messy_df, columns=["value"], group_by="group")
    assert ("a", "value") in table.index
    assert ("b", "value") in table.index
    assert table.loc[("a", "value"), "count"] + table.loc[("b", "value"), "count"] == 19


def test_unknown_column(linear_df):
    with pytest.raises(DatakitError):
        summary_stats(linear_df, columns=["nope"])


def test_non_numeric_column(messy_df):
    with pytest.raises(DatakitError):
        summary_stats(messy_df, columns=["group"])


def test_unknown_group_by(linear_df):
    with pytest.raises(DatakitError):
        summary_stats(linear_df, group_by="nope")
