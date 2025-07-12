"""
run_all.py

Runs all data cleaning and visualization scripts in order for the arXiv category analysis project.
"""
import subprocess
import sys
import os

CLEANING_DIR = "cleaning/src"
VISUALIZATION_DIR = "visualization/src"

cleaning_scripts = [
    "extract_official_categories.py",
    "extract_official_category_names.py",
    "extract_unique_categories.py",
    "extract_category_month_counts.py",
    "extract_major_category_month_counts.py",
    "extract_total_category_month_counts.py"
]

visualization_scripts = [
    "arxiv_category_visualization.py",
    "arxiv_category_monthly_publication_distribution.py",
    "arxiv_subcategory_monthly_distribution.py",
    "arxiv_subcategory_yearly_distribution.py",
    "arxiv_top_subcategories_by_year_compact.py"
]

def run_scripts(scripts, directory):
    for script in scripts:
        script_path = os.path.join(directory, script)
        print(f"\nRunning {script_path} ...")
        result = subprocess.run([sys.executable, script_path])
        if result.returncode != 0:
            print(f"Error running {script_path}")
            sys.exit(result.returncode)
        else:
            print(f"Finished {script_path}")

if __name__ == "__main__":
    print("Starting data cleaning...")
    run_scripts(cleaning_scripts, CLEANING_DIR)
    print("\nStarting visualizations...")
    run_scripts(visualization_scripts, VISUALIZATION_DIR)
    print("\nAll scripts completed successfully.")
