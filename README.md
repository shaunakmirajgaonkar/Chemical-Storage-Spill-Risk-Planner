# 🧪 Chemical Storage Spill-Risk Planner

Advanced 100% local-first Streamlit dashboard for screening potential chemical-storage spill-risk signals using inventory, storage conditions, containment, weather exposure, inspection history, operations, and nearby population data.

## Features

- Explainable 0–100 spill-risk screening score
- Low / Moderate / High / Critical classification
- Facility risk mapping
- Storage and containment analysis
- Weather-exposure analytics
- Inspection monitoring
- Transfer-activity analysis
- Nearby-population exposure
- Regional benchmarking
- Spill-risk priority ranking
- Historical risk trends
- Rule-based operational alerts
- What-if scenario studio
- Local CSV upload and filters

## Technology

Python • Streamlit • Pandas • NumPy • Plotly

## Run

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

No external APIs are required. Processing stays local. Sample data is synthetic.

## Disclaimer

This is a screening and decision-support tool. It does not predict an actual spill, certify storage safety, replace qualified professionals, or supersede applicable laws and safety standards.
