import pandas as pd
import pytest

from datakit.cli import main


def test_stats(messy_csv, capsys):
    assert main(["stats", messy_csv]) == 0
    out = capsys.readouterr().out
    assert "mean" in out
    assert "value" in out


def test_stats_group_by(messy_csv, capsys):
    assert main(["stats", messy_csv, "--columns", "value", "--group-by", "group"]) == 0
    out = capsys.readouterr().out
    assert "a" in out and "b" in out


def test_fit(linear_csv, capsys):
    assert main(["fit", linear_csv, "-x", "x", "-y", "y"]) == 0
    out = capsys.readouterr().out
    assert "slope" in out
    assert "R^2" in out


def test_fit_poly(linear_csv, capsys):
    assert main(["fit", linear_csv, "-x", "x", "-y", "y", "--model", "poly:2"]) == 0
    assert "c2" in capsys.readouterr().out


def test_plot_with_fit(linear_csv, tmp_path, capsys):
    out_png = tmp_path / "p.png"
    args = ["plot", linear_csv, "-x", "x", "-y", "y", "--fit", "linear", "--out", str(out_png)]
    assert main(args) == 0
    assert out_png.exists()
    assert "wrote" in capsys.readouterr().out


def test_plot_default_out(linear_csv, capsys):
    assert main(["plot", linear_csv, "-x", "x", "-y", "y"]) == 0
    out = capsys.readouterr().out
    assert "y_vs_x.png" in out


def test_clean(messy_csv, tmp_path, capsys):
    out_csv = tmp_path / "cleaned.csv"
    assert main(["clean", messy_csv, "--columns", "value", "--out", str(out_csv)]) == 0
    assert out_csv.exists()
    cleaned = pd.read_csv(out_csv)
    assert cleaned["value"].max() < 100
    assert "dropped 2 rows" in capsys.readouterr().out


def test_clean_flag_mode(messy_csv, tmp_path, capsys):
    out_csv = tmp_path / "flagged.csv"
    args = ["clean", messy_csv, "--mode", "flag", "--columns", "value", "--out", str(out_csv)]
    assert main(args) == 0
    flagged = pd.read_csv(out_csv)
    assert "_outlier" in flagged.columns
    assert len(flagged) == 20


def test_missing_file_is_error(capsys):
    assert main(["stats", "no_such_file.csv"]) == 1
    assert "file not found" in capsys.readouterr().err


def test_bad_model_is_error(linear_csv, capsys):
    assert main(["fit", linear_csv, "-x", "x", "-y", "y", "--model", "wat"]) == 1
    assert "unknown model" in capsys.readouterr().err


def test_version(capsys):
    with pytest.raises(SystemExit) as excinfo:
        main(["--version"])
    assert excinfo.value.code == 0
    assert "datakit" in capsys.readouterr().out
