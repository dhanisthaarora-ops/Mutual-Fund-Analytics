"""
Master pipeline runner for Bluestock Mutual Fund Analytics.

Runs data ingestion, cleaning/loading, metric computation,
and recommender-related outputs in sequence.
"""

import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]


def run_script(script_name):
    script_path = BASE_DIR / "scripts" / script_name
    print(f"Running {script_path.name}...")
    subprocess.run(["python", str(script_path)], check=True)
    print(f"Finished {script_path.name}")


def main():
    run_script("live_nav_fetch.py")
    run_script("etl_pipeline.py")
    print("Pipeline completed successfully.")


if __name__ == "__main__":
    main()
