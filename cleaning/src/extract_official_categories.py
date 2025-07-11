"""
Extracts official categories from arxiv-metadata JSON and saves to cleaning/asset/official_categories.json

Source data: arXiv metadata snapshot
Homepage: https://www.kaggle.com/datasets/Cornell-University/arxiv
"""
import dask.dataframe as dd
import json
from tqdm import tqdm
import os

DATA_PATH = 'data/arxiv-metadata-oai-snapshot.json'
OUTPUT_PATH = 'cleaning/asset/official_categories.json'

# List of official arXiv categories
OFFICIAL_ARXIV_CATEGORIES = set([
    # Computer Science
    'cs.AI','cs.CL','cs.CC','cs.CE','cs.CG','cs.GT','cs.CV','cs.CY','cs.CR','cs.DS','cs.DB','cs.DL','cs.DM','cs.DC','cs.ET','cs.FL','cs.GL','cs.GR','cs.AR','cs.HC','cs.IR','cs.IT','cs.LG','cs.LO','cs.MS','cs.MA','cs.MM','cs.NI','cs.NE','cs.NA','cs.OS','cs.OH','cs.PF','cs.PL','cs.RO','cs.SE','cs.SD','cs.SC',
    # Economics
    'econ.EM','econ.GN','econ.TH',
    # Electrical Engineering and Systems Science
    'eess.AS','eess.IV','eess.SP','eess.SY',
    # Mathematics
    'math.AG','math.AT','math.AP','math.CT','math.CA','math.CO','math.AC','math.CV','math.DG','math.DS','math.FA','math.GM','math.GN','math.GR','math.GT','math.HO','math.IT','math.KT','math.LO','math.MP','math.MG','math.NT','math.NA','math.OA','math.OC','math.PR','math.QA','math.RT','math.RA','math.SP','math.ST','math.SG',
    # Physics
    'physics.acc-ph','physics.ao-ph','physics.atom-ph','physics.atm-clus','physics.bio-ph','physics.chem-ph','physics.class-ph','physics.comp-ph','physics.data-an','physics.flu-dyn','physics.gen-ph','physics.geo-ph','physics.hist-ph','physics.ins-det','physics.med-ph','physics.optics','physics.ed-ph','physics.soc-ph','physics.plasm-ph','physics.pop-ph','physics.space-ph',
    # Quantitative Biology
    'q-bio.BM','q-bio.CB','q-bio.GN','q-bio.MN','q-bio.NC','q-bio.OT','q-bio.PE','q-bio.QM','q-bio.PX','q-bio.SC',
    # Quantitative Finance
    'q-fin.CP','q-fin.EC','q-fin.GN','q-fin.MF','q-fin.PM','q-fin.PR','q-fin.RM','q-fin.ST',
    # Statistics
    'stat.AP','stat.CO','stat.ME','stat.ML','stat.OT','stat.TH'
])

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
        print("Extracting official categories with progress bar...")
        unique_categories = set()
        cats_list = ddf['categories_list'].compute()
        for cats in tqdm(cats_list, desc="Processing rows"):
            if isinstance(cats, list):
                unique_categories.update(cats)
        official_categories = [cat for cat in unique_categories if cat in OFFICIAL_ARXIV_CATEGORIES]
        print("Writing JSON with progress bar...")
        os.makedirs('cleaning/asset', exist_ok=True)
        with tqdm(total=len(official_categories), desc="Saving categories") as pbar:
            with open(OUTPUT_PATH, 'w') as f:
                json.dump(official_categories, f, indent=2)
                pbar.update(len(official_categories))
        print(f"Saved to {OUTPUT_PATH}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
