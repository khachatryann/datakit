"""Summary statistics for numeric columns, with optional group-by."""

from __future__ import annotations

import pandas as pd

from datakit.io import DatakitError, numeric_columns


def summary_stats(
    df: pd.DataFrame,
    columns: list[str] | None = None,
    group_by: str | None = None,
) -> pd.DataFrame:
    """Return count, mean, std, min, quartiles, and max per numeric column.

    Without ``group_by`` the result has one row per column. With ``group_by``
    the result has a (group value, column) MultiIndex.
    """
    cols = numeric_columns(df, columns)
    if group_by is None:
        return df[cols].describe().T

    if group_by not in df.columns:
        raise DatakitError(
            f"group-by column not found: {group_by} (available: {', '.join(df.columns)})"
        )
    cols = [c for c in cols if c != group_by]
    if not cols:
        raise DatakitError("no numeric columns left to summarize besides the group-by column")
    parts = {
        key: sub[cols].describe().T for key, sub in df.groupby(group_by, sort=True, dropna=False)
    }
    return pd.concat(parts, names=[group_by, "column"])
