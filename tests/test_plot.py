import pytest

from datakit.fit import fit
from datakit.io import DatakitError
from datakit.plot import make_plot

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def test_scatter_png(linear_df, tmp_path):
    out = tmp_path / "plot.png"
    result = make_plot(linear_df, "x", "y", out)
    assert result == out
    assert out.read_bytes()[:8] == PNG_MAGIC


def test_line_with_fit_overlay(linear_df, tmp_path):
    fit_result = fit(linear_df, "x", "y", "linear")
    out = tmp_path / "fitplot.png"
    make_plot(linear_df, "x", "y", out, kind="line", fit_result=fit_result, title="demo")
    assert out.read_bytes()[:8] == PNG_MAGIC


def test_nan_rows_skipped(messy_df, tmp_path):
    out = tmp_path / "messy.png"
    make_plot(messy_df, "t", "value", out)
    assert out.exists()


def test_bad_kind(linear_df, tmp_path):
    with pytest.raises(DatakitError):
        make_plot(linear_df, "x", "y", tmp_path / "x.png", kind="pie")


def test_unknown_column(linear_df, tmp_path):
    with pytest.raises(DatakitError):
        make_plot(linear_df, "x", "nope", tmp_path / "x.png")
