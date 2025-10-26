"""
Reddit Data Collection Script
Collects posts and comments from specified subreddits using PRAW
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import praw
import pandas as pd
from datetime import datetime
import time
from tqdm import tqdm
import logging
import traceback
from utils import setup_logger, save_dataframe, save_json
from config.config_loader import ConfigLoader


class RedditScraper:
    """Reddit data scraper using PRAW"""
    
    def __init__(self, config):
        """
        Initialize Reddit API connection
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.logger = setup_logger(
            'data_collection',
            f'logs/data_collection_{datetime.now():%Y%m%d_%H%M%S}.log'
        )
        
        self.reddit = None
        self.posts_collected = []
        self.comments_collected = []
        
        self._initialize_reddit()
    
    def _initialize_reddit(self):
        """Initialize Reddit API connection"""
        try:
            reddit_config = self.config['reddit']
            
            self.reddit = praw.Reddit(
                client_id=reddit_config['client_id'],
                client_secret=reddit_config['client_secret'],
                user_agent=reddit_config['user_agent']
            )
            
            # Test connection
            self.logger.info(f"Connected to Reddit as: {self.reddit.read_only}")
            self.logger.info("Reddit API connection successful")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Reddit API: {e}")
            raise
    
    def get_post_data(self, submission):
        """
        Extract data from Reddit submission
        
        Args:
            submission: PRAW submission object
        
        Returns:
            dict: Post data
        """
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
                'permalink': submission.permalink
            }
        except Exception as e:
            self.logger.warning(f"Error extracting post data: {e}")
            return None
    
    def get_comments(self, submission, max_comments=50):
        """
        Extract comments from post
        
        Args:
            submission: PRAW submission object
            max_comments: Maximum comments to collect per post
        
        Returns:
            list: List of comment dictionaries
        """
        comments = []
        
        try:
            submission.comments.replace_more(limit=0)
            
            for i, comment in enumerate(submission.comments.list()[:max_comments]):
                try:
                    if isinstance(comment, praw.models.Comment):
                        comment_data = {
                            'comment_id': comment.id,
                            'post_id': submission.id,
                            'author': str(comment.author) if comment.author else '[deleted]',
                            'body': comment.body,
                            'score': comment.score,
                            'created_utc': datetime.fromtimestamp(comment.created_utc).isoformat(),
                            'parent_id': comment.parent_id
                        }
                        comments.append(comment_data)
                except Exception as e:
                    self.logger.warning(f"Error extracting comment: {e}")
                    continue
        
        except Exception as e:
            self.logger.warning(f"Error getting comments for post {submission.id}: {e}")
        
        return comments
    
    def search_subreddit(self, subreddit_name, keyword, limit=1000):
        """
        Search subreddit for keyword
        
        Args:
            subreddit_name: Name of subreddit
            keyword: Search keyword
            limit: Maximum posts to collect
        
        Returns:
            list: List of submissions
        """
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            
            data_config = self.config['data_collection']
            time_filter = data_config.get('time_filter', 'all')
            sort_by = data_config.get('sort_by', 'relevance')
            
            if sort_by == 'relevance':
                submissions = subreddit.search(
                    keyword,
                    time_filter=time_filter,
                    limit=limit
                )
            else:
                submissions = subreddit.top(time_filter=time_filter, limit=limit)
            
            return list(submissions)
        
        except Exception as e:
            self.logger.error(f"Error searching r/{subreddit_name} for '{keyword}': {e}")
            return []
    
    def collect_data(self):
        """
        Main collection function
        Collects posts and comments from configured subreddits
        """
        data_config = self.config['data_collection']
        subreddits = data_config['subreddits']
        keywords = data_config['keywords']
        target_posts = data_config.get('target_posts', 5000)
        
        self.logger.info("=" * 60)
        self.logger.info("Starting Reddit Data Collection")
        self.logger.info("=" * 60)
        self.logger.info(f"Target subreddits: {subreddits}")
        self.logger.info(f"Keywords: {keywords}")
        self.logger.info(f"Target posts: {target_posts}")
        
        total_posts_needed = target_posts
        posts_per_search = max(100, total_posts_needed // (len(subreddits) * len(keywords)))
        
        collected_post_ids = set()
        
        # Collect posts
        for subreddit in subreddits:
            for keyword in keywords:
                if len(self.posts_collected) >= total_posts_needed:
                    break
                
                self.logger.info(f"\nSearching r/{subreddit} for '{keyword}'...")
                
                try:
                    submissions = self.search_subreddit(
                        subreddit,
                        keyword,
                        limit=posts_per_search
                    )
                    
                    self.logger.info(f"Found {len(submissions)} submissions")
                    
                    for submission in tqdm(submissions, desc=f"r/{subreddit} - {keyword}"):
                        # Skip duplicates
                        if submission.id in collected_post_ids:
                            continue
                        
                        # Get post data
                        post_data = self.get_post_data(submission)
                        if post_data:
                            self.posts_collected.append(post_data)
                            collected_post_ids.add(submission.id)
                            
                            # Get comments
                            comments = self.get_comments(submission, max_comments=50)
                            self.comments_collected.extend(comments)
                        
                        # Rate limiting
                        time.sleep(0.5)
                        
                        # Save incrementally every 100 posts
                        if len(self.posts_collected) % 100 == 0:
                            self._save_incremental()
                    
                except Exception as e:
                    self.logger.error(f"Error collecting from r/{subreddit}: {e}")
                    self.logger.error(traceback.format_exc())
                    continue
                
                # Respect rate limits
                time.sleep(2)
        
        self.logger.info("=" * 60)
        self.logger.info("Data Collection Complete")
        self.logger.info(f"Total posts collected: {len(self.posts_collected)}")
        self.logger.info(f"Total comments collected: {len(self.comments_collected)}")
        self.logger.info("=" * 60)
    
    def _save_incremental(self):
        """Save data incrementally during collection"""
        try:
            if self.posts_collected:
                df_posts = pd.DataFrame(self.posts_collected)
                save_dataframe(df_posts, 'data/raw/posts_temp.csv', format='csv')
            
            if self.comments_collected:
                df_comments = pd.DataFrame(self.comments_collected)
                save_dataframe(df_comments, 'data/raw/comments_temp.csv', format='csv')
            
            self.logger.info(f"Incremental save: {len(self.posts_collected)} posts, {len(self.comments_collected)} comments")
        
        except Exception as e:
            self.logger.warning(f"Error during incremental save: {e}")
    
    def save_data(self):
        """Save collected data to files"""
        self.logger.info("Saving collected data...")
        
        # Convert to DataFrames
        df_posts = pd.DataFrame(self.posts_collected)
        df_comments = pd.DataFrame(self.comments_collected)
        
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
        
        # Clean up temp files
        try:
            Path('data/raw/posts_temp.csv').unlink(missing_ok=True)
            Path('data/raw/comments_temp.csv').unlink(missing_ok=True)
        except:
            pass
    
    def _generate_report(self, df_posts, df_comments):
        """
        Generate collection report
        
        Args:
            df_posts: Posts DataFrame
            df_comments: Comments DataFrame
        """
        report = {
            'collection_timestamp': datetime.now().isoformat(),
            'total_posts': len(df_posts),
            'total_comments': len(df_comments),
            'subreddits': self.config['data_collection']['subreddits'],
            'keywords': self.config['data_collection']['keywords'],
            'date_range': {
                'earliest_post': df_posts['created_utc'].min() if len(df_posts) > 0 else None,
                'latest_post': df_posts['created_utc'].max() if len(df_posts) > 0 else None
            },
            'posts_by_subreddit': df_posts['subreddit'].value_counts().to_dict() if len(df_posts) > 0 else {},
            'statistics': {
                'avg_score': float(df_posts['score'].mean()) if len(df_posts) > 0 else 0,
                'avg_comments_per_post': float(df_posts['num_comments'].mean()) if len(df_posts) > 0 else 0,
                'unique_authors': df_posts['author'].nunique() if len(df_posts) > 0 else 0
            }
        }
        
        report_path = 'data/metadata/collection_report.json'
        save_json(report, report_path)
        self.logger.info(f"Saved collection report to {report_path}")
        
        # Log summary
        self.logger.info("\n" + "=" * 60)
        self.logger.info("Collection Summary")
        self.logger.info("=" * 60)
        for key, value in report.items():
            if key not in ['subreddits', 'keywords', 'posts_by_subreddit']:
                self.logger.info(f"{key}: {value}")


def validate_collection():
    """Validate collected data meets requirements"""
    try:
        posts = pd.read_csv('data/raw/posts.csv')
        comments = pd.read_csv('data/raw/comments.csv')
        
        print("\n" + "=" * 60)
        print("Data Collection Validation")
        print("=" * 60)
        
        # Check minimum posts
        if len(posts) >= 1000:
            print(f"✓ Posts collected: {len(posts)} (minimum: 1000)")
        else:
            print(f"✗ Posts collected: {len(posts)} (minimum: 1000) - INSUFFICIENT")
        
        # Check comments
        if len(comments) >= 100:
            print(f"✓ Comments collected: {len(comments)}")
        else:
            print(f"⚠ Comments collected: {len(comments)} (low count)")
        
        # Check for duplicates
        duplicates = posts['post_id'].duplicated().sum()
        if duplicates == 0:
            print(f"✓ No duplicate posts")
        else:
            print(f"✗ Found {duplicates} duplicate posts")
        
        # Check for missing titles
        missing_titles = posts['title'].isna().sum()
        if missing_titles == 0:
            print(f"✓ All posts have titles")
        else:
            print(f"⚠ {missing_titles} posts missing titles")
        
        # Check subreddit coverage
        subreddits = posts['subreddit'].unique()
        print(f"✓ Subreddits covered: {len(subreddits)} ({', '.join(subreddits)})")
        
        # Check date range
        print(f"✓ Date range: {posts['created_utc'].min()} to {posts['created_utc'].max()}")
        
        print("=" * 60)
        
        return len(posts) >= 1000
    
    except FileNotFoundError:
        print("✗ Data files not found. Run collection first.")
        return False
    except Exception as e:
        print(f"✗ Validation error: {e}")
        return False


def main():
    """Main execution function"""
    try:
        # Load configuration
        loader = ConfigLoader()
        config = loader.load()
        
        # Validate credentials
        if not loader.validate_reddit_credentials():
            print("ERROR: Reddit API credentials not configured!")
            print("Please set up your .env file with valid credentials.")
            return
        
        # Initialize scraper
        scraper = RedditScraper(config)
        
        # Collect data
        scraper.collect_data()
        
        # Save data
        scraper.save_data()
        
        # Validate collection
        success = validate_collection()
        
        if success:
            print("\n✓ Module 1 Complete: Data collection successful!")
        else:
            print("\n⚠ Data collection complete but may need more data")
    
    except KeyboardInterrupt:
        print("\n\nCollection interrupted by user")
        print("Saving collected data...")
        if 'scraper' in locals():
            scraper.save_data()
    
    except Exception as e:
        print(f"\nERROR: {e}")
        print(traceback.format_exc())


if __name__ == '__main__':
    main()
