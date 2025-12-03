"""
Master Pipeline Script
----------------------
Runs the complete data collection and processing pipeline.

Usage:
    python run_pipeline.py              # Run full pipeline
    python run_pipeline.py --collect    # Only collect data
    python run_pipeline.py --process    # Only process data
"""

import argparse
import sys
from datetime import datetime

# Import both stages
from collect_data import DataCollector
from process_data import DataProcessor


def run_full_pipeline(headless: bool = True, max_pages: int = None, max_items: int = None):
    """Run both collection and processing stages."""
    
    print("\n" + "=" * 80)
    print("FROZEN FOODS PRICE COMPARISON PIPELINE")
    print("=" * 80)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Stage 1: Data Collection
    print("STAGE 1: Data Collection")
    print("-" * 80)
    
    collector = DataCollector(headless=headless, max_pages=max_pages, max_items=max_items)
    results = collector.collect_all()
    
    if not any(results.values()):
        print("\n✗ Data collection failed for all retailers. Aborting.")
        return False
    
    # Stage 2: Data Processing
    print("\n\nSTAGE 2: Data Processing")
    print("-" * 80)
    
    processor = DataProcessor()
    success = processor.process_all()
    
    if not success:
        print("\n✗ Data processing failed. Aborting.")
        return False
    
    print("\n" + "=" * 80)
    print("PIPELINE COMPLETE!")
    print("=" * 80)
    print(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print("Output files:")
    print("  • Raw data: data/raw/*_raw_*.xlsx")
    print("  • Comparison tables: data/processed/comparison_*.xlsx")
    print()
    
    return True


def run_collection_only(headless: bool = True, max_pages: int = None, max_items: int = None):
    """Run only data collection stage."""
    
    print("\n" + "=" * 80)
    print("DATA COLLECTION ONLY")
    print("=" * 80)
    
    collector = DataCollector(headless=headless, max_pages=max_pages, max_items=max_items)
    results = collector.collect_all()
    
    return any(results.values())


def run_processing_only():
    """Run only data processing stage."""
    
    print("\n" + "=" * 80)
    print("DATA PROCESSING ONLY")
    print("=" * 80)
    
    processor = DataProcessor()
    success = processor.process_all()
    
    return success


def main():
    """Main execution with command-line arguments."""
    
    parser = argparse.ArgumentParser(
        description='Frozen Foods Price Comparison Pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_pipeline.py                    # Run full pipeline
  python run_pipeline.py --collect          # Only collect data
  python run_pipeline.py --process          # Only process data
  python run_pipeline.py --headless         # Run in headless mode
  python run_pipeline.py --max-pages 5      # Scrape 5 pages per retailer
  python run_pipeline.py --max-items 50     # Limit to 50 items per retailer
        """
    )
    
    # Pipeline stage selection
    stage_group = parser.add_mutually_exclusive_group()
    stage_group.add_argument(
        '--collect',
        action='store_true',
        help='Run only data collection stage'
    )
    stage_group.add_argument(
        '--process',
        action='store_true',
        help='Run only data processing stage'
    )
    
    # Configuration options
    parser.add_argument(
        '--headless',
        action='store_true',
        help='Run browser in headless mode (faster, no GUI)'
    )
    parser.add_argument(
        '--max-pages',
        type=int,
        default=3,
        help='Maximum pages to scrape per retailer (default: 3)'
    )
    parser.add_argument(
        '--max-items',
        type=int,
        default=None,
        help='Maximum items to scrape per retailer (default: no limit)'
    )
    
    args = parser.parse_args()
    
    # Run appropriate stage
    if args.collect:
        success = run_collection_only(
            headless=args.headless,
            max_pages=args.max_pages,
            max_items=args.max_items
        )
    elif args.process:
        success = run_processing_only()
    else:
        # Run full pipeline
        success = run_full_pipeline(
            headless=args.headless,
            max_pages=args.max_pages,
            max_items=args.max_items
        )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
