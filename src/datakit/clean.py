"""Missing-value and outlier handling: drop offending rows or flag them."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from datakit.io import DatakitError, numeric_columns

DEFAULT_THRESHOLDS = {"iqr": 1.5, "zscore": 3.0}


@dataclass
class CleanReport:
    method: str
    threshold: float
    columns: list[str]
    n_rows: int
    n_missing: int
    n_outliers: int
    n_dropped: int  # always 0 in flag mode


def outlier_mask(
    df: pd.DataFrame,
    columns: list[str],
    method: str = "iqr",
    threshold: float | None = None,
) -> pd.Series:
    """Boolean Series: True where a row is an outlier in any of the given columns.

    Rows with NaN in a column are never outliers in that column (missing
    values are reported separately by :func:`clean`).
    """
    if method not in DEFAULT_THRESHOLDS:
        raise DatakitError(f"unknown method {method!r}: expected iqr or zscore")
    if threshold is None:
        threshold = DEFAULT_THRESHOLDS[method]
    if threshold <= 0:
        raise DatakitError("threshold must be positive")

    mask = pd.Series(False, index=df.index)
    for col in columns:
        values = df[col]
        if method == "iqr":
            q1, q3 = values.quantile(0.25), values.quantile(0.75)
            spread = q3 - q1
            mask |= (values < q1 - threshold * spread) | (values > q3 + threshold * spread)
        else:
            std = values.std()
            if not std or pd.isna(std):
                continue  # constant column: z-scores are undefined, nothing to flag
            mask |= ((values - values.mean()) / std).abs() > threshold
    return mask


def clean(
    df: pd.DataFrame,
    method: str = "iqr",
    threshold: float | None = None,
    mode: str = "drop",
    columns: list[str] | None = None,
) -> tuple[pd.DataFrame, CleanReport]:
    """Drop or flag rows with missing values or outliers in the given columns.

    In ``drop`` mode offending rows are removed; in ``flag`` mode all rows are
    kept and boolean ``_missing`` / ``_outlier`` columns are appended. A row
    counts as missing if any selected column is NaN; outliers are counted only
    among rows with no missing values, so the two counts never overlap.
    """
    if mode not in ("drop", "flag"):
        raise DatakitError(f"unknown mode {mode!r}: expected drop or flag")
    if method not in DEFAULT_THRESHOLDS:
        raise DatakitError(f"unknown method {method!r}: expected iqr or zscore")
    if threshold is None:
        threshold = DEFAULT_THRESHOLDS[method]

    cols = numeric_columns(df, columns)
    missing = df[cols].isna().any(axis=1)
    outliers = outlier_mask(df, cols, method=method, threshold=threshold) & ~missing
    bad = missing | outliers

    if mode == "drop":
        result = df.loc[~bad].reset_index(drop=True)
        n_dropped = int(bad.sum())
    else:
        result = df.copy()
        result["_missing"] = missing
        result["_outlier"] = outliers
        n_dropped = 0

    report = CleanReport(
        method=method,
        threshold=float(threshold),
        columns=cols,
        n_rows=len(df),
        n_missing=int(missing.sum()),
        n_outliers=int(outliers.sum()),
        n_dropped=n_dropped,
    )
    return result, report
