# NYC 311 Service Request Data Analysis

## Overview
Comprehensive analysis of NYC 311 service request data to identify complaint patterns, response times, and geographic distributions across New York City boroughs.

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the full analysis pipeline
python main.py
```

This generates:
- **dashboard.html** - Interactive HTML dashboard with all charts embedded
- **Report.pdf** - Executive summary

## Project Structure
```
GET_305_Data_Analysis/
├── main.py                 # ⭐ MAIN ENTRY POINT
├── requirements.txt        # Python dependencies
├── README.md               # This file
├── NYC311_analysis.ipynb   # Detailed Jupyter notebook
├── nyc311_sql_tasks.sql    # SQL cleaning queries
├── setup_database.py       # Database setup module
├── generate_dashboard.py   # HTML dashboard generator (frontend)
├── generate_report.py      # PDF report module
├── .gitignore              # Git ignore rules
└── 311_Service_Requests_from_2010_to_Present.csv/  # Raw data
```

## Usage

### Full Pipeline (Recommended)
```bash
python main.py
```

### Individual Steps
```bash
python main.py --setup      # Setup database only
python main.py --dashboard  # Generate HTML dashboard only
python main.py --report     # Generate PDF report only
python main.py --help       # Show all options
```

### Jupyter Notebook
For interactive analysis:
```bash
jupyter notebook NYC311_analysis.ipynb
```

## Generated Outputs

| File | Description |
|------|-------------|
| `nyc311.db` | SQLite database with raw and cleaned data |
| `dashboard.html` | **📊 HTML dashboard with embedded charts** |
| `Report.pdf` | Executive summary PDF |

## Dashboard Features
The `dashboard.html` is a professional frontend that includes:
- 📈 Time series of complaint volume
- 📋 Top 10 complaint types
- 🗺️ Geographic distribution map
- ⏱️ Response time analysis
- 📊 Borough comparison
- 🕐 Hourly patterns

**All charts are embedded directly in the HTML** - no separate image files!

## Data Pipeline
```
Raw CSV → SQLite (raw_311) → SQL Cleaning → 311_cleaned → Dashboard + Report
```

## Key Findings
1. Brooklyn has the highest complaint volume (~118,864 requests)
2. HEAT/HOT WATER is the most common complaint type
3. Significant differences in response times across boroughs (p < 0.05)
4. Strong association between complaint types and boroughs (p < 0.001)

## Requirements
- Python 3.9+
- See `requirements.txt` for dependencies

## Author
GET 305 Data Analysis Assignment
