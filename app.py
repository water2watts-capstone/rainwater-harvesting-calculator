import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Rainwater Harvesting Calculator", layout="wide")

# =====================================================================
# CREDITS & DISCLAIMERS
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
# LOAD PRECOMPUTED CSVs (FAST)
# =====================================================================

@st.cache_data
def load_daily():
    return pd.read_csv("daily_climatology_stats.csv")

@st.cache_data
def load_monthly():
    return pd.read_csv("monthly_totals.csv")

daily_df = load_daily()
monthly_df = load_monthly()

# Excel hard-coded operational days (11-year average)
excel_climo = pd.DataFrame({
    'month': [1,2,3,4,5,6,7,8,9,10,11,12],
    'excel_rain_days': [21,19,21,13,5,4,0,3,8,25,28,23]
})

# =====================================================================
# CONSTANTS
# =====================================================================

g = 9.81
rho = 1000
capture_eff = 0.7
turbine_eff = 0.5
carbon_intensity = 0.031104

ft_to_m = 0.3048
ft2_to_m2 = 0.09290304

phone_monthly_kwh = 0.15
led_monthly_kwh = 0.61
wifi_kwh_per_hour = 0.010972222

# =====================================================================
# FUNCTIONS
# =====================================================================

def get_roof_area_m2(choice, custom_ft2=None):
    if choice == "Alder Hall":
        area_ft2 = 10650
    elif choice == "IEB":
        area_ft2 = 12846
    else:
        area_ft2 = custom_ft2
    return area_ft2 * ft2_to_m2

def head_height_m(head_ft):
    return head_ft * ft_to_m

def compute_energy_applications(monthly_kwh):
    phone = (monthly_kwh / phone_monthly_kwh) / 30
    led = (monthly_kwh / led_monthly_kwh) / 30
    wifi = (monthly_kwh / wifi_kwh_per_hour) / 30
    return phone, led, wifi

def compute_monthly_energy(roof_area_m2, head_ft):
    head_m = head_height_m(head_ft)

    df = daily_df.copy()
    df['volume_m3'] = df['rainfall_m'] * roof_area_m2 * capture_eff
    df['energy_j'] = rho * g * head_m * df['volume_m3'] * turbine_eff
    df.loc[df['freeze_flag'] == 1, 'energy_j'] = 0
    df['energy_kwh'] = df['energy_j'] / 3.6e6
    df['carbon_kg'] = df['energy_kwh'] * carbon_intensity

    monthly = df.groupby('month').agg({
        "rainfall_m": "sum",
        "volume_m3": "sum",
        "energy_kwh": "sum",
        "carbon_kg": "sum",
        "rain_flag": "sum",
        "operational_day": "sum"
    }).reset_index()

    apps = monthly['energy_kwh'].apply(compute_energy_applications)
    monthly['phone_charges_per_day'] = apps.apply(lambda x: x[0])
    monthly['led_hours_per_day'] = apps.apply(lambda x: x[1])
    monthly['wifi_hours_per_day'] = apps.apply(lambda x: x[2])

    return monthly

# =====================================================================
# SIDEBAR
# =====================================================================

st.title("🌧️ Rainwater Harvesting & Power Generation Calculator")
st.write("Enter your building parameters to estimate water capture and renewable energy potential.")

st.sidebar.header("⚙️ Building Parameters")

roof_choice = st.sidebar.radio("Select building:", ["Alder Hall", "IEB", "Custom"])

if roof_choice == "Custom":
    custom_ft2 = st.sidebar.number_input("Custom roof area (sq ft):", min_value=100, value=10000, step=100)
    roof_area_m2 = get_roof_area_m2("Custom", custom_ft2)
else:
    roof_area_m2 = get_roof_area_m2(roof_choice)
    if roof_choice == "Alder Hall":
        st.sidebar.caption("10,650 sq ft")
    elif roof_choice == "IEB":
        st.sidebar.caption("12,846 sq ft")

head_ft = st.sidebar.slider("Head height (ft):", min_value=5.0, max_value=100.0, value=23.1, step=0.1)

mode = st.sidebar.radio(
    "Operational day definition:",
    ["Excel (rain only)", "Python (rain + non-freezing)"]
)

# =====================================================================
# COMPUTE RESULTS
# =====================================================================

monthly_energy_df = compute_monthly_energy(roof_area_m2, head_ft)
monthly_energy_df = monthly_energy_df.merge(excel_climo, on='month', how='left')

if mode == "Excel (rain only)":
    monthly_energy_df['Operational Days'] = monthly_energy_df['rain_flag']
else:
    monthly_energy_df['Operational Days'] = monthly_energy_df['operational_day']

annual_kwh = monthly_energy_df['energy_kwh'].sum()
annual_carbon_kg = monthly_energy_df['carbon_kg'].sum()
annual_rainfall_m = monthly_energy_df['rainfall_m'].sum()
annual_volume_m3 = monthly_energy_df['volume_m3'].sum()

# =====================================================================
# DISPLAY
# =====================================================================

st.subheader("📊 Annual Summary")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Annual kWh", f"{annual_kwh:.2f}")
col2.metric("CO₂ Offset (kg)", f"{annual_carbon_kg:.2f}")
col3.metric("Total Rainfall (m)", f"{annual_rainfall_m:.3f}")
col4.metric("Water Volume (m³)", f"{annual_volume_m3:.2f}")

st.divider()

st.subheader("📅 Monthly Breakdown")

display_df = monthly_energy_df[[
    'month',
    'excel_rain_days',
    'Operational Days',
    'rainfall_m',
    'volume_m3',
    'energy_kwh',
    'carbon_kg',
    'phone_charges_per_day',
    'led_hours_per_day',
    'wifi_hours_per_day'
]].copy()

display_df.columns = [
    'Month',
    'Excel Rain Days',
    'Operational Days',
    'Rainfall (m)',
    'Volume (m³)',
    'Energy (kWh)',
    'Carbon (kg)',
    'Phone Charges/Day',
    'LED Hours/Day',
    'WiFi Hours/Day'
]

for col in display_df.columns[2:]:
    display_df[col] = display_df[col].round(2)

st.dataframe(display_df, use_container_width=True, hide_index=True)

st.divider()

st.subheader("ℹ️ About This Calculator")
st.write("""
This calculator uses real NOAA precipitation and temperature data for Seattle to estimate:
- **Water Capture**  
- **Energy Generation**  
- **Carbon Offset**  
- **Operational Days**  
""")
