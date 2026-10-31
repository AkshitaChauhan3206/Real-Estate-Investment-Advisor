import json
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from config import DATA_FILES, EXPECTED_PARTS, FORECAST_YEARS, GOOD_INVESTMENT_THRESHOLD, GROWTH_SCENARIOS, PARTS, USING_SAMPLE
from predict import build_row, data_warnings, future_table, load_assets, score_breakdown, value_check

INDIGO, GOLD, TEAL, BRICK, INK, MUTED, LINE = "#2B3A8C", "#F2A900", "#1B998B", "#C8553D", "#1B2236", "#5B6577", "#DDE2EA"
TONES = {"indigo": INDIGO, "teal": TEAL, "gold": GOLD, "brick": BRICK}

st.set_page_config(page_title="Property Investment Advisor", page_icon="🏠", layout="wide", initial_sidebar_state="expanded")

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:wght@500;700&family=Source+Sans+3:wght@400;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Source Sans 3', 'Segoe UI', sans-serif; }
.stApp { background: #F5F7FA; color-scheme: light; }
.block-container { padding-top: 1.4rem; max-width: 1320px; }
#MainMenu, footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent; }
[data-testid="stMain"], [data-testid="stMain"] h1, [data-testid="stMain"] h2, [data-testid="stMain"] h3, [data-testid="stMain"] p,
[data-testid="stMain"] li, [data-testid="stMain"] label, [data-testid="stMain"] span, [data-testid="stMain"] summary { color: __INK__; }
[data-testid="stMain"] [data-testid="stCaptionContainer"] * { color: __MUTED__; }
[data-testid="stMain"] [data-baseweb="select"] > div, [data-testid="stMain"] [data-baseweb="input"] > div, [data-testid="stMain"] input { background: #FFFFFF; color: __INK__; }
[data-testid="stMain"] [data-baseweb="select"] *, [data-testid="stMain"] [data-baseweb="input"] * { color: __INK__; }
[data-testid^="stBaseButton-primary"], button[kind="primaryFormSubmit"], button[kind="primary"] { background: __INDIGO__; border-color: __INDIGO__; }
[data-testid^="stBaseButton-primary"] *, button[kind="primaryFormSubmit"] *, button[kind="primary"] * { color: #FFFFFF !important; }
[data-testid="stVerticalBlockBorderWrapper"] { background: #FFFFFF; border-color: __LINE__; border-radius: 6px; }
button[data-baseweb="tab"] * { color: __MUTED__; font-weight: 600; }
button[data-baseweb="tab"][aria-selected="true"] * { color: __INDIGO__; }
[data-baseweb="tab-highlight"] { background: __INDIGO__; }
section[data-testid="stSidebar"] { background: __INK__; }
section[data-testid="stSidebar"] * { color: #E8ECF4 !important; }
.brand { padding: 4px 0 14px 0; border-bottom: 1px solid #3A4260; margin-bottom: 14px; }
.brand .name { font-family: 'Bricolage Grotesque', sans-serif; font-size: 1.25rem; font-weight: 700; line-height: 1.2; }
.brand .sub { font-size: 0.8rem; opacity: 0.75; margin-top: 2px; }
.hdr { margin-bottom: 14px; padding-bottom: 10px; border-bottom: 1px solid __LINE__; }
.hdr .eyebrow { font-size: 0.75rem; letter-spacing: 0.12em; text-transform: uppercase; font-weight: 700; color: #B27F00; }
.hdr h1 { font-family: 'Bricolage Grotesque', sans-serif; font-size: 2.05rem; margin: 2px 0 2px 0; padding: 0; color: __INK__; letter-spacing: -0.01em; }
.hdr p { margin: 0; color: __MUTED__; font-size: 1.02rem; }
.sec { display: flex; align-items: baseline; gap: 12px; margin: 22px 0 8px 0; }
.sec h3 { font-family: 'Bricolage Grotesque', sans-serif; font-size: 1.2rem; margin: 0; padding: 0; color: __INK__; }
.sec span { color: __MUTED__; font-size: 0.88rem; }
.kpi { background: #FFFFFF; border: 1px solid __LINE__; border-top: 4px solid var(--c); border-radius: 6px; padding: 12px 16px 10px 16px; min-height: 108px; }
.kpi .label { color: __MUTED__; font-size: 0.72rem; letter-spacing: 0.08em; text-transform: uppercase; font-weight: 700; }
.kpi .value { color: __INK__; font-family: 'Bricolage Grotesque', sans-serif; font-size: 1.85rem; font-weight: 700; line-height: 1.25; }
.kpi .note { color: __MUTED__; font-size: 0.8rem; }
.ins { background: #FFFFFF; border: 1px solid __LINE__; border-left: 5px solid var(--c); border-radius: 6px; padding: 12px 16px; margin-bottom: 12px; min-height: 142px; }
.ins .tag { display: inline-block; background: var(--c); color: #FFFFFF !important; font-size: 0.66rem; letter-spacing: 0.1em; font-weight: 700; padding: 2px 8px; border-radius: 3px; }
.ins .tag * { color: #FFFFFF !important; }
.ins .title { color: __INK__; font-weight: 700; font-size: 1.05rem; margin: 6px 0 3px 0; }
.ins .body { color: __MUTED__; font-size: 0.93rem; line-height: 1.45; }
.take { background: #F1F4FA; border-radius: 4px; padding: 8px 12px; margin-top: 6px; font-size: 0.9rem; color: __INK__; }
.verdict { padding: 16px 20px; border-radius: 6px; background: #FFFFFF; border: 1px solid __LINE__; border-left: 8px solid var(--c); }
.verdict h2 { margin: 0 0 4px 0; font-family: 'Bricolage Grotesque', sans-serif; }
.caution { background: #FFF6DD; border-left: 5px solid __GOLD__; padding: 10px 14px; border-radius: 4px; margin: 10px 0; }
.warn { background: #FBE9E4; border-left: 5px solid __BRICK__; padding: 10px 14px; border-radius: 4px; margin: 10px 0; }
.verdict, .verdict *, .caution, .caution *, .warn, .warn *, .take, .take *, .kpi .value, .ins .title, .hdr h1, .sec h3 { color: __INK__; }
.kpi .label, .kpi .note, .ins .body, .hdr p, .sec span { color: __MUTED__; }
.hdr .eyebrow { color: #B27F00; }
.foot { color: __MUTED__; font-size: 0.8rem; margin-top: 26px; padding-top: 10px; border-top: 1px solid __LINE__; }
</style>
"""
for token, value in {"__INK__": INK, "__MUTED__": MUTED, "__INDIGO__": INDIGO, "__GOLD__": GOLD, "__BRICK__": BRICK, "__LINE__": LINE}.items():
    CSS = CSS.replace(token, value)
st.markdown(CSS, unsafe_allow_html=True)

USE_COLS = ["ID", "State", "City", "Property_Type", "BHK", "Size_in_SqFt", "Price_in_Lakhs", "Price_per_SqFt_INR", "Age_of_Property",
            "Availability_Status", "Furnished_Status", "Public_Transport_Accessibility", "Investment_Score", "Good_Investment",
            "Infrastructure_Score", "data_issue_count", "Owner_Type"]


@st.cache_data(show_spinner="Loading listings...")
def load_data():
    return pd.concat([pd.read_csv(f, usecols=USE_COLS) for f in DATA_FILES], ignore_index=True)


@st.cache_resource(show_spinner="Loading models...")
def get_assets():
    return load_assets()


@st.cache_data
def load_insights():
    return json.loads((ROOT / "insights.json").read_text())


def header(eyebrow, title, subtitle):
    st.markdown(f'<div class="hdr"><div class="eyebrow">{eyebrow}</div><h1>{title}</h1><p>{subtitle}</p></div>', unsafe_allow_html=True)


def section(title, note=""):
    st.markdown(f'<div class="sec"><h3>{title}</h3><span>{note}</span></div>', unsafe_allow_html=True)


def kpi(label, value, note="", tone="indigo"):
    st.markdown(f'<div class="kpi" style="--c:{TONES[tone]}"><div class="label">{label}</div><div class="value">{value}</div><div class="note">{note}</div></div>', unsafe_allow_html=True)


def kpi_row(items):
    for col, (label, value, note, tone) in zip(st.columns(len(items)), items):
        with col:
            kpi(label, value, note, tone)


def insight(tag, title, text, tone):
    st.markdown(f'<div class="ins" style="--c:{TONES[tone]}"><span class="tag">{tag}</span><div class="title">{title}</div><div class="body">{text}</div></div>', unsafe_allow_html=True)


def insight_grid(cards, per_row=2):
    for start in range(0, len(cards), per_row):
        for col, card in zip(st.columns(per_row), cards[start:start + per_row]):
            with col:
                insight(*card)


def takeaway(text):
    st.markdown(f'<div class="take"><b>So what:</b> {text}</div>', unsafe_allow_html=True)


def style(fig, height=340):
    fig.update_layout(template="plotly_white", height=height, margin=dict(l=10, r=10, t=48, b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#FFFFFF",
                      colorway=[INDIGO, GOLD, TEAL, BRICK, MUTED], font=dict(family="Source Sans 3, Segoe UI, sans-serif", color=INK, size=13),
                      title_font=dict(size=15, color=INK), legend=dict(orientation="h", y=-0.18, font=dict(color=INK)))
    fig.update_xaxes(color=INK, gridcolor="#E9EDF2", title_font=dict(color=INK), tickfont=dict(color=INK))
    fig.update_yaxes(color=INK, gridcolor="#E9EDF2", title_font=dict(color=INK), tickfont=dict(color=INK))
    return fig


def chart(build, height=340, note=None):
    with st.container(border=True):
        try:
            st.plotly_chart(style(build(), height), use_container_width=True, theme=None)
        except Exception as err:
            st.info("This chart could not be drawn: " + str(err)[:120])
        if note:
            takeaway(note)


def lakhs(x):
    return f"{x:,.1f} lakh" if x < 100 else f"{x / 100:,.2f} crore"


def bar_h(labels, values, title, color=INDIGO, fmt="%{x:,.1f}"):
    fig = go.Figure(go.Bar(x=values, y=labels, orientation="h", marker_color=color, text=values, texttemplate=fmt, textposition="outside"))
    fig.update_layout(title=title)
    fig.update_yaxes(autorange="reversed")
    return fig


def bar_v(labels, values, title, color=INDIGO, fmt="%{y:,.1f}", yrange=None):
    fig = go.Figure(go.Bar(x=labels, y=values, marker_color=color, text=values, texttemplate=fmt, textposition="outside"))
    fig.update_layout(title=title)
    if yrange:
        fig.update_yaxes(range=yrange)
    return fig


if not DATA_FILES:
    st.error("Data files not found. Upload housing_part_1.csv to housing_part_4.csv (or housing_sample_60k.csv) to the same folder as streamlit_app.py.")
    st.write("Files this app can see in its folder:", sorted(p.name for p in ROOT.iterdir()))
    st.stop()
if PARTS and len(PARTS) != EXPECTED_PARTS:
    st.error(f"Found {len(PARTS)} of {EXPECTED_PARTS} data parts. Upload all housing_part_1.csv to housing_part_4.csv.")
    st.write("Files this app can see in its folder:", sorted(p.name for p in ROOT.iterdir()))
    st.stop()
if not (ROOT / "insights.json").exists():
    st.error("insights.json is missing. Upload it to the same folder as streamlit_app.py.")
    st.stop()

data, assets, ins = load_data(), get_assets(), load_insights()
schema, results, quality = assets["schema"], assets["results"], assets["quality"]
reg, clf = results["regression"], results["classification"]
D, GB, LOC = ins["data"], ins["good_by"], ins["locality"]

PAGES = ["Executive summary", "Market explorer", "Data health", "Is there a signal?", "Investment checklist", "Property check", "Model report"]
st.sidebar.markdown('<div class="brand"><div class="name">Property Investment Advisor</div><div class="sub">Analyst dashboard for the business owner</div></div>', unsafe_allow_html=True)
page = st.sidebar.radio("Navigate", PAGES, label_visibility="collapsed")
st.sidebar.markdown("---")
st.sidebar.caption(f"Source: india_housing_prices.csv. {len(data):,} listings" + (" (random sample)" if USING_SAMPLE else "") + ", 42 cities, 20 states.")
if USING_SAMPLE:
    st.sidebar.caption("Report-wide figures use the full file. Charts of listings use the sample.")


def filters(df, key):
    st.sidebar.markdown("### Filters")
    states = st.sidebar.multiselect("State", sorted(df["State"].unique()), key=key + "s")
    if states:
        df = df[df["State"].isin(states)]
    cities = st.sidebar.multiselect("City", sorted(df["City"].unique()), key=key + "c")
    if cities:
        df = df[df["City"].isin(cities)]
    types = st.sidebar.multiselect("Property type", sorted(df["Property_Type"].unique()), key=key + "t")
    if types:
        df = df[df["Property_Type"].isin(types)]
    bhk = st.sidebar.slider("BHK", 1, 5, (1, 5), key=key + "b")
    price = st.sidebar.slider("Price (lakhs)", 10, 500, (10, 500), key=key + "p")
    status = st.sidebar.selectbox("Status", ["Any", "Ready_to_Move", "Under_Construction"], key=key + "u")
    df = df[df["BHK"].between(*bhk) & df["Price_in_Lakhs"].between(*price)]
    if status != "Any":
        df = df[df["Availability_Status"] == status]
    return df


def footer():
    st.markdown('<div class="foot">Growth rates and checklist weights are scenarios and rules, not results learned from sales. See "Model report" for limits.</div>', unsafe_allow_html=True)


def page_summary():
    header("Executive summary", "What the data tells us", "The main findings from the listings, in order of importance. Each one is backed by a test in the notebook.")
    sb, best = ins["size_bands"], ins["signal"][0]
    budget = GB["Budget (lakhs)"]
    kpi_row([
        ("Listings analysed", f"{D['rows']:,}", "42 cities, 20 states", "indigo"),
        ("Listings with clean data", f"{D['no_issue_pct']}%", "no impossible detail", "brick"),
        ("Pass the checklist", f"{D['pass_pct']}%", f"score of {GOOD_INVESTMENT_THRESHOLD} or more", "teal"),
        ("Pass and clean data", f"{D['clean_pass_pct']}%", f"{D['clean_pass']:,} listings: the safest shortlist", "gold"),
        ("Price model vs average", f"R2 {reg['test']['r2']:.3f}", "no gain, so no price estimates", "brick"),
    ])
    section("Key insights")
    insight_grid([
        ("RISK", "Most listings contain an impossible detail",
         f"{quality['rows_with_any_issue_pct']}% break at least one logic check. {quality['floor_no_above_total_floors_pct']}% have a floor above the building's total floors, and {quality['under_construction_but_old_pct_of_uc']}% of under-construction listings were built before 2023.", "brick"),
        ("FINDING", "Price does not follow size, city or amenities",
         f"The strongest column ({best['column']}) explains only {best['explained_pct']:.3f}% of price differences, which is what chance gives. Shuffled prices look just like the real ones.", "indigo"),
        ("RISK", "City and locality rankings are luck",
         f"When the data is re-ranked on random halves, only {LOC['avg_overlap']} of the top 5 localities stay on the list. The same locality leads in just {LOC['same_top1']} of 100 tries.", "brick"),
        ("FINDING", "The size trap",
         f"Price per sq ft falls from Rs {sb[0]['median_ppsf']:,} for small flats to Rs {sb[-1]['median_ppsf']:,} for big ones, while the median price stays near {sb[2]['median_price']:.0f} lakhs. Big flats look cheap only because of this.", "indigo"),
        ("FINDING", "The checklist works like a budget filter",
         f"{budget['10-100']}% of listings under 100 lakhs pass, against {budget['400-500']}% above 400 lakhs. Cheaper listings earn more value points.", "teal"),
        ("OPPORTUNITY", "A clean shortlist exists",
         f"{D['clean_pass']:,} listings ({D['clean_pass_pct']}%) pass the checklist and have no data problem. Start customer work here.", "gold"),
        ("FINDING", "Models: no gain on price",
         f"The price model's error is {reg['test']['rmse']:.0f} lakhs, the same as the average ({reg['baseline_test']['rmse']:.0f}). The checklist model reaches {100 * clf['test']['accuracy']:.0f}% against {100 * clf['baseline_test_accuracy']:.0f}%, but it mostly repeats our own rules.", "indigo"),
        ("ACTION", "Collect better data, then rerun",
         "Ask for real sale prices with dates, correct locations, rent and legal status. This project reruns in minutes once they arrive.", "gold"),
    ])
    section("The evidence at a glance")
    c1, c2, c3 = st.columns(3)
    with c1:
        labels = ["Floor above total floors", "Size does not fit BHK", "Under construction but old", "Price per sq ft outlier"]
        values = [quality["floor_no_above_total_floors_pct"], quality["size_not_matching_bhk_pct"], quality["under_construction_but_old_pct_of_uc"], quality["ppsf_outlier_pct"]]
        chart(lambda: bar_h(labels, values, "Listings with each problem (%)", BRICK, "%{x:.1f}%"), 300)
    with c2:
        chart(lambda: bar_v([b["band"] for b in sb], [b["median_ppsf"] for b in sb], "Median price per sq ft by size (Rs)", INDIGO, "%{y:,.0f}"), 300)
    with c3:
        chart(lambda: bar_v(list(budget.keys()), list(budget.values()), "Checklist pass rate by price (lakhs, %)", TEAL, "%{y:.1f}%"), 300)
    section("What to do next", "In order of importance")
    st.dataframe(pd.DataFrame([
        ["1", "Fix how floors, build status and location are collected", f"{quality['rows_with_any_issue_pct']}% of listings contradict themselves", "Flagged listings fall below 5%"],
        ["2", "Collect real sale prices with dates, and rent", "Price follows nothing today and there is no price history", "Price model beats the average on new sales"],
        ["3", "Pause city and locality rankings", "Top localities change in almost every random sample", "No customer complaint about a wrong ranking"],
        ["4", "Use the checklist as a first filter, with warnings", f"{D['pass_pct']}% pass. It is easy to explain", "Customers open more listings that pass"],
        ["5", "Compare flats of similar size only", "Price per sq ft changes about 6 times with size alone", "Value check agrees with agent opinion on 100 test listings"],
    ], columns=["Priority", "Action", "Why", "How to know it worked"]), hide_index=True, use_container_width=True)
    footer()


def page_explorer():
    header("Market explorer", "Prices, sizes and market mix", "Use the sidebar filters. Every chart on this page follows them.")
    view = filters(data, "ex")
    if view.empty:
        st.warning("No listings match these filters. Please widen them.")
        return
    kpi_row([
        ("Listings", f"{len(view):,}", "after filters", "indigo"),
        ("Median price", lakhs(view["Price_in_Lakhs"].median()), "middle listing", "indigo"),
        ("Median price per sq ft", f"Rs {view['Price_per_SqFt_INR'].median():,.0f}", "middle listing", "indigo"),
        ("Pass the checklist", f"{100 * view['Good_Investment'].mean():.1f}%", f"score of {GOOD_INVESTMENT_THRESHOLD} or more", "teal"),
        ("Clean data", f"{100 * (view['data_issue_count'] == 0).mean():.1f}%", "no impossible detail", "gold"),
    ])
    t1, t2, t3, t4 = st.tabs(["Prices", "Size and price", "Market mix", "City table"])
    with t1:
        choice = st.radio("Show cities with", ["Highest price per sq ft", "Lowest price per sq ft"], horizontal=True, key="ex_rank")
        city = view.groupby("City")["Price_per_SqFt_INR"].median().sort_values(ascending=choice.startswith("Lowest")).head(12).reset_index()
        a, b = st.columns(2)
        with a:
            chart(lambda: bar_h(city["City"].tolist(), city["Price_per_SqFt_INR"].round(0).tolist(), "Median price per sq ft (Rs)", INDIGO, "%{x:,.0f}"), 420,
                  "Cities differ by only a few percent, and the differences are within chance. Use this to explore, not to rank.")
        with b:
            chart(lambda: px.histogram(view, x="Price_in_Lakhs", nbins=40, title="How prices are spread (lakhs)", color_discrete_sequence=[GOLD]), 420,
                  "The spread is almost flat from 10 to 500 lakhs. Real markets bunch near the low end.")
        sample = view.sample(min(len(view), 20000), random_state=42)
        chart(lambda: px.box(sample, x="Property_Type", y="Price_per_SqFt_INR", points=False, title="Price per sq ft by property type (Rs)", color_discrete_sequence=[INDIGO]), 340,
              "Apartments, houses and villas have the same price per sq ft. In real markets they differ.")
    with t2:
        sample = view.sample(min(len(view), 12000), random_state=42)
        a, b = st.columns(2)
        with a:
            chart(lambda: px.scatter(sample, x="Size_in_SqFt", y="Price_in_Lakhs", opacity=0.25, title="Size vs price (sample)", color_discrete_sequence=[INDIGO]), 380,
                  "No upward pattern: big flats do not cost more than small ones.")
        with b:
            chart(lambda: px.scatter(sample, x="Size_in_SqFt", y="Price_per_SqFt_INR", opacity=0.25, log_y=True, title="Size vs price per sq ft (sample, log scale)", color_discrete_sequence=[GOLD]), 380,
                  "Price per sq ft drops as size grows. This is the size trap: never compare flats of different sizes by this number.")
        bhk = view.groupby("BHK")["Price_in_Lakhs"].median().round(1).reset_index()
        chart(lambda: bar_v([f"{b} BHK" for b in bhk["BHK"]], bhk["Price_in_Lakhs"].tolist(), "Median price by BHK (lakhs)", TEAL, "%{y:,.1f}", [0, 320]), 320,
              "A 5 BHK costs the same as a 1 BHK in this file. That cannot be true in a real market.")
    with t3:
        types = sorted(view["Property_Type"].unique())
        mix = pd.crosstab(view["Property_Type"], view["BHK"], normalize="index") * 100

        def mix_fig():
            fig = go.Figure()
            for b in mix.columns:
                fig.add_trace(go.Bar(name=f"{b} BHK", x=list(mix.index), y=mix[b].round(1).tolist()))
            fig.update_layout(barmode="stack", title="BHK mix within each property type (%)")
            return fig
        a, b = st.columns(2)
        with a:
            chart(mix_fig, 360, "Each property type has about 20% of every BHK size.")
        with b:
            status = view["Availability_Status"].value_counts()
            owner = view["Owner_Type"].value_counts()

            def sup_fig():
                fig = go.Figure()
                fig.add_trace(go.Bar(name="Availability", x=[s.replace("_", " ") for s in status.index], y=status.values.tolist()))
                fig.add_trace(go.Bar(name="Seller type", x=list(owner.index), y=owner.values.tolist()))
                fig.update_layout(barmode="group", title="Listings by availability and seller")
                return fig
            chart(sup_fig, 360, "Listings split almost exactly in halves and thirds. Real listings are not this even.")
    with t4:
        city_table = pd.DataFrame(ins["cities"]).rename(columns={"city": "City", "state": "State", "listings": "Listings", "mean_price": "Average price (lakhs)", "ci": "Plus or minus (lakhs)",
                                                                  "median_ppsf": "Median price per sq ft (Rs)", "good_pct": "Pass checklist (%)", "issue_pct": "Listings with a problem (%)"})
        st.caption("All listings, not affected by the filters. The 'plus or minus' column is the 95% range. Most ranges overlap, so the order is not reliable.")
        st.dataframe(city_table.sort_values("Average price (lakhs)", ascending=False), hide_index=True, use_container_width=True, height=480)
        st.download_button("Download city table (CSV)", city_table.to_csv(index=False).encode(), "city_table.csv", "text/csv")
    footer()


def page_health():
    header("Data health", "Can we trust each listing?", "The file has no missing values and no copies, but many details contradict each other.")
    kpi_row([
        ("Listings with a problem", f"{quality['rows_with_any_issue_pct']}%", "at least one logic check failed", "brick"),
        ("Floor above total floors", f"{quality['floor_no_above_total_floors_pct']}%", "impossible in real life", "brick"),
        ("Size does not fit BHK", f"{quality['size_not_matching_bhk_pct']}%", f"{D['one_bhk_over_2000_pct']}% of 1 BHK are over 2,000 sq ft", "brick"),
        ("Under construction, but old", f"{quality['under_construction_but_old_pct_of_uc']}%", "built before 2023", "brick"),
        ("Clean listings", f"{D['no_issue_pct']}%", "pass all three checks", "teal"),
    ])
    a, b = st.columns(2)
    with a:
        labels = ["Floor above total floors", "Size does not fit BHK", "Under construction but old"]
        values = [quality["floor_no_above_total_floors_pct"], quality["size_not_matching_bhk_pct"], quality["under_construction_but_old_pct_of_uc"]]
        chart(lambda: bar_h(labels, values, "Listings with each problem (%)", BRICK, "%{x:.1f}%"), 330, "Nearly half of all floor numbers are impossible. Single-listing facts cannot be trusted.")
    with b:
        by_type = ins["issues_by_type"]

        def type_fig():
            fig = go.Figure()
            for key, name in [("floor", "Floor above total"), ("size_bhk", "Size vs BHK"), ("status_age", "Status vs age")]:
                fig.add_trace(go.Bar(name=name, x=list(by_type.keys()), y=[by_type[t][key] for t in by_type]))
            fig.update_layout(barmode="group", title="Problem rate by property type (%)")
            return fig
        chart(type_fig, 330, "The rate is the same for every type. The cause is how the data was made or collected, not one property type.")
    section("Other findings")
    insight_grid([
        ("RISK", "Locality names do not point to places", f"Every locality name appears in all {LOC['cities_per_locality']} cities. A locality rank or filter has no real meaning.", "brick"),
        ("RISK", "Price per sq ft ranges from Rs " + f"{D['min_ppsf']:,} to Rs {D['max_ppsf']:,}", f"{quality['ppsf_outlier_pct']}% of listings are outliers. They come from small flats at high prices, not from typing errors.", "brick"),
        ("FINDING", "Build status and build year disagree", "Under-construction listings include buildings built as early as 1990. Use the status with care.", "indigo"),
        ("ACTION", "Fields the brief mentions but the file does not have", "Crime rate, RERA status, rent and a 'Sold' status are missing. Ask the owner for them.", "gold"),
    ], per_row=2)
    section("Examples of contradicting rows")
    bad = data[data["data_issue_count"] == data["data_issue_count"].max()].head(10)
    st.dataframe(bad[["ID", "City", "Property_Type", "BHK", "Size_in_SqFt", "Price_in_Lakhs", "Age_of_Property", "Availability_Status", "data_issue_count"]], hide_index=True, use_container_width=True)
    section("What to ask the data owner")
    st.dataframe(pd.DataFrame([
        ["Floor number and total floors", "Were they entered by hand or generated? Which one is correct?"],
        ["Build year and availability status", "Which one is the source of truth?"],
        ["Locality", "Can we get real locality names, or latitude and longitude?"],
        ["Price and size", "Are prices real sale or asking prices? Do they have dates?"],
        ["Missing items", "Rent, RERA status, builder, legal status and crime rate."],
    ], columns=["Topic", "Question"]), hide_index=True, use_container_width=True)
    footer()


def group_fig(col, title):
    items = ins["price_by"][col]
    fig = go.Figure(go.Bar(x=list(items.keys()), y=[v["mean"] for v in items.values()], marker_color=INDIGO,
                           error_y=dict(type="data", array=[v["ci"] for v in items.values()], color=MUTED)))
    fig.update_layout(title=title)
    fig.update_yaxes(range=[0, 320])
    return fig


def page_signal():
    header("Is there a signal?", "Does anything move price?", "We tested every column against price. If a real pattern existed, some column would explain a clear share of it.")
    best, sh, sb = ins["signal"][0], ins["shuffle"], ins["size_bands"]
    kpi_row([
        ("Best single column", best["column"], f"explains {best['explained_pct']:.3f}% of price", "indigo"),
        ("Expected by chance", f"{best['chance_pct']:.3f}%", "for that same column", "gold"),
        ("Real data vs shuffled prices", f"{sh['percentile']:.0f}th percentile", "inside the range of random chance", "teal"),
        ("Price model R2", f"{reg['test']['r2']:.4f}", "on listings it never saw", "brick"),
    ])
    t1, t2, t3, t4, t5 = st.tabs(["Every column", "Shuffle test", "Rankings are luck", "Size trap", "Group differences"])
    with t1:
        rows = ins["signal"][::-1]

        def signal_fig():
            fig = go.Figure()
            fig.add_trace(go.Bar(x=[r["explained_pct"] for r in rows], y=[r["column"] for r in rows], orientation="h", name="Share of price explained", marker_color=INDIGO))
            fig.add_trace(go.Scatter(x=[r["chance_pct"] for r in rows], y=[r["column"] for r in rows], mode="markers", name="Expected by chance", marker=dict(color=GOLD, size=9, symbol="diamond")))
            fig.update_layout(title="Share of price differences explained by each column (%)")
            return fig
        chart(signal_fig, 560, "No column explains even 0.02% of price. Real markets show several columns above 5%. Every diamond sits on its bar, so these results are chance.")
    with t2:
        def shuffle_fig():
            fig = px.histogram(x=sh["fake"], nbins=25, title="City-to-city spread of average price: 300 random shuffles vs the real data", color_discrete_sequence=[MUTED])
            fig.add_vline(x=sh["real"], line_color=GOLD, line_width=4, annotation_text="Real data")
            fig.update_xaxes(title_text="Spread of city averages (lakhs)")
            return fig
        chart(shuffle_fig, 380, f"We mixed up the prices at random 300 times. The real data (gold line) sits at the {sh['percentile']:.0f}th percentile, so it looks like random data.")
    with t3:
        a, b = st.columns([1, 1.3])
        with a:
            top = pd.DataFrame({"Locality": list(LOC["top5"].keys()), "Average price (lakhs)": list(LOC["top5"].values())})
            st.markdown("**The top 5 localities by average price**")
            st.dataframe(top, hide_index=True, use_container_width=True)
            insight("RISK", "Not stable", f"On 100 random halves of the data, the new top 5 shared only {LOC['avg_overlap']} of 5 names with this list. The same locality came first in {LOC['same_top1']} of 100 tries.", "brick")
        with b:
            chart(lambda: px.histogram(x=LOC["all_means"], nbins=30, title="Average price of all 500 localities (lakhs)", color_discrete_sequence=[INDIGO]), 360,
                  f"The spread between localities ({LOC['spread']}) is almost the same as pure chance ({LOC['chance_spread']}). The top 5 are a lucky draw.")
    with t4:
        a, b, c = st.columns(3)
        with a:
            chart(lambda: bar_v([x["band"] for x in sb], [x["median_ppsf"] for x in sb], "Median price per sq ft (Rs)", INDIGO, "%{y:,.0f}"), 330)
        with b:
            chart(lambda: bar_v([x["band"] for x in sb], [x["median_price"] for x in sb], "Median price (lakhs)", TEAL, "%{y:,.1f}", [0, 320]), 330)
        with c:
            chart(lambda: bar_v([x["band"] for x in sb], [x["full_value_pct"] for x in sb], "Listings with full value points (%)", GOLD, "%{y:.1f}%"), 330)
        takeaway(f"The price stays near {sb[2]['median_price']:.0f} lakhs for every size, so price per sq ft falls {sb[0]['median_ppsf'] / sb[-1]['median_ppsf']:.0f} times from small to big flats. "
                 f"The share getting full value points rises from {sb[0]['full_value_pct']}% to {sb[-1]['full_value_pct']}%. Compare flats of similar size only.")
    with t5:
        a, b = st.columns(2)
        with a:
            chart(lambda: group_fig("Furnished_Status", "Average price by furnishing (lakhs)"), 300)
        with b:
            chart(lambda: group_fig("Facing", "Average price by facing direction (lakhs)"), 300)
        a, b = st.columns(2)
        with a:
            chart(lambda: group_fig("Parking_Space", "Average price by parking (lakhs)"), 300)
        with b:
            chart(lambda: group_fig("Public_Transport_Accessibility", "Average price by public transport (lakhs)"), 300)
        takeaway("The bars look the same because they are the same. The thin lines show the 95% range and they overlap. Furnishing, facing, parking and transport do not change price here.")
    footer()


def page_checklist():
    header("Investment checklist", "How the Good Investment score works", "A clear 100-point checklist. A property passes with 60 points or more. Weights are a starting point to agree with the owner.")
    mark = st.radio("Pass mark", ["40", "50", "60", "70", "80"], index=2, horizontal=True, key="mark")
    share = ins["thresholds"][mark]
    kpi_row([
        ("Pass mark", mark, "points out of 100", "indigo"),
        ("Listings that pass", f"{share}%", f"about {int(D['rows'] * share / 100):,} listings", "teal"),
        ("Pass and clean data", f"{D['clean_pass_pct']}%", "at the standard mark of 60", "gold"),
        ("Cities differ?", "No", f"pass rate is the same in every city (p = {ins['city_good_chi_p']})", "indigo"),
    ])
    t1, t2, t3 = st.tabs(["How it scores", "Who passes", "Clean shortlist"])
    with t1:
        a, b = st.columns(2)
        pts = ins["avg_points"]
        with a:
            chart(lambda: bar_h(list(pts.keys()), list(pts.values()), "Average points earned from each item", INDIGO, "%{x:.1f}"), 340,
                  "Price versus the city median gives the most points on average, so it decides most results.")
        with b:
            thr = ins["thresholds"]
            chart(lambda: go.Figure(go.Bar(x=list(thr.keys()), y=list(thr.values()), marker_color=[GOLD if k == mark else INDIGO for k in thr], text=list(thr.values()),
                                           texttemplate="%{y:.1f}%", textposition="outside")).update_layout(title="Share of listings that pass at each mark (%)"), 340,
                  "A higher mark shrinks the list fast. Choose the mark that gives the owner a list of the size they can follow up.")
        a, b = st.columns(2)
        vp = ins["value_points_to_good"]
        with a:
            chart(lambda: bar_v([f"{k} price points" for k in vp], list(vp.values()), "Pass rate by price points earned (%)", TEAL, "%{y:.1f}%"), 330,
                  "Without price points almost nothing passes. With full price points, most listings pass.")
        with b:
            hist = ins["score_hist"]
            chart(lambda: bar_v([f"{i * 5}" for i in range(len(hist))], hist, "Number of listings by score (in steps of 5)", MUTED, "%{y:,.0f}"), 330, "Scores are spread widely. There is no natural gap that separates good from bad.")
    with t2:
        a, b = st.columns(2)
        with a:
            g = GB["Budget (lakhs)"]
            chart(lambda: bar_v(list(g.keys()), list(g.values()), "Pass rate by price band (lakhs, %)", TEAL, "%{y:.1f}%"), 330,
                  f"{g['10-100']}% of listings under 100 lakhs pass but only {g['400-500']}% above 400 lakhs. The checklist behaves like a budget filter.")
        with b:
            g = GB["Public_Transport_Accessibility"]
            chart(lambda: bar_v(list(g.keys()), list(g.values()), "Pass rate by public transport (%)", INDIGO, "%{y:.1f}%"), 330, "This gap comes from the points we give for transport. It is our rule, not a market result.")
        a, b = st.columns(2)
        with a:
            g = GB["Availability_Status"]
            chart(lambda: bar_v([k.replace("_", " ") for k in g], list(g.values()), "Pass rate by availability (%)", GOLD, "%{y:.1f}%"), 330, "Ready-to-move listings earn 15 extra points.")
        with b:
            g = GB["BHK"]
            chart(lambda: bar_v([f"{k} BHK" for k in g], list(g.values()), "Pass rate by BHK (%)", TEAL, "%{y:.1f}%"), 330, "Three BHK and above get 10 extra points, so the pass rate jumps at 3 BHK.")
    with t3:
        st.caption("Listings that pass the checklist (score 60 or more) and have no data problem. This is the safest place to start.")
        c1, c2, c3, c4 = st.columns(4)
        cities = c1.multiselect("City", sorted(data["City"].unique()), key="sl_city")
        bhk = c2.slider("BHK", 1, 5, (1, 5), key="sl_bhk")
        budget = c3.slider("Price (lakhs)", 10, 500, (10, 500), key="sl_price")
        min_score = c4.slider("Minimum score", 60, 100, 60, key="sl_score")
        short = data[(data["Good_Investment"] == 1) & (data["data_issue_count"] == 0) & (data["Investment_Score"] >= min_score)]
        short = short[short["BHK"].between(*bhk) & short["Price_in_Lakhs"].between(*budget)]
        if cities:
            short = short[short["City"].isin(cities)]
        st.markdown(f"**{len(short):,} listings match.** Showing the top 300 by score.")
        cols = ["ID", "City", "Property_Type", "BHK", "Size_in_SqFt", "Price_in_Lakhs", "Price_per_SqFt_INR", "Availability_Status", "Investment_Score"]
        top = short.sort_values(["Investment_Score", "Price_per_SqFt_INR"], ascending=[False, True]).head(300)[cols]
        st.dataframe(top, hide_index=True, use_container_width=True, height=420)
        st.download_button("Download this shortlist (CSV)", top.to_csv(index=False).encode(), "clean_shortlist.csv", "text/csv")
    footer()


def page_check():
    header("Property check", "Check one property", "Enter the details and the asking price. You get a checklist score, a price check against the city and similar sizes, and a 5-year scenario.")
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
        go_button = st.form_submit_button("Check this property", type="primary")

    if not go_button:
        st.markdown('<div class="take">Fill in the form and press <b>Check this property</b>.</div>', unsafe_allow_html=True)
        footer()
        return
    inp = {"City": city, "Property_Type": ptype, "BHK": int(bhk), "Size_in_SqFt": int(size), "Year_Built": int(year), "Furnished_Status": furnished,
           "Floor_No": int(floor), "Total_Floors": int(total_floors), "Nearby_Schools": int(schools), "Nearby_Hospitals": int(hospitals),
           "Public_Transport_Accessibility": transport, "Parking_Space": parking, "Security": security, "Facing": facing,
           "Owner_Type": owner, "Availability_Status": status, "Amenities": amenities}
    row = build_row(inp, schema)
    check = value_check(price, size, city, assets["city_medians"])
    parts, total, good = score_breakdown(inp, check["points"])
    colour = TEAL if good else BRICK
    headline = "Meets the investment checklist" if good else "Does not meet the investment checklist"
    st.markdown(f'<div class="verdict" style="--c:{colour}"><h2>{headline}</h2><p>Checklist score: <b>{total} out of 100</b>. A pass needs {GOOD_INVESTMENT_THRESHOLD}.</p></div>', unsafe_allow_html=True)
    st.markdown("")
    a, b = st.columns(2)
    with a:
        chart(lambda: bar_h(list(parts.keys()), list(parts.values()), "Where the points come from", INDIGO, "%{x:.0f}"), 340)
    with b:
        diff = (check["ratio"] - 1) * 100
        word = "below" if diff < 0 else "above"
        band = ins["size_bands"][min(int((size - 1) // 1000), 4)]
        diff_band = (check["ppsf"] / band["median_ppsf"] - 1) * 100
        word_band = "below" if diff_band < 0 else "above"
        prob = float(assets["investment_model"].predict_proba(row)[0, 1])
        with st.container(border=True):
            st.markdown(f"**Price check.** This property costs **Rs {check['ppsf']:,.0f}** per sq ft. The {city} median is **Rs {check['city_median']:,.0f}**, so it is **{abs(diff):.0f}% {word}** the city median.")
            st.markdown(f"**Fairer check for its size.** Listings of {band['band']} sq ft have a median of **Rs {band['median_ppsf']:,}** per sq ft. This property is **{abs(diff_band):.0f}% {word_band}** that. Use this one when the flat is much bigger or smaller than usual.")
            st.markdown(f"**Checklist model.** It gives a **{100 * prob:.0f}%** chance of passing, without using the price. It mostly repeats the checklist rules and the size effect, so treat it as a cross-check only.")
    notes = data_warnings(row)
    if notes:
        st.markdown('<div class="warn"><b>Data warnings for these inputs:</b> ' + " ".join(notes) + "</div>", unsafe_allow_html=True)
    section(f"Value in {FORECAST_YEARS} years", "Scenarios, not predictions")
    fut = future_table(price)
    years = list(range(FORECAST_YEARS + 1))

    def future_fig():
        fig = go.Figure()
        for (name, rate), colr in zip(GROWTH_SCENARIOS.items(), [MUTED, INDIGO, GOLD]):
            fig.add_trace(go.Scatter(x=years, y=[price * (1 + rate) ** y for y in years], mode="lines+markers", name=name, line=dict(color=colr, width=3)))
        fig.update_layout(title="Price path for each growth scenario (lakhs)", xaxis_title="Years from today")
        return fig
    a, b = st.columns([1.3, 1])
    with a:
        chart(future_fig, 340)
    with b:
        table = pd.DataFrame({"Scenario": list(fut.keys()), f"Price in {FORECAST_YEARS} years": [lakhs(v) for v in fut.values()], "Gain": [lakhs(v - price) for v in fut.values()]})
        st.dataframe(table, hide_index=True, use_container_width=True)
        st.markdown('<div class="caution">Growth rates are our scenarios. The file has no price history. Replace them with local figures before deciding.</div>', unsafe_allow_html=True)
    footer()


def page_models():
    header("Model report", "What the models can and cannot do", "Every model is compared with a simple guess, on listings it never saw.")
    sig = results["signal_test_price"]
    kpi_row([
        ("Price model error", f"{reg['test']['rmse']:.0f} lakhs", f"the average guess: {reg['baseline_test']['rmse']:.0f}", "brick"),
        ("Checklist model accuracy", f"{100 * clf['test']['accuracy']:.1f}%", f"always guessing no: {100 * clf['baseline_test_accuracy']:.1f}%", "indigo"),
        ("On cities it never saw", f"{100 * clf['unseen_city_test']['accuracy']:.1f}%", "checklist model accuracy", "teal"),
        ("Cheaper than city median?", f"{100 * sig['accuracy']:.1f}%", f"coin flip is {100 * sig['baseline_accuracy']:.1f}%", "brick"),
    ])
    t1, t2, t3, t4 = st.tabs(["Models vs a simple guess", "How well it works", "What drives it", "Limits and next steps"])
    with t1:
        a, b = st.columns(2)
        cr = pd.DataFrame(ins["cv_regression"])
        cc = pd.DataFrame(ins["cv_classification"])
        with a:
            chart(lambda: bar_h(cr["model"].tolist(), cr["rmse_mean"].round(2).tolist(), "Price models: error in lakhs (lower is better)", MUTED, "%{x:,.2f}"), 330, "Every price model is level with the average guess. More complex models give no gain.")
        with b:
            chart(lambda: bar_h(cc["model"].tolist(), (100 * cc["acc_mean"]).round(1).tolist(), "Checklist models: accuracy % (higher is better)", INDIGO, "%{x:.1f}%"), 330, "The gain over guessing comes from rules we built into the label.")
        st.dataframe(pd.DataFrame([
            ["Price (lakhs)", f"error {reg['test']['rmse']:.1f}, R2 {reg['test']['r2']:.4f}", f"error {reg['baseline_test']['rmse']:.1f}", "No gain. Do not use for valuation."],
            ["Good Investment", f"accuracy {100 * clf['test']['accuracy']:.1f}%, F1 {clf['test']['f1']:.2f}, AUC {clf['test']['roc_auc']:.2f}", f"accuracy {100 * clf['baseline_test_accuracy']:.1f}%", "Learns our rules and the size effect."],
            ["Cheaper than city median price", f"accuracy {100 * sig['accuracy']:.1f}%, AUC {sig['roc_auc']:.2f}", f"accuracy {100 * sig['baseline_accuracy']:.1f}%", "No pattern to learn."],
        ], columns=["Task", "Model result (unseen listings)", "Simple guess", "Verdict"]), hide_index=True, use_container_width=True)
    with t2:
        a, b = st.columns(2)
        cm = clf["confusion_matrix"]

        def cm_fig():
            fig = go.Figure(go.Heatmap(z=cm, x=["Predicted not good", "Predicted good"], y=["Actually not good", "Actually good"], colorscale="Blues", showscale=False,
                                       text=[[f"{v:,}" for v in r] for r in cm], texttemplate="%{text}"))
            fig.update_layout(title="Checklist model: confusion matrix (test set)")
            fig.update_yaxes(autorange="reversed")
            return fig
        with a:
            chart(cm_fig, 360)
        sub = pd.DataFrame(results["subgroups_clf"])
        sub["label"] = sub["group"].str.replace("_", " ") + ": " + sub["value"].astype(str).str.replace("_", " ")
        sub = sub.sort_values("accuracy")
        with b:
            chart(lambda: bar_h(sub["label"].tolist(), (100 * sub["accuracy"]).round(1).tolist(), "Accuracy by group (%)", TEAL, "%{x:.1f}%"), 360, "Accuracy differs by transport and availability because those items are part of the checklist rules.")
        ci = clf["accuracy_95ci"]
        takeaway(f"95% range for accuracy: {100 * ci[0]:.1f}% to {100 * ci[1]:.1f}%. Train accuracy is {100 * clf['train_sample']['accuracy']:.1f}%, so the model is not overfitting. Price model R2 range: {reg['r2_95ci'][0]} to {reg['r2_95ci'][1]}.")
    with t3:
        imp = pd.read_csv(ROOT / "feature_importance.csv")
        a, b = st.columns(2)
        for col, task, title in [(a, "good_investment", "Checklist model: top features"), (b, "price", "Price model: top features")]:
            top = imp[imp["task"] == task].nlargest(8, "importance")
            with col:
                chart(lambda t=top, ti=title: bar_h(t["feature"].tolist(), t["importance"].round(4).tolist(), ti, INDIGO, "%{x:.3f}"), 360,
                      "Size is the top input. This is the size trap at work." if task == "good_investment" else "All values are close to zero. No feature helps.")
    with t4:
        st.markdown("**Limits to tell the owner**")
        st.markdown(
            "- The prices look random, so no model can predict them from this file.\n"
            "- The Good Investment label is our rule. Nobody checked whether those properties made money.\n"
            "- The 5-year value is a scenario. There is no price history.\n"
            "- The checklist favours ready-to-move, well-connected and large properties by design.\n"
            "- Crime rate, rent and RERA status are not in the file."
        )
        st.markdown("**Running it for real**")
        st.dataframe(pd.DataFrame([
            ["Refresh", "Monthly, or when new sale data arrives"],
            ["Monitor", "Share of flagged listings, price spread, and model error against the simple average. Alert if the model stops beating it."],
            ["Retrain", "Every quarter, or when an alert fires. Compare with the old model before replacing it."],
            ["Scale", "250,000 rows run on a laptop. For millions of rows, use a database and cached queries."],
            ["Connect", "Call the checklist and price check from the owner's website or CRM."],
        ], columns=["Step", "Plan"]), hide_index=True, use_container_width=True)
    footer()


{"Executive summary": page_summary, "Market explorer": page_explorer, "Data health": page_health, "Is there a signal?": page_signal,
 "Investment checklist": page_checklist, "Property check": page_check, "Model report": page_models}[page]()
