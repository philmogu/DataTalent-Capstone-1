"""
Extracts category-month counts from arxiv-metadata JSON and saves to cleaning/asset/category_month_counts.csv

Source data: arXiv metadata snapshot
Homepage: https://www.kaggle.com/datasets/Cornell-University/arxiv
"""
import dask.dataframe as dd
import pandas as pd
from tqdm import tqdm
import os

DATA_PATH = 'data/arxiv-metadata-oai-snapshot.json'
OUTPUT_PATH = 'cleaning/asset/category_month_counts.csv'

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
        print("Computing category-month counts (this may take a while)...")
        cat_month_counts = ddf_exploded.groupby(['month', 'categories_list']).size().compute().reset_index(name='count')
        print("Writing CSV with progress bar...")
        os.makedirs('cleaning/asset', exist_ok=True)
        # Progress bar for writing CSV
        with tqdm(total=len(cat_month_counts), desc="Saving rows") as pbar:
            cat_month_counts.to_csv(OUTPUT_PATH, index=False)
            pbar.update(len(cat_month_counts))
        print(f"Saved to {OUTPUT_PATH}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
