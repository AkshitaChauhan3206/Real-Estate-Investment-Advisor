# Property Investment Advisor - Streamlit app

All files are in this one folder. Do not move them into sub-folders.

| File | Purpose |
|---|---|
| streamlit_app.py | The dashboard (main file) |
| config.py | File paths and settings |
| predict.py | Score, price check, 5-year scenario and data-warning functions |
| housing_part_1.csv to housing_part_4.csv | The cleaned listings, all 250,000 rows, split into 4 files of about 7 MB each so GitHub accepts them |
| housing_sample_60k.csv | Backup: random sample of 60,000 listings (5 MB). Used only if the four parts are missing |
| investment_model.joblib | Good Investment model |
| price_model.joblib | Price model (shown only to prove it is no better than the average) |
| app_schema.json | Dropdown choices and the model input list |
| model_results.json | Model numbers shown in the app |
| city_medians.json | Median price per sq ft for each city |
| data_quality_report.json | Data-problem numbers |
| feature_importance.csv | Data for the "what the model uses most" chart |
| requirements.txt | Libraries to install |

## Run on your computer

1. Use Python 3.11, 3.12 or 3.13.
2. Open a terminal in this folder and run `python -m venv .venv`
3. Activate it. Windows: `.venv\Scripts\activate`. Mac or Linux: `source .venv/bin/activate`
4. Run `pip install -r requirements.txt`
5. Run `streamlit run streamlit_app.py`

The first load takes a few seconds. After that it is cached.

## Deploy on Streamlit Community Cloud

1. Upload all these files to one GitHub repository, in the main folder (no sub-folders).
2. Go to share.streamlit.io and choose "Create app".
3. Main file path: `streamlit_app.py`
4. Advanced settings: choose Python 3.12.
5. Deploy.

## Data files

Upload all four `housing_part_*.csv` files. The app joins them. If you upload only `housing_sample_60k.csv`, the app runs on the 60,000-row sample and says so in the sidebar.

If you see "Data files not found", the app also prints the list of files it can see. Compare it with the table above.

Use the zip file to get the files. Some browsers silently unpack single downloaded `.gz` files, which is why this version uses plain `.csv` files.

## Colours in dark mode (optional but recommended)

The dashboard is designed for a light page. The app now sets its own text and chart colours, so it stays readable when your browser or computer is in dark mode. To lock the light theme completely, create one extra file in your GitHub repository. Click "Add file", then "Create new file", type `.streamlit/config.toml` as the name (typing the slash makes the folder), and paste this:

```
[theme]
base = "light"
primaryColor = "#2B3A8C"
backgroundColor = "#F4F6F8"
secondaryBackgroundColor = "#FFFFFF"
textColor = "#1B2236"
```

## If the models do not load

The models were trained with scikit-learn 1.8.0, which is pinned in requirements.txt. If you change that version, retrain in the full project and replace the two .joblib files.
