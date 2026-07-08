"""Shared CSV loading and column validation for all datakit subcommands."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


class DatakitError(Exception):
    """A user-facing error: bad input file, unknown column, invalid option."""


def load_csv(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    if not path.is_file():
        raise DatakitError(f"file not found: {path}")
    try:
        df = pd.read_csv(path)
    except pd.errors.EmptyDataError:
        raise DatakitError(f"{path} is empty") from None
    except pd.errors.ParserError as exc:
        raise DatakitError(f"could not parse {path}: {exc}") from None
    if df.empty:
        raise DatakitError(f"{path} has a header but no data rows")
    return df


def numeric_columns(df: pd.DataFrame, columns: list[str] | None = None) -> list[str]:
    """Return the numeric columns to operate on.

    With ``columns=None`` every numeric column is returned; otherwise the
    given names are validated to exist and be numeric.
    """
    numeric = df.select_dtypes(include="number").columns.tolist()
    if columns is None:
        if not numeric:
            raise DatakitError("no numeric columns found in the file")
        return numeric
    missing = [c for c in columns if c not in df.columns]
    if missing:
        raise DatakitError(
            f"column(s) not found: {', '.join(missing)} (available: {', '.join(df.columns)})"
        )
    non_numeric = [c for c in columns if c not in numeric]
    if non_numeric:
        raise DatakitError(f"column(s) are not numeric: {', '.join(non_numeric)}")
    return list(columns)


def numeric_series(df: pd.DataFrame, name: str) -> pd.Series:
    """Return one column as floats, validating that it exists and holds numbers."""
    if name not in df.columns:
        raise DatakitError(f"column not found: {name} (available: {', '.join(df.columns)})")
    series = pd.to_numeric(df[name], errors="coerce")
    if series.notna().sum() == 0:
        raise DatakitError(f"column {name!r} has no numeric values")
    return series.astype(float)
