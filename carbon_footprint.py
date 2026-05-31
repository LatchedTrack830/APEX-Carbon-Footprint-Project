import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(page_title="Carbon Footprint Calculator", page_icon="🌍", layout="wide")
st.title("🌍 Household Carbon Footprint Calculator")
st.caption("Estimates annual CO₂e emissions in metric tonnes")

# --- HOME ENERGY ---
st.header("🏠 Home Energy")
col1, col2 = st.columns(2)
with col1:
    people = st.number_input("Household size (people)", min_value=1, max_value=20, value=4)
    kwh = st.number_input("Electricity (kWh/month)", min_value=0, value=900, help="US average ~900 kWh/month")
    gas = st.number_input("Natural gas (therms/month)", min_value=0, value=50, help="US average ~55 therms/month. Enter 0 if all-electric")
with col2:
    oil = st.number_input("Heating oil (gallons/month)", min_value=0, value=0, help="US average around 100-200 gallons/month")
    solar = st.selectbox("Solar panels?", options=[
        ("No", 0.0),
        ("Partial offset (~50%)", 0.5),
        ("Full offset (~90%)", 0.9),
    ], format_func=lambda x: x[0])
    solar_factor = 1 - solar[1]

home_elec = kwh * 12 * 0.000386 * solar_factor
home_gas = gas * 12 * 0.005302
home_oil = oil * 12 * 0.010156
home_total = home_elec + home_gas + home_oil

# --- VEHICLES ---
st.header("🚗 Vehicles")
num_cars = st.number_input("Number of vehicles", min_value=0, max_value=6, value=1)
drive_total = 0.0
for i in range(num_cars):
    st.subheader(f"Vehicle {i+1}")
    c1, c2, c3 = st.columns(3)
    with c1:
        vtype = st.selectbox("Type", ["Gasoline", "Hybrid", "Electric (EV)"], key=f"vtype_{i}")
    with c2:
        label = "Efficiency (MPGe)" if vtype == "Electric (EV)" else "Fuel economy (MPG)"
        mpg = st.number_input(label, min_value=1, value=28, key=f"mpg_{i}", help="Around 25mpg on average, newer models closer to 30mpg.")
    with c3:
        miles = st.number_input("Miles/year", min_value=0, value=12000, key=f"miles_{i}", help="12,000-14,000 miles per year.")

    if vtype == "Electric (EV)":
        drive_total += (miles / mpg) * 0.000386 * 33.7 * solar_factor * 0.5
    else:
        drive_total += (miles / mpg) * 8.887
drive_total /= 1000

# --- FLIGHTS ---
st.header("✈️ Flights (per year, all passengers)")
c1, c2, c3 = st.columns(3)
with c1:
    f_short = st.number_input("Short haul (<3 hrs)", min_value=0, value=0, help="~0.25 t each")
with c2:
    f_med = st.number_input("Medium haul (3–6 hrs)", min_value=0, value=0, help="~0.7 t each")
with c3:
    f_long = st.number_input("Long haul (>6 hrs)", min_value=0, value=0, help="~1.6 t each")
fly_total = f_short * 0.25 + f_med * 0.7 + f_long * 1.6

# --- DIET ---
st.header("🥗 Diet")
diet_map = {
    "Meat-heavy (beef most days)": 3.3,
    "Average omnivore": 2.5,
    "Low meat (a few times/week)": 1.9,
    "Pescatarian": 1.5,
    "Vegetarian": 1.1,
    "Vegan": 0.7,
}
diet_choice = st.selectbox("Dietary pattern (per person)", list(diet_map.keys()), index=1)
diet_total = diet_map[diet_choice] * people

# --- SHOPPING ---
st.header("🛍️ Shopping & Consumption")
c1, c2, c3 = st.columns(3)
with c1:
    clothes = st.number_input("Monthly spend on clothes ($)", min_value=0, value=100)
with c2:
    electronics = st.number_input("Monthly spend on electronics ($)", min_value=0, value=30)
with c3:
    goods = st.number_input("Monthly spend on other goods ($)", min_value=0, value=200)
shop_total = (clothes * 0.0005 + electronics * 0.0008 + goods * 0.0003) * 12

# --- RESULTS ---
total = home_total + drive_total + fly_total + diet_total + shop_total
avg = 15 * people

st.divider()
st.header("📊 Results")

col1, col2, col3 = st.columns(3)
col1.metric("Total Annual Footprint", f"{total:.1f} t CO₂e")
col2.metric("US Average (your household size)", f"{avg:.1f} t CO₂e")
diff = total - avg
col3.metric("vs. Average", f"{diff:+.1f} t", delta_color="inverse")

st.subheader("Breakdown")
categories = {
    "🏠 Home Energy": home_total,
    "🚗 Driving": drive_total,
    "✈️ Flights": fly_total,
    "🥗 Diet": diet_total,
    "🛍️ Shopping": shop_total,
}

for label, val in categories.items():
    pct = (val / total * 100) if total > 0 else 0
    cols = st.columns([2, 5, 1])
    cols[0].write(label)
    cols[1].progress(min(pct / 100, 1.0))
    cols[2].write(f"{val:.1f} t")

# --- PIE CHART ---
st.subheader("Pie Chart")
if total > 0:
    labels = ["Home Energy", "Driving", "Flights", "Diet", "Shopping"]
    values = [home_total, drive_total, fly_total, diet_total, shop_total]
    colors = ["#1D9E75", "#7F77DD", "#D85A30", "#EF9F27", "#D4537E"]

    fig, ax = plt.subplots(figsize=(4, 4))
    wedges, texts, autotexts = ax.pie(
        values,
        labels=None,
        autopct=lambda p: f"{p:.1f}%" if p > 2 else "",
        colors=colors,
        startangle=140,
        wedgeprops={"edgecolor": "white", "linewidth": 1.5},
        pctdistance=0.75,
    )
    for at in autotexts:
        at.set_fontsize(11)
        at.set_color("white")
        at.set_fontweight("bold")

    legend_labels = [f"{l}  ({v:.1f} t)" for l, v in zip(labels, values)]
    ax.legend(
        wedges,
        legend_labels,
        loc="lower center",
        bbox_to_anchor=(0.5, -0.15),
        ncol=2,
        fontsize=10,
        frameon=False,
    )
    ax.set_title(f"Total: {total:.1f} t CO₂e/year", fontsize=13, pad=16)
    fig.patch.set_alpha(0)
    _, chart_col, _ = st.columns([1, 2, 1])
    with chart_col:
        st.pyplot(fig)
else:
    st.info("Enter your data above to see the chart.")

st.divider()
st.caption("Emission factors: EPA eGRID (electricity), EPA GHG inventory (gas/oil/fuel), OWID (diet), BEIS (flights). Results are estimates.")