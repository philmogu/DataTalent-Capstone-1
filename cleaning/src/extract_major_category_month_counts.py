"""
Extracts major category-month counts from arxiv-metadata JSON and saves to cleaning/asset/major_category_month_counts.csv

Source data: arXiv metadata snapshot
Homepage: https://www.kaggle.com/datasets/Cornell-University/arxiv
"""
import dask.dataframe as dd
import pandas as pd
from tqdm import tqdm
import os

DATA_PATH = 'data/arxiv-metadata-oai-snapshot.json'
OUTPUT_PATH = 'cleaning/asset/major_category_month_counts.csv'

def map_major_category(cat):
    if isinstance(cat, str):
        if cat.startswith('cs'): return 'Computer Science'
        elif cat.startswith('econ'): return 'Economics'
        elif cat.startswith('eess'): return 'Electrical Engineering and Systems Science'
        elif cat.startswith('math'): return 'Mathematics'
        elif cat.startswith('physics'): return 'Physics'
        elif cat.startswith('q-bio'): return 'Quantitative Biology'
        elif cat.startswith('q-fin'): return 'Quantitative Finance'
        elif cat.startswith('stat'): return 'Statistics'
        else: return 'Other'
    return 'Other'

def main():
    print(f"Loading {DATA_PATH} ...")
    try:
        dtypes = {
            'id': 'object',
            'submitter': 'object',
            'authors': 'object',
            'title': 'object',
            'comments': 'object',
            'journal-ref': 'object',
            'doi': 'object',
            'report-no': 'object',
            'categories': 'object',
            'license': 'object',
            'abstract': 'object',
            'versions': 'object',
            'update_date': 'object',
            'authors_parsed': 'object'
        }
        ddf = dd.read_json(DATA_PATH, lines=True, blocksize="64MB", dtype=dtypes)
        ddf['month'] = ddf['update_date'].str[:7]
        ddf['categories_list'] = ddf['categories'].str.split()
        ddf_exploded = ddf.explode('categories_list')
        print("Computing major category-month counts (this may take a while)...")
        cat_month_counts = ddf_exploded.groupby(['month', 'categories_list']).size().compute().reset_index(name='count')
        cat_month_counts['major_category'] = cat_month_counts['categories_list'].apply(map_major_category)
        major_cat_month_counts = cat_month_counts.groupby(['month', 'major_category'])['count'].sum().reset_index()
        print("Writing CSV with progress bar...")
        os.makedirs('cleaning/asset', exist_ok=True)
        with tqdm(total=len(major_cat_month_counts), desc="Saving rows") as pbar:
            major_cat_month_counts.to_csv(OUTPUT_PATH, index=False)
            pbar.update(len(major_cat_month_counts))
        print(f"Saved to {OUTPUT_PATH}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
