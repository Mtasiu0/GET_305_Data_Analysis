"""
Run analysis and generate all outputs for NYC 311 assignment.
This script runs the essential analysis and generates visualizations + HTML profile.
"""
import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

print("=" * 60)
print("NYC 311 Data Analysis - Generating Outputs")
print("=" * 60)

# Load data
print("\n1. Loading data from database...")
conn = sqlite3.connect('nyc311.db')
df = pd.read_sql('SELECT * FROM "311_cleaned"', conn)
conn.close()
print(f"   Loaded {len(df):,} records")

# Convert dates
print("\n2. Processing dates...")
df['created_date'] = pd.to_datetime(df['created_date_raw'], format='%m/%d/%Y %I:%M:%S %p', errors='coerce')
df['closed_date'] = pd.to_datetime(df['closed_date_raw'], format='%m/%d/%Y %I:%M:%S %p', errors='coerce')

# Feature engineering
print("\n3. Engineering features...")
df['response_time_hours'] = (df['closed_date'] - df['created_date']).dt.total_seconds() / 3600
df.loc[df['response_time_hours'] < 0, 'response_time_hours'] = np.nan
df['hour_of_day'] = df['created_date'].dt.hour
df['day_of_week'] = df['created_date'].dt.dayofweek
df['year_month'] = df['created_date'].dt.to_period('M')
df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette('husl')

print("\n4. Generating visualizations...")

# Visualization 1: Time series
print("   - Time series of complaint volume...")
monthly_volume = df.groupby('year_month').size()
fig, ax = plt.subplots(figsize=(14, 6))
monthly_volume.plot(ax=ax, linewidth=2, color='steelblue', marker='o', markersize=4)
ax.set_xlabel('Month', fontsize=12)
ax.set_ylabel('Number of Complaints', fontsize=12)
ax.set_title('NYC 311 Complaint Volume Over Time (Monthly)', fontsize=14, fontweight='bold')
ax.tick_params(axis='x', rotation=45)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('viz_01_time_series.png', dpi=150, bbox_inches='tight')
plt.close()

# Visualization 2: Top complaint types
print("   - Bar chart of top complaint types...")
top_complaints = df['complaint_type'].value_counts().head(10)
fig, ax = plt.subplots(figsize=(12, 7))
colors = sns.color_palette('viridis', len(top_complaints))
bars = ax.barh(range(len(top_complaints)), top_complaints.values, color=colors)
ax.set_yticks(range(len(top_complaints)))
ax.set_yticklabels(top_complaints.index)
ax.set_xlabel('Number of Complaints', fontsize=12)
ax.set_ylabel('Complaint Type', fontsize=12)
ax.set_title('Top 10 NYC 311 Complaint Types', fontsize=14, fontweight='bold')
for i, (bar, val) in enumerate(zip(bars, top_complaints.values)):
    ax.text(val + 500, i, f'{val:,}', va='center', fontsize=10)
ax.invert_yaxis()
plt.tight_layout()
plt.savefig('viz_02_complaint_types.png', dpi=150, bbox_inches='tight')
plt.close()

# Visualization 3: Geospatial plot
print("   - Geospatial scatter plot...")
geo_df = df[(df['has_valid_coordinates'] == 1) & 
            (df['latitude'].notna()) & 
            (df['longitude'].notna())].sample(min(50000, len(df)), random_state=42)
fig, ax = plt.subplots(figsize=(12, 10))
boroughs = geo_df['borough'].dropna().unique()
colors = sns.color_palette('Set2', len(boroughs))
borough_colors = dict(zip(boroughs, colors))
for borough in boroughs:
    if borough:
        borough_data = geo_df[geo_df['borough'] == borough]
        ax.scatter(borough_data['longitude'], borough_data['latitude'], 
                   c=[borough_colors[borough]], label=borough, alpha=0.4, s=5)
ax.set_xlabel('Longitude', fontsize=12)
ax.set_ylabel('Latitude', fontsize=12)
ax.set_title('Geographic Distribution of 311 Complaints in NYC', fontsize=14, fontweight='bold')
ax.legend(title='Borough', loc='upper left', markerscale=3)
ax.set_xlim(-74.3, -73.7)
ax.set_ylim(40.5, 40.95)
plt.tight_layout()
plt.savefig('viz_03_geospatial.png', dpi=150, bbox_inches='tight')
plt.close()

# Visualization 4: Response time distribution
print("   - Response time distribution...")
response_df = df[(df['response_time_hours'].notna()) & 
                 (df['response_time_hours'] > 0) & 
                 (df['response_time_hours'] < 720)]
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
axes[0].hist(response_df['response_time_hours'], bins=50, color='teal', edgecolor='white', alpha=0.7)
axes[0].axvline(response_df['response_time_hours'].median(), color='red', linestyle='--', 
                label=f'Median: {response_df["response_time_hours"].median():.1f}h')
axes[0].axvline(response_df['response_time_hours'].mean(), color='orange', linestyle='--', 
                label=f'Mean: {response_df["response_time_hours"].mean():.1f}h')
axes[0].set_xlabel('Response Time (hours)', fontsize=12)
axes[0].set_ylabel('Frequency', fontsize=12)
axes[0].set_title('Distribution of Response Times', fontsize=13, fontweight='bold')
axes[0].legend()
response_df.boxplot(column='response_time_hours', by='borough', ax=axes[1], 
                    patch_artist=True, showfliers=False)
axes[1].set_xlabel('Borough', fontsize=12)
axes[1].set_ylabel('Response Time (hours)', fontsize=12)
axes[1].set_title('Response Time by Borough', fontsize=13, fontweight='bold')
plt.suptitle('')
axes[1].tick_params(axis='x', rotation=45)
plt.tight_layout()
plt.savefig('viz_04_response_time.png', dpi=150, bbox_inches='tight')
plt.close()

print("\n   Visualizations saved as PNG files!")

# Generate profiling report
print("\n5. Generating profiling report (this may take a few minutes)...")
try:
    from ydata_profiling import ProfileReport
    profile_df = df.sample(min(30000, len(df)), random_state=42)
    profile_columns = ['unique_key', 'agency', 'complaint_type', 'complaint_category', 
                       'borough', 'latitude', 'longitude', 'status',
                       'response_time_hours', 'hour_of_day', 'day_of_week', 'is_weekend']
    profile_df = profile_df[profile_columns]
    profile = ProfileReport(profile_df, title='NYC 311 Data Profiling Report', minimal=True)
    profile.to_file('nyc311_profile.html')
    print("   nyc311_profile.html generated!")
except Exception as e:
    print(f"   Warning: Could not generate profile report: {e}")
    print("   You can generate it manually by running the notebook.")

print("\n" + "=" * 60)
print("All outputs generated successfully!")
print("=" * 60)
print("\nGenerated files:")
print("  - viz_01_time_series.png")
print("  - viz_02_complaint_types.png")
print("  - viz_03_geospatial.png")
print("  - viz_04_response_time.png")
print("  - nyc311_profile.html")
