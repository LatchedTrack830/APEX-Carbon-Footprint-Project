import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(page_title="Carbon Footprint Calculator", page_icon="🌍", layout="wide")
st.title("🌍 Household Carbon Footprint Calculator")
st.caption("Estimates annual CO₂e emissions in metric tonnes")

# --- HOME ENERGY ---
st.header("Home Energy")
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
st.header("Vehicles")
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
st.header("Flights (per year, all passengers)")
c1, c2, c3 = st.columns(3)
with c1:
    f_short = st.number_input("Short haul (<3 hrs)", min_value=0, value=0, help="~0.25 t each")
with c2:
    f_med = st.number_input("Medium haul (3–6 hrs)", min_value=0, value=0, help="~0.7 t each")
with c3:
    f_long = st.number_input("Long haul (>6 hrs)", min_value=0, value=0, help="~1.6 t each")
fly_total = f_short * 0.25 + f_med * 0.7 + f_long * 1.6

# --- DIET ---
st.header("Diet")
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
st.header("Shopping & Consumption")
c1, c2, c3 = st.columns(3)
with c1:
    clothes = st.number_input("Monthly spend on clothes ($)", min_value=0, value=100)
with c2:
    electronics = st.number_input("Monthly spend on electronics ($)", min_value=0, value=30)
with c3:
    goods = st.number_input("Monthly spend on other goods (things like groceries) ($)", min_value=0, value=200)
shop_total = (clothes * 0.0005 + electronics * 0.0008 + goods * 0.0003) * 12

# --- RESULTS ---
total = home_total + drive_total + fly_total + diet_total + shop_total
avg = 16 * people

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
st.subheader("Breakdown of your carbon footprint.")
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

# --- RECOMMENDATIONS ---
st.header("Recommendations based on your input.")

if total == 0:
    st.info("Fill in your data above to get personalized recommendations.")
else:
    # Score each category as fraction of total, build targeted tips
    recs = []

    # Home energy
    if home_total / total > 0.15:
        if solar[1] == 0.0:
            recs.append(("🏠", "Install solar panels", f"Your home energy accounts for {home_total:.1f} t. Solar panels can offset 50–90% of your electricity emissions and typically pay back in 6–10 years."))
        if kwh > 1000:
            recs.append(("🏠", "Reduce electricity usage", f"At {kwh} kWh/month you're above average. Switching to LED bulbs, smart thermostats, and Energy Star appliances can cut usage by 20–30%."))
        if gas > 60:
            recs.append(("🏠", "Switch from gas to electric heating/cooking", f"You're using {gas} therms/month of natural gas. Heat pumps are 2–4x more efficient than gas furnaces and eliminate gas emissions entirely."))

    # Driving
    if drive_total / total > 0.15:
        has_gas_car = any(True for i in range(num_cars) if st.session_state.get(f"vtype_{i}", "Gasoline") != "Electric (EV)")
        recs.append(("🚗", "Switch to an electric vehicle", f"Driving contributes {drive_total:.1f} t to your footprint. Replacing a gas car with an EV can save 1.5–3 t CO₂e per year depending on your grid."))
        recs.append(("🚗", "Drive less", f"You're driving a lot. Combining errands, carpooling, or working from home 1–2 days/week can cut mileage — and emissions — by 10–20%."))

    # Flights
    if fly_total > 1.0:
        recs.append(("✈️", "Reduce flights", f"Flights add {fly_total:.1f} t — one of the highest-impact single actions. Taking one fewer long-haul flight saves ~1.6 t. Consider train travel for shorter trips."))
    if fly_total > 3.0:
        recs.append(("✈️", "Purchase carbon offsets for flights", "Since flights are a large share of your footprint, high-quality carbon offsets (e.g. Gold Standard certified) can neutralize the impact while you work on reducing travel."))

    # Diet
    if diet_choice == "Meat-heavy (beef most days)":
        recs.append(("🥗", "Reduce beef consumption", f"A meat-heavy diet contributes {diet_total:.1f} t. Cutting beef to 2–3x/week and replacing with chicken, fish, or plant-based meals can save 0.5–1.5 t per person per year."))
    elif diet_choice == "Average omnivore":
        recs.append(("🥗", "Try a flexitarian diet", f"Shifting toward less meat a few more days per week could save ~0.3–0.6 t per person. You don't need to go fully vegetarian to make a meaningful difference."))

    # Shopping
    if shop_total / total > 0.15:
        recs.append(("🛍️", "Buy less, buy secondhand", f"Shopping contributes {shop_total:.1f} t. Buying secondhand clothes, extending device lifespans by 1–2 years, and avoiding impulse purchases are among the easiest cuts."))
    if electronics > 50:
        recs.append(("🛍️", "Keep electronics longer", f"You spend ~${electronics}/month on electronics. Manufacturing a new smartphone emits ~70 kg CO₂e. Keeping devices an extra year or two adds up significantly."))

    # Always add a general tip if footprint is high
    if total > avg:
        recs.append(("🌱", "You're above the US average", f"Your household emits {diff:+.1f} t more than the US average for {people} people. The tips above, if all acted on, could realistically cut your footprint by 30–50%."))

    if not recs:
        st.success(f"Your footprint of {total:.1f} t is already below the US average for your household size. Keep it up!")
    else:
        for icon, title, desc in recs:
            with st.expander(f"{icon} {title}"):
                st.write(desc)

