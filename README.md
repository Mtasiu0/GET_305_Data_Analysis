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
- **nyc311_profile.html** - Interactive HTML profiling report with all charts embedded
- **Report.pdf** - Executive summary

## Project Structure
```
GET_305_Data_Analysis/
├── main.py                 # ⭐ MAIN ENTRY POINT
├── requirements.txt        # Python dependencies
├── README.md               # This file
├── NYC311_analysis.ipynb   # Detailed Jupyter notebook with statistics
├── nyc311_sql_tasks.sql    # SQL cleaning queries
├── setup_database.py       # Database setup module
├── generate_dashboard.py   # HTML profiling report generator
├── generate_report.py      # PDF report module
├── nyc311_profile.html     # Generated profiling report
├── Report.pdf              # Generated PDF report
└── .gitignore              # Git ignore rules
```

## Usage

### Full Pipeline (Recommended)
```bash
python main.py
```

### Individual Steps
```bash
python main.py --setup      # Setup database only
python main.py --dashboard  # Generate HTML profiling report only
python main.py --report     # Generate PDF report only
python main.py --help       # Show all options
```

### Jupyter Notebook
For interactive analysis with statistics:
```bash
jupyter notebook NYC311_analysis.ipynb
```

## Generated Outputs

| File | Description |
|------|-------------|
| `nyc311.db` | SQLite database with raw and cleaned data |
| `nyc311_profile.html` | **📊 HTML profiling report with embedded charts** |
| `Report.pdf` | Executive summary PDF |

## Profiling Report Features
The `nyc311_profile.html` includes:
- 📈 Time series of complaint volume
- 📋 Top 10 complaint types
- 🗺️ Geographic distribution map
- ⏱️ Response time analysis
- 📊 Borough comparison
- 🕐 Hourly patterns
- 📉 Data quality statistics

All charts are embedded directly in the HTML - no separate image files!

## Data Pipeline
```
Raw CSV → SQLite (raw_311) → SQL Cleaning → 311_cleaned → Profiling + Report
```

## Key Findings
1. Brooklyn has the highest complaint volume (~118,864 requests)
2. HEAT/HOT WATER is the most common complaint type
3. Significant differences in response times across boroughs (p < 0.05)
4. Strong association between complaint types and boroughs (p < 0.001)

## Statistical Analysis (in Notebook)
- **Hypothesis Test 1**: Two-sample t-test (Manhattan vs Brooklyn response times)
- **Hypothesis Test 2**: Chi-square test of independence (complaint type × borough)
- **Correlation Analysis**: Pearson and Spearman coefficients
- **Regression**: OLS model predicting response time

## Requirements
- Python 3.9+
- See `requirements.txt` for dependencies

## Author
GET 305 Data Analysis Assignment
