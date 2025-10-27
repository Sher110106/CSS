#!/usr/bin/env python3
"""
Data Collection Runner
Easy-to-use script for running Reddit data collection
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.config_loader import ConfigLoader
import argparse

# Import the scraper class
import importlib.util
spec = importlib.util.spec_from_file_location("data_collection", 
                                               Path(__file__).parent / "01_data_collection.py")
collection_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(collection_module)
RedditScraper = collection_module.RedditScraper


def main():
    """Main execution"""
    parser = argparse.ArgumentParser(
        description='Run Reddit data collection',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Collect 10,000 posts with 8 hour limit (default):
  python scripts/run_collection.py
  
  # Collect 20,000 posts with 12 hour limit:
  python scripts/run_collection.py --target 20000 --hours 12
  
  # Resume from checkpoint:
  python scripts/run_collection.py --resume
  
  # Quick test run:
  python scripts/run_collection.py --target 100 --hours 0.5

Features:
  - Automatic checkpointing every 5 minutes
  - Resume capability after interruption
  - Adaptive rate limiting
  - Error recovery and retry logic
  - Graceful shutdown on Ctrl+C
  - Progress tracking and reporting
        """
    )
    
    parser.add_argument(
        '--target',
        type=int,
        default=10000,
        help='Target number of posts to collect (default: 10000)'
    )
    
    parser.add_argument(
        '--hours',
        type=float,
        default=8.0,
        help='Maximum runtime in hours (default: 8.0)'
    )
    
    parser.add_argument(
        '--resume',
        action='store_true',
        help='Resume from last checkpoint'
    )
    
    parser.add_argument(
        '--no-confirm',
        action='store_true',
        help='Skip confirmation prompt and start immediately'
    )
    
    args = parser.parse_args()
    
    print("\n" + "=" * 80)
    print("REDDIT DATA COLLECTION")
    print("=" * 80)
    
    try:
        # Load configuration
        loader = ConfigLoader()
        config = loader.load()
        
        # Validate credentials
        if not loader.validate_reddit_credentials():
            print("\n❌ ERROR: Reddit API credentials not configured!")
            print("\nPlease create/update your .env file with:")
            print("  REDDIT_CLIENT_ID=your_client_id")
            print("  REDDIT_CLIENT_SECRET=your_client_secret")
            print("  REDDIT_USER_AGENT=your_user_agent")
            print("\nGet credentials from: https://www.reddit.com/prefs/apps")
            return 1
        
        print("✓ Configuration loaded")
        print("✓ Reddit credentials validated")
        
        # Show configuration
        print(f"\nCollection Configuration:")
        print(f"  Target posts:     {args.target:,}")
        print(f"  Max runtime:      {args.hours} hours")
        print(f"  Subreddits:       {', '.join(config['data_collection']['subreddits'])}")
        print(f"  Keywords:         {', '.join(config['data_collection']['keywords'])}")
        print(f"  Resume mode:      {'Yes' if args.resume else 'No'}")
        
        print(f"\nFeatures:")
        print(f"  ✓ Auto-save every 5 minutes")
        print(f"  ✓ Resume capability")
        print(f"  ✓ Adaptive rate limiting")
        print(f"  ✓ Error recovery")
        print(f"  ✓ Progress tracking")
        
        print(f"\nOutput files:")
        print(f"  Posts:      data/raw/posts.csv")
        print(f"  Comments:   data/raw/comments.csv")
        print(f"  Report:     data/metadata/collection_report.json")
        print(f"  Logs:       logs/collection_*.log")
        
        print("\n" + "=" * 80)
        print("IMPORTANT NOTES:")
        print("=" * 80)
        print("• Press Ctrl+C at any time to stop gracefully")
        print("• Data is auto-saved every 5 minutes")
        print("• You can resume by running with --resume flag")
        print("• Check logs/ directory for detailed progress")
        print("• Reddit API has rate limits - script handles this automatically")
        print("=" * 80)
        
        # Confirmation
        if not args.no_confirm:
            response = input("\nPress Enter to start collection (or Ctrl+C to cancel): ")
        
        print("\nStarting collection...")
        print("Monitor progress in the log file or watch this console.")
        print("=" * 80 + "\n")
        
        # Initialize scraper
        scraper = RedditScraper(config)
        
        # Collect data
        scraper.collect_data(
            target_posts=args.target,
            max_runtime_hours=args.hours
        )
        
        # Save final data
        scraper.save_final_data()
        
        # Final summary
        print("\n" + "=" * 80)
        print("✅ COLLECTION COMPLETE!")
        print("=" * 80)
        print(f"✓ Posts collected:     {len(scraper.posts_collected):,}")
        print(f"✓ Comments collected:  {len(scraper.comments_collected):,}")
        print(f"✓ Total errors:        {scraper.total_errors}")
        print(f"\n✓ Data saved to:")
        print(f"    data/raw/posts.csv")
        print(f"    data/raw/comments.csv")
        print(f"\n✓ Report saved to:")
        print(f"    data/metadata/collection_report.json")
        print("=" * 80)
        print("\nNext steps:")
        print("  1. Run preprocessing: python scripts/02_data_preprocessing.py")
        print("  2. Or review data: pandas.read_csv('data/raw/posts.csv')")
        print("=" * 80 + "\n")
        
        return 0
    
    except KeyboardInterrupt:
        print("\n\n" + "=" * 80)
        print("⚠ COLLECTION INTERRUPTED BY USER")
        print("=" * 80)
        if 'scraper' in locals():
            print("Saving progress...")
            try:
                scraper._save_checkpoint()
                scraper.save_final_data()
                print(f"✓ Saved {len(scraper.posts_collected):,} posts")
                print(f"✓ Saved {len(scraper.comments_collected):,} comments")
                print("\n✓ You can resume by running:")
                print("    python scripts/run_collection.py --resume")
            except Exception as e:
                print(f"❌ Error saving: {e}")
        print("=" * 80 + "\n")
        return 130  # Standard exit code for SIGINT
    
    except Exception as e:
        print("\n" + "=" * 80)
        print("❌ ERROR OCCURRED")
        print("=" * 80)
        print(f"Error: {e}")
        import traceback
        print("\nFull traceback:")
        print(traceback.format_exc())
        print("=" * 80)
        
        if 'scraper' in locals():
            print("\nAttempting to save collected data...")
            try:
                scraper.save_final_data()
                print(f"✓ Saved {len(scraper.posts_collected):,} posts")
                print(f"✓ Saved {len(scraper.comments_collected):,} comments")
            except:
                print("❌ Could not save data")
        
        print("\nCheck the log file in logs/ directory for details")
        print("=" * 80 + "\n")
        return 1


if __name__ == '__main__':
    sys.exit(main())
