"""
NYC 311 Data Analysis - Main Entry Point
=========================================
This is the standard way to run the complete analysis pipeline.

Usage:
    python main.py              # Run full pipeline
    python main.py --setup      # Setup database only
    python main.py --dashboard  # Generate HTML dashboard only
    python main.py --report     # Generate PDF report only
    python main.py --help       # Show help
"""

import argparse
import os
import sys


def check_csv_exists():
    """Check if the source CSV file exists."""
    csv_path = '311_Service_Requests_from_2010_to_Present.csv/311_Service_Requests_from_2010_to_Present.csv'
    if not os.path.exists(csv_path):
        print("ERROR: CSV data file not found!")
        print(f"Expected path: {csv_path}")
        print("\nPlease download the NYC 311 data from NYC Open Data.")
        return False
    return True


def check_database_exists():
    """Check if the database exists."""
    return os.path.exists('nyc311.db')


def run_setup():
    """Run database setup."""
    print("\n" + "=" * 60)
    print("STEP 1: DATABASE SETUP")
    print("=" * 60)
    
    if not check_csv_exists():
        return False
    
    import setup_database
    setup_database.create_database()
    return True


def run_dashboard():
    """Generate HTML dashboard with embedded charts."""
    print("\n" + "=" * 60)
    print("STEP 2: GENERATING HTML DASHBOARD")
    print("=" * 60)
    
    if not check_database_exists():
        print("ERROR: Database not found. Run with --setup first.")
        return False
    
    import generate_dashboard
    generate_dashboard.main()
    return True


def run_report():
    """Generate PDF report."""
    print("\n" + "=" * 60)
    print("STEP 3: GENERATING PDF REPORT")
    print("=" * 60)
    
    if not check_database_exists():
        print("ERROR: Database not found. Run with --setup first.")
        return False
    
    import generate_report
    generate_report.generate_report()
    return True


def run_full_pipeline():
    """Run the complete analysis pipeline."""
    print("=" * 60)
    print("NYC 311 DATA ANALYSIS - FULL PIPELINE")
    print("=" * 60)
    print("\nThis will run the complete analysis pipeline:")
    print("  1. Setup database (import CSV, run SQL cleaning)")
    print("  2. Generate HTML dashboard (with embedded charts)")
    print("  3. Generate PDF report")
    print()
    
    # Step 1: Setup
    if not check_database_exists():
        if not run_setup():
            return False
    else:
        print("\nDatabase already exists. Skipping setup.")
        print("(To rebuild, delete nyc311.db and run again)")
    
    # Step 2: Dashboard
    run_dashboard()
    
    # Step 3: Report
    run_report()
    
    # Summary
    print("\n" + "=" * 60)
    print("PIPELINE COMPLETE!")
    print("=" * 60)
    print("\nGenerated outputs:")
    outputs = [
        ('nyc311.db', 'SQLite database with raw and cleaned data'),
        ('nyc311_profile.html', 'Interactive HTML profiling dashboard with charts'),
        ('Report.pdf', 'Executive summary PDF'),
    ]
    
    for filename, description in outputs:
        exists = "✓" if os.path.exists(filename) else "✗"
        print(f"  {exists} {filename} - {description}")
    
    print("\nOpen nyc311_profile.html in your browser to view the analysis.")
    print("For detailed analysis, open: NYC311_analysis.ipynb")
    return True


def main():
    parser = argparse.ArgumentParser(
        description='NYC 311 Data Analysis Pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py              Run full pipeline
  python main.py --setup      Setup database from CSV
  python main.py --dashboard  Generate HTML dashboard
  python main.py --report     Generate PDF summary report
        """
    )
    
    parser.add_argument('--setup', action='store_true',
                        help='Setup database (import CSV and run SQL cleaning)')
    parser.add_argument('--dashboard', action='store_true',
                        help='Generate HTML dashboard with embedded charts')
    parser.add_argument('--report', action='store_true',
                        help='Generate PDF summary report')
    
    args = parser.parse_args()
    
    # If no specific flag, run full pipeline
    if not any([args.setup, args.dashboard, args.report]):
        run_full_pipeline()
    else:
        if args.setup:
            run_setup()
        if args.dashboard:
            run_dashboard()
        if args.report:
            run_report()


if __name__ == '__main__':
    main()
