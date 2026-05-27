import streamlit as st
import pandas as pd

st.set_page_config(page_title="Simple Rainwater Harvesting Calculator", layout="wide")

# =====================================================================
# 📋 Attribution & Disclaimer
# =====================================================================

with st.expander("📋 Attribution & Disclaimer"):
    st.write("""
    **Data & Calculations:**  
    Based on the Water2Watts shared Excel file and climatology work by  
    Peyton G., Kyle R., and Willa C.

    **App Development:**  
    - Concept: Kyle R.  
    - Python adaptation: Paulinne A.  
    - AI assistance: Microsoft Copilot + Claude Haiku  
    - All AI-generated code reviewed and adapted by Paulinne A.
    """)

# =====================================================================
# TITLE & INTRO
# =====================================================================

st.title("🌧️ Rainwater Harvesting Calculator (Excel-Equivalent Version)")
st.write("This version reproduces the exact math used in the Excel model.")

st.divider()

# =====================================================================
# SIDEBAR INPUTS WITH PRESETS
# =====================================================================

st.sidebar.header("⚙️ Building Parameters")

# --- Roof area presets ---
roof_preset = st.sidebar.selectbox(
    "Choose roof area preset:",
    ["Custom", "Alder Hall (10,650 ft²)", "IEB (12,846 ft²)"]
)

if roof_preset == "Alder Hall (10,650 ft²)":
    roof_area_ft2 = 10650
elif roof_preset == "IEB (12,846 ft²)":
    roof_area_ft2 = 12846
else:
    roof_area_ft2 = st.sidebar.number_input(
        "Custom roof area (sq ft):",
        min_value=100,
        max_value=100000,
        value=10000
    )

# --- Head height presets ---
head_preset = st.sidebar.selectbox(
    "Choose head height:",
    ["23.1 ft (default pipe height)", "183 ft (IEB full height)", "Custom"]
)

if head_preset == "23.1 ft (default pipe height)":
    head_ft = 23.1
elif head_preset == "183 ft (IEB full height)":
    head_ft = 183.0
else:
    head_ft = st.sidebar.number_input(
        "Custom head height (ft):",
        min_value=1.0,
        max_value=300.0,
        value=23.1
    )

# =====================================================================
# CONSTANTS (Excel-equivalent)
# =====================================================================

ft2_to_m2 = 0.09290304
ft_to_m = 0.3048
rho = 1000          # kg/m³
g = 9.81            # m/s²
capture_eff = 0.7   # Excel constant
turbine_eff = 0.5   # Excel constant
carbon_intensity = 0.031104  # kg CO2e per kWh (Excel constant)

roof_area_m2 = roof_area_ft2 * ft2_to_m2
head_m = head_ft * ft_to_m

# =====================================================================
# 📌 HARD‑CODED EXCEL MONTHLY RAINFALL TOTALS (meters)
# =====================================================================

monthly = pd.DataFrame({
    "month": [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ],
    "rainfall_m": [
        0.135,  # January
        0.103,  # February
        0.092,  # March
        0.069,  # April
        0.044,  # May
        0.034,  # June
        0.018,  # July
        0.024,  # August
        0.056,  # September
        0.120,  # October
        0.158,  # November
        0.133   # December
    ]
})

# =====================================================================
# 📌 Excel‑equivalent calculations
# =====================================================================

monthly["volume_m3"] = monthly["rainfall_m"] * roof_area_m2 * capture_eff

monthly["energy_kwh"] = (
    rho * g * head_m * monthly["volume_m3"] * turbine_eff
) / 3.6e6

monthly["carbon_kg"] = monthly["energy_kwh"] * carbon_intensity

# =====================================================================
# 📌 Display results
# =====================================================================

st.subheader("📅 Monthly Results")
st.dataframe(monthly, use_container_width=True)

st.divider()

st.subheader("📊 Annual Totals (Excel‑equivalent)")
st.metric("Annual kWh", f"{monthly['energy_kwh'].sum():.2f}")
st.metric("Annual Carbon Offset (kg)", f"{monthly['carbon_kg'].sum():.2f}")

st.write("This version reproduces the exact Excel math using your processed monthly totals.")
