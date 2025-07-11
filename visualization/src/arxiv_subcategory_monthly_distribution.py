# arxiv_subcategory_monthly_distribution.py
"""
Visualize monthly distribution of arXiv subcategories:
1. Stacked bar chart of absolute paper counts per subcategory per month (grouped by main category, alternating colors).
2. Stacked bar chart of normalized percentage per subcategory per month.
Saves images to visualization/asset/.
"""
import os
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm
import numpy as np
import json
from matplotlib import colors as mcolors
from matplotlib import cm

# Paths
category_names_path = 'cleaning/asset/official_category_names.json'
main_categories_path = 'cleaning/asset/official_categories.json'
count_path = 'cleaning/asset/category_month_counts.csv'
asset_dir = 'visualization/asset'
os.makedirs(asset_dir, exist_ok=True)

# Load color and category mapping
try:
    with open(category_names_path, 'r') as f:
        category_names = json.load(f)
except FileNotFoundError:
    print(f"Error: {category_names_path} not found.")
    category_names = []
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
main_cat_counts = {}
for cat in category_names:
    main_cat = get_main_category(cat)
    main_cat_map[cat] = main_cat
    main_cat_counts[main_cat] = main_cat_counts.get(main_cat, 0) + 1
ordered_main_cats = sorted(main_cat_counts, key=main_cat_counts.get, reverse=True)

# Color palette for main categories
import matplotlib
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

# Aggregate counts by month and subcategory
agg = df.groupby(['month', 'categories_list'])['count'].sum().reset_index()

# Pivot for plotting
pivot = agg.pivot(index='month', columns='categories_list', values='count').fillna(0)

# Consistent ordering: group subcategories by main category, sort by size within each main category

# Shared color assignment function for subcategory bands

# Global sorting: sort subcategories by total count across all months (largest at bottom)

# Group subcategories by main category, then sort within each main category by total count (largest at bottom)
subcat_total_counts = pivot.sum(axis=0).to_dict()
subcat_ordered = []
for main_cat in ordered_main_cats:
    group = [cat for cat in pivot.columns if main_cat_map.get(cat, get_main_category(cat)) == main_cat]
    group_sorted = sorted(group, key=lambda c: subcat_total_counts.get(c, 0), reverse=True)
    subcat_ordered.extend(group_sorted)

# Assign colors using the same logic, grouped and sorted within main categories

# Use the same color assignment function as the yearly chart for consistency

# Alternate brightness for subcategories within each main category (like yearly chart)
def assign_subcat_colors_alternating(subcat_ordered, main_cat_map, main_cat_to_color, ordered_main_cats, spread=0.15):
    subcat_colors_dict = {}
    for main_cat in ordered_main_cats:
        group = [cat for cat in subcat_ordered if main_cat_map.get(cat, get_main_category(cat)) == main_cat]
        base_rgb = np.array(main_cat_to_color.get(main_cat, [0.5, 0.5, 0.5])[:3])
        base_hsv = mcolors.rgb_to_hsv(base_rgb)
        n_subcats = len(group)
        for j, subcat in enumerate(group):
            hsv = base_hsv.copy()
            # Alternate brightness: even index = base, odd index = base +/- spread
            if n_subcats > 1:
                if j % 2 == 0:
                    hsv[2] = min(1.0, max(0.0, base_hsv[2]))
                else:
                    hsv[2] = min(1.0, max(0.0, base_hsv[2] - spread))
            rgb = mcolors.hsv_to_rgb(hsv)
            subcat_colors_dict[subcat] = rgb
    # Assign a default color for any subcat not in subcat_colors_dict
    default_rgb = np.array([0.7, 0.7, 0.7])
    return [subcat_colors_dict.get(subcat, default_rgb) for subcat in subcat_ordered]

subcat_colors = assign_subcat_colors_alternating(subcat_ordered, main_cat_map, main_cat_to_color, ordered_main_cats, spread=0.04)
pivot = pivot[subcat_ordered]