# --- WHAT IF SCENARIOS ---
st.divider()
st.header("🔄 What If?")

st.write(
    "Choose one realistic change and see how much it would reduce your footprint and save you each year."
)

change = st.selectbox(
    "Which change would you realistically make?",
    [
        "Convert meals to vegetarian",
        "Drive less",
        "Take fewer flights",
        "Reduce electricity usage",
        "Install solar panels",
    ]
)

savings = 0.0          # tonnes CO₂e
money_saved = 0.0      # dollars

# --- VEGETARIAN MEALS ---
if change == "Convert meals to vegetarian":

    veg_meals = st.number_input(
        "How many meals per week would you convert to vegetarian?",
        min_value=0,
        max_value=21,
        value=3,
    )

    # ~2 kg CO₂e saved per meal
    savings = veg_meals * 52 * 2 / 1000 * people

    # Assume vegetarian meal costs ~$2 less
    money_saved = veg_meals * 52 * 2 * people

# --- DRIVE LESS ---
elif change == "Drive less":

    fewer_miles = st.number_input(
        "How many miles per year would you reduce?",
        min_value=0,
        value=2000,
    )

    avg_vehicle_emission = 0

    if num_cars > 0:
        total_emissions_kg = 0

        for i in range(num_cars):
            vtype = st.session_state.get(f"vtype_{i}", "Gasoline")
            mpg = st.session_state.get(f"mpg_{i}", 28)

            if vtype == "Electric (EV)":
                kg_per_mile = (1 / mpg) * 33.7 * 0.386 * solar_factor
            else:
                kg_per_mile = 8.887 / mpg

            total_emissions_kg += kg_per_mile

        avg_vehicle_emission = total_emissions_kg / num_cars

    savings = fewer_miles * avg_vehicle_emission / 1000

    # Fuel + maintenance
    money_saved = fewer_miles * 0.15

# --- FEWER FLIGHTS ---
elif change == "Take fewer flights":

    flight_type = st.selectbox(
        "Flight type",
        [
            "Short haul (<3 hrs)",
            "Medium haul (3–6 hrs)",
            "Long haul (>6 hrs)",
        ]
    )

    num_flights_cut = st.number_input(
        "Number of flights avoided per year",
        min_value=0,
        value=1,
    )

    flight_map = {
        "Short haul (<3 hrs)": 0.25,
        "Medium haul (3–6 hrs)": 0.7,
        "Long haul (>6 hrs)": 1.6,
    }

    savings = flight_map[flight_type] * num_flights_cut

    flight_cost_map = {
        "Short haul (<3 hrs)": 250,
        "Medium haul (3–6 hrs)": 500,
        "Long haul (>6 hrs)": 1200,
    }

    money_saved = (
        flight_cost_map[flight_type]
        * num_flights_cut
    )

# --- ELECTRICITY REDUCTION ---
elif change == "Reduce electricity usage":

    reduction_pct = st.slider(
        "Percent reduction in electricity use",
        min_value=0,
        max_value=50,
        value=15,
    )

    savings = home_elec * (reduction_pct / 100)

    annual_electric_bill = kwh * 12 * 0.17
    money_saved = annual_electric_bill * (reduction_pct / 100)

# --- SOLAR ---
elif change == "Install solar panels":

    solar_choice = st.radio(
        "Solar system size",
        [
            "Partial offset (~50%)",
            "Full offset (~90%)",
        ]
    )

    if solar_choice == "Partial offset (~50%)":
        new_factor = 0.5
    else:
        new_factor = 0.1

    new_home_elec = kwh * 12 * 0.000386 * new_factor

    savings = max(home_elec - new_home_elec, 0)

    annual_electric_bill = kwh * 12 * 0.17

    if solar_choice == "Partial offset (~50%)":
        money_saved = annual_electric_bill * 0.50
    else:
        money_saved = annual_electric_bill * 0.90

# --- RESULTS ---
if total > 0:

    savings = min(savings, total)

    new_total = total - savings
    reduction_pct = (savings / total) * 100

    st.subheader("Estimated Impact")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            "CO₂e Saved",
            f"{savings:.2f} t/year"
        )

    with c2:
        st.metric(
            "Reduction",
            f"{reduction_pct:.1f}%"
        )

    with c3:
        st.metric(
            "New Footprint",
            f"{new_total:.1f} t/year"
        )

    with c4:
        st.metric(
            "Money Saved",
            f"${money_saved:,.0f}/year"
        )

    trees_equivalent = savings / 0.021

    st.info(
        f"This change would save approximately "
        f"**{savings:.2f} tonnes of CO₂e per year** and about "
        f"**${money_saved:,.0f} per year**. "
        f"That's roughly equivalent to the annual carbon absorption of "
        f"**{trees_equivalent:.0f} mature trees**."
    )

    if money_saved > 1000:
        st.success(
            f"This change could save over ${money_saved:,.0f} every year."
        )

st.divider()
st.caption("Chat did I cook?")
#i think i cooked
