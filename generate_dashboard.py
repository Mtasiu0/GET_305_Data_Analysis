"""
Generate Dashboard HTML Report for NYC 311 Data Analysis
=========================================================
This script generates a professional HTML dashboard with embedded charts.
The dashboard serves as the frontend for viewing analysis results.
"""
import sqlite3
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import base64
from io import BytesIO
import warnings
warnings.filterwarnings('ignore')


def fig_to_base64(fig):
    """Convert matplotlib figure to base64 string for HTML embedding."""
    buf = BytesIO()
    fig.savefig(buf, format='png', dpi=120, bbox_inches='tight', facecolor='white')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    plt.close(fig)
    return img_base64


def load_data():
    """Load and prepare data from database."""
    conn = sqlite3.connect('nyc311.db')
    df = pd.read_sql('SELECT * FROM "311_cleaned"', conn)
    conn.close()
    
    # Convert dates
    df['created_date'] = pd.to_datetime(df['created_date_raw'], format='%m/%d/%Y %I:%M:%S %p', errors='coerce')
    df['closed_date'] = pd.to_datetime(df['closed_date_raw'], format='%m/%d/%Y %I:%M:%S %p', errors='coerce')
    
    # Feature engineering
    df['response_time_hours'] = (df['closed_date'] - df['created_date']).dt.total_seconds() / 3600
    df.loc[df['response_time_hours'] < 0, 'response_time_hours'] = np.nan
    df['hour_of_day'] = df['created_date'].dt.hour
    df['day_of_week'] = df['created_date'].dt.dayofweek
    df['year_month'] = df['created_date'].dt.to_period('M')
    
    return df


def create_time_series_chart(df):
    """Create time series chart of complaint volume."""
    monthly_volume = df.groupby('year_month').size()
    
    fig, ax = plt.subplots(figsize=(12, 5))
    monthly_volume.plot(ax=ax, linewidth=2.5, color='#3498db', marker='o', markersize=4)
    ax.fill_between(range(len(monthly_volume)), monthly_volume.values, alpha=0.3, color='#3498db')
    ax.set_xlabel('Month', fontsize=11, fontweight='bold')
    ax.set_ylabel('Number of Complaints', fontsize=11, fontweight='bold')
    ax.set_title('Complaint Volume Over Time', fontsize=14, fontweight='bold', pad=15)
    ax.tick_params(axis='x', rotation=45)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    
    return fig_to_base64(fig)


def create_complaint_types_chart(df):
    """Create horizontal bar chart of top complaint types."""
    top_complaints = df['complaint_type'].value_counts().head(10)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    colors = sns.color_palette('Blues_r', len(top_complaints))
    bars = ax.barh(range(len(top_complaints)), top_complaints.values, color=colors)
    ax.set_yticks(range(len(top_complaints)))
    ax.set_yticklabels(top_complaints.index, fontsize=10)
    ax.set_xlabel('Number of Complaints', fontsize=11, fontweight='bold')
    ax.set_title('Top 10 Complaint Types', fontsize=14, fontweight='bold', pad=15)
    
    for i, (bar, val) in enumerate(zip(bars, top_complaints.values)):
        ax.text(val + 200, i, f'{val:,}', va='center', fontsize=9, fontweight='bold')
    
    ax.invert_yaxis()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(True, alpha=0.3, axis='x', linestyle='--')
    plt.tight_layout()
    
    return fig_to_base64(fig)


def create_borough_chart(df):
    """Create pie chart of complaints by borough."""
    borough_counts = df['borough'].value_counts()
    
    fig, ax = plt.subplots(figsize=(8, 8))
    colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6']
    explode = [0.02] * len(borough_counts)
    
    wedges, texts, autotexts = ax.pie(
        borough_counts.values, 
        labels=borough_counts.index,
        autopct='%1.1f%%',
        colors=colors[:len(borough_counts)],
        explode=explode,
        shadow=True,
        startangle=90
    )
    
    for autotext in autotexts:
        autotext.set_fontsize(10)
        autotext.set_fontweight('bold')
    
    ax.set_title('Complaints by Borough', fontsize=14, fontweight='bold', pad=15)
    plt.tight_layout()
    
    return fig_to_base64(fig)


