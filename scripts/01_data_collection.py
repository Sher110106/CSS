"""
Enhanced Reddit Data Collection Script
Features:
- Robust error handling and retry logic
- Adaptive rate limiting
- Checkpoint/resume capability
- Multiple collection strategies
- Graceful degradation on errors
- Progress tracking and reporting
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import praw
import pandas as pd
from datetime import datetime, timedelta
import time
from tqdm import tqdm
import logging
import traceback
import json
import signal
from utils import setup_logger, save_dataframe, save_json
from config.config_loader import ConfigLoader


class RedditScraper:
    """Enhanced Reddit scraper designed for long-running collection"""
    
    def __init__(self, config, checkpoint_file='data/raw/checkpoint.json'):
        """
        Initialize Reddit API connection
        
        Args:
            config: Configuration dictionary
            checkpoint_file: Path to checkpoint file for resuming
        """
        self.config = config
        self.checkpoint_file = checkpoint_file
        self.logger = setup_logger(
            'data_collection',
            f'logs/collection_{datetime.now():%Y%m%d_%H%M%S}.log'
        )
        
        self.reddit = None
        self.posts_collected = []
        self.comments_collected = []
        self.collected_post_ids = set()
        
        # Rate limiting configuration
        self.requests_count = 0
        self.requests_start_time = time.time()
        self.max_requests_per_minute = 50  # Conservative limit
        self.request_delay = 1.2  # Seconds between requests
        
        # Error tracking
        self.consecutive_errors = 0
        self.max_consecutive_errors = 10
        self.total_errors = 0
        
        # Collection progress
        self.start_time = datetime.now()
        self.last_save_time = datetime.now()
        self.save_interval_minutes = 5
        
        # Graceful shutdown
        self.should_stop = False
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        self._initialize_reddit()
        self._load_checkpoint()
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        self.logger.warning(f"Received signal {signum}. Initiating graceful shutdown...")
        self.should_stop = True
    
    def _initialize_reddit(self):
        """Initialize Reddit API connection with retry"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                reddit_config = self.config['reddit']
                
                self.reddit = praw.Reddit(
                    client_id=reddit_config['client_id'],
                    client_secret=reddit_config['client_secret'],
                    user_agent=reddit_config['user_agent'],
                    timeout=30  # 30 second timeout
                )
                
                # Test connection
                _ = self.reddit.user.me()
                self.logger.info(f"Connected to Reddit (read-only: {self.reddit.read_only})")
                self.logger.info("Reddit API connection successful")
                return
                
            except Exception as e:
                self.logger.warning(f"Connection attempt {attempt + 1}/{max_retries} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(5 * (attempt + 1))
                else:
                    self.logger.error("Failed to initialize Reddit API after all retries")
                    raise
    
    def _load_checkpoint(self):
        """Load checkpoint from previous run if exists"""
        checkpoint_path = Path(self.checkpoint_file)
        
        if checkpoint_path.exists():
            try:
                with open(checkpoint_path, 'r') as f:
                    checkpoint = json.load(f)
                
                self.logger.info(f"Loading checkpoint from {checkpoint_path}")
                self.logger.info(f"Previous run collected: {checkpoint.get('posts_count', 0)} posts, "
                               f"{checkpoint.get('comments_count', 0)} comments")
                
                # Load existing data
                if Path('data/raw/posts_checkpoint.csv').exists():
                    df_posts = pd.read_csv('data/raw/posts_checkpoint.csv')
                    self.posts_collected = df_posts.to_dict('records')
                    self.collected_post_ids = set(df_posts['post_id'].unique())
                    self.logger.info(f"Loaded {len(self.posts_collected)} posts from checkpoint")
                
                if Path('data/raw/comments_checkpoint.csv').exists():
                    df_comments = pd.read_csv('data/raw/comments_checkpoint.csv')
                    self.comments_collected = df_comments.to_dict('records')
                    self.logger.info(f"Loaded {len(self.comments_collected)} comments from checkpoint")
                
                self.logger.info("Checkpoint loaded successfully. Resuming collection...")
                
            except Exception as e:
                self.logger.warning(f"Failed to load checkpoint: {e}. Starting fresh.")
                self.collected_post_ids = set()
    
    def _save_checkpoint(self):
        """Save checkpoint for resuming later"""
        try:
            checkpoint = {
                'timestamp': datetime.now().isoformat(),
                'posts_count': len(self.posts_collected),
                'comments_count': len(self.comments_collected),
                'collected_post_ids': list(self.collected_post_ids),
                'total_errors': self.total_errors,
                'runtime_minutes': (datetime.now() - self.start_time).total_seconds() / 60
            }
            
            # Save checkpoint metadata
            with open(self.checkpoint_file, 'w') as f:
                json.dump(checkpoint, f, indent=2)
            
            # Save data
            if self.posts_collected:
                df_posts = pd.DataFrame(self.posts_collected)
                save_dataframe(df_posts, 'data/raw/posts_checkpoint.csv', format='csv')
            
            if self.comments_collected:
                df_comments = pd.DataFrame(self.comments_collected)
                save_dataframe(df_comments, 'data/raw/comments_checkpoint.csv', format='csv')
            
            self.last_save_time = datetime.now()
            self.logger.info(f"Checkpoint saved: {len(self.posts_collected)} posts, "
                           f"{len(self.comments_collected)} comments")
            
        except Exception as e:
            self.logger.error(f"Failed to save checkpoint: {e}")
    
    def _respect_rate_limit(self):
        """Adaptive rate limiting with backoff"""
        self.requests_count += 1
        
        # Check if we should slow down based on requests per minute
        elapsed = time.time() - self.requests_start_time
        if elapsed >= 60:
            requests_per_minute = self.requests_count / (elapsed / 60)
            if requests_per_minute > self.max_requests_per_minute:
                self.logger.warning(f"Rate limit approaching ({requests_per_minute:.1f} req/min). Slowing down...")
                self.request_delay = min(self.request_delay * 1.5, 5.0)
            
            # Reset counter
            self.requests_count = 0
            self.requests_start_time = time.time()
        
        # Base delay between requests
        time.sleep(self.request_delay)
    
    def _handle_api_error(self, error, context=""):
        """Handle API errors with exponential backoff"""
        self.consecutive_errors += 1
        self.total_errors += 1
        
        error_str = str(error).lower()
        
        # Check for rate limiting
        if 'rate limit' in error_str or '429' in error_str:
            wait_time = min(60 * (2 ** self.consecutive_errors), 600)  # Max 10 minutes
            self.logger.warning(f"Rate limit hit. Waiting {wait_time} seconds...")
            time.sleep(wait_time)
            return True  # Can retry
        
        # Check for server errors
        elif '500' in error_str or '502' in error_str or '503' in error_str:
            wait_time = min(30 * (2 ** self.consecutive_errors), 300)  # Max 5 minutes
            self.logger.warning(f"Server error. Waiting {wait_time} seconds...")
            time.sleep(wait_time)
            return True  # Can retry
        
        # Check for timeout
        elif 'timeout' in error_str or 'timed out' in error_str:
            self.logger.warning(f"Timeout error in {context}. Retrying...")
            time.sleep(10)
            return True  # Can retry
        
        # Check if we should stop due to too many errors
        elif self.consecutive_errors >= self.max_consecutive_errors:
            self.logger.error(f"Too many consecutive errors ({self.consecutive_errors}). Stopping collection.")
            self.should_stop = True
            return False  # Stop
        
        else:
            self.logger.error(f"Error in {context}: {error}")
            time.sleep(5)
            return True  # Can retry for unknown errors
    
    def get_post_data(self, submission):
        """Extract data from Reddit submission with error handling"""
        try:
            return {
                'post_id': submission.id,
                'author': str(submission.author) if submission.author else '[deleted]',
                'title': submission.title,
                'selftext': submission.selftext,
                'score': submission.score,
                'num_comments': submission.num_comments,
                'created_utc': datetime.fromtimestamp(submission.created_utc).isoformat(),
                'subreddit': str(submission.subreddit),
                'url': submission.url,
                'upvote_ratio': submission.upvote_ratio,
                'is_self': submission.is_self,
                'permalink': submission.permalink,
                'collected_at': datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.warning(f"Error extracting post data: {e}")
            return None
    
    def get_comments(self, submission, max_comments=100):
        """Extract comments from post with enhanced error handling"""
        comments = []
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                submission.comments.replace_more(limit=2)  # Get some nested comments
                
                for comment in submission.comments.list()[:max_comments]:
                    try:
                        if isinstance(comment, praw.models.Comment):
                            comment_data = {
                                'comment_id': comment.id,
                                'post_id': submission.id,
                                'author': str(comment.author) if comment.author else '[deleted]',
                                'body': comment.body,
                                'score': comment.score,
                                'created_utc': datetime.fromtimestamp(comment.created_utc).isoformat(),
                                'parent_id': comment.parent_id,
                                'collected_at': datetime.now().isoformat()
                            }
                            comments.append(comment_data)
                    except Exception as e:
                        continue
                
                # Success - reset consecutive errors
                if len(comments) > 0:
                    self.consecutive_errors = 0
                
                return comments
            
            except Exception as e:
                if attempt < max_retries - 1:
                    can_retry = self._handle_api_error(e, f"getting comments (attempt {attempt + 1})")
                    if not can_retry:
                        break
                else:
                    self.logger.warning(f"Failed to get comments for post {submission.id} after {max_retries} attempts")
        
        return comments
    
    def search_subreddit(self, subreddit_name, keyword=None, limit=1000, method='search'):
        """
        Search subreddit with multiple collection methods
        
        Args:
            subreddit_name: Name of subreddit
            keyword: Search keyword (for search method)
            limit: Maximum posts to collect
            method: 'search', 'hot', 'top', 'new'
        
        Returns:
            list: List of submissions
        """
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                subreddit = self.reddit.subreddit(subreddit_name)
                data_config = self.config['data_collection']
                
                if method == 'search' and keyword:
                    submissions = subreddit.search(
                        keyword,
                        time_filter=data_config.get('time_filter', 'all'),
                        limit=limit
                    )
                elif method == 'hot':
                    submissions = subreddit.hot(limit=limit)
                elif method == 'top':
                    submissions = subreddit.top(
                        time_filter=data_config.get('time_filter', 'all'),
                        limit=limit
                    )
                elif method == 'new':
                    submissions = subreddit.new(limit=limit)
                else:
                    submissions = subreddit.hot(limit=limit)
                
                # Convert to list to catch errors early
                submission_list = list(submissions)
                self.consecutive_errors = 0  # Reset on success
                return submission_list
            
            except Exception as e:
                if attempt < max_retries - 1:
                    can_retry = self._handle_api_error(e, f"searching r/{subreddit_name} (attempt {attempt + 1})")
                    if not can_retry:
                        return []
                else:
                    self.logger.error(f"Failed to search r/{subreddit_name} after {max_retries} attempts")
                    return []
        
        return []
    
    def collect_data(self, target_posts=10000, max_runtime_hours=8):
        """
        Main collection function with multiple strategies
        
        Args:
            target_posts: Target number of posts to collect
            max_runtime_hours: Maximum hours to run
        """
        data_config = self.config['data_collection']
        subreddits = data_config['subreddits']
        keywords = data_config['keywords']
        
        self.logger.info("=" * 80)
        self.logger.info("REDDIT DATA COLLECTION")
        self.logger.info("=" * 80)
        self.logger.info(f"Target posts: {target_posts}")
        self.logger.info(f"Max runtime: {max_runtime_hours} hours")
        self.logger.info(f"Subreddits: {subreddits}")
        self.logger.info(f"Keywords: {keywords}")
        self.logger.info(f"Starting with {len(self.posts_collected)} existing posts")
        self.logger.info("=" * 80)
        
        max_runtime = timedelta(hours=max_runtime_hours)
        collection_methods = ['search', 'hot', 'top', 'new']
        
        # Main collection loop
        method_index = 0
        subreddit_index = 0
        
        while not self.should_stop:
            # Check stopping conditions
            if len(self.posts_collected) >= target_posts:
                self.logger.info(f"Target reached: {len(self.posts_collected)} posts collected")
                break
            
            if datetime.now() - self.start_time > max_runtime:
                self.logger.info(f"Max runtime reached: {(datetime.now() - self.start_time).total_seconds() / 3600:.1f} hours")
                break
            
            # Save checkpoint periodically
            if (datetime.now() - self.last_save_time).total_seconds() > self.save_interval_minutes * 60:
                self._save_checkpoint()
                self._print_progress(target_posts)
            
            # Get current collection parameters
            subreddit = subreddits[subreddit_index % len(subreddits)]
            method = collection_methods[method_index % len(collection_methods)]
            
            # Cycle through keywords for search method
            if method == 'search':
                keyword = keywords[(subreddit_index + method_index) % len(keywords)]
                self.logger.info(f"\nSearching r/{subreddit} for '{keyword}' using {method} method...")
            else:
                keyword = None
                self.logger.info(f"\nCollecting from r/{subreddit} using {method} method...")
            
            try:
                # Get submissions
                posts_per_request = min(100, (target_posts - len(self.posts_collected)) // 10)
                posts_per_request = max(50, posts_per_request)  # At least 50
                
                submissions = self.search_subreddit(
                    subreddit,
                    keyword=keyword,
                    limit=posts_per_request,
                    method=method
                )
                
                self.logger.info(f"Found {len(submissions)} submissions")
                
                new_posts_count = 0
                new_comments_count = 0
                
                # Process submissions
                for submission in tqdm(submissions, desc=f"r/{subreddit}", leave=False):
                    if self.should_stop:
                        break
                    
                    # Skip duplicates
                    if submission.id in self.collected_post_ids:
                        continue
                    
                    try:
                        # Get post data
                        post_data = self.get_post_data(submission)
                        if post_data:
                            self.posts_collected.append(post_data)
                            self.collected_post_ids.add(submission.id)
                            new_posts_count += 1
                            
                            # Get comments
                            comments = self.get_comments(submission, max_comments=100)
                            if comments:
                                self.comments_collected.extend(comments)
                                new_comments_count += len(comments)
                        
                        # Rate limiting
                        self._respect_rate_limit()
                    
                    except Exception as e:
                        self.logger.warning(f"Error processing submission {submission.id}: {e}")
                        continue
                
                self.logger.info(f"Collected {new_posts_count} new posts, {new_comments_count} new comments")
                
            except Exception as e:
                self.logger.error(f"Error in collection loop: {e}")
                self.logger.error(traceback.format_exc())
            
            # Move to next combination
            subreddit_index += 1
            if subreddit_index % len(subreddits) == 0:
                method_index += 1
            
            # Brief pause between batches
            if not self.should_stop:
                time.sleep(5)
        
        self.logger.info("=" * 80)
        self.logger.info("Collection loop ended")
        self.logger.info(f"Total posts collected: {len(self.posts_collected)}")
        self.logger.info(f"Total comments collected: {len(self.comments_collected)}")
        self.logger.info(f"Total runtime: {(datetime.now() - self.start_time).total_seconds() / 3600:.2f} hours")
        self.logger.info(f"Total errors: {self.total_errors}")
        self.logger.info("=" * 80)
    
    def _print_progress(self, target_posts):
        """Print collection progress"""
        runtime = datetime.now() - self.start_time
        posts_per_hour = len(self.posts_collected) / max(runtime.total_seconds() / 3600, 0.01)
        progress_pct = (len(self.posts_collected) / target_posts) * 100
        
        self.logger.info("\n" + "=" * 80)
        self.logger.info("PROGRESS UPDATE")
        self.logger.info("=" * 80)
        self.logger.info(f"Posts collected: {len(self.posts_collected):,} / {target_posts:,} ({progress_pct:.1f}%)")
        self.logger.info(f"Comments collected: {len(self.comments_collected):,}")
        self.logger.info(f"Runtime: {runtime.total_seconds() / 3600:.2f} hours")
        self.logger.info(f"Collection rate: {posts_per_hour:.1f} posts/hour")
        self.logger.info(f"Total errors: {self.total_errors}")
        self.logger.info(f"Current delay: {self.request_delay:.2f}s")
        self.logger.info("=" * 80 + "\n")
    
    def save_final_data(self):
        """Save final collected data"""
        self.logger.info("Saving final data...")
        
        # Convert to DataFrames
        df_posts = pd.DataFrame(self.posts_collected)
        df_comments = pd.DataFrame(self.comments_collected)
        
        # Remove duplicates (just in case)
        if len(df_posts) > 0:
            df_posts = df_posts.drop_duplicates(subset=['post_id'], keep='first')
        if len(df_comments) > 0:
            df_comments = df_comments.drop_duplicates(subset=['comment_id'], keep='first')
        
        # Save posts
        posts_path = 'data/raw/posts.csv'
        save_dataframe(df_posts, posts_path, format='csv')
        self.logger.info(f"Saved {len(df_posts)} posts to {posts_path}")
        
        # Save comments
        comments_path = 'data/raw/comments.csv'
        save_dataframe(df_comments, comments_path, format='csv')
        self.logger.info(f"Saved {len(df_comments)} comments to {comments_path}")
        
        # Generate collection report
        self._generate_report(df_posts, df_comments)
        
        # Clean up checkpoint files
        self.logger.info("Cleaning up checkpoint files...")
        try:
            Path('data/raw/posts_checkpoint.csv').unlink(missing_ok=True)
            Path('data/raw/comments_checkpoint.csv').unlink(missing_ok=True)
            Path(self.checkpoint_file).unlink(missing_ok=True)
            self.logger.info("Checkpoint files removed")
        except Exception as e:
            self.logger.warning(f"Failed to remove checkpoint files: {e}")
    
    def _generate_report(self, df_posts, df_comments):
        """Generate comprehensive collection report"""
        runtime = datetime.now() - self.start_time
        
        report = {
            'collection_timestamp': datetime.now().isoformat(),
            'start_time': self.start_time.isoformat(),
            'runtime_hours': runtime.total_seconds() / 3600,
            'total_posts': len(df_posts),
            'total_comments': len(df_comments),
            'total_errors': self.total_errors,
            'subreddits': self.config['data_collection']['subreddits'],
            'keywords': self.config['data_collection']['keywords'],
            'collection_rate': {
                'posts_per_hour': len(df_posts) / max(runtime.total_seconds() / 3600, 0.01),
                'comments_per_hour': len(df_comments) / max(runtime.total_seconds() / 3600, 0.01)
            }
        }
        
        if len(df_posts) > 0:
            report.update({
                'date_range': {
                    'earliest_post': df_posts['created_utc'].min(),
                    'latest_post': df_posts['created_utc'].max()
                },
                'posts_by_subreddit': df_posts['subreddit'].value_counts().to_dict(),
                'statistics': {
                    'avg_score': float(df_posts['score'].mean()),
                    'avg_comments_per_post': float(df_posts['num_comments'].mean()),
                    'unique_authors': df_posts['author'].nunique(),
                    'self_posts': int(df_posts['is_self'].sum()),
                    'total_upvotes': int(df_posts['score'].sum())
                }
            })
        
        report_path = 'data/metadata/collection_report.json'
        save_json(report, report_path)
        self.logger.info(f"Saved collection report to {report_path}")
        
        # Log detailed summary
        self.logger.info("\n" + "=" * 80)
        self.logger.info("FINAL COLLECTION SUMMARY")
        self.logger.info("=" * 80)
        self.logger.info(f"Total Posts: {report['total_posts']:,}")
        self.logger.info(f"Total Comments: {report['total_comments']:,}")
        self.logger.info(f"Runtime: {report['runtime_hours']:.2f} hours")
        self.logger.info(f"Collection Rate: {report['collection_rate']['posts_per_hour']:.1f} posts/hour")
        self.logger.info(f"Total Errors: {report['total_errors']}")
        if 'posts_by_subreddit' in report:
            self.logger.info("\nPosts by Subreddit:")
            for sub, count in report['posts_by_subreddit'].items():
                self.logger.info(f"  r/{sub}: {count:,}")
        self.logger.info("=" * 80)


def main():
    """Main execution function"""
    try:
        print("\n" + "=" * 80)
        print("REDDIT DATA COLLECTION")
        print("=" * 80)
        
        # Load configuration
        loader = ConfigLoader()
        config = loader.load()
        
        # Validate credentials
        if not loader.validate_reddit_credentials():
            print("ERROR: Reddit API credentials not configured!")
            print("Please set up your .env file with valid credentials.")
            return
        
        # Get collection parameters
        target_posts = int(input("Enter target number of posts (default 10000): ") or "10000")
        max_hours = float(input("Enter maximum runtime in hours (default 8): ") or "8")
        
        print(f"\nConfiguration:")
        print(f"  Target posts: {target_posts:,}")
        print(f"  Max runtime: {max_hours} hours")
        print(f"  Checkpoint saves: every 5 minutes")
        print(f"  Can resume if interrupted")
        print("\nPress Ctrl+C at any time to stop gracefully and save progress.")
        print("=" * 80 + "\n")
        
        input("Press Enter to start collection...")
        
        # Initialize scraper
        scraper = RedditScraper(config)
        
        # Collect data
        scraper.collect_data(target_posts=target_posts, max_runtime_hours=max_hours)
        
        # Save final data
        scraper.save_final_data()
        
        print("\n" + "=" * 80)
        print("✓ Collection Complete!")
        print(f"✓ Collected {len(scraper.posts_collected):,} posts")
        print(f"✓ Collected {len(scraper.comments_collected):,} comments")
        print("=" * 80)
    
    except KeyboardInterrupt:
        print("\n\nCollection interrupted by user")
        if 'scraper' in locals():
            print("Saving progress...")
            scraper._save_checkpoint()
            scraper.save_final_data()
            print("Progress saved. You can resume by running this script again.")
    
    except Exception as e:
        print(f"\nERROR: {e}")
        print(traceback.format_exc())
        if 'scraper' in locals():
            print("Attempting to save collected data...")
            try:
                scraper.save_final_data()
            except:
                pass


if __name__ == '__main__':
    main()
