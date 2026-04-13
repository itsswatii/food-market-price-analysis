
# Dataset: USDA Food Access Research Atlas (Kaggle)

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from folium.plugins import HeatMap

# 1. LOAD DATA

df = pd.read_csv('data/food_access_research_atlas.csv', encoding='utf-8-sig')
print("Shape:", df.shape)
print(df.head(3))


# 2. DATA CLEANING & PREPROCESSING

# Select key columns for analysis
cols = [
    'CensusTract', 'State', 'County', 'Urban',
    'POP2010', 'PovertyRate', 'MedianFamilyIncome',
    'LILATracts_1And10', 'LILATracts_halfAnd10',
    'LowIncomeTracts', 'HUNVFlag',
    'TractSNAP', 'TractHUNV',
    'lapop1', 'lalowi1'
]
df = df[cols]

# Drop rows with missing key values
df = df.dropna(subset=['PovertyRate', 'MedianFamilyIncome', 'POP2010'])

# Label Urban vs Rural
df['AreaType'] = df['Urban'].map({1: 'Urban', 0: 'Rural'})

print("\nShape after cleaning:", df.shape)
print("\nMissing Values:")
print(df.isnull().sum())


# 3. EXPLORATORY DATA ANALYSIS


#  1. Poverty Rate: Urban vs Rural 
plt.figure(figsize=(8, 5))
sns.boxplot(data=df, x='AreaType', y='PovertyRate', palette='Set2')
plt.title('Poverty Rate: Urban vs Rural Census Tracts')
plt.xlabel('Area Type')
plt.ylabel('Poverty Rate (%)')
plt.tight_layout()
plt.savefig('visuals/poverty_rate_urban_rural.png')
plt.show()

#  2. Median Family Income: Urban vs Rural 
plt.figure(figsize=(8, 5))
sns.boxplot(data=df, x='AreaType', y='MedianFamilyIncome', palette='coolwarm')
plt.title('Median Family Income: Urban vs Rural')
plt.xlabel('Area Type')
plt.ylabel('Median Family Income ($)')
plt.tight_layout()
plt.savefig('visuals/median_income_urban_rural.png')
plt.show()

#  3. Top 15 States by Low Income & Low Access Tracts 
plt.figure(figsize=(10, 6))
lila_by_state = df.groupby('State')['LILATracts_1And10'].sum().sort_values(ascending=False).head(15)
sns.barplot(x=lila_by_state.values, y=lila_by_state.index, palette='Reds_r')
plt.title('Top 15 States by Low Income & Low Food Access Tracts')
plt.xlabel('Number of LILA Tracts')
plt.ylabel('State')
plt.tight_layout()
plt.savefig('visuals/lila_tracts_by_state.png')
plt.show()

#  4. SNAP Participation by Area Type 
plt.figure(figsize=(8, 5))
snap_area = df.groupby('AreaType')['TractSNAP'].mean()
snap_area.plot(kind='bar', color=['steelblue', 'coral'], edgecolor='black')
plt.title('Average SNAP Participation by Area Type')
plt.xlabel('Area Type')
plt.ylabel('Avg SNAP Participants per Tract')
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig('visuals/snap_by_area_type.png')
plt.show()

# 5. Poverty Rate Distribution by State (Top 10) 
plt.figure(figsize=(12, 6))
top_states = df.groupby('State')['PovertyRate'].mean().sort_values(ascending=False).head(10)
sns.barplot(x=top_states.index, y=top_states.values, palette='OrRd')
plt.title('Top 10 States by Average Poverty Rate')
plt.xlabel('State')
plt.ylabel('Average Poverty Rate (%)')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('visuals/poverty_rate_by_state.png')
plt.show()


# 4. KPI SUMMARY

print("\n========== KPI SUMMARY ==========")
print(f"Total Census Tracts Analyzed: {len(df):,}")
print(f"Total States Covered: {df['State'].nunique()}")
print(f"Total Population Covered: {df['POP2010'].sum():,.0f}")
print(f"Overall Avg Poverty Rate: {df['PovertyRate'].mean():.2f}%")
print(f"Urban Avg Poverty Rate: {df[df['AreaType']=='Urban']['PovertyRate'].mean():.2f}%")
print(f"Rural Avg Poverty Rate: {df[df['AreaType']=='Rural']['PovertyRate'].mean():.2f}%")
print(f"Overall Avg Median Family Income: ${df['MedianFamilyIncome'].mean():,.2f}")
print(f"Urban Avg Median Family Income: ${df[df['AreaType']=='Urban']['MedianFamilyIncome'].mean():,.2f}")
print(f"Rural Avg Median Family Income: ${df[df['AreaType']=='Rural']['MedianFamilyIncome'].mean():,.2f}")
print(f"Total LILA Tracts (1 mile & 10 miles): {df['LILATracts_1And10'].sum():,.0f}")
print(f"Total Low Income Tracts: {df['LowIncomeTracts'].sum():,.0f}")



import folium
import json
import urllib.request


# 5. COUNTY LEVEL PRICE DISPARITY ANALYSIS

# Aggregate data at county level
county_df = df.groupby(['State', 'County']).agg(
    AvgPovertyRate=('PovertyRate', 'mean'),
    AvgMedianIncome=('MedianFamilyIncome', 'mean'),
    TotalPopulation=('POP2010', 'sum'),
    TotalLILATracts=('LILATracts_1And10', 'sum'),
    TotalLowIncomeTracts=('LowIncomeTracts', 'sum'),
    UrbanCount=('Urban', 'sum'),
    TotalTracts=('Urban', 'count')
).reset_index()