def create_response_time_chart(df):
    """Create response time distribution chart."""
    response_df = df[(df['response_time_hours'].notna()) & 
                     (df['response_time_hours'] > 0) & 
                     (df['response_time_hours'] < 720)]
    
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.hist(response_df['response_time_hours'], bins=50, color='#2ecc71', edgecolor='white', alpha=0.8)
    
    median_val = response_df['response_time_hours'].median()
    mean_val = response_df['response_time_hours'].mean()
    
    ax.axvline(median_val, color='#e74c3c', linestyle='--', linewidth=2, label=f'Median: {median_val:.1f}h')
    ax.axvline(mean_val, color='#f39c12', linestyle='--', linewidth=2, label=f'Mean: {mean_val:.1f}h')
    
    ax.set_xlabel('Response Time (hours)', fontsize=11, fontweight='bold')
    ax.set_ylabel('Frequency', fontsize=11, fontweight='bold')
    ax.set_title('Distribution of Response Times', fontsize=14, fontweight='bold', pad=15)
    ax.legend(fontsize=10)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(True, alpha=0.3, axis='y', linestyle='--')
    plt.tight_layout()
    
    return fig_to_base64(fig)


def create_hourly_pattern_chart(df):
    """Create hourly complaint pattern chart."""
    hourly_counts = df.groupby('hour_of_day').size()
    
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(hourly_counts.index, hourly_counts.values, color='#9b59b6', edgecolor='white', alpha=0.8)
    ax.set_xlabel('Hour of Day', fontsize=11, fontweight='bold')
    ax.set_ylabel('Number of Complaints', fontsize=11, fontweight='bold')
    ax.set_title('Complaint Volume by Hour of Day', fontsize=14, fontweight='bold', pad=15)
    ax.set_xticks(range(0, 24, 2))
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(True, alpha=0.3, axis='y', linestyle='--')
    plt.tight_layout()
    
    return fig_to_base64(fig)


def create_geospatial_chart(df):
    """Create geospatial scatter plot."""
    geo_df = df[(df['has_valid_coordinates'] == 1) & 
                (df['latitude'].notna()) & 
                (df['longitude'].notna())].sample(min(30000, len(df)), random_state=42)
    
    fig, ax = plt.subplots(figsize=(10, 10))
    
    boroughs = geo_df['borough'].dropna().unique()
    colors = {'BROOKLYN': '#3498db', 'QUEENS': '#e74c3c', 'MANHATTAN': '#2ecc71', 
              'BRONX': '#f39c12', 'STATEN ISLAND': '#9b59b6'}
    
    for borough in boroughs:
        if borough and borough in colors:
            borough_data = geo_df[geo_df['borough'] == borough]
            ax.scatter(borough_data['longitude'], borough_data['latitude'], 
                       c=colors[borough], label=borough, alpha=0.4, s=3)
    
    ax.set_xlabel('Longitude', fontsize=11, fontweight='bold')
    ax.set_ylabel('Latitude', fontsize=11, fontweight='bold')
    ax.set_title('Geographic Distribution of Complaints', fontsize=14, fontweight='bold', pad=15)
    ax.legend(title='Borough', loc='upper left', markerscale=4)
    ax.set_xlim(-74.3, -73.7)
    ax.set_ylim(40.5, 40.95)
    ax.grid(True, alpha=0.3, linestyle='--')
    plt.tight_layout()
    
    return fig_to_base64(fig)


