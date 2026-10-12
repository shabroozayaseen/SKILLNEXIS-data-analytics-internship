"""
Week 3 assignment: clean a messy dataset in Pandas.
  1. handle missing values   2. filter rows   3. create new columns

Usage:  python clean_data.py data.csv            -> writes data_cleaned.csv
The script inspects the columns itself, so it works on any messy CSV.
"""
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

path = sys.argv[1] if len(sys.argv) > 1 else "data.csv"
df = pd.read_csv(path)
print(f"Loaded {path}: {df.shape[0]} rows x {df.shape[1]} columns\n")

# ---------------------------------------------------------------- 0. Inspect
print("=== BEFORE ===")
df.info()
print("\nMissing values per column:\n", df.isna().sum(), "\n")
print("Duplicate rows:", df.duplicated().sum(), "\n")

# ------------------------------------------------------------ 1. Tidy basics
# Consistent column names: lower case, underscores
df.columns = (df.columns.str.strip().str.lower()
              .str.replace(r"[^0-9a-z]+", "_", regex=True).str.strip("_"))

# Trim whitespace in text columns and turn placeholder strings into real NaN
placeholders = ["", "na", "n/a", "nan", "null", "none", "-", "--", "?", "missing", "unknown"]
def is_text(s):
    return not (pd.api.types.is_numeric_dtype(s) or pd.api.types.is_datetime64_any_dtype(s))

text_cols = [c for c in df.columns if is_text(df[c])]
for c in text_cols:
    df[c] = df[c].astype("string").str.strip()
    df[c] = df[c].mask(df[c].str.lower().isin(placeholders), pd.NA)

# Convert columns that are really numbers (e.g. "$1,200", "45 ") or dates
for c in text_cols:
    cleaned = df[c].str.replace(r"[,$€₹%\s]", "", regex=True)
    as_num = pd.to_numeric(cleaned, errors="coerce")
    if as_num.notna().sum() >= 0.8 * df[c].notna().sum() and df[c].notna().any():
        df[c] = as_num
        continue
    if any(k in c for k in ("date", "time", "day", "joined", "created", "dob")):
        as_date = pd.to_datetime(df[c], errors="coerce")
        if as_date.notna().sum() >= 0.8 * df[c].notna().sum():
            df[c] = as_date

# Consistent text casing for categories (e.g. "delhi", "DELHI", " Delhi")
for c in [c for c in df.columns if is_text(df[c])]:
    df[c] = df[c].astype("string").str.title()

# Duplicates
df = df.drop_duplicates()

# ------------------------------------------------------ 2. Missing values
num_cols = df.select_dtypes(include="number").columns
cat_cols = [c for c in df.columns if is_text(df[c])]
date_cols = df.select_dtypes(include="datetime").columns

# Drop rows that are mostly empty (fewer than half of the columns filled)
df = df.dropna(thresh=int(np.ceil(df.shape[1] / 2)))

for c in num_cols:                      # numbers  -> median (robust to outliers)
    df[c] = df[c].fillna(df[c].median())
for c in cat_cols:                      # text     -> most common value, else "Unknown"
    mode = df[c].mode(dropna=True)
    df[c] = df[c].fillna(mode.iloc[0] if len(mode) else "Unknown")
for c in date_cols:                     # dates    -> forward fill, then back fill
    df[c] = df[c].ffill().bfill()

# ------------------------------------------------------------ 3. Filter rows
# Remove impossible negative values in columns that should not be negative
for c in num_cols:
    if any(k in c for k in ("age", "price", "salary", "amount", "quantity", "qty", "sales", "income")):
        df = df[df[c] >= 0]

# Remove extreme outliers with the IQR rule (only on columns with real spread)
for c in num_cols:
    q1, q3 = df[c].quantile([0.25, 0.75])
    iqr = q3 - q1
    if iqr > 0:
        df = df[df[c].between(q1 - 3 * iqr, q3 + 3 * iqr)]

# ------------------------------------------------------ 4. New columns
for c in date_cols:
    df[f"{c}_year"] = df[c].dt.year
    df[f"{c}_month"] = df[c].dt.month
    df[f"{c}_weekday"] = df[c].dt.day_name()

for c in num_cols:
    if df[c].nunique() > 4:
        # Low / Medium / High band based on quartiles
        df[f"{c}_band"] = pd.qcut(df[c], q=3, labels=["Low", "Medium", "High"], duplicates="drop")
        # Standardised score (how many std-devs from the mean)
        std = df[c].std()
        df[f"{c}_zscore"] = ((df[c] - df[c].mean()) / std).round(2) if std else 0.0

df = df.reset_index(drop=True)

# ---------------------------------------------------------------- Report
print("\n=== AFTER ===")
print(f"{df.shape[0]} rows x {df.shape[1]} columns")
print("Missing values left:", int(df.isna().sum().sum()))
print(df.head(10).to_string())

out = path.rsplit(".", 1)[0] + "_cleaned.csv"
df.to_csv(out, index=False)
print(f"\nSaved {out}")

# ------------------------------------- 5. Quick visuals (Matplotlib + Seaborn)
sns.set_theme(style="whitegrid")
base_num = [c for c in num_cols if c in df.columns][:4]
if base_num:
    fig, axes = plt.subplots(1, len(base_num), figsize=(4.5 * len(base_num), 3.8))
    axes = np.atleast_1d(axes)
    for ax, c in zip(axes, base_num):
        sns.histplot(df[c], kde=True, ax=ax)
        ax.set_title(f"Distribution of {c}")
    plt.tight_layout()
    plt.savefig("distributions.png", dpi=130)
    plt.close()
    print("Saved distributions.png")
