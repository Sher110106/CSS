"""
Module 3: Exploratory Data Analysis
Performs comprehensive EDA on preprocessed data
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
from wordcloud import WordCloud
import json
from datetime import datetime
import os
import ast
from pathlib import Path
import logging
from utils import setup_logger, load_config, save_json

# Setup
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("viridis")


class ExploratoryAnalysis:
    """Comprehensive Exploratory Data Analysis"""
    
    def __init__(self, config_path='config/config.yaml'):
        """Initialize EDA analyzer"""
        self.config = load_config(config_path)
        self.logger = setup_logger(
            'eda',
            'logs/exploratory_analysis.log'
        )
        
        # Paths
        self.processed_path = self.config['paths']['processed_data']
        self.viz_path = self.config['paths']['visualizations']
        self.metadata_path = self.config['paths']['metadata']
        
        # Create EDA visualization directory
        self.eda_viz_path = os.path.join(self.viz_path, 'eda')
        os.makedirs(self.eda_viz_path, exist_ok=True)
        
        # Data containers
        self.df = None
        self.posts_df = None
        self.comments_df = None
        self.stats = {}
        
        self.logger.info("EDA Analyzer initialized")
    
    def load_data(self):
        """Load all processed data"""
        self.logger.info("Loading processed data...")
        
        try:
            # Load combined dataset
            combined_path = os.path.join(self.processed_path, 'combined_processed.csv')
            self.df = pd.read_csv(combined_path)
            
            # Parse tokens column (stored as string representation of list)
            self.df['tokens'] = self.df['tokens'].apply(ast.literal_eval)
            
            # Convert timestamp to datetime
            self.df['created_utc'] = pd.to_datetime(self.df['created_utc'])
            
            # Load separate posts and comments for specific analyses
            posts_path = os.path.join(self.processed_path, 'posts_processed.csv')
            comments_path = os.path.join(self.processed_path, 'comments_processed.csv')
            
            self.posts_df = pd.read_csv(posts_path)
            self.posts_df['created_utc'] = pd.to_datetime(self.posts_df['created_utc'])
            
            self.comments_df = pd.read_csv(comments_path)
            self.comments_df['created_utc'] = pd.to_datetime(self.comments_df['created_utc'])
            
            self.logger.info(f"Loaded {len(self.df)} documents successfully")
            self.logger.info(f"  - Posts: {len(self.posts_df)}")
            self.logger.info(f"  - Comments: {len(self.comments_df)}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading data: {e}", exc_info=True)
            return False
    
    def basic_statistics(self):
        """Calculate comprehensive basic statistics"""
        self.logger.info("Calculating basic statistics...")
        
        stats = {
            'total_documents': int(len(self.df)),
            'total_posts': int(len(self.posts_df)),
            'total_comments': int(len(self.comments_df)),
            'date_range': {
                'earliest': str(self.df['created_utc'].min()),
                'latest': str(self.df['created_utc'].max()),
                'span_days': int((self.df['created_utc'].max() - self.df['created_utc'].min()).days)
            },
            'subreddit_distribution': self.df['subreddit'].value_counts().to_dict(),
            'document_type_distribution': self.df['doc_type'].value_counts().to_dict(),
            'token_statistics': {
                'total_tokens': int(self.df['token_count'].sum()),
                'mean_tokens': float(self.df['token_count'].mean()),
                'median_tokens': float(self.df['token_count'].median()),
                'min_tokens': int(self.df['token_count'].min()),
                'max_tokens': int(self.df['token_count'].max()),
                'std_tokens': float(self.df['token_count'].std())
            },
            'score_statistics': {
                'mean_score': float(self.df['score'].mean()),
                'median_score': float(self.df['score'].median()),
                'max_score': int(self.df['score'].max()),
                'posts_with_positive_score': int((self.df['score'] > 0).sum())
            }
        }
        
        # Document length categories
        self.df['length_category'] = pd.cut(
            self.df['token_count'],
            bins=[0, 25, 50, 100, float('inf')],
            labels=['Very Short (10-25)', 'Short (26-50)', 'Medium (51-100)', 'Long (100+)']
        )
        stats['length_distribution'] = self.df['length_category'].value_counts().to_dict()
        
        self.stats.update(stats)
        
        self.logger.info(f"Basic statistics calculated")
        self.logger.info(f"  - Date range: {stats['date_range']['span_days']} days")
        self.logger.info(f"  - Mean tokens: {stats['token_statistics']['mean_tokens']:.1f}")
        
        return stats
    
    def temporal_analysis(self):
        """Analyze posting patterns over time"""
        self.logger.info("Performing temporal analysis...")
        
        # Aggregate by month
        self.df['year_month'] = self.df['created_utc'].dt.to_period('M')
        temporal_dist = self.df.groupby('year_month').size()
        
        # Convert to dict with string keys for JSON serialization
        temporal_dict = {str(k): int(v) for k, v in temporal_dist.items()}
        
        self.stats['temporal_distribution'] = {
            'posts_by_month': temporal_dict,
            'most_active_month': str(temporal_dist.idxmax()),
            'max_posts_in_month': int(temporal_dist.max()),
            'least_active_month': str(temporal_dist.idxmin()),
            'min_posts_in_month': int(temporal_dist.min())
        }
        
        # Plot temporal distribution
        fig, axes = plt.subplots(2, 1, figsize=(14, 10))
        
        # Posts over time
        ax1 = axes[0]
        temporal_series = pd.Series(temporal_dist.values, index=temporal_dist.index.to_timestamp())
        temporal_series.plot(ax=ax1, linewidth=2, marker='o', markersize=4)
        ax1.set_title('Posting Activity Over Time', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Date', fontsize=12)
        ax1.set_ylabel('Number of Posts/Comments', fontsize=12)
        ax1.grid(True, alpha=0.3)
        
        # Posts by document type over time
        ax2 = axes[1]
        temporal_by_type = self.df.groupby(['year_month', 'doc_type']).size().unstack(fill_value=0)
        temporal_by_type.index = temporal_by_type.index.to_timestamp()
        temporal_by_type.plot(ax=ax2, linewidth=2, marker='o', markersize=3)
        ax2.set_title('Posts vs Comments Over Time', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Date', fontsize=12)
        ax2.set_ylabel('Count', fontsize=12)
        ax2.legend(title='Type')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(
            os.path.join(self.eda_viz_path, 'temporal_analysis.png'),
            dpi=300,
            bbox_inches='tight'
        )
        plt.close()
        
        self.logger.info("Temporal analysis complete")
        
        return self.stats['temporal_distribution']
    
    def vocabulary_analysis(self):
        """Comprehensive vocabulary analysis"""
        self.logger.info("Performing vocabulary analysis...")
        
        # Flatten all tokens
        all_tokens = [token for tokens in self.df['tokens'] for token in tokens]
        token_freq = Counter(all_tokens)
        
        # Get top N words
        top_50 = token_freq.most_common(50)
        top_100 = token_freq.most_common(100)
        
        # Vocabulary statistics
        vocab_stats = {
            'total_tokens': len(all_tokens),
            'unique_tokens': len(token_freq),
            'vocabulary_richness': len(token_freq) / len(all_tokens),  # Type-token ratio
            'top_50_words': [(word, int(count)) for word, count in top_50],
            'top_100_words': [(word, int(count)) for word, count in top_100],
            'singleton_words': sum(1 for count in token_freq.values() if count == 1),
            'words_appearing_more_than_10_times': sum(1 for count in token_freq.values() if count > 10),
            'words_appearing_more_than_100_times': sum(1 for count in token_freq.values() if count > 100)
        }
        
        self.stats['vocabulary'] = vocab_stats
        
        # Create word frequency visualization
        fig, axes = plt.subplots(2, 1, figsize=(14, 12))
        
        # Top 30 words bar chart
        ax1 = axes[0]
        top_30 = token_freq.most_common(30)
        words, counts = zip(*top_30)
        y_pos = np.arange(len(words))
        
        ax1.barh(y_pos, counts, color='steelblue', alpha=0.8)
        ax1.set_yticks(y_pos)
        ax1.set_yticklabels(words)
        ax1.invert_yaxis()
        ax1.set_xlabel('Frequency', fontsize=12)
        ax1.set_title('Top 30 Most Frequent Words', fontsize=14, fontweight='bold')
        ax1.grid(axis='x', alpha=0.3)
        
        # Word frequency distribution (log scale)
        ax2 = axes[1]
        frequencies = sorted(token_freq.values(), reverse=True)
        ax2.plot(range(1, len(frequencies) + 1), frequencies, linewidth=2)
        ax2.set_xscale('log')
        ax2.set_yscale('log')
        ax2.set_xlabel('Word Rank (log scale)', fontsize=12)
        ax2.set_ylabel('Frequency (log scale)', fontsize=12)
        ax2.set_title("Zipf's Law: Word Frequency Distribution", fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3, which='both')
        
        plt.tight_layout()
        plt.savefig(
            os.path.join(self.eda_viz_path, 'vocabulary_analysis.png'),
            dpi=300,
            bbox_inches='tight'
        )
        plt.close()
        
        self.logger.info(f"Vocabulary analysis complete")
        self.logger.info(f"  - Unique tokens: {vocab_stats['unique_tokens']:,}")
        self.logger.info(f"  - Top word: {top_50[0][0]} ({top_50[0][1]:,} occurrences)")
        
        return vocab_stats
    
    def ngram_analysis(self):
        """Analyze bigrams and trigrams"""
        self.logger.info("Performing n-gram analysis...")
        
        # Extract bigrams and trigrams
        bigrams = []
        trigrams = []
        
        for tokens in self.df['tokens']:
            if len(tokens) >= 2:
                bigrams.extend([' '.join(tokens[i:i+2]) for i in range(len(tokens)-1)])
            if len(tokens) >= 3:
                trigrams.extend([' '.join(tokens[i:i+3]) for i in range(len(tokens)-2)])
        
        bigram_freq = Counter(bigrams)
        trigram_freq = Counter(trigrams)
        
        top_bigrams = bigram_freq.most_common(30)
        top_trigrams = trigram_freq.most_common(20)
        
        self.stats['ngrams'] = {
            'top_bigrams': [(bg, int(count)) for bg, count in top_bigrams],
            'top_trigrams': [(tg, int(count)) for tg, count in top_trigrams],
            'total_bigrams': len(bigrams),
            'unique_bigrams': len(bigram_freq),
            'total_trigrams': len(trigrams),
            'unique_trigrams': len(trigram_freq)
        }
        
        # Visualize top bigrams and trigrams
        fig, axes = plt.subplots(1, 2, figsize=(16, 8))
        
        # Bigrams
        ax1 = axes[0]
        bg_words, bg_counts = zip(*top_bigrams[:20])
        y_pos = np.arange(len(bg_words))
        ax1.barh(y_pos, bg_counts, color='coral', alpha=0.8)
        ax1.set_yticks(y_pos)
        ax1.set_yticklabels(bg_words, fontsize=9)
        ax1.invert_yaxis()
        ax1.set_xlabel('Frequency', fontsize=12)
        ax1.set_title('Top 20 Bigrams', fontsize=14, fontweight='bold')
        ax1.grid(axis='x', alpha=0.3)
        
        # Trigrams
        ax2 = axes[1]
        tg_words, tg_counts = zip(*top_trigrams[:15])
        y_pos = np.arange(len(tg_words))
        ax2.barh(y_pos, tg_counts, color='mediumseagreen', alpha=0.8)
        ax2.set_yticks(y_pos)
        ax2.set_yticklabels(tg_words, fontsize=9)
        ax2.invert_yaxis()
        ax2.set_xlabel('Frequency', fontsize=12)
        ax2.set_title('Top 15 Trigrams', fontsize=14, fontweight='bold')
        ax2.grid(axis='x', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(
            os.path.join(self.eda_viz_path, 'ngram_analysis.png'),
            dpi=300,
            bbox_inches='tight'
        )
        plt.close()
        
        self.logger.info("N-gram analysis complete")
        
        return self.stats['ngrams']
    
    def generate_initial_wordcloud(self):
        """Create overall word cloud"""
        self.logger.info("Generating word cloud...")
        
        # Combine all tokens
        all_text = ' '.join([' '.join(tokens) for tokens in self.df['tokens']])
        
        # Generate word cloud
        wordcloud = WordCloud(
            width=1600,
            height=800,
            background_color='white',
            colormap='viridis',
            max_words=150,
            relative_scaling=0.5,
            min_font_size=10
        ).generate(all_text)
        
        # Plot
        fig, ax = plt.subplots(figsize=(16, 8))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        ax.set_title('Overall Word Cloud: Semaglutide Reddit Discussions',
                    fontsize=16, fontweight='bold', pad=20)
        
        plt.tight_layout()
        plt.savefig(
            os.path.join(self.eda_viz_path, 'overall_wordcloud.png'),
            dpi=300,
            bbox_inches='tight',
            facecolor='white'
        )
        plt.close()
        
        self.logger.info("Word cloud generated")
    
    def subreddit_analysis(self):
        """Analyze subreddit-specific patterns"""
        self.logger.info("Analyzing subreddit patterns...")
        
        subreddit_stats = {}
        
        for subreddit in self.df['subreddit'].unique():
            sub_df = self.df[self.df['subreddit'] == subreddit]
            
            subreddit_stats[subreddit] = {
                'document_count': int(len(sub_df)),
                'avg_tokens': float(sub_df['token_count'].mean()),
                'avg_score': float(sub_df['score'].mean()),
                'date_range': {
                    'earliest': str(sub_df['created_utc'].min()),
                    'latest': str(sub_df['created_utc'].max())
                }
            }
        
        self.stats['subreddit_analysis'] = subreddit_stats
        
        # Visualize subreddit distribution
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))
        
        # Document count by subreddit
        ax1 = axes[0]
        subreddit_counts = self.df['subreddit'].value_counts()
        subreddit_counts.plot(kind='bar', ax=ax1, color='skyblue', alpha=0.8)
        ax1.set_title('Documents by Subreddit', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Subreddit', fontsize=12)
        ax1.set_ylabel('Document Count', fontsize=12)
        ax1.tick_params(axis='x', rotation=45)
        ax1.grid(axis='y', alpha=0.3)
        
        # Average token count by subreddit
        ax2 = axes[1]
        avg_tokens = self.df.groupby('subreddit')['token_count'].mean().sort_values(ascending=False)
        avg_tokens.plot(kind='bar', ax=ax2, color='lightcoral', alpha=0.8)
        ax2.set_title('Average Token Count by Subreddit', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Subreddit', fontsize=12)
        ax2.set_ylabel('Average Tokens', fontsize=12)
        ax2.tick_params(axis='x', rotation=45)
        ax2.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(
            os.path.join(self.eda_viz_path, 'subreddit_analysis.png'),
            dpi=300,
            bbox_inches='tight'
        )
        plt.close()
        
        self.logger.info("Subreddit analysis complete")
        
        return subreddit_stats
    
    def document_length_analysis(self):
        """Analyze document length distributions"""
        self.logger.info("Analyzing document lengths...")
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # Overall distribution
        ax1 = axes[0, 0]
        self.df['token_count'].hist(bins=50, ax=ax1, color='steelblue', alpha=0.7, edgecolor='black')
        ax1.set_title('Token Count Distribution', fontsize=12, fontweight='bold')
        ax1.set_xlabel('Token Count', fontsize=10)
        ax1.set_ylabel('Frequency', fontsize=10)
        ax1.axvline(self.df['token_count'].mean(), color='red', linestyle='--', 
                   linewidth=2, label=f'Mean: {self.df["token_count"].mean():.1f}')
        ax1.legend()
        ax1.grid(alpha=0.3)
        
        # Box plot by document type
        ax2 = axes[0, 1]
        self.df.boxplot(column='token_count', by='doc_type', ax=ax2)
        ax2.set_title('Token Count by Document Type', fontsize=12, fontweight='bold')
        ax2.set_xlabel('Document Type', fontsize=10)
        ax2.set_ylabel('Token Count', fontsize=10)
        plt.sca(ax2)
        plt.xticks(rotation=0)
        
        # Length category distribution
        ax3 = axes[1, 0]
        length_dist = self.df['length_category'].value_counts()
        length_dist.plot(kind='bar', ax=ax3, color='lightgreen', alpha=0.8, edgecolor='black')
        ax3.set_title('Document Length Categories', fontsize=12, fontweight='bold')
        ax3.set_xlabel('Length Category', fontsize=10)
        ax3.set_ylabel('Count', fontsize=10)
        ax3.tick_params(axis='x', rotation=45)
        ax3.grid(axis='y', alpha=0.3)
        
        # Cumulative distribution
        ax4 = axes[1, 1]
        sorted_tokens = np.sort(self.df['token_count'])
        cumulative = np.arange(1, len(sorted_tokens) + 1) / len(sorted_tokens) * 100
        ax4.plot(sorted_tokens, cumulative, linewidth=2, color='purple')
        ax4.set_title('Cumulative Distribution of Token Counts', fontsize=12, fontweight='bold')
        ax4.set_xlabel('Token Count', fontsize=10)
        ax4.set_ylabel('Cumulative Percentage', fontsize=10)
        ax4.grid(alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(
            os.path.join(self.eda_viz_path, 'document_length_analysis.png'),
            dpi=300,
            bbox_inches='tight'
        )
        plt.close()
        
        self.logger.info("Document length analysis complete")
    
    def create_eda_report(self):
        """Generate comprehensive EDA report"""
        self.logger.info("Generating comprehensive EDA report...")
        
        report = {
            'report_metadata': {
                'generated_at': datetime.now().isoformat(),
                'data_source': 'combined_processed.csv',
                'total_documents_analyzed': int(len(self.df))
            },
            'basic_statistics': self.stats.get('basic_statistics', {}),
            'temporal_analysis': self.stats.get('temporal_distribution', {}),
            'vocabulary': self.stats.get('vocabulary', {}),
            'ngrams': self.stats.get('ngrams', {}),
            'subreddit_analysis': self.stats.get('subreddit_analysis', {}),
            'key_findings': self._generate_key_findings()
        }
        
        # Update stats with all info
        self.stats.update(report)
        
        # Save report
        report_path = os.path.join(self.metadata_path, 'eda_report.json')
        save_json(report, report_path)
        
        self.logger.info(f"EDA report saved to {report_path}")
        
        return report
    
    def _generate_key_findings(self):
        """Generate key findings from EDA"""
        findings = []
        
        # Data coverage
        findings.append(f"Dataset contains {len(self.df):,} documents spanning "
                       f"{self.stats.get('date_range', {}).get('span_days', 0)} days")
        
        # Top topics from vocabulary
        if 'vocabulary' in self.stats:
            top_words = self.stats['vocabulary']['top_50_words'][:5]
            top_word_str = ', '.join([f"'{w}'" for w, _ in top_words])
            findings.append(f"Most frequent terms: {top_word_str}")
        
        # Document characteristics
        if 'token_statistics' in self.stats:
            avg_tokens = self.stats['token_statistics']['mean_tokens']
            findings.append(f"Average document length: {avg_tokens:.1f} tokens")
        
        # Subreddit distribution
        if 'subreddit_distribution' in self.stats:
            top_sub = max(self.stats['subreddit_distribution'].items(), key=lambda x: x[1])
            findings.append(f"Most active subreddit: r/{top_sub[0]} ({top_sub[1]:,} documents)")
        
        # Temporal patterns
        if 'temporal_distribution' in self.stats:
            most_active = self.stats['temporal_distribution'].get('most_active_month', 'N/A')
            findings.append(f"Most active period: {most_active}")
        
        return findings
    
    def run_full_analysis(self):
        """Run complete EDA pipeline"""
        self.logger.info("="*60)
        self.logger.info("Starting Exploratory Data Analysis")
        self.logger.info("="*60)
        
        # Load data
        if not self.load_data():
            self.logger.error("Failed to load data. Exiting.")
            return False
        
        # Run all analyses
        try:
            self.basic_statistics()
            self.temporal_analysis()
            self.vocabulary_analysis()
            self.ngram_analysis()
            self.generate_initial_wordcloud()
            self.subreddit_analysis()
            self.document_length_analysis()
            
            # Generate final report
            report = self.create_eda_report()
            
            self.logger.info("="*60)
            self.logger.info("EDA Complete!")
            self.logger.info("="*60)
            self.logger.info("\nKey Findings:")
            for finding in report['key_findings']:
                self.logger.info(f"  • {finding}")
            
            self.logger.info(f"\nVisualizations saved to: {self.eda_viz_path}")
            self.logger.info(f"Report saved to: {os.path.join(self.metadata_path, 'eda_report.json')}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error during EDA: {e}", exc_info=True)
            return False


def main():
    """Main execution function"""
    import sys
    
    # Initialize analyzer
    analyzer = ExploratoryAnalysis()
    
    # Run analysis
    success = analyzer.run_full_analysis()
    
    if success:
        print("\n✓ Module 3: Exploratory Data Analysis - COMPLETE")
        sys.exit(0)
    else:
        print("\n✗ Module 3: Exploratory Data Analysis - FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()
