import pandas as pd

# Load ONLY the sheet you need
df = pd.read_excel(
    "Seattle_precipitation_and_temperature_copy_2026_may_26.xlsx",
    sheet_name="Seattle_prcp_and_temp"
)

# Save ONLY that sheet as a clean CSV
df.to_csv("Seattle_precipitation_and_temperature.csv", index=False)

print("✓ CSV created successfully")
