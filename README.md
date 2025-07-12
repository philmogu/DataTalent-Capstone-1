
# Capstone #1: Analyzing arXiv Categories

This project explores patterns in arXiv metadata, focusing on category trends and their evolution. arXiv is an open-access platform for research papers, especially preprints, with rapid feedback but no formal peer review.

**Key Findings:**
- Computer Science, Mathematics, and Physics account for over 70% of submissions.
- AI-related subcategories (Machine Learning, Computer Vision, Artificial Intelligence) have dominated since 2018.
- Paper submissions are rising steadily, with Computer Science growing fastest and EESS as the newest major category.
- May is the most popular month for submissions; August is the least.

**Future Directions:**
- Analyze author-category connections and subcategory trends in more detail.

## Data Cleaning & Visualization Process

### Data Cleaning
- Raw arXiv metadata (JSON) is loaded using Dask for efficient processing of large files.
- Key fields extracted: ID, submitter, authors, title, comments, journal-ref, DOI, abstract, categories, versions, update_date.
- Categories are split into lists, and exploded so each row represents a single category for a paper.
- Month and year are parsed from the update date for time-based analysis.
- Major categories are mapped from subcategory prefixes (e.g., 'cs' → Computer Science).
- Unique categories and official category names are extracted and saved as JSON for reference.
- Aggregated counts (e.g., category-month, major-category-month, total counts) are saved as CSVs in `cleaning/asset/`.
- Progress bars (tqdm) are used to track long-running operations.
- Basic error handling is included for missing files.

### Visualization
- Data is loaded from cleaned CSVs and JSONs using pandas.
- Visualizations are created using matplotlib.
- Types of plots include pie charts (category distribution), stacked bar charts (yearly/monthly trends), and line charts (growth over time).
- Categories are grouped and color-coded for clarity; color palettes are chosen for distinctness.
- Each visualization is saved as an image file (PNG) in `visualization/asset/`.
- Progress bars are shown during data processing for visualizations.
- Scripts are modular and well-commented for clarity and reproducibility.

For more details, see scripts in `cleaning/src/` and `visualization/src/`.
---

## Environment & Requirements
This project uses Python 3.8+ and the following packages:
- pandas
- numpy
- tqdm
- dask

## How to Run Scripts
You can run all data cleaning and visualization scripts automatically with:
```bash
python run_all.py
```

Alternatively, to run scripts step-by-step:
1. Run scripts in `cleaning/src/` to preprocess and aggregate the raw metadata.
2. Run scripts in `visualization/src/` to generate and save visualizations to `visualization/asset/`.

## Data Source Reference
Original arXiv metadata from Kaggle:
https://www.kaggle.com/datasets/Cornell-University/arxiv

## License/Attribution
arXiv metadata is provided under the terms specified by arXiv and Kaggle. Please review their respective licenses for usage details.