# Calculate % urban per county
county_df['PctUrban'] = (county_df['UrbanCount'] / county_df['TotalTracts']) * 100

# Income disparity between highest and lowest income counties
highest_income = county_df.nlargest(10, 'AvgMedianIncome')[['County', 'State', 'AvgMedianIncome']]
lowest_income = county_df.nsmallest(10, 'AvgMedianIncome')[['County', 'State', 'AvgMedianIncome']]

print("\n--- Top 10 Highest Income Counties ---")
print(highest_income.to_string(index=False))

print("\n--- Top 10 Lowest Income Counties ---")
print(lowest_income.to_string(index=False))

# Price disparity calculation
max_income = county_df['AvgMedianIncome'].max()
min_income = county_df[county_df['AvgMedianIncome'] > 0]['AvgMedianIncome'].min()
disparity_pct = ((max_income - min_income) / min_income) * 100
print(f"\nIncome Disparity between highest and lowest counties: {disparity_pct:.1f}%")

# --- County Level Income Disparity Bar Chart ---
plt.figure(figsize=(12, 6))
top5_high = county_df.nlargest(5, 'AvgMedianIncome')
top5_low = county_df.nsmallest(5, 'AvgMedianIncome')
compare_df = pd.concat([top5_high, top5_low])
compare_df['Label'] = compare_df['County'] + ', ' + compare_df['State']
colors = ['green'] * 5 + ['red'] * 5

plt.barh(compare_df['Label'], compare_df['AvgMedianIncome'], color=colors)
plt.title('Top 5 Highest vs Lowest Income Counties')
plt.xlabel('Average Median Family Income ($)')
plt.axvline(x=county_df['AvgMedianIncome'].mean(), color='blue', linestyle='--', label='National Average')
plt.legend()
plt.tight_layout()
plt.savefig('visuals/county_income_disparity.png')
plt.show()

# --- LILA Tracts by County (Top 15) ---
plt.figure(figsize=(12, 6))
top_lila_counties = county_df.nlargest(15, 'TotalLILATracts')
top_lila_counties['Label'] = top_lila_counties['County'] + ', ' + top_lila_counties['State']
sns.barplot(x='TotalLILATracts', y='Label', data=top_lila_counties, palette='Reds_r')
plt.title('Top 15 Counties by Low Income & Low Access (LILA) Tracts')
plt.xlabel('Total LILA Tracts')
plt.ylabel('County')
plt.tight_layout()
plt.savefig('visuals/lila_tracts_by_county.png')
plt.show()


# 6. CHOROPLETH MAP USING FOLIUM

# Aggregate poverty rate by state for choropleth
state_df = df.groupby('State').agg(
    AvgPovertyRate=('PovertyRate', 'mean'),
    AvgMedianIncome=('MedianFamilyIncome', 'mean'),
    TotalLILATracts=('LILATracts_1And10', 'sum')
).reset_index()

# Download US states GeoJSON
geo_url = "https://raw.githubusercontent.com/python-visualization/folium/master/examples/data/us-states.json"
try:
    urllib.request.urlretrieve(geo_url, 'data/us-states.json')
    print("GeoJSON downloaded successfully!")

    # Create choropleth map
    m = folium.Map(location=[37.8, -96], zoom_start=4)

    folium.Choropleth(
        geo_data='data/us-states.json',
        name='choropleth',
        data=state_df,
        columns=['State', 'AvgPovertyRate'],
        key_on='feature.properties.name',
        fill_color='YlOrRd',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name='Average Poverty Rate (%)'
    ).add_to(m)

    folium.LayerControl().add_to(m)
    m.save('visuals/poverty_choropleth_map.html')
    print("Choropleth map saved to visuals/poverty_choropleth_map.html")

except Exception as e:
    print(f"Could not download GeoJSON: {e}")
    print("Skipping choropleth map generation.")


# 7. UPDATED KPI SUMMARY

print("\n========== UPDATED KPI SUMMARY ==========")
print(f"Total Census Tracts Analyzed: {len(df):,}")
print(f"Total Counties Analyzed: {len(county_df):,}")
print(f"Total States Covered: {df['State'].nunique()}")
print(f"Total Population Covered: {df['POP2010'].sum():,.0f}")
print(f"Overall Avg Poverty Rate: {df['PovertyRate'].mean():.2f}%")
print(f"Urban Avg Poverty Rate: {df[df['AreaType']=='Urban']['PovertyRate'].mean():.2f}%")
print(f"Rural Avg Poverty Rate: {df[df['AreaType']=='Rural']['PovertyRate'].mean():.2f}%")
print(f"Overall Avg Median Family Income: ${df['MedianFamilyIncome'].mean():,.2f}")
print(f"Urban Avg Median Family Income: ${df[df['AreaType']=='Urban']['MedianFamilyIncome'].mean():,.2f}")
print(f"Rural Avg Median Family Income: ${df[df['AreaType']=='Rural']['MedianFamilyIncome'].mean():,.2f}")
print(f"Total LILA Tracts: {df['LILATracts_1And10'].sum():,.0f}")
print(f"Total Low Income Tracts: {df['LowIncomeTracts'].sum():,.0f}")
print(f"County Income Disparity (highest vs lowest): {disparity_pct:.1f}%")
