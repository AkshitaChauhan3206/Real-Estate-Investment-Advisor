import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from config import CLEAN_FILE, FORECAST_YEARS, GOOD_INVESTMENT_THRESHOLD, GROWTH_SCENARIOS, USING_SAMPLE
from predict import build_row, data_warnings, future_table, load_assets, score_breakdown, value_check

INDIGO, GOLD, TEAL, BRICK, INK, MUTED = "#2B3A8C", "#F2A900", "#1B998B", "#C8553D", "#1B2236", "#5B6577"

st.set_page_config(page_title="Property Investment Advisor", page_icon="🏠", layout="wide")

st.markdown(
    f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:wght@500;700&family=Source+Sans+3:wght@400;600&display=swap');
html, body, [class*="css"] {{ font-family: 'Source Sans 3', 'Segoe UI', sans-serif; color: {INK}; }}
h1, h2, h3 {{ font-family: 'Bricolage Grotesque', 'Segoe UI', sans-serif; letter-spacing: -0.01em; }}
.stApp {{ background: #F4F6F8; }}
section[data-testid="stSidebar"] {{ background: {INK}; }}
section[data-testid="stSidebar"] * {{ color: #E8ECF4 !important; }}
.hero {{ border-left: 6px solid {GOLD}; padding: 6px 0 6px 18px; margin-bottom: 18px; }}
.hero h1 {{ margin: 0; font-size: 2rem; }}
.hero p {{ margin: 4px 0 0 0; color: {MUTED}; font-size: 1.05rem; }}
.kpi {{ background: #FFFFFF; border-top: 3px solid {INDIGO}; padding: 12px 16px; border-radius: 4px; }}
.kpi .label {{ color: {MUTED}; font-size: 0.85rem; }}
.kpi .value {{ font-family: 'Bricolage Grotesque', sans-serif; font-size: 1.7rem; font-weight: 700; }}
.kpi .note {{ color: {MUTED}; font-size: 0.8rem; }}
.verdict {{ padding: 16px 20px; border-radius: 4px; background: #FFFFFF; border-left: 8px solid var(--c); }}
.verdict h2 {{ margin: 0 0 4px 0; }}
.caution {{ background: #FFF6DD; border-left: 5px solid {GOLD}; padding: 10px 14px; border-radius: 4px; margin: 10px 0; }}
.warn {{ background: #FBE9E4; border-left: 5px solid {BRICK}; padding: 10px 14px; border-radius: 4px; margin: 10px 0; }}
</style>
""",
    unsafe_allow_html=True,
)

USE_COLS = ["ID", "State", "City", "Property_Type", "BHK", "Size_in_SqFt", "Price_in_Lakhs", "Price_per_SqFt_INR", "Age_of_Property",
            "Availability_Status", "Furnished_Status", "Public_Transport_Accessibility", "Investment_Score", "Good_Investment",
            "Infrastructure_Score", "data_issue_count", "Owner_Type"]


@st.cache_data(show_spinner="Loading listings...")
def load_data():
    return pd.read_csv(CLEAN_FILE, usecols=USE_COLS)


@st.cache_resource(show_spinner="Loading models...")
def get_assets():
    return load_assets()


def hero(title, text):
    st.markdown(f'<div class="hero"><h1>{title}</h1><p>{text}</p></div>', unsafe_allow_html=True)


def kpi(label, value, note=""):
    st.markdown(f'<div class="kpi"><div class="label">{label}</div><div class="value">{value}</div><div class="note">{note}</div></div>', unsafe_allow_html=True)


def style(fig, height=380):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=50, b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#FFFFFF",
                      font=dict(family="Source Sans 3, Segoe UI, sans-serif", color=INK), title_font=dict(size=16))
    return fig


def lakhs(x):
    return f"{x:,.1f} lakh" if x < 100 else f"{x / 100:,.2f} crore"


if not CLEAN_FILE.exists():
    st.error("Data file not found. Upload housing_clean.csv.gz (or housing_clean_sample_60k.csv.gz) to the same folder as streamlit_app.py.")
    st.stop()
data, assets = load_data(), get_assets()
schema, results, quality = assets["schema"], assets["results"], assets["quality"]

st.sidebar.markdown("## Property Investment Advisor")
page = st.sidebar.radio("Go to", ["Market overview", "Find properties", "Check a property", "How far can we trust this?"])
st.sidebar.markdown("---")
st.sidebar.caption(f"Data: india_housing_prices.csv, {len(data):,} listings" + (" (random sample)" if USING_SAMPLE else "") + ", 42 cities.")


def filters(df):
    st.sidebar.markdown("### Filters")
    states = st.sidebar.multiselect("State", sorted(df["State"].unique()))
    if states:
        df = df[df["State"].isin(states)]
    cities = st.sidebar.multiselect("City", sorted(df["City"].unique()))
    if cities:
        df = df[df["City"].isin(cities)]
    types = st.sidebar.multiselect("Property type", sorted(df["Property_Type"].unique()))
    if types:
        df = df[df["Property_Type"].isin(types)]
    bhk = st.sidebar.slider("BHK", 1, 5, (1, 5))
    price = st.sidebar.slider("Price (lakhs)", 10, 500, (10, 500))
    status = st.sidebar.selectbox("Status", ["Any", "Ready_to_Move", "Under_Construction"])
    df = df[df["BHK"].between(*bhk) & df["Price_in_Lakhs"].between(*price)]
    if status != "Any":
        df = df[df["Availability_Status"] == status]
    return df


if page == "Market overview":
    hero("Market overview", "What the listings say about prices, sizes and the investment checklist, with your filters applied.")
    view = filters(data)
    if view.empty:
        st.warning("No listings match these filters. Please widen them.")
        st.stop()
    cols = st.columns(5)
    with cols[0]:
        kpi("Listings", f"{len(view):,}")
    with cols[1]:
        kpi("Median price", lakhs(view["Price_in_Lakhs"].median()))
    with cols[2]:
        kpi("Median price per sq ft", f"Rs {view['Price_per_SqFt_INR'].median():,.0f}")
    with cols[3]:
        kpi("Pass the checklist", f"{100 * view['Good_Investment'].mean():.1f}%", f"score of {GOOD_INVESTMENT_THRESHOLD} or more")
    with cols[4]:
        kpi("Cities", f"{view['City'].nunique()}")
    st.markdown("")
    left, right = st.columns(2)
    city = view.groupby("City")["Price_per_SqFt_INR"].median().sort_values().reset_index()
    fig = px.bar(city.tail(15), x="Price_per_SqFt_INR", y="City", orientation="h", title="Top 15 cities by median price per sq ft", color_discrete_sequence=[INDIGO])
    left.plotly_chart(style(fig), use_container_width=True)
    fig = px.histogram(view, x="Price_in_Lakhs", nbins=40, title="Price spread (lakhs)", color_discrete_sequence=[GOLD])
    right.plotly_chart(style(fig), use_container_width=True)
    left, right = st.columns(2)
    sample = view.sample(min(len(view), 15000), random_state=42)
    fig = px.scatter(sample, x="Size_in_SqFt", y="Price_in_Lakhs", opacity=0.25, title="Size vs price (sample)", color_discrete_sequence=[INDIGO])
    left.plotly_chart(style(fig), use_container_width=True)
    rate = view.groupby("Property_Type")["Good_Investment"].mean().mul(100).reset_index()
    fig = px.bar(rate, x="Property_Type", y="Good_Investment", title="Share passing the checklist, by property type (%)", color_discrete_sequence=[TEAL])
    right.plotly_chart(style(fig), use_container_width=True)
    st.markdown('<div class="caution"><b>Read this first.</b> Prices in this file barely change with size, city, type or amenities. '
                'Differences you see between cities are mostly chance. Use the charts to explore, not to rank places. See the last page.</div>', unsafe_allow_html=True)

elif page == "Find properties":
    hero("Find properties", "Filter the listings and sort by the checklist score. Check the data flags before you rely on a row.")
    view = filters(data)
    sort_by = st.selectbox("Sort by", ["Investment_Score", "Price_per_SqFt_INR", "Price_in_Lakhs", "Size_in_SqFt"])
    only_clean = st.checkbox("Hide rows with data problems", value=False)
    if only_clean:
        view = view[view["data_issue_count"] == 0]
    view = view.sort_values(sort_by, ascending=(sort_by != "Investment_Score")).head(500)
    st.caption(f"Showing the top {len(view)} rows. Download to see them all in Excel.")
    show = ["ID", "City", "Property_Type", "BHK", "Size_in_SqFt", "Price_in_Lakhs", "Price_per_SqFt_INR", "Availability_Status", "Investment_Score", "data_issue_count"]
    st.dataframe(view[show], use_container_width=True, height=520)
    st.download_button("Download these rows (CSV)", view[show].to_csv(index=False).encode(), "selected_properties.csv", "text/csv")

elif page == "Check a property":
    hero("Check a property", "Enter the details and the asking price. You get a checklist score, a price check against the city, and a 5-year scenario.")
    with st.form("property_form"):
        c1, c2, c3 = st.columns(3)
        city = c1.selectbox("City", schema["categories"]["City"])
        ptype = c2.selectbox("Property type", schema["categories"]["Property_Type"])
        status = c3.selectbox("Availability", schema["categories"]["Availability_Status"])
        c1, c2, c3 = st.columns(3)
        bhk = c1.number_input("BHK", 1, 5, 3)
        size = c2.number_input("Size (sq ft)", 300, 6000, 1500, step=50)
        price = c3.number_input("Asking price (lakhs)", 5.0, 1000.0, 120.0, step=5.0)
        c1, c2, c3 = st.columns(3)
        year = c1.number_input("Year built", 1980, 2025, 2015)
        floor = c2.number_input("Floor number", 0, 60, 5)
        total_floors = c3.number_input("Total floors", 1, 60, 10)
        c1, c2, c3 = st.columns(3)
        schools = c1.slider("Nearby schools (1 to 10)", 1, 10, 6)
        hospitals = c2.slider("Nearby hospitals (1 to 10)", 1, 10, 6)
        transport = c3.selectbox("Public transport", schema["categories"]["Public_Transport_Accessibility"], index=0)
        c1, c2, c3 = st.columns(3)
        furnished = c1.selectbox("Furnishing", schema["categories"]["Furnished_Status"])
        owner = c2.selectbox("Seller", schema["categories"]["Owner_Type"])
        facing = c3.selectbox("Facing", schema["categories"]["Facing"])
        c1, c2, c3 = st.columns(3)
        parking = c1.selectbox("Parking", schema["categories"]["Parking_Space"], index=1)
        security = c2.selectbox("Security", schema["categories"]["Security"], index=1)
        amenities = c3.multiselect("Amenities", ["Clubhouse", "Garden", "Gym", "Playground", "Pool"], default=["Gym"])
        go_button = st.form_submit_button("Check this property")

    if go_button:
        inp = {"City": city, "Property_Type": ptype, "BHK": int(bhk), "Size_in_SqFt": int(size), "Year_Built": int(year), "Furnished_Status": furnished,
               "Floor_No": int(floor), "Total_Floors": int(total_floors), "Nearby_Schools": int(schools), "Nearby_Hospitals": int(hospitals),
               "Public_Transport_Accessibility": transport, "Parking_Space": parking, "Security": security, "Facing": facing,
               "Owner_Type": owner, "Availability_Status": status, "Amenities": amenities}
        row = build_row(inp, schema)
        check = value_check(price, size, city, assets["city_medians"])
        parts, total, good = score_breakdown(inp, check["points"])
        colour = TEAL if good else BRICK
        headline = "Meets the investment checklist" if good else "Does not meet the investment checklist"
        st.markdown(f'<div class="verdict" style="--c:{colour}"><h2>{headline}</h2><p>Checklist score: <b>{total} out of 100</b> (a pass needs {GOOD_INVESTMENT_THRESHOLD}).</p></div>', unsafe_allow_html=True)
        st.markdown("")
        a, b = st.columns(2)
        pts = pd.DataFrame({"Item": list(parts.keys()), "Points": list(parts.values())})
        fig = px.bar(pts, x="Points", y="Item", orientation="h", title="Where the points come from", color_discrete_sequence=[INDIGO])
        a.plotly_chart(style(fig, 340), use_container_width=True)
        diff = (check["ratio"] - 1) * 100
        word = "below" if diff < 0 else "above"
        b.markdown(f"### Price check\nThis property costs **Rs {check['ppsf']:,.0f}** per sq ft. The median in {city} is **Rs {check['city_median']:,.0f}**, "
                   f"so it is **{abs(diff):.0f}% {word}** the city median.")
        prob = float(assets["investment_model"].predict_proba(row)[0, 1])
        b.markdown(f"### Checklist model\nThe model gives a **{100 * prob:.0f}%** chance of passing the checklist, without using the price. "
                   f"It was right on {100 * results['classification']['test']['accuracy']:.0f}% of test listings, against {100 * results['classification']['baseline_test_accuracy']:.0f}% for always guessing 'no'. "
                   "It mostly repeats the checklist rules and the size effect, so treat it as a cross-check only.")
        notes = data_warnings(row)
        if notes:
            st.markdown('<div class="warn"><b>Data warnings for these inputs:</b> ' + " ".join(notes) + "</div>", unsafe_allow_html=True)
        st.markdown(f"### Value in {FORECAST_YEARS} years (scenarios)")
        fut = future_table(price)
        years = list(range(FORECAST_YEARS + 1))
        fig = go.Figure()
        for (name, rate), colour in zip(GROWTH_SCENARIOS.items(), [MUTED, INDIGO, GOLD]):
            fig.add_trace(go.Scatter(x=years, y=[price * (1 + rate) ** y for y in years], mode="lines+markers", name=name, line=dict(color=colour, width=3)))
        fig.update_layout(title="Price path for each growth scenario", xaxis_title="Years from today", yaxis_title="Lakhs")
        a, b = st.columns([1.2, 1])
        a.plotly_chart(style(fig, 340), use_container_width=True)
        table = pd.DataFrame({"Scenario": list(fut.keys()), f"Price in {FORECAST_YEARS} years": [lakhs(v) for v in fut.values()], "Gain": [lakhs(v - price) for v in fut.values()]})
        b.dataframe(table, hide_index=True, use_container_width=True)
        st.markdown('<div class="caution">The growth rates are scenarios chosen by us. The file has no price history, so no model can learn real growth from it. '
                    'Replace them with local figures from the owner before making a decision.</div>', unsafe_allow_html=True)
        with st.expander("Why we do not show a model price estimate"):
            reg = results["regression"]
            st.write(f"We trained a price model. On unseen listings it scored R2 = {reg['test']['r2']:.4f}, the same as always guessing the average price "
                     f"(error of {reg['test']['rmse']:.0f} lakhs against {reg['baseline_test']['rmse']:.0f} for the average). "
                     "A model that is no better than the average should not be used to value a property.")

else:
    hero("How far can we trust this?", "The honest summary of the data, the models and the limits. Read this before using any number in the app.")
    cols = st.columns(4)
    with cols[0]:
        kpi("Rows with a data problem", f"{quality['rows_with_any_issue_pct']}%", "at least one of three checks")
    with cols[1]:
        kpi("Floor above total floors", f"{quality['floor_no_above_total_floors_pct']}%", "impossible in real life")
    with cols[2]:
        kpi("Under construction, but old", f"{quality['under_construction_but_old_pct_of_uc']}%", "of under-construction listings")
    with cols[3]:
        kpi("Price model gain over average", f"{results['regression']['test']['r2']:.3f}", "R2 on unseen listings")
    st.markdown("")
    left, right = st.columns(2)
    reg, clf = results["regression"], results["classification"]
    summary = pd.DataFrame([
        {"Model": "Price (lakhs)", "Result": f"error {reg['test']['rmse']:.1f}", "Simple guess": f"error {reg['baseline_test']['rmse']:.1f}", "Verdict": "No gain"},
        {"Model": "Good Investment", "Result": f"accuracy {100 * clf['test']['accuracy']:.1f}%", "Simple guess": f"accuracy {100 * clf['baseline_test_accuracy']:.1f}%", "Verdict": "Gain comes from the checklist rules"},
        {"Model": "Cheaper than city median price?", "Result": f"accuracy {100 * results['signal_test_price']['accuracy']:.1f}%", "Simple guess": f"accuracy {100 * results['signal_test_price']['baseline_accuracy']:.1f}%", "Verdict": "No pattern to learn"},
    ])
    left.markdown("### Models against a simple guess")
    left.dataframe(summary, hide_index=True, use_container_width=True)
    imp = pd.read_csv(ROOT / "feature_importance.csv")
    top = imp[imp["task"] == "good_investment"].nlargest(8, "importance").iloc[::-1]
    fig = px.bar(top, x="importance", y="feature", orientation="h", title="What the checklist model uses most", color_discrete_sequence=[INDIGO])
    right.plotly_chart(style(fig, 330), use_container_width=True)
    st.markdown("### Limits you should tell the owner")
    st.markdown(
        "- **Prices look random.** Size, city, type, furnishing and amenities explain almost none of the price. Rankings of cities or localities are noise.\n"
        "- **Locality has no place meaning.** Every locality name appears in all 42 cities.\n"
        "- **Some fields contradict themselves.** Floor above total floors, tiny or huge flats for the BHK count, and old buildings listed as under construction.\n"
        "- **No dates.** There is no sale date, so real growth cannot be measured. The 5-year view is a scenario.\n"
        "- **Checklist is our rule.** The score weights are a starting point. Change them with the owner's own view of risk.\n"
        "- **To make this a real advisor** the owner needs real sale prices with dates, correct locations, and RERA or legal status."
    )
