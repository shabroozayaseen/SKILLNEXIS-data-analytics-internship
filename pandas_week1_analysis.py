from pathlib import Path

import pandas as pd


BASE_DIR = Path("/Users/suhailsayar/Documents/Codex/2026-10-12/remove-duplicates-and-handle-missing-values")
SOURCE_XLSX = Path("/Users/suhailsayar/Downloads/global_superstore_2016.xlsx")
OUTPUT_DIR = BASE_DIR / "outputs" / "pandas_week1"

SOURCE_CSV = OUTPUT_DIR / "global_superstore_orders.csv"
CLEANED_CSV = OUTPUT_DIR / "global_superstore_orders_cleaned.csv"
BASIC_INFO_TXT = OUTPUT_DIR / "basic_info.txt"
CATEGORY_REVENUE_CSV = OUTPUT_DIR / "category_revenue.csv"
SORTED_PREVIEW_CSV = OUTPUT_DIR / "sorted_data_preview.csv"
CORRELATION_MATRIX_CSV = OUTPUT_DIR / "correlation_matrix.csv"


def export_orders_sheet_to_csv() -> None:
    """Create a CSV source file from the Orders sheet for the Pandas task."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    orders = pd.read_excel(SOURCE_XLSX, sheet_name="Orders")
    orders.to_csv(SOURCE_CSV, index=False)


def load_csv() -> pd.DataFrame:
    """Load the CSV file using Pandas."""
    return pd.read_csv(SOURCE_CSV)


def save_basic_info(df: pd.DataFrame) -> None:
    """Save basic dataset information similar to df.info()."""
    missing_values = df.isna().sum()
    summary = [
        "Basic Dataset Information",
        "",
        f"Rows: {df.shape[0]}",
        f"Columns: {df.shape[1]}",
        "",
        "Column data types:",
        df.dtypes.to_string(),
        "",
        "Missing values by column:",
        missing_values[missing_values > 0].to_string() if (missing_values > 0).any() else "No missing values",
        "",
        "First five rows:",
        df.head().to_string(),
    ]
    BASIC_INFO_TXT.write_text("\n".join(summary), encoding="utf-8")
    print("\n".join(summary))


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Handle missing values and duplicates."""
    cleaned = df.drop_duplicates().copy()

    # Postal Code is an identifier, not a measurement. Keep missing postal codes
    # as N/A instead of filling them with a numeric statistic.
    cleaned["Postal Code"] = cleaned["Postal Code"].astype("string").fillna("N/A")

    date_columns = ["Order Date", "Ship Date"]
    for column in date_columns:
        cleaned[column] = pd.to_datetime(cleaned[column], errors="coerce")

    numeric_columns = cleaned.select_dtypes(include="number").columns
    text_columns = cleaned.select_dtypes(include="object").columns

    for column in numeric_columns:
        if cleaned[column].isna().any():
            cleaned[column] = cleaned[column].fillna(cleaned[column].median())

    for column in text_columns:
        if cleaned[column].isna().any():
            mode_value = cleaned[column].mode(dropna=True)
            cleaned[column] = cleaned[column].fillna(mode_value.iloc[0] if not mode_value.empty else "Unknown")

    return cleaned


def group_revenue_by_category(df: pd.DataFrame) -> pd.DataFrame:
    """Group data by Category and calculate total revenue."""
    return (
        df.groupby("Category", as_index=False)["Sales"]
        .sum()
        .rename(columns={"Sales": "Total Revenue"})
        .sort_values("Total Revenue", ascending=False)
    )


def sort_data(df: pd.DataFrame) -> pd.DataFrame:
    """Sort by multiple columns using Python."""
    return df.sort_values(
        by=["Category", "Sales", "Profit"],
        ascending=[True, False, False],
    )


def create_correlation_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Create a correlation matrix for numerical columns."""
    numeric_df = df.select_dtypes(include="number")
    return numeric_df.corr()


def main() -> None:
    export_orders_sheet_to_csv()

    df = load_csv()
    save_basic_info(df)

    cleaned = clean_data(df)
    category_revenue = group_revenue_by_category(cleaned)
    sorted_data = sort_data(cleaned)
    correlation_matrix = create_correlation_matrix(cleaned)

    cleaned.to_csv(CLEANED_CSV, index=False)
    category_revenue.to_csv(CATEGORY_REVENUE_CSV, index=False)
    sorted_data.head(100).to_csv(SORTED_PREVIEW_CSV, index=False)
    correlation_matrix.to_csv(CORRELATION_MATRIX_CSV)

    print("\nCleaning Summary")
    print(f"Original rows: {len(df)}")
    print(f"Rows after removing duplicates: {len(cleaned)}")
    print(f"Duplicate rows removed: {len(df) - len(cleaned)}")
    print(f"Missing values after cleaning: {cleaned.isna().sum().sum()}")

    print("\nCategory-wise Total Revenue")
    print(category_revenue.to_string(index=False))

    print("\nCorrelation Matrix")
    print(correlation_matrix.to_string())


if __name__ == "__main__":
    main()
