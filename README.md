# NYC 311 Service Request Data Analysis

## Overview
This project analyzes NYC 311 service request data to identify complaint patterns, response times, and geographic distributions across New York City boroughs.

## Project Structure
```
├── nyc311.db                    # SQLite database with raw and cleaned data
├── nyc311_sql_tasks.sql         # SQL cleaning and transformation queries
├── NYC311_analysis.ipynb        # Main analysis notebook
├── nyc311_profile.html          # Automated data profiling report
├── Report.pdf                   # Summary report of findings
├── setup_database.py            # Database setup script
└── README.md                    # This file
```

## Prerequisites
- Python 3.9+
- Required libraries: pandas, numpy, sqlalchemy, matplotlib, seaborn, scipy, statsmodels, ydata_profiling

## Installation
```bash
pip install pandas numpy sqlalchemy matplotlib seaborn scipy statsmodels ydata-profiling jupyter
```

## How to Reproduce

### Step 1: Database Setup
If the database doesn't exist, run:
```bash
python setup_database.py
```
This imports the CSV data and creates the cleaned analytical table.

### Step 2: Run Analysis
Open and execute the Jupyter notebook:
```bash
jupyter notebook NYC311_analysis.ipynb
```

### Step 3: Generate Profiling Report
The notebook generates `nyc311_profile.html` automatically when executed.

## Data Description
- **Source**: NYC Open Data - 311 Service Requests
- **Records**: 364,558 service requests
- **Key Fields**: Complaint type, borough, dates, coordinates, status

## Key Findings
1. Brooklyn has the highest complaint volume (118,864 requests)
2. HEAT/HOT WATER is the most common complaint type
3. Statistically significant differences in response times across boroughs
4. Strong association between complaint types and boroughs

## Deliverables
- `nyc311_sql_tasks.sql` - Documented SQL queries
- `NYC311_analysis.ipynb` - Complete Python analysis
- `nyc311_profile.html` - Automated profiling report
- `Report.pdf` - Executive summary

## Author
GET 305 Data Analysis Assignment
