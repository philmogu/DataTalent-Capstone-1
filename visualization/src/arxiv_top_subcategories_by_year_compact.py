# arxiv_top_subcategories_by_year_compact.py
"""
Create a compact CSV with the top 3 subcategories for each year, with percentage in the same cell.
Output: visualization/asset/arxiv_top_subcategories_by_year_compact.csv
"""
import os
import pandas as pd
from tqdm import tqdm

count_path = 'cleaning/asset/category_month_counts.csv'
asset_dir = 'visualization/asset'
os.makedirs(asset_dir, exist_ok=True)

# Load data
official_categories_path = 'cleaning/asset/official_categories.json'
try:
    df = pd.read_csv(count_path)
except FileNotFoundError:
    print(f"Error: {count_path} not found.")
    exit(1)

# Extract year from 'month' column (format YYYY-MM)
official_categories_path = 'cleaning/asset/official_categories.json'
df['year'] = df['month'].apply(lambda x: str(x)[:4])

# Aggregate total papers by year and subcategory
year_subcat_counts = df.groupby(['year', 'categories_list'])['count'].sum().reset_index()

# Aggregate total papers by year
year_total_counts = df.groupby('year')['count'].sum().to_dict()

# For each year, get top 3 subcategories and their percentage
rows = []
for year in sorted(year_total_counts.keys()):
    subcat_df = year_subcat_counts[year_subcat_counts['year'] == year]
    top3 = subcat_df.sort_values('count', ascending=False).head(3)
    top_subcats = [f'{row["categories_list"]} ({round(100*row["count"]/year_total_counts[year],2)}%)' for _, row in top3.iterrows()]
    # Pad with empty strings if less than 3
    while len(top_subcats) < 3:
        top_subcats.append('')
    rows.append({'year': year, 'top_1': top_subcats[0], 'top_2': top_subcats[1], 'top_3': top_subcats[2]})

# Save to CSV
csv_path = os.path.join(asset_dir, 'arxiv_top_subcategories_by_year_compact.csv')
pd.DataFrame(rows).to_csv(csv_path, index=False)
print(f"Saved compact CSV to {csv_path}")
