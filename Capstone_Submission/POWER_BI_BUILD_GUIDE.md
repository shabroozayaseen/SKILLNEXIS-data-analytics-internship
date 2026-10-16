# Power BI Dashboard — Build Guide (≈20–30 minutes)

A `.pbix` file can only be created inside **Power BI Desktop**, so it could not be generated automatically.
Everything else is prepared: the cleaned data (`financial_sample_clean.csv`), every DAX measure, the exact visuals
and a layout. Follow these steps, then **File → Save as → `Capstone_Dashboard.pbix`** and submit that file.

> Prefer Tableau? The same visuals work; the DAX measures map to Tableau calculated fields (see the bottom).

---

## 1. Load the data
1. Open Power BI Desktop → **Home → Get data → Text/CSV** → choose `financial_sample_clean.csv` → **Transform Data**.
2. In Power Query, check the column types:
   | Column | Type |
   |---|---|
   | Segment, Country, Product, Discount Band, Month Name | Text |
   | Units Sold, Manufacturing Price, Sale Price, Gross Sales, Discounts, Sales, COGS, Profit | Decimal number |
   | Month Number, Year | Whole number |
   | Date | Date |
   | Profit Margin %, Discount % | Decimal number |
3. Rename the query from `financial_sample_clean` to **`Orders`**.
4. **Close & Apply**.

> "None" in *Discount Band* is a real category. If it ever shows as blank, re-check the column is Text and that
> no "replace values" step turned it into null.

## 2. Sorting columns (so charts read in order)
- Select **Month Name** → *Column tools → Sort by column* → **Month Number**.
- Create a calculated column for the band order, then sort *Discount Band* by it:
  ```DAX
  Band Order = SWITCH ( Orders[Discount Band], "None", 1, "Low", 2, "Medium", 3, "High", 4 )
  ```
  Select **Discount Band** → *Sort by column* → **Band Order**.
- Optional month label that sorts chronologically:
  ```DAX
  Month Label = FORMAT ( Orders[Date], "mmm yy" )
  ```
  Sort *Month Label* by **Date**.

## 3. DAX measures (Home → New measure)
```DAX
Total Sales        = SUM ( Orders[Sales] )
Total Profit       = SUM ( Orders[Profit] )
Total Units        = SUM ( Orders[Units Sold] )
Total Discounts    = SUM ( Orders[Discounts] )
Gross Sales Total  = SUM ( Orders[Gross Sales] )

Profit Margin %    = DIVIDE ( [Total Profit], [Total Sales] )
Discount Rate %    = DIVIDE ( [Total Discounts], [Gross Sales Total] )
Avg Order Sales    = DIVIDE ( [Total Sales], COUNTROWS ( Orders ) )

Loss-Making Orders = CALCULATE ( COUNTROWS ( Orders ), Orders[Profit] < 0 )
Loss Amount        = CALCULATE ( [Total Profit], Orders[Profit] < 0 )

Sales Share %      = DIVIDE ( [Total Sales],  CALCULATE ( [Total Sales],  ALLSELECTED ( Orders ) ) )
Profit Share %     = DIVIDE ( [Total Profit], CALCULATE ( [Total Profit], ALLSELECTED ( Orders ) ) )

Margin Colour =
    SWITCH ( TRUE (),
        [Profit Margin %] < 0,    "#C0392B",
        [Profit Margin %] < 0.12, "#DD8452",
        "#2A9D8F" )
```
Format: Sales/Profit/Discounts → **Currency, 0 decimals**; the % measures → **Percentage, 1 decimal**.

## 4. Report page layout — "Sales & Profit Overview"
Canvas 16:9. Use one palette: blue `#2B6CB0` for sales, teal `#2A9D8F` for good profit, red `#C0392B` for losses.

| # | Visual | Fields | Notes |
|---|---|---|---|
| 1 | **Title text box** | "Sales & Profit Overview — Sep 2013 to Dec 2014" | top-left |
| 2–6 | **Five Cards** (top row) | `Total Sales`, `Total Profit`, `Profit Margin %`, `Discount Rate %`, `Loss-Making Orders` | rename titles; make Loss-Making Orders red |
| 7 | **Slicers** (left or top) | `Year`, `Segment`, `Country`, `Product` | Year as buttons; others as dropdown |
| 8 | **Clustered bar chart** | Y: `Segment`; X: `Total Sales`, `Total Profit` | title: "Government drives sales and profit; Enterprise loses money" |
| 9 | **Column chart** | X: `Discount Band` (sorted); Y: `Profit Margin %` | conditional colour by `Margin Colour` (fx → Field value); title: "Deeper discounts cut margin" |
| 10 | **Line / column chart** | X: `Month Label` (or Date hierarchy by month); Y: `Total Sales` | title: "October and December are peak months" |
| 11 | **Bar chart** | Y: `Country`; X: `Total Sales` | optional filled map if you prefer |
| 12 | **Matrix** (heat map) | Rows: `Segment`; Columns: `Discount Band`; Values: `Profit Margin %` | Format → Cell elements → Background colour → *Gradient* (red → yellow → green, centre 0.10) |
| 13 | **Table** | `Segment`, `Product`, `Total Sales`, `Total Profit`, `Profit Margin %` | sort by `Total Profit` descending; data bars on Profit |

Tips: turn off gridlines on bars, add data labels, set a consistent font (Segoe UI), and align visuals with
*Format → Align*.

## 5. Check your numbers (no filters applied)
| Measure | Expected |
|---|---|
| Total Sales | **$118,726,350** |
| Total Profit | **$16,893,702** |
| Profit Margin % | **14.2%** |
| Discount Rate % | **7.2%** |
| Loss-Making Orders | **58** (all Enterprise) |
| Government sales share | 44.2% (profit share 67.4%) |
| Enterprise margin | −3.1% |
| Margin by band | None 21.9% · Low 17.9% · Medium 14.4% · High 9.1% |

If a number differs, check the column types in step 1.

## 6. Insights to display (text box or second page)
1. Government = 44% of sales, 67% of profit.
2. Enterprise margin −3.1%; all 58 loss-making orders are Enterprise.
3. High discounts → 9.1% margin vs 21.9% with no discount.
4. October and December are the peak months; countries are evenly spread.
5. Recommendations: reprice Enterprise, gate deep discounts, scale Channel Partners / Midmarket after testing.

## 7. Save and submit
**File → Save as → `Capstone_Dashboard.pbix`**. Optionally add a screenshot (File → Export → PDF) for the report.

---

### Tableau equivalents (if you choose Tableau)
| Power BI | Tableau calculated field |
|---|---|
| Profit Margin % | `SUM([Profit]) / SUM([Sales])` |
| Discount Rate % | `SUM([Discounts]) / SUM([Gross Sales])` |
| Loss-Making Orders | `SUM(IF [Profit] < 0 THEN 1 ELSE 0 END)` |
| Sales Share % | `SUM([Sales]) / TOTAL(SUM([Sales]))` |
