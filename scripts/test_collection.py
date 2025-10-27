"""
Test Script for Data Collection
Quick test to verify the collection system works before running overnight
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.config_loader import ConfigLoader
import pandas as pd

# Import the scraper class
import importlib.util
spec = importlib.util.spec_from_file_location("overnight_collection", 
                                               Path(__file__).parent / "01_data_collection_overnight.py")
overnight_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(overnight_module)
OvernightRedditScraper = overnight_module.OvernightRedditScraper


def test_small_collection():
    """Test collection with small dataset"""
    print("\n" + "=" * 80)
    print("TESTING DATA COLLECTION")
    print("=" * 80)
    print("This will collect ~50 posts to verify everything works")
    print("Should take about 2-3 minutes")
    print("=" * 80 + "\n")
    
    try:
        # Load configuration
        loader = ConfigLoader()
        config = loader.load()
        
        # Validate credentials
        if not loader.validate_reddit_credentials():
            print("❌ ERROR: Reddit API credentials not configured!")
            print("Please set up your .env file with valid credentials.")
            return False
        
        print("✓ Configuration loaded")
        print("✓ Reddit credentials validated")
        
        # Initialize scraper
        print("\nInitializing scraper...")
        scraper = OvernightRedditScraper(config, checkpoint_file='data/raw/test_checkpoint.json')
        print("✓ Scraper initialized")
        
        # Test collection with small target
        print("\nStarting test collection (target: 50 posts, max 5 minutes)...")
        scraper.collect_data(target_posts=50, max_runtime_hours=0.1)  # 6 minutes max
        
        # Save data
        print("\nSaving test data...")
        scraper.save_final_data()
        
        # Verify results
        print("\n" + "=" * 80)
        print("TEST RESULTS")
        print("=" * 80)
        
        if Path('data/raw/posts.csv').exists():
            df_posts = pd.read_csv('data/raw/posts.csv')
            print(f"✓ Posts collected: {len(df_posts)}")
            print(f"✓ Unique posts: {df_posts['post_id'].nunique()}")
            print(f"✓ Subreddits: {', '.join(df_posts['subreddit'].unique())}")
        else:
            print("❌ No posts file created")
            return False
        
        if Path('data/raw/comments.csv').exists():
            df_comments = pd.read_csv('data/raw/comments.csv')
            print(f"✓ Comments collected: {len(df_comments)}")
        else:
            print("⚠ No comments file created (this may be OK if posts had no comments)")
        
        print(f"\n✓ Total errors during collection: {scraper.total_errors}")
        
        if len(df_posts) >= 10:
            print("\n" + "=" * 80)
            print("✅ TEST PASSED - Collection system working!")
            print("=" * 80)
            print("\nYou can now run the overnight collection with confidence.")
            print("Use: python scripts/run_overnight_collection.py")
            return True
        else:
            print("\n" + "=" * 80)
            print("⚠ TEST INCOMPLETE - Less than 10 posts collected")
            print("=" * 80)
            print("This might be due to:")
            print("  - Reddit API rate limits")
            print("  - Limited matching posts in subreddits")
            print("  - Network issues")
            print("\nThe script is working, but you may want to adjust:")
            print("  - Keywords in config.yaml")
            print("  - Subreddits in config.yaml")
            print("  - Try running again in a few minutes")
            return True
        
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        return False
    
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        print(traceback.format_exc())
        return False


if __name__ == '__main__':
    success = test_small_collection()
    sys.exit(0 if success else 1)
