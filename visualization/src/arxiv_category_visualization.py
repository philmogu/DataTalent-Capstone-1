# arxiv_category_visualization.py
"""
Visualize arXiv categories: all categories grouped by main category, and main categories only.
Saves two images to visualization/asset/.
"""
import os
import json
import matplotlib.pyplot as plt
from tqdm import tqdm
import csv

subcategory_names_path = 'cleaning/asset/official_category_names.json'
main_categories_path = 'cleaning/asset/official_categories.json'
asset_dir = 'visualization/asset'
os.makedirs(asset_dir, exist_ok=True)

# Load subcategory names mapping (detailed names)
try:
    with open(subcategory_names_path, 'r') as f:
        subcategory_names = json.load(f)
except FileNotFoundError:
    print(f"Error: {subcategory_names_path} not found.")
    subcategory_names = {}

# Load main categories
try:
    with open(main_categories_path, 'r') as f:
        main_categories = set(json.load(f))
except FileNotFoundError:
    print(f"Error: {main_categories_path} not found.")
    main_categories = set()

# Map each category to its main category (assume main category is prefix before dot)
def get_main_category(cat):
    return cat.split('.')[0] if '.' in cat else cat

# Build mapping and counts
main_cat_map = {}
main_cat_counts = {}
for cat in tqdm(subcategory_names, desc="Processing categories"):
    main_cat = get_main_category(cat)
    main_cat_map[cat] = main_cat
    main_cat_counts[main_cat] = main_cat_counts.get(main_cat, 0) + 1

# Order main categories by count (descending)
ordered_main_cats = sorted(main_cat_counts, key=main_cat_counts.get, reverse=True)



# 1. Pie chart: all subcategories as slices, grouped by main category

import numpy as np
from matplotlib import colors as mcolors

# Use a maximally distinct color palette for main categories
from matplotlib import cm
distinct_cmaps = [cm.get_cmap('tab20'), cm.get_cmap('Set3'), cm.get_cmap('tab10')]
num_main = len(ordered_main_cats)
base_colors = []
for cmap in distinct_cmaps:
    base_colors.extend([cmap(i) for i in range(cmap.N)])
base_colors = base_colors[:num_main]
main_cat_to_color = {cat: base_colors[i] for i, cat in enumerate(ordered_main_cats)}


# Load subcategory counts from category_month_counts.csv
import pandas as pd
subcat_count_path = 'cleaning/asset/category_month_counts.csv'
try:
    df_counts = pd.read_csv(subcat_count_path)
except FileNotFoundError:
    print(f"Error: {subcat_count_path} not found.")
    df_counts = pd.DataFrame(columns=['month', 'categories_list', 'count'])

subcat_total_counts = df_counts.groupby('categories_list')['count'].sum().to_dict()

# Debug: print subcategories in CSV not found in mapping
missing_subcats = [cat for cat in subcat_total_counts if cat not in subcategory_names]
if missing_subcats:
    print("Subcategories in CSV missing from mapping (showing up to 20):")
    print(missing_subcats[:20])
    print(f"Total missing: {len(missing_subcats)}")

# For each main category, get its subcategories and their counts

subcat_labels = []
subcat_sizes = []
subcat_colors = []
for i, main_cat in enumerate(ordered_main_cats):
    # Use all subcategories from the subcategory_names mapping that match this main category
    group = [cat for cat in subcategory_names.keys() if get_main_category(cat) == main_cat]
    group_sorted = sorted(group, key=lambda c: subcat_total_counts.get(c, 0), reverse=True)
    base_rgb = np.array(main_cat_to_color[main_cat][:3])  # ignore alpha
    base_hsv = mcolors.rgb_to_hsv(base_rgb)
    for j, subcat in enumerate(group_sorted):
        # Two shades: slightly lighter and slightly darker than base
        if j % 2 == 0:
            hsv = base_hsv.copy()
            hsv[2] = min(1.0, base_hsv[2] + 0.04)  # slightly lighter
        else:
            hsv = base_hsv.copy()
            hsv[2] = max(0.0, base_hsv[2] - 0.04)  # slightly darker
        rgb = mcolors.hsv_to_rgb(hsv)
        subcat_labels.append(subcat)
        subcat_sizes.append(subcat_total_counts.get(subcat, 0))
        subcat_colors.append(rgb)


# Use same figure size and radius for both pie charts
pie_figsize = (14, 14)
pie_radius = 1.1

# Calculate main category shares by paper count (from subcategories)
main_cat_paper_counts = {cat: 0 for cat in ordered_main_cats}
for subcat, size in zip(subcat_labels, subcat_sizes):
    main_cat = main_cat_map[subcat]
    main_cat_paper_counts[main_cat] += size
total_papers = sum(main_cat_paper_counts.values())
main_cat_paper_percents = {cat: (main_cat_paper_counts[cat] / total_papers * 100 if total_papers > 0 else 0) for cat in ordered_main_cats}

# Pie chart for subcategories

fig1, ax1 = plt.subplots(figsize=pie_figsize)
wedges, texts = ax1.pie(subcat_sizes, labels=None, colors=subcat_colors, startangle=140, radius=pie_radius, labeldistance=1.05)
cs_idx = ordered_main_cats.index('cs') if 'cs' in ordered_main_cats else None
if cs_idx is not None:
    main_cat_start_indices = []
    idx = 0
    for cat in ordered_main_cats:
        main_cat_start_indices.append(idx)
        idx += sum(1 for subcat in subcat_labels if main_cat_map[subcat] == cat)
    cs_end_idx = main_cat_start_indices[cs_idx] + sum(1 for subcat in subcat_labels if main_cat_map[subcat] == 'cs')
    cs_math_border_angle = 360 * sum(subcat_sizes[:cs_end_idx]) / sum(subcat_sizes) if sum(subcat_sizes) > 0 else 0
    rotation_angle = 90 - cs_math_border_angle
