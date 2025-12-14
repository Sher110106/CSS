#!/usr/bin/env python3
"""
Module 1: Data Collection with BAScraper (ArcticShift)
Collects Reddit data evenly distributed across 2019-2025 for semaglutide research.
Uses ArcticShiftAsync for comprehensive historical coverage.
"""

import os
import sys
import json
import logging
import pandas as pd
import asyncio
from datetime import datetime, timedelta
from BAScraper.BAScraper_async import ArcticShiftAsync
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f"bascraper_collection_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
SUBREDDITS = ['Ozempic', 'Semaglutide', 'WeightLossAdvice', 'diabetes_t2', 'diabetes', 'loseit']
KEYWORDS = ['semaglutide', 'ozempic', 'wegovy', 'rybelsus']

# Time periods for even distribution (2019-2025)
YEAR_PERIODS = [
    ('2019-01-01', '2019-12-31'),
    ('2020-01-01', '2020-12-31'),
    ('2021-01-01', '2021-12-31'),
    ('2022-01-01', '2022-12-31'),
    ('2023-01-01', '2023-12-31'),
    ('2024-01-01', '2024-12-31'),
    ('2025-01-01', '2025-12-01'),
]

# Targets
POSTS_PER_YEAR_TARGET = 300
COMMENTS_SAMPLE_SIZE = 500


