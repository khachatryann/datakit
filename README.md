# datakit

[![CI](https://github.com/khachatryann/datakit/actions/workflows/ci.yml/badge.svg)](https://github.com/khachatryann/datakit/actions/workflows/ci.yml)

A Python command-line tool for quick analysis of CSV measurement data, aimed at
engineers and students: summary statistics, least-squares curve fitting, plots,
and dataset cleaning — with numpy, pandas, and matplotlib doing the heavy lifting.

## Install

Requires Python 3.10+.

```console
pip install git+https://github.com/khachatryann/datakit
```

Or from a clone:

```console
git clone https://github.com/khachatryann/datakit
cd datakit
pip install .
```

## Quickstart

The repository ships a sample dataset in [`examples/sensor_data.csv`](examples/sensor_data.csv).

```console
# Summary statistics for every numeric column, optionally per sensor
datakit stats examples/sensor_data.csv
datakit stats examples/sensor_data.csv --columns temperature_c --group-by sensor

# Least-squares fit: linear, poly:N, or exp — prints coefficients and R^2
datakit fit examples/sensor_data.csv -x temperature_c -y voltage_v --model linear

# Scatter or line plot saved to PNG, with an optional fitted-curve overlay
datakit plot examples/sensor_data.csv -x temperature_c -y voltage_v --fit linear

# Drop (or just flag) rows with missing values and outliers, write a cleaned CSV
datakit clean examples/sensor_data.csv --method iqr --mode drop
```

See [`docs/usage.md`](docs/usage.md) for every flag, and
[`examples/README.md`](examples/README.md) for a walkthrough on the sample data.

## Subcommands at a glance

| Command | What it does |
|---|---|
| `datakit stats <file>` | count, mean, std, min, quartiles, max per numeric column; `--group-by` splits by a category column |
| `datakit fit <file> -x COL -y COL` | least-squares fit (`linear`, `poly:N`, `exp`), prints coefficients and R² |
| `datakit plot <file> -x COL -y COL` | scatter/line plot to PNG; `--fit MODEL` overlays the fitted curve |
| `datakit clean <file>` | drop or flag rows with missing values and outliers (IQR or z-score) |

## Development

```console
pip install -e ".[dev]"
pytest        # run the test suite
ruff check .  # lint
```

The code layout keeps the CLI thin: `src/datakit/cli.py` only parses arguments
and dispatches to `stats.py`, `fit.py`, `plot.py`, and `clean.py`, which are
plain functions over pandas DataFrames and are tested directly.

## License

[MIT](LICENSE) © 2026 Anton Khachatryan
