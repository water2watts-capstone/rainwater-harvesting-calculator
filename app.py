import streamlit as st
import pandas as pd

st.set_page_config(page_title="Rainwater Harvesting Calculator", layout="wide")

# =====================================================================
# TITLE
# =====================================================================

st.title("🌧️ Rainwater Harvesting Calculator (Excel‑Equivalent)")
st.write("Enter your building parameters below. Rainfall values use Seattle climatology.")

st.divider()

# =====================================================================
# MAIN‑BODY BUILDING INPUTS (NOT SIDEBAR)
# =====================================================================

st.subheader("🏢 Building Parameters")

col1, col2 = st.columns(2)

with col1:
    roof_preset = st.selectbox(
        "Roof Area Preset:",
        ["Custom", "Alder Hall (10,650 ft²)", "IEB (12,846 ft²)"]
    )

with col2:
    head_preset = st.selectbox(
        "Head Height Preset:",
        ["Custom", "23.1 ft (default pipe height)", "183 ft (IEB full height)"]
    )

# --- Roof area logic ---
if roof_preset == "Alder Hall (10,650 ft²)":
    roof_area_ft2 = 10650
elif roof_preset == "IEB (12,846 ft²)":
    roof_area_ft2 = 12846
else:
    roof_area_ft2 = st.slider(
        "Custom Roof Area (sq ft):",
        min_value=100,
        max_value=200000,
        value=10000,
        step=50
    )

# --- Head height logic ---
if head_preset == "23.1 ft (default pipe height)":
    head_ft = 23.1
elif head_preset == "183 ft (IEB full height)":
    head_ft = 183.0
else:
    head_ft = st.slider(
        "Custom Head Height (ft):",
        min_value=1.0,
        max_value=300.0,
        value=23.1,
        step=0.1
    )

st.divider()

# =====================================================================
# CONSTANTS
# =====================================================================

ft2_to_m2 = 0.09290304
ft_to_m = 0.3048
rho = 1000
g = 9.81
capture_eff = 0.7
turbine_eff = 0.5
carbon_intensity = 0.031104

roof_area_m2 = roof_area_ft2 * ft2_to_m2
head_m = head_ft * ft_to_m

# =====================================================================
# MONTHLY RAINFALL (HARD‑CODED)
# =====================================================================

monthly = pd.DataFrame({
    "month": [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ],
    "rainfall_m": [
        0.135, 0.103, 0.092, 0.069, 0.044, 0.034,
        0.018, 0.024, 0.056, 0.120, 0.158, 0.133
    ]
})

# =====================================================================
# CALCULATIONS
# =====================================================================

monthly["volume_m3"] = monthly["rainfall_m"] * roof_area_m2 * capture_eff

monthly["energy_kwh"] = (
    rho * g * head_m * monthly["volume_m3"] * turbine_eff
) / 3.6e6

monthly["carbon_kg"] = monthly["energy_kwh"] * carbon_intensity

# =====================================================================
# DISPLAY RESULTS
# =====================================================================

st.subheader("📅 Monthly Results")
st.dataframe(monthly, use_container_width=True)

st.divider()

st.subheader("📊 Annual Totals")
st.metric("Annual kWh", f"{monthly['energy_kwh'].sum():.2f}")
st.metric("Annual Carbon Offset (kg)", f"{monthly['carbon_kg'].sum():.2f}")

st.write("This version reproduces the exact Excel math using Seattle's monthly rainfall totals.")