def generate_html(df, charts):
    """Generate the complete HTML dashboard."""
    
    # Calculate statistics
    total_records = len(df)
    total_boroughs = df['borough'].nunique()
    total_complaint_types = df['complaint_type'].nunique()
    avg_response_time = df['response_time_hours'].mean()
    median_response_time = df['response_time_hours'].median()
    
    # Borough stats
    borough_stats = df.groupby('borough').agg({
        'unique_key': 'count',
        'response_time_hours': 'mean'
    }).round(1)
    borough_stats.columns = ['Complaints', 'Avg Response (hrs)']
    borough_stats = borough_stats.sort_values('Complaints', ascending=False)
    
    # Top complaints
    top_complaints = df['complaint_type'].value_counts().head(10)
    
    # Date range
    min_date = df['created_date'].min().strftime('%Y-%m-%d') if df['created_date'].notna().any() else 'N/A'
    max_date = df['created_date'].max().strftime('%Y-%m-%d') if df['created_date'].notna().any() else 'N/A'
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NYC 311 Data Analysis Dashboard</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #ffffff;
            min-height: 100vh;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        header {{
            text-align: center;
            padding: 40px 20px;
            background: linear-gradient(135deg, #0f3460 0%, #16213e 100%);
            border-radius: 15px;
            margin-bottom: 30px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
        }}
        
        header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            background: linear-gradient(90deg, #e94560, #0f3460);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        header p {{
            color: #a0a0a0;
            font-size: 1.1em;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: linear-gradient(145deg, #1f4068 0%, #16213e 100%);
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 5px 20px rgba(0, 0, 0, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.1);
            transition: transform 0.3s ease;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
        }}
        
        .stat-value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #e94560;
            display: block;
        }}
        
        .stat-label {{
            color: #a0a0a0;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-top: 5px;
        }}
        
        .section {{
            background: linear-gradient(145deg, #1f4068 0%, #16213e 100%);
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 5px 20px rgba(0, 0, 0, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }}
        
        .section h2 {{
            color: #e94560;
            margin-bottom: 20px;
            font-size: 1.5em;
            border-bottom: 2px solid #e94560;
            padding-bottom: 10px;
        }}
        
        .section h3 {{
            color: #ffffff;
            margin: 20px 0 15px 0;
            font-size: 1.2em;
        }}
        
        .chart-container {{
            background: #ffffff;
            border-radius: 10px;
            padding: 15px;
            margin: 20px 0;
            text-align: center;
        }}
        
        .chart-container img {{
            max-width: 100%;
            height: auto;
            border-radius: 5px;
        }}
        
        .grid-2 {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 30px;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}
        
        th, td {{
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }}
        
        th {{
            background: rgba(233, 69, 96, 0.2);
            color: #e94560;
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.85em;
            letter-spacing: 1px;
        }}
        
        tr:hover {{
            background: rgba(255, 255, 255, 0.05);
        }}
        
        .highlight {{
            color: #e94560;
            font-weight: bold;
        }}
        
        .insight-box {{
            background: rgba(233, 69, 96, 0.1);
            border-left: 4px solid #e94560;
            padding: 15px 20px;
            margin: 20px 0;
            border-radius: 0 10px 10px 0;
        }}
        
        .insight-box h4 {{
            color: #e94560;
            margin-bottom: 10px;
        }}
        
        footer {{
            text-align: center;
            padding: 30px;
            color: #a0a0a0;
            font-size: 0.9em;
        }}
        
        footer a {{
            color: #e94560;
            text-decoration: none;
        }}
        
        @media (max-width: 768px) {{
            .grid-2 {{
                grid-template-columns: 1fr;
            }}
            
            header h1 {{
                font-size: 1.8em;
            }}
            
            .stat-value {{
                font-size: 2em;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🗽 NYC 311 Data Analysis Dashboard</h1>
            <p>Comprehensive analysis of service requests across New York City</p>
            <p style="margin-top: 10px; font-size: 0.9em;">Data Period: {min_date} to {max_date}</p>
        </header>
        
        <!-- Key Statistics -->
        <div class="stats-grid">
            <div class="stat-card">
                <span class="stat-value">{total_records:,}</span>
                <span class="stat-label">Total Complaints</span>
            </div>
            <div class="stat-card">
                <span class="stat-value">{total_boroughs}</span>
                <span class="stat-label">Boroughs</span>
            </div>
            <div class="stat-card">
                <span class="stat-value">{total_complaint_types}</span>
                <span class="stat-label">Complaint Types</span>
            </div>
            <div class="stat-card">
                <span class="stat-value">{avg_response_time:.1f}h</span>
                <span class="stat-label">Avg Response Time</span>
            </div>
            <div class="stat-card">
                <span class="stat-value">{median_response_time:.1f}h</span>
                <span class="stat-label">Median Response</span>
            </div>
        </div>
        
        <!-- Time Series Analysis -->
        <section class="section">
            <h2>📈 Temporal Analysis</h2>
            <p>Understanding how complaint volumes change over time helps identify seasonal patterns and trends.</p>
            
            <div class="chart-container">
                <img src="data:image/png;base64,{charts['time_series']}" alt="Time Series Chart">
            </div>
            
            <div class="insight-box">
                <h4>Key Insight</h4>
                <p>The time series shows monthly fluctuations in complaint volume. Peaks often correspond to 
                seasonal factors such as heating issues in winter months.</p>
            </div>
            
            <h3>Hourly Pattern</h3>
            <div class="chart-container">
                <img src="data:image/png;base64,{charts['hourly']}" alt="Hourly Pattern Chart">
            </div>
        </section>
        
        <!-- Complaint Types -->
        <section class="section">
            <h2>📋 Complaint Analysis</h2>
            
            <div class="grid-2">
                <div>
                    <h3>Top 10 Complaint Types</h3>
                    <div class="chart-container">
                        <img src="data:image/png;base64,{charts['complaints']}" alt="Complaint Types Chart">
                    </div>
                </div>
                
                <div>
                    <h3>Complaints by Borough</h3>
                    <div class="chart-container">
                        <img src="data:image/png;base64,{charts['borough']}" alt="Borough Distribution Chart">
                    </div>
                </div>
            </div>
            
            <div class="insight-box">
                <h4>Key Insight</h4>
                <p><span class="highlight">HEAT/HOT WATER</span> is the most common complaint type, reflecting 
                the critical nature of heating infrastructure in NYC residential buildings. Brooklyn leads 
                in total complaint volume, consistent with its large population.</p>
            </div>
        </section>
        
        <!-- Response Time Analysis -->
        <section class="section">
            <h2>⏱️ Response Time Analysis</h2>
            <p>Analyzing response times helps evaluate city service efficiency across different areas.</p>
            
            <div class="chart-container">
                <img src="data:image/png;base64,{charts['response_time']}" alt="Response Time Distribution">
            </div>
            
            <h3>Response Time by Borough</h3>
            <table>
                <thead>
                    <tr>
                        <th>Borough</th>
                        <th>Total Complaints</th>
                        <th>Avg Response Time (hrs)</th>
                    </tr>
                </thead>
                <tbody>
"""
    
    for borough, row in borough_stats.iterrows():
        if borough:
            html += f"""
                    <tr>
                        <td>{borough}</td>
                        <td>{int(row['Complaints']):,}</td>
                        <td>{row['Avg Response (hrs)']:.1f}</td>
                    </tr>
"""
    
    html += f"""
                </tbody>
            </table>
            
            <div class="insight-box">
                <h4>Key Insight</h4>
                <p>The distribution of response times is positively skewed, with the median 
                ({median_response_time:.1f} hours) being significantly lower than the mean ({avg_response_time:.1f} hours). 
                This indicates that while most complaints are resolved quickly, some take considerably longer.</p>
            </div>
        </section>
        
        <!-- Geographic Analysis -->
        <section class="section">
            <h2>🗺️ Geographic Distribution</h2>
            <p>Visualizing complaint locations across NYC reveals spatial patterns in service requests.</p>
            
            <div class="chart-container">
                <img src="data:image/png;base64,{charts['geospatial']}" alt="Geographic Distribution">
            </div>
            
            <div class="insight-box">
                <h4>Key Insight</h4>
                <p>The scatter plot clearly shows the distinct shapes of NYC's five boroughs. Higher density 
                areas indicate neighborhoods with more frequent service requests, which may correlate with 
                population density or specific infrastructure challenges.</p>
            </div>
        </section>
        
        <!-- Data Quality -->
        <section class="section">
            <h2>📊 Data Quality Summary</h2>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <span class="stat-value">{100*df['has_valid_borough'].mean():.1f}%</span>
                    <span class="stat-label">Valid Borough</span>
                </div>
                <div class="stat-card">
                    <span class="stat-value">{100*df['has_valid_coordinates'].mean():.1f}%</span>
                    <span class="stat-label">Valid Coordinates</span>
                </div>
                <div class="stat-card">
                    <span class="stat-value">{100*df['has_closed_date'].mean():.1f}%</span>
                    <span class="stat-label">Has Closed Date</span>
                </div>
                <div class="stat-card">
                    <span class="stat-value">{df.duplicated().sum():,}</span>
                    <span class="stat-label">Duplicate Rows</span>
                </div>
            </div>
        </section>
        
        <footer>
            <p>NYC 311 Data Analysis Dashboard | GET 305 Data Analysis Assignment</p>
            <p>Data source: <a href="https://data.cityofnewyork.us" target="_blank">NYC Open Data</a></p>
            <p style="margin-top: 10px;">For detailed statistical analysis, see <code>NYC311_analysis.ipynb</code></p>
        </footer>
    </div>
</body>
</html>
"""
    
    return html


def main():
    """Main function to generate the dashboard."""
    print("=" * 60)
    print("NYC 311 Data Analysis Dashboard Generator")
    print("=" * 60)
    
    # Load data
    print("\n1. Loading data from database...")
    df = load_data()
    print(f"   Loaded {len(df):,} records")
    
    # Generate charts
    print("\n2. Generating charts...")
    charts = {}
    
    print("   - Time series chart...")
    charts['time_series'] = create_time_series_chart(df)
    
    print("   - Complaint types chart...")
    charts['complaints'] = create_complaint_types_chart(df)
    
    print("   - Borough distribution chart...")
    charts['borough'] = create_borough_chart(df)
    
    print("   - Response time chart...")
    charts['response_time'] = create_response_time_chart(df)
    
    print("   - Hourly pattern chart...")
    charts['hourly'] = create_hourly_pattern_chart(df)
    
    print("   - Geospatial chart...")
    charts['geospatial'] = create_geospatial_chart(df)
    
    # Generate HTML
    print("\n3. Generating HTML dashboard...")
    html_content = generate_html(df, charts)
    
    # Save file
    with open('dashboard.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("\n" + "=" * 60)
    print("SUCCESS: dashboard.html generated!")
    print("=" * 60)
    print("\nOpen dashboard.html in your browser to view the analysis.")


if __name__ == '__main__':
    main()
