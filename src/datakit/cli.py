"""Command-line interface: a thin argparse layer over the datakit modules."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

from datakit import __version__
from datakit.clean import clean
from datakit.fit import MODELS_HELP, fit
from datakit.io import DatakitError, load_csv
from datakit.plot import make_plot
from datakit.stats import summary_stats


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="datakit", description="Quick analysis of CSV measurement data."
    )
    parser.add_argument("--version", action="version", version=f"datakit {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    p_stats = sub.add_parser("stats", help="summary statistics per numeric column")
    p_stats.add_argument("file", help="input CSV file")
    p_stats.add_argument(
        "--columns", nargs="+", metavar="COL", help="columns to summarize (default: all numeric)"
    )
    p_stats.add_argument("--group-by", metavar="COL", help="split statistics by this column")
    p_stats.set_defaults(func=cmd_stats)

    p_fit = sub.add_parser("fit", help="least-squares curve fitting")
    p_fit.add_argument("file", help="input CSV file")
    p_fit.add_argument("-x", required=True, metavar="COL", help="independent variable column")
    p_fit.add_argument("-y", required=True, metavar="COL", help="dependent variable column")
    p_fit.add_argument("--model", default="linear", help=f"one of: {MODELS_HELP} (default: linear)")
    p_fit.set_defaults(func=cmd_fit)

    p_plot = sub.add_parser("plot", help="scatter/line plot saved to PNG")
    p_plot.add_argument("file", help="input CSV file")
    p_plot.add_argument("-x", required=True, metavar="COL", help="x-axis column")
    p_plot.add_argument("-y", required=True, metavar="COL", help="y-axis column")
    p_plot.add_argument("--kind", choices=["scatter", "line"], default="scatter")
    p_plot.add_argument("--fit", metavar="MODEL", help=f"overlay a fitted curve: {MODELS_HELP}")
    p_plot.add_argument(
        "--out", metavar="PNG", help="output path (default: <file>_<y>_vs_<x>.png)"
    )
    p_plot.add_argument("--title", help="plot title")
    p_plot.set_defaults(func=cmd_plot)

    p_clean = sub.add_parser("clean", help="drop or flag rows with missing values and outliers")
    p_clean.add_argument("file", help="input CSV file")
    p_clean.add_argument("--method", choices=["iqr", "zscore"], default="iqr")
    p_clean.add_argument(
        "--threshold", type=float, help="outlier cutoff (default: 1.5 for iqr, 3.0 for zscore)"
    )
    p_clean.add_argument(
        "--mode",
        choices=["drop", "flag"],
        default="drop",
        help="drop offending rows, or keep them and add _missing/_outlier columns",
    )
    p_clean.add_argument(
        "--columns", nargs="+", metavar="COL", help="columns to check (default: all numeric)"
    )
    p_clean.add_argument("--out", metavar="CSV", help="output path (default: <file>_clean.csv)")
    p_clean.set_defaults(func=cmd_clean)

    return parser


def cmd_stats(args: argparse.Namespace) -> int:
    df = load_csv(args.file)
    table = summary_stats(df, columns=args.columns, group_by=args.group_by)
    with pd.option_context("display.float_format", lambda v: f"{v:.6g}"):
        print(table.to_string())
    return 0


def cmd_fit(args: argparse.Namespace) -> int:
    df = load_csv(args.file)
    result = fit(df, x=args.x, y=args.y, model=args.model)
    print(f"model:    {result.model}")
    print(f"equation: {result.equation}")
    for name, value in result.coefficients.items():
        print(f"  {name} = {value:.6g}")
    print(f"R^2:      {result.r_squared:.6f}")
    print(f"points:   {result.n_points}")
    for note in result.warnings:
        print(f"note: {note}", file=sys.stderr)
    return 0


def cmd_plot(args: argparse.Namespace) -> int:
    df = load_csv(args.file)
    fit_result = fit(df, x=args.x, y=args.y, model=args.fit) if args.fit else None
    out = (
        Path(args.out)
        if args.out
        else Path(args.file).with_name(f"{Path(args.file).stem}_{args.y}_vs_{args.x}.png")
    )
    path = make_plot(
        df, x=args.x, y=args.y, out_path=out, kind=args.kind, fit_result=fit_result,
        title=args.title,
    )
    if fit_result is not None:
        for note in fit_result.warnings:
            print(f"note: {note}", file=sys.stderr)
    print(f"wrote {path}")
    return 0


def cmd_clean(args: argparse.Namespace) -> int:
    df = load_csv(args.file)
    result, report = clean(
        df, method=args.method, threshold=args.threshold, mode=args.mode, columns=args.columns
    )
    out = (
        Path(args.out)
        if args.out
        else Path(args.file).with_name(f"{Path(args.file).stem}_clean.csv")
    )
    result.to_csv(out, index=False)
    print(f"checked {report.n_rows} rows across columns: {', '.join(report.columns)}")
    print(f"method: {report.method} (threshold {report.threshold:g})")
    print(f"rows with missing values: {report.n_missing}")
    print(f"outlier rows: {report.n_outliers}")
    if args.mode == "drop":
        print(f"dropped {report.n_dropped} rows; kept {len(result)}")
    else:
        print("flag mode: added _missing and _outlier columns; kept all rows")
    print(f"wrote {out}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except DatakitError as exc:
        print(f"datakit: error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
