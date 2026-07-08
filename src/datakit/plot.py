"""Scatter/line plots saved to PNG, with an optional fitted-curve overlay."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # datakit only writes files; must be set before pyplot loads

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from datakit.fit import FitResult  # noqa: E402
from datakit.io import DatakitError, numeric_series  # noqa: E402

# Colors from a CVD-validated categorical palette; chrome stays recessive so
# the data marks carry the figure.
DATA_COLOR = "#2a78d6"
FIT_COLOR = "#e34948"
GRID_COLOR = "#e1e0d9"
AXIS_COLOR = "#c3c2b7"
INK = "#0b0b0b"
MUTED = "#898781"


def make_plot(
    df: pd.DataFrame,
    x: str,
    y: str,
    out_path: str | Path,
    kind: str = "scatter",
    fit_result: FitResult | None = None,
    title: str | None = None,
) -> Path:
    """Plot y against x and save a PNG; returns the output path."""
    if kind not in ("scatter", "line"):
        raise DatakitError(f"unknown plot kind {kind!r}: expected scatter or line")
    xs = numeric_series(df, x).to_numpy()
    ys = numeric_series(df, y).to_numpy()
    mask = ~(np.isnan(xs) | np.isnan(ys))
    xs, ys = xs[mask], ys[mask]
    if xs.size == 0:
        raise DatakitError(f"no rows with numeric values in both {x!r} and {y!r}")

    fig, ax = plt.subplots(figsize=(8, 5), dpi=150)
    if kind == "line":
        order = np.argsort(xs, kind="stable")
        ax.plot(xs[order], ys[order], color=DATA_COLOR, linewidth=2, label=y)
    else:
        ax.scatter(xs, ys, s=24, color=DATA_COLOR, alpha=0.85, edgecolors="none", label=y)

    if fit_result is not None:
        grid = np.linspace(xs.min(), xs.max(), 200)
        ax.plot(
            grid,
            fit_result.predict(grid),
            color=FIT_COLOR,
            linewidth=2,
            label=f"{fit_result.equation}  ($R^2$ = {fit_result.r_squared:.4f})",
        )
        # Two series on the axes now, so identity needs a legend; a lone
        # series is already named by the axis labels.
        ax.legend(frameon=False, labelcolor=INK)

    ax.set_xlabel(x, color=INK)
    ax.set_ylabel(y, color=INK)
    if title:
        ax.set_title(title, color=INK)
    ax.grid(True, color=GRID_COLOR, linewidth=0.8)
    ax.set_axisbelow(True)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    for spine in ("left", "bottom"):
        ax.spines[spine].set_color(AXIS_COLOR)
    ax.tick_params(colors=MUTED)

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(out_path, facecolor="white")
    plt.close(fig)
    return out_path
