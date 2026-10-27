import json

import joblib
import pandas as pd

from config import (AMENITY_LIST, CURRENT_YEAR, FORECAST_YEARS, GOOD_INVESTMENT_THRESHOLD, GROWTH_SCENARIOS,
                    MODEL_DIR, REPORT_DIR, TRANSPORT_POINTS)


def load_assets():
    assets = {
        "schema": json.loads((MODEL_DIR / "app_schema.json").read_text()),
        "results": json.loads((REPORT_DIR / "model_results.json").read_text()),
        "city_medians": json.loads((REPORT_DIR / "city_medians.json").read_text()),
        "quality": json.loads((REPORT_DIR / "data_quality_report.json").read_text()),
    }
    assets["price_model"] = joblib.load(MODEL_DIR / "price_model.joblib")
    assets["investment_model"] = joblib.load(MODEL_DIR / "investment_model.joblib")
    return assets


def build_row(inp, schema):
    age = CURRENT_YEAR - inp["Year_Built"]
    amenities = set(inp["Amenities"])
    row = dict(inp)
    row["Age_of_Property"] = age
    for name in AMENITY_LIST:
        row["Has_" + name] = int(name in amenities)
    row["Amenity_Count"] = len(amenities & set(AMENITY_LIST))
    row["Sqft_per_BHK"] = inp["Size_in_SqFt"] / inp["BHK"]
    row["Is_Ready"] = int(inp["Availability_Status"] == "Ready_to_Move")
    transport = {"High": 30, "Medium": 15, "Low": 0}[inp["Public_Transport_Accessibility"]]
    row["Infrastructure_Score"] = round(inp["Nearby_Schools"] / 10 * 40 + inp["Nearby_Hospitals"] / 10 * 30 + transport, 1)
    row["floor_invalid"] = int(inp["Floor_No"] > inp["Total_Floors"])
    row["size_bhk_mismatch"] = int(row["Sqft_per_BHK"] < 250 or row["Sqft_per_BHK"] > 1500)
    row["status_age_conflict"] = int(inp["Availability_Status"] == "Under_Construction" and age > 2)
    row["data_issue_count"] = row["floor_invalid"] + row["size_bhk_mismatch"] + row["status_age_conflict"]
    return pd.DataFrame([row])[schema["features"]]


def value_check(price_lakhs, size_sqft, city, city_medians):
    ppsf = price_lakhs * 100000 / size_sqft
    median = city_medians[city]
    ratio = ppsf / median
    points = 40 if ratio <= 1.0 else 20 if ratio <= 1.15 else 0
    return {"ppsf": ppsf, "city_median": median, "ratio": ratio, "points": points}


def score_breakdown(inp, value_points):
    schools = 10 if inp["Nearby_Schools"] >= 7 else 5 if inp["Nearby_Schools"] >= 5 else 0
    hospitals = 10 if inp["Nearby_Hospitals"] >= 7 else 5 if inp["Nearby_Hospitals"] >= 5 else 0
    parts = {
        "Price compared with city median": value_points,
        "Ready to move in": 15 if inp["Availability_Status"] == "Ready_to_Move" else 0,
        "Public transport": TRANSPORT_POINTS[inp["Public_Transport_Accessibility"]],
        "Schools nearby": schools,
        "Hospitals nearby": hospitals,
        "3 or more BHK": 10 if inp["BHK"] >= 3 else 0,
    }
    total = sum(parts.values())
    return parts, total, total >= GOOD_INVESTMENT_THRESHOLD


def future_table(price_lakhs):
    return {name: price_lakhs * (1 + rate) ** FORECAST_YEARS for name, rate in GROWTH_SCENARIOS.items()}


def data_warnings(row):
    notes = []
    if row["floor_invalid"].iloc[0]:
        notes.append("Floor number is higher than total floors.")
    if row["size_bhk_mismatch"].iloc[0]:
        notes.append("Size does not look normal for this number of BHK.")
    if row["status_age_conflict"].iloc[0]:
        notes.append("Property is marked under construction but is more than 2 years old.")
    return notes
