# Property Investment Advisor - Streamlit app

All files are in this one folder. Do not move them into sub-folders.

| File | Purpose |
|---|---|
| streamlit_app.py | The dashboard (main file) |
| config.py | File paths and settings |
| predict.py | Score, price check, 5-year scenario and data-warning functions |
| housing_clean.csv.gz | Cleaned listings (250,000 rows) |
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

The first load takes a few seconds because it reads 250,000 rows. After that it is cached.

## Deploy on Streamlit Community Cloud

1. Upload all these files to one GitHub repository, in the main folder (no sub-folders).
2. Go to share.streamlit.io and choose "Create app".
3. Main file path: `streamlit_app.py`
4. Advanced settings: choose Python 3.12.
5. Deploy.

## If the models do not load

The models were trained with scikit-learn 1.8.0, which is pinned in requirements.txt. If you change that version, retrain in the full project and replace the two .joblib files.
