# datakit usage reference

All subcommands read a CSV file with a header row. Errors (missing file,
unknown column, invalid model) are printed to stderr and exit with status 1.
`datakit --version` prints the version.

## datakit stats

```
datakit stats <file> [--columns COL ...] [--group-by COL]
```

Prints count, mean, std, min, 25%/50%/75% percentiles, and max for each
numeric column. NaN values are excluded from all statistics.

| Flag | Meaning |
|---|---|
| `--columns COL ...` | restrict to these columns (must exist and be numeric) |
| `--group-by COL` | compute the statistics separately for each value of `COL` |

Example:

```console
datakit stats measurements.csv --columns temperature_c voltage_v --group-by sensor
```

## datakit fit

```
datakit fit <file> -x COL -y COL [--model MODEL]
```

Least-squares curve fitting. Prints the fitted equation, the named
coefficients, R², and the number of points used. Rows where either column is
missing are ignored (with a note on stderr).

| Model | Form | Notes |
|---|---|---|
| `linear` (default) | y = m·x + b | coefficients named `slope` and `intercept` |
| `poly:N` | degree-N polynomial | coefficients named `cN` … `c0`, highest power first |
| `exp` | y = a·e^(b·x) | fitted by log-linearization; rows with y ≤ 0 are ignored with a note |

Example:

```console
datakit fit measurements.csv -x time_min -y pressure_kpa --model exp
```

## datakit plot

```
datakit plot <file> -x COL -y COL [--kind scatter|line] [--fit MODEL]
                    [--out PNG] [--title TITLE]
```

Saves a PNG plot of `y` against `x`. Rows with a missing value in either
column are skipped; line plots are drawn in x-sorted order.

| Flag | Meaning |
|---|---|
| `--kind` | `scatter` (default) or `line` |
| `--fit MODEL` | overlay a fitted curve (same model syntax as `datakit fit`); the legend shows the equation and R² |
| `--out PNG` | output path; default is `<file>_<y>_vs_<x>.png` next to the input |
| `--title TITLE` | plot title |

Example:

```console
datakit plot measurements.csv -x temperature_c -y voltage_v --fit linear --out volt.png
```

## datakit clean

```
datakit clean <file> [--method iqr|zscore] [--threshold T] [--mode drop|flag]
                     [--columns COL ...] [--out CSV]
```

Finds rows with missing values or outliers in the selected numeric columns
(default: all numeric columns) and writes a new CSV. Prints a report of what
was found.

| Flag | Meaning |
|---|---|
| `--method` | `iqr` (default): outlier if outside [Q1 − T·IQR, Q3 + T·IQR]; `zscore`: outlier if \|z\| > T |
| `--threshold T` | cutoff; defaults to 1.5 for `iqr` and 3.0 for `zscore` |
| `--mode` | `drop` (default) removes offending rows; `flag` keeps every row and appends boolean `_missing` and `_outlier` columns |
| `--columns COL ...` | columns to check (must be numeric) |
| `--out CSV` | output path; default is `<file>_clean.csv` next to the input |

A row counts as *missing* if any selected column is NaN. Outliers are counted
only among rows without missing values, so the two counts never overlap.
Constant columns produce no z-score outliers.

Example:

```console
datakit clean measurements.csv --method zscore --threshold 2.5 --mode flag
```
