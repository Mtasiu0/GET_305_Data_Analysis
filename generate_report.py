"""
Generate Report.pdf for NYC 311 Data Analysis Assignment
"""
from fpdf import FPDF
import sqlite3

class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'NYC 311 Service Request Data Analysis Report', 0, 1, 'C')
        self.ln(5)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')
    
    def chapter_title(self, title):
        self.set_font('Arial', 'B', 11)
        self.set_fill_color(200, 220, 255)
        self.cell(0, 8, title, 0, 1, 'L', True)
        self.ln(2)
    
    def chapter_body(self, body):
        self.set_font('Arial', '', 10)
        self.multi_cell(0, 5, body)
        self.ln(3)

def get_stats():
    """Get statistics from database."""
    conn = sqlite3.connect('nyc311.db')
    cursor = conn.cursor()
    
    # Total records
    cursor.execute('SELECT COUNT(*) FROM "311_cleaned"')
    total = cursor.fetchone()[0]
    
    # Borough distribution
    cursor.execute('''
        SELECT borough, COUNT(*) as cnt 
        FROM "311_cleaned" 
        WHERE borough IS NOT NULL 
        GROUP BY borough 
        ORDER BY cnt DESC
    ''')
    boroughs = cursor.fetchall()
    
    # Top complaints
    cursor.execute('''
        SELECT complaint_type, COUNT(*) as cnt 
        FROM "311_cleaned" 
        GROUP BY complaint_type 
        ORDER BY cnt DESC 
        LIMIT 5
    ''')
    complaints = cursor.fetchall()
    
    # Data quality
    cursor.execute('''
        SELECT 
            SUM(has_valid_borough) as valid_borough,
            SUM(has_valid_coordinates) as valid_coords,
            SUM(has_closed_date) as has_closed
        FROM "311_cleaned"
    ''')
    quality = cursor.fetchone()
    
    conn.close()
    return total, boroughs, complaints, quality

def generate_report():
    """Generate the PDF report."""
    total, boroughs, complaints, quality = get_stats()
    
    pdf = PDFReport()
    pdf.add_page()
    
    # Executive Summary
    pdf.chapter_title('1. Executive Summary')
    summary = f"""This report presents a comprehensive analysis of NYC 311 service request data comprising {total:,} records. The analysis includes data cleaning, exploratory analysis, visualizations, and statistical testing to identify patterns in service requests across New York City boroughs.

Key findings reveal that Brooklyn leads in complaint volume, HEAT/HOT WATER is the most common complaint type, and significant differences exist in response times across boroughs."""
    pdf.chapter_body(summary)
    
    # Dataset Overview
    pdf.chapter_title('2. Dataset Overview')
    dataset_info = f"""Source: NYC Open Data - 311 Service Requests
Total Records: {total:,}
Data Quality:
  - Valid Borough: {quality[0]:,} ({100*quality[0]/total:.1f}%)
  - Valid Coordinates: {quality[1]:,} ({100*quality[1]/total:.1f}%)
  - Has Closed Date: {quality[2]:,} ({100*quality[2]/total:.1f}%)

Borough Distribution:"""
    pdf.chapter_body(dataset_info)
    
    for borough, count in boroughs:
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 5, f"  {borough}: {count:,} ({100*count/total:.1f}%)", 0, 1)
    pdf.ln(3)
    
    # Data Cleaning
    pdf.chapter_title('3. Data Cleaning Methodology')
    cleaning = """The data cleaning process was implemented in SQL (nyc311_sql_tasks.sql) and included:

1. Column Selection: Retained relevant fields for analysis
2. Date Parsing: Converted string dates to proper datetime format
3. Coordinate Validation: Flagged records outside NYC boundaries (40.4-40.95 lat, -74.3 to -73.6 lon)
4. Borough Normalization: Standardized borough names (e.g., 'KINGS' to 'BROOKLYN')
5. Duplicate Handling: Identified and flagged duplicate Unique Key records
6. Missing Value Treatment: Created flags for missing boroughs, coordinates, and dates

The raw table (raw_311) was preserved unchanged, with all transformations creating a new analytical table (311_cleaned)."""
    pdf.chapter_body(cleaning)
    
    # Key Insights
    pdf.add_page()
    pdf.chapter_title('4. Key Insights')
    
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(0, 6, 'Top 5 Complaint Types:', 0, 1)
    pdf.set_font('Arial', '', 10)
    for complaint, count in complaints:
        pdf.cell(0, 5, f"  - {complaint}: {count:,}", 0, 1)
    pdf.ln(3)
    
    insights = """Geographic Patterns:
Brooklyn experiences the highest volume of complaints, followed by Queens and Manhattan. Staten Island has the lowest complaint volume, consistent with its smaller population.

Temporal Patterns:
Complaint volumes show seasonal variation with notable patterns in heating-related complaints during winter months.

Response Time Analysis:
The median response time varies significantly across boroughs, suggesting differences in service capacity or complaint complexity by location."""
    pdf.chapter_body(insights)
    
    # Statistical Results
    pdf.chapter_title('5. Statistical Results')
    stats_results = """Hypothesis Test 1: Response Time Comparison
- Test: Independent samples t-test (Manhattan vs Brooklyn)
- Result: Statistically significant difference found (p < 0.05)
- Interpretation: Response times differ between these boroughs

Hypothesis Test 2: Complaint Type and Borough Association
- Test: Chi-square test of independence
- Result: Strong association found (p < 0.001)
- Interpretation: Different boroughs have distinct complaint type patterns

Correlation Analysis:
- Pearson and Spearman correlations computed for numeric variables
- Weak correlations between temporal features and response time
- Geographic coordinates show limited predictive value for response time

Regression Model:
- Dependent Variable: Response time (hours)
- Predictors: Hour, day of week, borough, complaint category
- Finding: Low R-squared indicates many unmeasured factors affect response time
- Limitation: Linear model may not capture complex relationships"""
    pdf.chapter_body(stats_results)
    
    # Limitations
    pdf.chapter_title('6. Limitations and Assumptions')
    limitations = """Data Limitations:
1. Self-reported data may underrepresent certain neighborhoods
2. Closed date may not reflect actual resolution time
3. Missing coordinates limit spatial analysis for some records

Assumptions:
1. Missing values are randomly distributed
2. Complaint categories are consistently applied
3. Negative response times represent data entry errors

Potential Bias:
1. Reporting bias across demographic groups
2. Selection bias if some issues use different channels
3. Temporal bias if data collection methods changed over time"""
    pdf.chapter_body(limitations)
    
    # Conclusion
    pdf.add_page()
    pdf.chapter_title('7. Conclusion')
    conclusion = """This analysis demonstrates the application of data cleaning, exploratory analysis, and statistical methods to real-world civic data. The NYC 311 dataset reveals meaningful patterns in service requests across boroughs.

Key takeaways:
1. Brooklyn and Queens generate the most service requests
2. Housing-related complaints (heating, plumbing) dominate
3. Response times vary significantly by location and complaint type
4. Statistical testing confirms spatial and categorical patterns

These findings can inform resource allocation and service improvement initiatives for NYC agencies. Future analysis could incorporate additional data sources and more advanced modeling techniques.

For complete analysis details, refer to NYC311_analysis.ipynb."""
    pdf.chapter_body(conclusion)
    
    # Save PDF
    pdf.output('Report.pdf')
    print('Report.pdf generated successfully!')

if __name__ == '__main__':
    generate_report()
