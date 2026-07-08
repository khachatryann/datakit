import pandas as pd
import pytest

from datakit.clean import clean, outlier_mask
from datakit.io import DatakitError


def test_iqr_drop(messy_df):
    result, report = clean(messy_df, method="iqr", mode="drop", columns=["value"])
    assert report.n_missing == 1
    assert report.n_outliers == 1
    assert report.n_dropped == 2
    assert len(result) == len(messy_df) - 2
    assert result["value"].max() < 100
    assert not result["value"].isna().any()


def test_zscore_drop(messy_df):
    _, report = clean(messy_df, method="zscore", mode="drop", columns=["value"])
    assert report.n_outliers == 1
    assert report.n_missing == 1


def test_flag_mode_keeps_rows(messy_df):
    result, report = clean(messy_df, method="iqr", mode="flag", columns=["value"])
    assert len(result) == len(messy_df)
    assert report.n_dropped == 0
    assert result["_missing"].sum() == 1
    assert result["_outlier"].sum() == 1
    assert bool(result.loc[result["value"] == 100.0, "_outlier"].iloc[0])


def test_clean_data_untouched(linear_df):
    result, report = clean(linear_df)
    assert report.n_dropped == 0
    assert len(result) == len(linear_df)


def test_zscore_constant_column():
    df = pd.DataFrame({"a": [5.0] * 10})
    _, report = clean(df, method="zscore")
    assert report.n_outliers == 0


def test_outlier_mask_direct(messy_df):
    mask = outlier_mask(messy_df, ["value"], method="iqr")
    assert mask.sum() == 1


def test_bad_method(messy_df):
    with pytest.raises(DatakitError):
        clean(messy_df, method="magic")


def test_bad_mode(messy_df):
    with pytest.raises(DatakitError):
        clean(messy_df, mode="explode")


def test_bad_threshold(messy_df):
    with pytest.raises(DatakitError):
        clean(messy_df, threshold=-1.0)
