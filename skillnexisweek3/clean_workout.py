"""
Week 3 assignment - clean the messy workout dataset (data.csv) with Pandas.

Problems found in the raw file:
  * Date: wrapped in quotes, one row in a different format (20201226), one row missing
  * Calories: 2 missing values
  * 1 duplicate row (2020/12/12)
  * Duration: one outlier (450 minutes - a typo for 45)
  * Pulse > Maxpulse in one row (the two values were swapped)

Usage:  python clean_workout.py data.csv out_folder
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

src = sys.argv[1] if len(sys.argv) > 1 else "data.csv"
out_dir = Path(sys.argv[2] if len(sys.argv) > 2 else ".")
out_dir.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(src)
raw = df.copy()
log = []

# ------------------------------------------------------------ 1. Dates
# Remove the quotes and slashes so every format becomes YYYYMMDD, then parse once.
digits = df["Date"].astype("string").str.replace(r"[^0-9]", "", regex=True)
df["Date"] = pd.to_datetime(digits, format="%Y%m%d", errors="coerce")
log.append(f"Dates: standardised all formats to YYYY-MM-DD ({int((digits == '20201226').sum())} row had format 20201226)")

# ------------------------------------------------------------ 2. Duplicates
n = df.duplicated().sum()
df = df.drop_duplicates().reset_index(drop=True)
log.append(f"Duplicates: removed {n} duplicate row(s)")

# ------------------------------------------------------------ 3. Missing values
# Date: the log is one session per day, so a missing date is the previous day + 1.
n = df["Date"].isna().sum()
df["Date"] = df["Date"].fillna(df["Date"].shift(1) + pd.Timedelta(days=1))
log.append(f"Date: filled {n} missing date(s) using the previous day + 1")

# Calories: fill with the average for sessions of the same length (45 vs 60 min).
n = df["Calories"].isna().sum()
# (the Duration typo is fixed first, below, so it does not skew these averages)
bad = df["Duration"] > 180
df.loc[bad, "Duration"] = df.loc[bad, "Duration"] / 10
log.append(f"Duration: corrected {int(bad.sum())} impossible value(s) (450 -> 45, a typo; calories 253.3 match other 45-min sessions)")
df["Calories"] = df["Calories"].fillna(df.groupby("Duration")["Calories"].transform("mean")).round(1)
log.append(f"Calories: filled {n} missing value(s) with the mean of sessions of the same duration")

# ------------------------------------------------------------ 4. Fix / filter rows
# Pulse can never exceed Maxpulse - swap the values where that happens.
swap = df["Pulse"] > df["Maxpulse"]
df.loc[swap, ["Pulse", "Maxpulse"]] = df.loc[swap, ["Maxpulse", "Pulse"]].values
log.append(f"Pulse/Maxpulse: swapped {int(swap.sum())} row(s) where Pulse > Maxpulse")

# ------------------------------------------------------------ 5. New columns
df["Weekday"] = df["Date"].dt.day_name()
df["Week"] = df["Date"].dt.isocalendar().week.astype(int)
df["Cal_per_min"] = (df["Calories"] / df["Duration"]).round(2)
df["Pulse_range"] = df["Maxpulse"] - df["Pulse"]
df["Intensity"] = pd.cut(df["Cal_per_min"], bins=[0, 5, 6.5, np.inf],
                         labels=["Low", "Medium", "High"])
df["Is_weekend"] = df["Date"].dt.dayofweek >= 5

# Filtering demo: the hardest sessions (high calorie burn per minute)
high = df[(df["Intensity"] == "High")]
log.append(f"Filter: {len(high)} high-intensity sessions (> 6.5 cal/min)")

# ------------------------------------------------------------ Save + report
df.to_csv(out_dir / "data_cleaned.csv", index=False)
high.to_csv(out_dir / "high_intensity_sessions.csv", index=False)

print(f"Raw: {raw.shape[0]} rows | Cleaned: {df.shape[0]} rows x {df.shape[1]} columns")
print("Missing values left:", int(df.isna().sum().sum()), "\n")
print("What was done:")
for line in log:
    print(" -", line)
print("\n", df.head(8).to_string(), "\n")

# ------------------------------------------------------------ 6. Charts
sns.set_theme(style="whitegrid", rc={"grid.color": "#e6e6e6", "axes.edgecolor": "#bbbbbb"})
ink, accent = "#2b2b2b", "#2f6fdb"
fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 4.4))

sns.lineplot(data=df, x="Date", y="Calories", color=accent, linewidth=2, marker="o", markersize=5, ax=a1)
a1.set_title("Calories burned per session, Dec 2020", loc="left", color=ink, fontsize=12)
a1.set_xlabel(""); a1.set_ylabel("Calories")
a1.tick_params(axis="x", rotation=40)

sns.scatterplot(data=df, x="Pulse", y="Calories", color=accent, s=50, edgecolor="white", linewidth=1, ax=a2)
a2.set_title("Higher average pulse, more calories", loc="left", color=ink, fontsize=12)
a2.set_xlabel("Average pulse (bpm)"); a2.set_ylabel("Calories")

sns.despine()
plt.tight_layout()
plt.savefig(out_dir / "workout_charts.png", dpi=140)
print("Saved data_cleaned.csv, high_intensity_sessions.csv, workout_charts.png in", out_dir)
