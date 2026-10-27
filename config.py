from pathlib import Path

ROOT = Path(__file__).resolve().parent
CLEAN_FILE = ROOT / "housing_clean.csv.gz"
MODEL_DIR = ROOT
REPORT_DIR = ROOT

CURRENT_YEAR = 2025
GOOD_INVESTMENT_THRESHOLD = 60
GROWTH_SCENARIOS = {"Cautious (5% a year)": 0.05, "Base (8% a year)": 0.08, "Optimistic (10% a year)": 0.10}
FORECAST_YEARS = 5

AMENITY_LIST = ["Clubhouse", "Garden", "Gym", "Playground", "Pool"]
TRANSPORT_POINTS = {"High": 15, "Medium": 8, "Low": 0}
