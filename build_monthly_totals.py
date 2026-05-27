import pandas as pd

df = pd.read_csv("monthly_total.csv")

# Convert inches → meters
inch_to_m = 0.0254
df["rainfall_m"] = df["PRCP [in]"] * inch_to_m

# Sum across all years → Excel climatology
monthly = df.groupby("month")["rainfall_m"].sum().reset_index()

monthly.to_csv("monthly_totals.csv", index=False)
