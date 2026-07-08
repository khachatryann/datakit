"""Least-squares curve fitting: linear, polynomial, and exponential models."""

from __future__ import annotations

import math
from collections.abc import Callable
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from datakit.io import DatakitError, numeric_series

MODELS_HELP = "linear, poly:N (polynomial of degree N), exp (y = a*exp(b*x))"


@dataclass
class FitResult:
    model: str
    coefficients: dict[str, float]
    r_squared: float
    equation: str
    predict: Callable[[np.ndarray], np.ndarray]
    n_points: int
    warnings: list[str] = field(default_factory=list)


def parse_model(spec: str) -> tuple[str, int]:
    """Parse a --model spec into (kind, degree); kind is 'poly' or 'exp'."""
    spec = spec.strip().lower()
    if spec == "linear":
        return "poly", 1
    if spec == "exp":
        return "exp", 0
    if spec.startswith("poly:"):
        raw = spec.split(":", 1)[1]
        try:
            degree = int(raw)
        except ValueError:
            degree = -1
        if degree < 1:
            raise DatakitError(f"invalid polynomial degree {raw!r}: expected poly:N with N >= 1")
        return "poly", degree
    raise DatakitError(f"unknown model {spec!r}: expected one of {MODELS_HELP}")


def fit(df: pd.DataFrame, x: str, y: str, model: str = "linear") -> FitResult:
    kind, degree = parse_model(model)
    xs = numeric_series(df, x).to_numpy()
    ys = numeric_series(df, y).to_numpy()

    warnings: list[str] = []
    mask = ~(np.isnan(xs) | np.isnan(ys))
    dropped = int((~mask).sum())
    if dropped:
        warnings.append(f"ignored {dropped} row(s) with missing {x} or {y}")
    xs, ys = xs[mask], ys[mask]

    if kind == "exp":
        return _fit_exp(xs, ys, model, warnings)
    return _fit_poly(xs, ys, degree, model, warnings)


def _fit_poly(
    xs: np.ndarray, ys: np.ndarray, degree: int, model: str, warnings: list[str]
) -> FitResult:
    if len(xs) < degree + 1:
        raise DatakitError(
            f"need at least {degree + 1} data points for a degree-{degree} fit, got {len(xs)}"
        )
    if len(np.unique(xs)) < degree + 1:
        raise DatakitError(
            f"need at least {degree + 1} distinct x values for a degree-{degree} fit"
        )
    coeffs = np.polyfit(xs, ys, degree)

    def predict(values):
        return np.polyval(coeffs, np.asarray(values, dtype=float))

    if degree == 1:
        named = {"slope": float(coeffs[0]), "intercept": float(coeffs[1])}
    else:
        named = {f"c{degree - i}": float(c) for i, c in enumerate(coeffs)}
    return FitResult(
        model=model,
        coefficients=named,
        r_squared=_r_squared(ys, predict(xs)),
        equation=_poly_equation(coeffs),
        predict=predict,
        n_points=len(xs),
        warnings=warnings,
    )


def _fit_exp(xs: np.ndarray, ys: np.ndarray, model: str, warnings: list[str]) -> FitResult:
    positive = ys > 0
    dropped = int((~positive).sum())
    if dropped:
        warnings.append(f"exp model requires y > 0: ignored {dropped} non-positive row(s)")
    xs, ys = xs[positive], ys[positive]
    if len(xs) < 2 or len(np.unique(xs)) < 2:
        raise DatakitError("need at least 2 data points with distinct x and y > 0 for an exp fit")

    # Log-linearize: ln(y) = ln(a) + b*x, then fit a line.
    b, log_a = np.polyfit(xs, np.log(ys), 1)
    a, b = float(np.exp(log_a)), float(b)

    def predict(values):
        return a * np.exp(b * np.asarray(values, dtype=float))

    return FitResult(
        model=model,
        coefficients={"a": a, "b": b},
        r_squared=_r_squared(ys, predict(xs)),
        equation=f"y = {a:.6g}*exp({b:.6g}*x)",
        predict=predict,
        n_points=len(xs),
        warnings=warnings,
    )


def _r_squared(y: np.ndarray, y_hat: np.ndarray) -> float:
    ss_res = float(np.sum((y - y_hat) ** 2))
    ss_tot = float(np.sum((y - np.mean(y)) ** 2))
    if ss_tot == 0.0:
        return 1.0 if math.isclose(ss_res, 0.0, abs_tol=1e-12) else 0.0
    return 1.0 - ss_res / ss_tot


def _poly_equation(coeffs: np.ndarray) -> str:
    degree = len(coeffs) - 1
    terms = []
    for i, c in enumerate(coeffs):
        power = degree - i
        if power == 0:
            terms.append(f"{c:.6g}")
        elif power == 1:
            terms.append(f"{c:.6g}*x")
        else:
            terms.append(f"{c:.6g}*x^{power}")
    equation = terms[0]
    for term in terms[1:]:
        equation += f" - {term[1:]}" if term.startswith("-") else f" + {term}"
    return "y = " + equation
