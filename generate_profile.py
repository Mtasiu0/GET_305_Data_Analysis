"""Generate profiling report for NYC 311 data."""
import sqlite3
import pandas as pd
from ydata_profiling import ProfileReport

# Load cleaned data (sample for performance)
conn = sqlite3.connect('nyc311.db')
df = pd.read_sql('SELECT * FROM "311_cleaned" LIMIT 30000', conn)
conn.close()

print(f"Loaded {len(df)} records for profiling...")

# Generate profile
profile = ProfileReport(df, title='NYC 311 Data Profiling Report', minimal=True)
profile.to_file('nyc311_profile.html')
print('nyc311_profile.html generated successfully!')
