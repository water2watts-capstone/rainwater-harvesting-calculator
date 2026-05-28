import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="Water2Watts SHEW Calculator", layout="wide")

# =====================================================================
# TITLE & INTRO
# =====================================================================

st.title("💧 Water2Watts SHEW Calculator")

st.markdown("""
### 🏢 Enter Building Parameters  
This tool estimates the potential electrical energy that could be harvested from rooftop rainwater runoff with a Self-sufficient Harvester of Electricity-Water (SHEW) system.  
Rainfall values are based on **11 years of average Seattle precipitation (NOAA)**.

---

### ⚙️ How the Calculation Works  
We use the standard hydropower equation to estimate energy from falling water:



\[
P = \eta \cdot \rho g Q H
\]



Where:  
- **\(P\)** = power (Watts)  
- **\(\eta\)** = turbine efficiency  
- **\(\rho\)** = water density  
- **\(g\)** = gravity  
- **\(Q\)** = flow rate from roof runoff  
- **\(H\)** = head height (vertical drop)

Flow rate is computed from rainfall depth × roof area × capture efficiency.

---

### ⚠️ Important Notes  
This calculator provides a **rough engineering estimate** using simplifying assumptions:  
- Constant rainfall intensity within each month  
- 70% capture efficiency (losses from gutters, splash, etc.)  
- 50% turbine efficiency  
- No friction or pipe losses 

Actual performance will vary.

---

### 📋 Attribution  
**Data & Calculations:**  
Based on the Water2Watts Excel model and 11‑year average Seattle precipitation (NOAA).

**App Development:**  
- Concept: Kyle R.  
- Python adaptation: Paulinne A.  
- AI assistance: Microsoft Copilot + Claude Haiku  
- All AI-generated code reviewed and adapted by Paulinne A.

---

""")

st.divider()

# =====================================================================
# MAIN‑BODY BUILDING INPUTS (WITH SLIDERS)
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
# MONTHLY RAINFALL (11-YEAR NOAA AVERAGE)
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

annual_kwh = monthly["energy_kwh"].sum()
annual_carbon = monthly["carbon_kg"].sum()

# =====================================================================
# BAR CHARTS
# =====================================================================

st.subheader("📊 Monthly Rainfall (m)")
rain_chart = alt.Chart(monthly).mark_bar().encode(
    x="month",
    y="rainfall_m",
    tooltip=["month", "rainfall_m"]
)
st.altair_chart(rain_chart, use_container_width=True)

st.subheader("⚡ Monthly Energy Generation (kWh)")
energy_chart = alt.Chart(monthly).mark_bar(color="#4CAF50").encode(
    x="month",
    y="energy_kwh",
    tooltip=["month", "energy_kwh"]
)
st.altair_chart(energy_chart, use_container_width=True)

st.divider()

# =====================================================================
# ANNUAL TOTALS
# =====================================================================

st.subheader("📈 Annual Totals")
st.metric("Annual kWh", f"{annual_kwh:.2f}")
st.metric("Annual Carbon Offset (kg)", f"{annual_carbon:.2f}")

st.divider()

# =====================================================================
# ENERGY APPLICATIONS (CORRECTED)
# =====================================================================

st.subheader("🔌 Energy Applications")

# Correct device monthly energy needs
phone_monthly_need = 0.15   # kWh/month
led_monthly_need = 0.30     # kWh/month
wifi_monthly_need = 7.2     # kWh/month

# Phone charges
phone_charges_per_year = annual_kwh / phone_monthly_need
phone_charges_per_day = phone_charges_per_year / 365

# LED bulb hours
led_hours_per_year = annual_kwh / led_monthly_need
led_hours_per_day = led_hours_per_year / 365

# WiFi router runtime
wifi_days = annual_kwh / wifi_monthly_need
wifi_months = wifi_days / 30

colA, colB, colC = st.columns(3)

with colA:
    st.metric("📱 Phone Charges / Day", f"{phone_charges_per_day:.2f}")
    st.metric("📱 Phone Charges / Year", f"{phone_charges_per_year:.1f}")

with colB:
    st.metric("💡 LED Hours / Day", f"{led_hours_per_day:.2f}")
    st.metric("💡 LED Hours / Year", f"{led_hours_per_year:.1f}")

with colC:
    st.metric("📶 WiFi Runtime (Days)", f"{wifi_days:.1f}")
    st.metric("📶 WiFi Runtime (Months)", f"{wifi_months:.2f}")

st.write("This calculator uses 11 years of NOAA rainfall data and Excel‑equivalent hydropower formulas.")
