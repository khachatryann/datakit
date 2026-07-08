# Example: sensor_data.csv

A synthetic but realistic bench log: two sensors (A and B) sampled every 30
seconds for 30 minutes.

| Column | Meaning |
|---|---|
| `time_min` | elapsed time in minutes |
| `sensor` | which sensor took the reading (`A` or `B`) |
| `temperature_c` | temperature in °C — rises over time; sensor B reads ~1.5 °C hotter |
| `voltage_v` | thermocouple output, roughly linear in temperature |
| `pressure_kpa` | chamber pressure, growing exponentially with time |

The file deliberately contains **two missing values** and **two outliers**
(a stuck-sensor temperature spike and a voltage dropout), so every subcommand
has something to find. Run these from the repository root:

```console
# Per-sensor summary of the temperature channel
datakit stats examples/sensor_data.csv --columns temperature_c --group-by sensor

# Voltage is linear in temperature — fit it and check R^2
datakit fit examples/sensor_data.csv -x temperature_c -y voltage_v --model linear

# Pressure grows exponentially with time
datakit fit examples/sensor_data.csv -x time_min -y pressure_kpa --model exp

# Plot voltage vs temperature with the fitted line overlaid
datakit plot examples/sensor_data.csv -x temperature_c -y voltage_v --fit linear

# See what clean would remove (flag mode keeps all rows)...
datakit clean examples/sensor_data.csv --mode flag --out /tmp/flagged.csv

# ...then actually drop the bad rows
datakit clean examples/sensor_data.csv --mode drop
```

Tip: run `clean` first and point `fit`/`plot` at the cleaned file to see how
much the outliers were distorting the fit.