class BAScraperCollector:
    """Reddit data collector using BAScraper with ArcticShift"""
    
    def __init__(self):
        """Initialize BAScraper"""
        logger.info("Initializing BAScraper (ArcticShift) Data Collector")
        
        # Initialize ArcticShiftAsync
        self.scraper = ArcticShiftAsync(
            save_dir=os.getcwd(),
            task_num=3,
            log_level='INFO',
            log_stream_level='INFO'
        )
        
        self.all_posts = []
        self.all_comments = []
        
    async def collect_submissions_for_period(self, subreddit, after, before, query_term):
        """Collect submissions for a specific period and query"""
        try:
            logger.info(f"  Searching r/{subreddit} for '{query_term}' ({after} to {before})")
            
            result = await self.scraper.fetch(
                mode='submissions_search',
                subreddit=subreddit,
                query=query_term,
                after=after,
                before=before,
                limit=100,  # 100 per request
                sort='asc',
                fields=['id', 'title', 'selftext', 'author', 'created_utc', 'subreddit',
                       'score', 'num_comments', 'url', 'link_flair_text']
            )
            
            if result:
                posts_list = list(result.values())
                logger.info(f"    Found {len(posts_list)} posts")
                return posts_list
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error collecting from r/{subreddit}: {e}")
            return []
    
    async def collect_all_submissions(self):
        """Collect submissions across all years and subreddits"""
        logger.info("="*80)
        logger.info("COLLECTING SUBMISSIONS")
        logger.info("="*80)
        
        posts_by_year = {year.split('-')[0]: [] for year, _ in YEAR_PERIODS}
        
        for after, before in YEAR_PERIODS:
            year = after[:4]
            logger.info(f"\n{'='*60}")
            logger.info(f"YEAR: {year}")
            logger.info(f"{'='*60}")
            
            year_posts = []
            
            for subreddit in SUBREDDITS:
                for keyword in KEYWORDS:
                    posts = await self.collect_submissions_for_period(
                        subreddit, after, before, keyword
                    )
                    year_posts.extend(posts)
                    await asyncio.sleep(1)  # Rate limiting
            
            # Remove duplicates within year
            unique_posts = {p['id']: p for p in year_posts}
            posts_by_year[year] = list(unique_posts.values())
            
            logger.info(f"Year {year} total: {len(posts_by_year[year])} unique posts")
        
        # Flatten all posts
        for year_posts in posts_by_year.values():
            self.all_posts.extend(year_posts)
        
        logger.info(f"\n{'='*80}")
        logger.info(f"TOTAL SUBMISSIONS COLLECTED: {len(self.all_posts)}")
        logger.info(f"{'='*80}")
        
        return self.all_posts
    
    async def collect_comments_for_submissions(self, submission_ids, limit=30):
        """Collect comments for sampled submissions"""
        logger.info(f"\nCollecting comments for {len(submission_ids)} submissions")
        
        all_comments = []
        
        for i, sub_id in enumerate(submission_ids):
            try:
                if (i + 1) % 50 == 0:
                    logger.info(f"  Progress: {i+1}/{len(submission_ids)}")
                
                result = await self.scraper.fetch(
                    mode='comments_search',
                    link_id=sub_id,
                    limit=limit,
                    fields=['id', 'body', 'author', 'created_utc', 'subreddit',
                           'score', 'link_id', 'parent_id']
                )
                
                if result:
                    comments_list = list(result.values())
                    all_comments.extend(comments_list)
                
                await asyncio.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                logger.debug(f"Error collecting comments for {sub_id}: {e}")
                continue
        
        logger.info(f"Collected {len(all_comments)} comments")
        return all_comments
    
    async def run_collection(self):
        """Main collection orchestration"""
        logger.info("Starting BAScraper collection pipeline")
        
        # Collect submissions
        await self.collect_all_submissions()
        
        # Sample submissions for comment collection (stratified by year)
        df = pd.DataFrame(self.all_posts)
        df['created_datetime'] = pd.to_datetime(df['created_utc'], unit='s')
        df['year'] = df['created_datetime'].dt.year
        
        # Sample posts for comments (proportional to year distribution, max 500 total)
        sample_ids = []
        for year in df['year'].unique():
            year_posts = df[df['year'] == year]
            n_sample = min(100, len(year_posts))  # Max 100 per year
            sampled = year_posts.sample(n=n_sample, random_state=42)
            sample_ids.extend(sampled['id'].tolist())
        
        # Limit to 500 total
        if len(sample_ids) > COMMENTS_SAMPLE_SIZE:
            sample_ids = sample_ids[:COMMENTS_SAMPLE_SIZE]
        
        logger.info(f"\nSampled {len(sample_ids)} posts for comment collection")
        
        # Collect comments
        self.all_comments = await self.collect_comments_for_submissions(sample_ids)
        
        return self.all_posts, self.all_comments
    
    def save_data(self):
        """Save collected data to CSV files"""
        os.makedirs('data/raw', exist_ok=True)
        
        # Process and save posts
        posts_df = pd.DataFrame(self.all_posts)
        
        # Add engagement metrics
        posts_df['engagement_score'] = posts_df['score'] + (posts_df['num_comments'] * 2)
        
        # Add temporal features
        posts_df['created_datetime'] = pd.to_datetime(posts_df['created_utc'], unit='s')
        posts_df['year'] = posts_df['created_datetime'].dt.year
        posts_df['month'] = posts_df['created_datetime'].dt.month
        posts_df['quarter'] = posts_df['created_datetime'].dt.quarter
        
        posts_file = 'data/raw/posts.csv'
        posts_df.to_csv(posts_file, index=False)
        logger.info(f"\n✓ Saved {len(posts_df)} posts to {posts_file}")
        
        # Process and save comments
        comments_df = pd.DataFrame(self.all_comments)
        if not comments_df.empty:
            comments_df['created_datetime'] = pd.to_datetime(comments_df['created_utc'], unit='s')
        
        comments_file = 'data/raw/comments.csv'
        comments_df.to_csv(comments_file, index=False)
        logger.info(f"✓ Saved {len(comments_df)} comments to {comments_file}")
        
        # Generate collection report
        report = {
            'collection_metadata': {
                'collection_date': datetime.now().isoformat(),
                'scraper': 'BAScraper (ArcticShift)',
                'version': '0.2.0',
            },
            'data_summary': {
                'total_posts': len(self.all_posts),
                'total_comments': len(self.all_comments),
                'unique_authors_posts': posts_df['author'].nunique(),
                'unique_subreddits': posts_df['subreddit'].nunique(),
            },
            'configuration': {
                'subreddits': SUBREDDITS,
                'keywords': KEYWORDS,
                'year_periods': YEAR_PERIODS,
            },
            'temporal_distribution': {
                'date_range': {
                    'start': posts_df['created_datetime'].min().isoformat(),
                    'end': posts_df['created_datetime'].max().isoformat(),
                },
                'posts_per_year': posts_df['year'].value_counts().sort_index().to_dict(),
                'posts_per_quarter': posts_df.groupby(['year', 'quarter']).size().to_dict(),
            },
            'subreddit_distribution': posts_df['subreddit'].value_counts().to_dict(),
            'engagement_statistics': {
                'mean_score': float(posts_df['score'].mean()),
                'median_score': float(posts_df['score'].median()),
                'mean_comments': float(posts_df['num_comments'].mean()),
                'mean_engagement': float(posts_df['engagement_score'].mean()),
            },
        }
        
        os.makedirs('data/metadata', exist_ok=True)
        report_file = 'data/metadata/collection_report.json'
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        logger.info(f"✓ Saved collection report to {report_file}")
        
        # Print summary
        logger.info(f"\n{'='*80}")
        logger.info("COLLECTION SUMMARY")
        logger.info(f"{'='*80}")
        logger.info(f"\nTemporal Distribution:")
        for year, count in sorted(posts_df['year'].value_counts().items()):
            pct = (count / len(posts_df)) * 100
            logger.info(f"  {year}: {count:4d} posts ({pct:5.1f}%)")
        
        logger.info(f"\nSubreddit Distribution:")
        for sub, count in posts_df['subreddit'].value_counts().head(10).items():
            logger.info(f"  r/{sub}: {count} posts")
        
        logger.info(f"\nEngagement Metrics:")
        logger.info(f"  Mean Score: {posts_df['score'].mean():.1f}")
        logger.info(f"  Mean Comments: {posts_df['num_comments'].mean():.1f}")
        logger.info(f"  Mean Engagement: {posts_df['engagement_score'].mean():.1f}")
        
        return posts_df, comments_df


async def main():
    """Main execution"""
    try:
        logger.info("="*80)
        logger.info("BASCRAPER DATA COLLECTION PIPELINE")
        logger.info("="*80)
        
        collector = BAScraperCollector()
        await collector.run_collection()
        posts_df, comments_df = collector.save_data()
        
        logger.info(f"\n{'='*80}")
        logger.info("✓ DATA COLLECTION COMPLETE!")
        logger.info(f"{'='*80}")
        logger.info(f"\nCollected:")
        logger.info(f"  - {len(posts_df)} posts")
        logger.info(f"  - {len(comments_df)} comments")
        logger.info(f"\nNext step: Run preprocessing")
        logger.info(f"  → python scripts/02_data_preprocessing.py")
        
        return 0
        
    except Exception as e:
        logger.error(f"Collection failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
