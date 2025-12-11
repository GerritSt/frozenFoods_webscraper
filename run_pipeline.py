"""
Master Pipeline Script
----------------------
Runs the complete data collection and processing pipeline.
Simply executes collect_data.py then process_data.py.
"""

import sys
from datetime import datetime
import collect_data
import process_data


def main():
    """Run the full pipeline: collection then processing."""
    
    print("\n" + "=" * 80)
    print("FROZEN FOODS PRICE COMPARISON PIPELINE")
    print("=" * 80)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Stage 1: Data Collection
    print("STAGE 1: Data Collection")
    print("-" * 80)
    collect_data.main()
    
    # Stage 2: Data Processing
    print("\n\nSTAGE 2: Data Processing")
    print("-" * 80)
    process_data.main()
    
    print("\n" + "=" * 80)
    print("PIPELINE COMPLETE!")
    print("=" * 80)
    print(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nOutput: data/processed/price_comparison.xlsx\n")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n✗ Pipeline failed: {e}")
        sys.exit(1)