else:
    rotation_angle = 140

fig1, ax1 = plt.subplots(figsize=pie_figsize)
wedges, texts = ax1.pie(subcat_sizes, labels=None, colors=subcat_colors, startangle=rotation_angle, radius=pie_radius, labeldistance=1.05)

fig1, ax1 = plt.subplots(figsize=pie_figsize)
wedges, texts = ax1.pie(subcat_sizes, labels=None, colors=subcat_colors, startangle=rotation_angle, radius=pie_radius, labeldistance=1.05)
# Annotate only every 10th label for readability, and stagger top labels
for i, (txt, wedge) in enumerate(zip(texts, wedges)):
    slice_angle = abs(wedge.theta2 - wedge.theta1)
    if slice_angle > 4:
        txt.set_text(subcat_labels[i])
    else:
        txt.set_text("")
ax1.set_title('All arXiv Subcategories Grouped by Main Category')
# Add legend for main categories and their percentage in the pie
legend_labels = [f"{cat}: {main_cat_paper_percents[cat]:.1f}%" for cat in ordered_main_cats]
legend_colors = [main_cat_to_color[cat] for cat in ordered_main_cats]
ax1.legend(handles=[plt.Line2D([0], [0], color=legend_colors[i], lw=6) for i in range(len(ordered_main_cats))],
           labels=legend_labels, loc='center left', bbox_to_anchor=(1, 0.5), fontsize=10, title="Main Categories")
plt.tight_layout()
plt.savefig(f'{asset_dir}/arxiv_all_subcategories_pie.png', bbox_inches='tight')
plt.close()
print(f"Saved all subcategories pie chart to {asset_dir}/arxiv_all_subcategories_pie.png")

# 2. Pie chart: main categories only (same base colors)
# Calculate subcategory percentage per main category for comparison
main_cat_subcat_counts_list = [main_cat_counts[cat] for cat in ordered_main_cats]
main_cat_subcat_total = sum(main_cat_subcat_counts_list)
main_cat_subcat_percents = [(count / main_cat_subcat_total * 100 if main_cat_subcat_total > 0 else 0) for count in main_cat_subcat_counts_list]

main_cat_paper_counts_list = [main_cat_paper_counts[cat] for cat in ordered_main_cats]
main_cat_labels = ordered_main_cats
main_cat_base_colors = [main_cat_to_color[cat] for cat in main_cat_labels]
main_cat_paper_total = sum(main_cat_paper_counts_list)
main_cat_paper_percents_list = [(count / main_cat_paper_total * 100 if main_cat_paper_total > 0 else 0) for count in main_cat_paper_counts_list]
cs_idx_main = ordered_main_cats.index('cs') if 'cs' in ordered_main_cats else None
if cs_idx_main is not None:
    cs_math_border_angle_main = 360 * sum(main_cat_paper_counts_list[:cs_idx_main+1]) / sum(main_cat_paper_counts_list) if sum(main_cat_paper_counts_list) > 0 else 0
    rotation_angle_main = 90 - cs_math_border_angle_main
else:
    rotation_angle_main = 140

fig2, ax2 = plt.subplots(figsize=pie_figsize)
wedges2, texts2, autotexts2 = ax2.pie(main_cat_paper_counts_list, labels=None, colors=main_cat_base_colors,
        autopct='%1.1f%%', startangle=rotation_angle_main, textprops={'fontsize': 10}, radius=pie_radius)
for i, txt in enumerate(texts2):
    txt.set_text(main_cat_labels[i])
ax2.set_title('Main arXiv Categories (Number of Papers)')
# Add legend for main categories and their percentage in the pie
legend_labels2 = [f"{cat}: {main_cat_paper_percents_list[i]:.1f}%" for i, cat in enumerate(main_cat_labels)]
ax2.legend(handles=[plt.Line2D([0], [0], color=main_cat_base_colors[i], lw=6) for i in range(len(main_cat_labels))],
           labels=legend_labels2, loc='center left', bbox_to_anchor=(1, 0.5), fontsize=10, title="Main Categories")
plt.tight_layout()
plt.savefig(f'{asset_dir}/arxiv_main_categories_pie.png', bbox_inches='tight')
plt.close()
print(f"Saved main categories pie chart to {asset_dir}/arxiv_main_categories_pie.png")

# Save to CSV for spreadsheet use
"""
Export top 10 biggest subcategories (by paper count) to CSV
"""
top10_subcat = sorted(
    zip(subcat_labels, subcat_sizes),
    key=lambda x: x[1],
    reverse=True
)[:10]
top10_rows = []
for rank, (subcat_id, count) in enumerate(top10_subcat, 1):
    main_cat = main_cat_map.get(subcat_id, get_main_category(subcat_id))
    expanded_name = subcategory_names.get(subcat_id, subcat_id)
    percent = (count / sum(subcat_sizes) * 100) if sum(subcat_sizes) > 0 else 0
    top10_rows.append([rank, main_cat, subcat_id, expanded_name, f"{percent:.2f}"])
top10_csv_path = os.path.join(asset_dir, 'top10_subcategories.csv')
with open(top10_csv_path, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Rank', 'Main Category', 'Subcategory ID', 'Expanded Name', 'Percent of Pie'])
    writer.writerows(top10_rows)
print(f"Saved top 10 subcategories to {top10_csv_path}")
csv_path = os.path.join(asset_dir, 'main_category_comparison.csv')
# Move this block after comparison_rows is defined
