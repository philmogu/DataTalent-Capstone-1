"""
Extracts unique categories from arxiv-metadata JSON and saves to cleaning/asset/unique_categories.json

Source data: arXiv metadata snapshot
Homepage: https://www.kaggle.com/datasets/Cornell-University/arxiv
"""
import dask.dataframe as dd
import json
from tqdm import tqdm
import os

DATA_PATH = 'data/arxiv-metadata-oai-snapshot.json'
OUTPUT_PATH = 'cleaning/asset/unique_categories.json'

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
        ddf['categories_list'] = ddf['categories'].str.split()
        print("Extracting unique categories with progress bar...")
        unique_categories = set()
        cats_list = ddf['categories_list'].compute()
        for cats in tqdm(cats_list, desc="Processing rows"):
            if isinstance(cats, list):
                unique_categories.update(cats)
        unique_categories_list = sorted(unique_categories)
        print("Writing JSON with progress bar...")
        os.makedirs('cleaning/asset', exist_ok=True)
        with tqdm(total=len(unique_categories_list), desc="Saving categories") as pbar:
            with open(OUTPUT_PATH, 'w') as f:
                json.dump(unique_categories_list, f, indent=2)
                pbar.update(len(unique_categories_list))
        print(f"Saved to {OUTPUT_PATH}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