# 1. Stacked bar chart (absolute counts)
fig1, ax1 = plt.subplots(figsize=(22, 10))
bar_width = 1.0
bottom = None
for idx, subcat in enumerate(tqdm(subcat_ordered, desc="Plotting monthly absolute counts")):
    color = subcat_colors[idx]
    ax1.bar(pivot.index, pivot[subcat], bottom=bottom, color=color, width=bar_width, align='center')
    if bottom is None:
        bottom = pivot[subcat].copy()
    else:
        bottom += pivot[subcat]

ax1.set_title('Monthly Distribution of Papers by Subcategory (Grouped by Main Category, Absolute Counts)')
ax1.set_xlabel('Month')
ax1.set_ylabel('Number of Papers')



# Label only January of each year
months = list(pivot.index)
jan_indices = [i for i, m in enumerate(months) if str(m)[-2:] == '01']
jan_labels = [str(months[i]) for i in jan_indices]
ax1.set_xticks([months[i] for i in jan_indices])
ax1.set_xticklabels(jan_labels, rotation=45, ha='right')

ax1.set_xlim([months[0], months[-1]])

main_legend_handles = [plt.Line2D([0], [0], color=main_cat_to_color[cat], lw=8) for cat in ordered_main_cats]
main_legend_labels = [cat for cat in ordered_main_cats]
ax1.legend(handles=main_legend_handles, labels=main_legend_labels, loc='center left', bbox_to_anchor=(1, 0.5), fontsize=10, title="Main Categories")
plt.tight_layout()
plt.savefig(f'{asset_dir}/arxiv_subcategory_monthly_counts_grouped.png', bbox_inches='tight')
plt.close()
print(f"Saved grouped monthly absolute counts chart to {asset_dir}/arxiv_subcategory_monthly_counts_grouped.png")

# 2. Stacked bar chart (normalized percentages)
pivot_pct = pivot.div(pivot.sum(axis=1), axis=0).fillna(0) * 100
fig2, ax2 = plt.subplots(figsize=(22, 10))
bar_width = 1.0
bottom = None
for idx, subcat in enumerate(tqdm(subcat_ordered, desc="Plotting monthly normalized percentages")):
    color = subcat_colors[idx]
    ax2.bar(pivot_pct.index, pivot_pct[subcat], bottom=bottom, color=color, width=bar_width, align='center')
    if bottom is None:
        bottom = pivot_pct[subcat].copy()
    else:
        bottom += pivot_pct[subcat]

ax2.set_title('Monthly Distribution of Papers by Subcategory (Grouped by Main Category, Normalized Percentages)')
ax2.set_xlabel('Month')
ax2.set_ylabel('Percentage of Papers (%)')



# Label only January of each year
months_pct = list(pivot_pct.index)
jan_indices_pct = [i for i, m in enumerate(months_pct) if str(m)[-2:] == '01']
jan_labels_pct = [str(months_pct[i]) for i in jan_indices_pct]
ax2.set_xticks([months_pct[i] for i in jan_indices_pct])
ax2.set_xticklabels(jan_labels_pct, rotation=45, ha='right')

ax2.set_xlim([months_pct[0], months_pct[-1]])

main_legend_handles2 = [plt.Line2D([0], [0], color=main_cat_to_color[cat], lw=8) for cat in ordered_main_cats]
main_legend_labels2 = [cat for cat in ordered_main_cats]
ax2.legend(handles=main_legend_handles2, labels=main_legend_labels2, loc='center left', bbox_to_anchor=(1, 0.5), fontsize=10, title="Main Categories")
plt.tight_layout()
plt.savefig(f'{asset_dir}/arxiv_subcategory_monthly_percent_grouped.png', bbox_inches='tight')
plt.close()
print(f"Saved grouped monthly normalized percentage chart to {asset_dir}/arxiv_subcategory_monthly_percent_grouped.png")
