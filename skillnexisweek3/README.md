# Week 3 Assignment: Cleaning a Messy Dataset with Pandas

Data Analyst Course, Week 3 (Python & Data Wrangling).

The task: clean a messy dataset in Pandas by handling missing values, filtering rows and creating new columns.

## Dataset

`data.csv` is a workout log with 32 rows and 5 columns: `Duration`, `Date`, `Pulse`, `Maxpulse`, `Calories`.

## Problems found and how they were fixed

| Problem | Fix |
|---|---|
| Dates wrapped in quotes, one in a different format (`20201226`) | Standardized all dates to `YYYY-MM-DD` |
| 1 duplicate row (2020/12/12) | Removed |
| 1 missing date | Filled with the previous day + 1 (one session per day) |
| Duration of 450 minutes (outlier) | Corrected to 45, a likely typo (its calories match other 45-minute sessions) |
| 2 missing `Calories` values | Filled with the mean of sessions of the same duration |
| `Pulse` greater than `Maxpulse` in one row | Swapped the two values |

Result: 32 rows became 31 rows, with no missing values left.

## New columns

- `Weekday`: day name of the session
- `Week`: ISO week number
- `Cal_per_min`: calories burned per minute
- `Pulse_range`: `Maxpulse` minus `Pulse`
- `Intensity`: Low, Medium or High, based on `Cal_per_min`
- `Is_weekend`: True for Saturday and Sunday

## Files

- `clean_workout.py`: the cleaning script
- `data.csv`: the raw dataset
- `data_cleaned.csv`: the cleaned dataset
- `workout_charts.png`: calories per session over time, and calories vs. average pulse

## How to run

```bash
pip install pandas numpy matplotlib seaborn
python clean_workout.py data.csv .
```

The script prints a summary of what it changed and saves `data_cleaned.csv`, `high_intensity_sessions.csv` and `workout_charts.png` in the output folder (here, the current folder).
