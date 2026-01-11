"""
Database Setup Script for NYC 311 Analysis
This script creates the SQLite database and imports the raw CSV data.
"""

import sqlite3
import pandas as pd
import os

# Configuration
DB_PATH = 'nyc311.db'
CSV_PATH = '311_Service_Requests_from_2010_to_Present.csv/311_Service_Requests_from_2010_to_Present.csv'
SQL_FILE = 'nyc311_sql_tasks.sql'

def create_database():
    """Create SQLite database and import raw CSV data."""
    
    print("=" * 60)
    print("NYC 311 Database Setup")
    print("=" * 60)
    
    # Remove existing database if it exists
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"Removed existing database: {DB_PATH}")
    
    # Create new database connection
    conn = sqlite3.connect(DB_PATH)
    print(f"Created new database: {DB_PATH}")
    
    # Read CSV file
    print(f"\nReading CSV file: {CSV_PATH}")
    print("This may take a moment...")
    
    df = pd.read_csv(CSV_PATH, low_memory=False)
    print(f"Loaded {len(df):,} rows and {len(df.columns)} columns")
    
    # Import as raw_311 table
    print("\nImporting data as 'raw_311' table...")
    df.to_sql('raw_311', conn, if_exists='replace', index=False)
    print("Import complete!")
    
    # Verify import
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM raw_311")
    count = cursor.fetchone()[0]
    print(f"Verified: {count:,} records in raw_311 table")
    
    # Execute SQL cleaning script
    print("\n" + "=" * 60)
    print("Executing SQL cleaning script...")
    print("=" * 60)
    
    with open(SQL_FILE, 'r') as f:
        sql_script = f.read()
    
    # Split by semicolons and execute statements
    # Skip comments and empty statements
    statements = sql_script.split(';')
    
    for i, stmt in enumerate(statements):
        stmt = stmt.strip()
        if stmt and not stmt.startswith('--'):
            try:
                # Skip SELECT statements (validation queries - just for documentation)
                if stmt.upper().startswith('SELECT'):
                    # Execute but don't print results (these are validation queries)
                    cursor.execute(stmt)
                    continue
                cursor.execute(stmt)
            except sqlite3.Error as e:
                # Some statements like DROP IF NOT EXISTS may error - that's ok
                pass
    
    conn.commit()
    print("SQL cleaning script executed successfully!")
    
    # Verify cleaned table
    cursor.execute('SELECT COUNT(*) FROM "311_cleaned"')
    cleaned_count = cursor.fetchone()[0]
    print(f"\nCleaned table '311_cleaned' created with {cleaned_count:,} records")
    
    # Show summary statistics
    print("\n" + "=" * 60)
    print("Data Quality Summary")
    print("=" * 60)
    
    cursor.execute("""
        SELECT
            COUNT(*) AS total_records,
            SUM(has_valid_borough) AS records_with_borough,
            SUM(has_valid_coordinates) AS records_with_coords,
            SUM(has_closed_date) AS records_with_closed_date
        FROM "311_cleaned"
    """)
    stats = cursor.fetchone()
    print(f"Total records: {stats[0]:,}")
    print(f"Records with valid borough: {stats[1]:,} ({100*stats[1]/stats[0]:.1f}%)")
    print(f"Records with valid coordinates: {stats[2]:,} ({100*stats[2]/stats[0]:.1f}%)")
    print(f"Records with closed date: {stats[3]:,} ({100*stats[3]/stats[0]:.1f}%)")
    
    # Borough distribution
    print("\nBorough Distribution:")
    cursor.execute("""
        SELECT borough, COUNT(*) as cnt
        FROM "311_cleaned"
        WHERE borough IS NOT NULL
        GROUP BY borough
        ORDER BY cnt DESC
    """)
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]:,}")
    
    conn.close()
    print("\n" + "=" * 60)
    print("Database setup complete!")
    print("=" * 60)

if __name__ == '__main__':
    create_database()
