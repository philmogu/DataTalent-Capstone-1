# arxiv_category_monthly_publication_distribution.py
"""
Visualize the distribution of arXiv publications by month (across all years), grouped by main category.
Shows which months have the most papers published for each main category.
Saves image to visualization/asset/arxiv_category_monthly_publication_distribution.png
"""
import os
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm
import numpy as np
import json
from matplotlib import colors as mcolors

# Paths
category_names_path = 'cleaning/asset/official_category_names.json'
main_categories_path = 'cleaning/asset/official_categories.json'
count_path = 'cleaning/asset/category_month_counts.csv'
asset_dir = 'visualization/asset'
os.makedirs(asset_dir, exist_ok=True)

try:
    with open(category_names_path, 'r') as f:
        category_names = json.load(f)
except FileNotFoundError:
    print(f"Error: {category_names_path} not found.")
    category_names = {}
try:
    with open(main_categories_path, 'r') as f:
        main_categories = set(json.load(f))
except FileNotFoundError:
    print(f"Error: {main_categories_path} not found.")
    main_categories = set()

def get_main_category(cat):
    return cat.split('.')[0] if '.' in cat else cat

# Build mapping and counts
main_cat_map = {}
for cat in tqdm(category_names.keys(), desc="Mapping subcategories to main categories"):
    main_cat = get_main_category(cat)
    main_cat_map[cat] = main_cat

# Color palette for main categories

# Use the same ordering and color scheme as other bar charts
import matplotlib
from collections import Counter
main_cat_counts = Counter([get_main_category(cat) for cat in category_names.keys()])
ordered_main_cats = sorted(main_cat_counts, key=main_cat_counts.get, reverse=True)
distinct_cmaps = [plt.colormaps['tab20'], plt.colormaps['Set3'], plt.colormaps['tab10']]
num_main = len(ordered_main_cats)
base_colors = []
for cmap in distinct_cmaps:
    base_colors.extend([cmap(i) for i in range(cmap.N)])
base_colors = base_colors[:num_main]
main_cat_to_color = {cat: base_colors[i] for i, cat in enumerate(ordered_main_cats)}

# Load data
try:
    df = pd.read_csv(count_path)
except FileNotFoundError:
    print(f"Error: {count_path} not found.")
    exit(1)

# Extract month (MM) from 'month' column (format YYYY-MM)
df['pub_month'] = df['month'].apply(lambda x: str(x)[-2:])

# Aggregate total publications by month and main category
agg = df.copy()
agg['main_category'] = agg['categories_list'].apply(get_main_category)
month_cat_counts = agg.groupby(['pub_month', 'main_category'])['count'].sum().reset_index()

# Pivot for plotting
pivot = month_cat_counts.pivot(index='pub_month', columns='main_category', values='count').fillna(0)

# Sort months in calendar order
month_order = [f'{i:02d}' for i in range(1, 13)]
pivot = pivot.reindex(month_order)

# Plot




# Stacked bar chart
fig, ax = plt.subplots(figsize=(14, 8))
bottom = None
for idx, cat in enumerate(ordered_main_cats):
    color = main_cat_to_color[cat]
    ax.bar(pivot.index, pivot[cat], bottom=bottom, color=color, label=cat)
    if bottom is None:
        bottom = pivot[cat].copy()
    else:
        bottom += pivot[cat]
ax.set_title('arXiv Publications by Month (Grouped by Main Category)')
ax.set_xlabel('Month', fontsize=16)
ax.set_ylabel('Number of Papers', fontsize=16)
month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
ax.set_xticks(pivot.index)
ax.set_xticklabels(month_names, fontsize=14)
ax.tick_params(axis='x', labelsize=14, length=8, width=2)
ax.tick_params(axis='y', labelsize=14)
ax.xaxis.grid(True, which='major', linestyle='--', alpha=0.5)
ax.legend(title='Main Category', bbox_to_anchor=(1, 1), loc='upper left')
plt.tight_layout()
plt.savefig(f'{asset_dir}/arxiv_category_monthly_publication_distribution.png', bbox_inches='tight')
plt.close()
print(f"Saved monthly publication distribution chart to {asset_dir}/arxiv_category_monthly_publication_distribution.png")

# Normalized line chart for each main category
fig2, ax2 = plt.subplots(figsize=(14, 8))
for idx, cat in enumerate(ordered_main_cats):
    color = main_cat_to_color[cat]
    # Normalize so sum for each category is 1
    values = pivot[cat].values
    norm_values = values / values.sum() if values.sum() > 0 else values
    ax2.plot(pivot.index, norm_values, label=cat, color=color, linewidth=2)
ax2.set_title('Normalized Monthly Submission Pattern by Main Category')
ax2.set_xlabel('Month', fontsize=16)
ax2.set_ylabel('Fraction of Submissions', fontsize=16)
ax2.set_xticks(pivot.index)
ax2.set_xticklabels(month_names, fontsize=14)
ax2.tick_params(axis='x', labelsize=14, length=8, width=2)
ax2.tick_params(axis='y', labelsize=14)
ax2.xaxis.grid(True, which='major', linestyle='--', alpha=0.5)
ax2.legend(title='Main Category', bbox_to_anchor=(1, 1), loc='upper left')
plt.tight_layout()
plt.savefig(f'{asset_dir}/arxiv_category_monthly_publication_linechart.png', bbox_inches='tight')
plt.close()
print(f"Saved normalized monthly line chart to {asset_dir}/arxiv_category_monthly_publication_linechart.png")
