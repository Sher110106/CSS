"""
Module 5: Sentiment Analysis using VADER
Analyzes sentiment across all documents and by topic
"""

import pandas as pd
import numpy as np
import json
import os
from datetime import datetime
from pathlib import Path
import logging
from tqdm import tqdm

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from utils import setup_logger, load_config, save_json


class SentimentAnalyzer:
    """VADER Sentiment Analysis"""
    
    def __init__(self, config_path='config/config.yaml'):
        """Initialize sentiment analyzer"""
        self.config = load_config(config_path)
        self.logger = setup_logger(
            'sentiment_analysis',
            'logs/sentiment_analysis.log'
        )
        
        # Initialize VADER
        self.analyzer = SentimentIntensityAnalyzer()
        
        # Paths
        self.processed_path = self.config['paths']['processed_data']
        self.metadata_path = self.config['paths']['metadata']
        
        # Sentiment thresholds from config
        self.pos_threshold = self.config['sentiment']['compound_threshold_positive']
        self.neg_threshold = self.config['sentiment']['compound_threshold_negative']
        
        # Data container
        self.df = None
        
        self.logger.info("Sentiment Analyzer initialized")
        self.logger.info(f"Positive threshold: {self.pos_threshold}")
        self.logger.info(f"Negative threshold: {self.neg_threshold}")
    
    def load_data(self):
        """Load documents with topics"""
        self.logger.info("Loading documents with topics...")
        
        try:
            df_path = os.path.join(self.processed_path, 'documents_with_topics.csv')
            self.df = pd.read_csv(df_path)
            
            # Convert timestamp to datetime
            self.df['created_utc'] = pd.to_datetime(self.df['created_utc'])
            
            self.logger.info(f"Loaded {len(self.df)} documents")
            self.logger.info(f"Columns: {list(self.df.columns)}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading data: {e}", exc_info=True)
            return False
    
    def analyze_sentiment(self, text):
        """Analyze sentiment of single text using VADER"""
        try:
            scores = self.analyzer.polarity_scores(str(text))
            return scores
        except Exception as e:
            self.logger.error(f"Error analyzing text: {e}")
            return {
                'compound': 0.0,
                'pos': 0.0,
                'neu': 1.0,
                'neg': 0.0
            }
    
    def classify_sentiment(self, compound_score):
        """Classify sentiment based on compound score"""
        if compound_score >= self.pos_threshold:
            return 'positive'
        elif compound_score <= self.neg_threshold:
            return 'negative'
        else:
            return 'neutral'
    
    def analyze_all_documents(self):
        """Analyze sentiment for all documents"""
        self.logger.info("Analyzing sentiment for all documents...")
        
        try:
            # Analyze each document
            sentiments = []
            
            for text in tqdm(self.df['cleaned_text'], desc="Analyzing sentiment"):
                sentiment = self.analyze_sentiment(text)
                sentiments.append(sentiment)
            
            # Add sentiment columns
            self.df['compound'] = [s['compound'] for s in sentiments]
            self.df['pos'] = [s['pos'] for s in sentiments]
            self.df['neu'] = [s['neu'] for s in sentiments]
            self.df['neg'] = [s['neg'] for s in sentiments]
            
            # Classify sentiment
            self.df['sentiment_class'] = self.df['compound'].apply(self.classify_sentiment)
            
            # Log statistics
            self.logger.info("\nSentiment Statistics:")
            self.logger.info(f"  Mean compound: {self.df['compound'].mean():.4f}")
            self.logger.info(f"  Std compound: {self.df['compound'].std():.4f}")
            self.logger.info(f"  Min compound: {self.df['compound'].min():.4f}")
            self.logger.info(f"  Max compound: {self.df['compound'].max():.4f}")
            
            # Distribution
            sentiment_dist = self.df['sentiment_class'].value_counts()
            self.logger.info("\nSentiment Distribution:")
            for sentiment, count in sentiment_dist.items():
                pct = (count / len(self.df)) * 100
                self.logger.info(f"  {sentiment}: {count} ({pct:.1f}%)")
            
            # Save documents with sentiment
            output_path = os.path.join(self.processed_path, 'documents_with_sentiment.csv')
            self.df.to_csv(output_path, index=False)
            
            self.logger.info(f"Documents with sentiment saved to {output_path}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error analyzing documents: {e}", exc_info=True)
            return False
    
    def sentiment_by_topic(self):
        """Analyze sentiment by topic"""
        self.logger.info("Analyzing sentiment by topic...")
        
        try:
            # Group by topic
            topic_sentiment = self.df.groupby('dominant_topic').agg({
                'compound': ['mean', 'std', 'min', 'max'],
                'pos': 'mean',
                'neu': 'mean',
                'neg': 'mean',
                'doc_id': 'count'
            }).round(4)
            
            # Flatten column names
            topic_sentiment.columns = ['_'.join(col).strip() for col in topic_sentiment.columns.values]
            topic_sentiment.rename(columns={'doc_id_count': 'document_count'}, inplace=True)
            
            # Add sentiment class distribution per topic
            sentiment_by_topic_class = pd.crosstab(
                self.df['dominant_topic'],
                self.df['sentiment_class'],
                normalize='index'
            ).round(4)
            
            # Merge
            topic_sentiment = topic_sentiment.join(sentiment_by_topic_class)
            
            self.logger.info("\nSentiment by Topic:")
            for topic_id in topic_sentiment.index:
                mean_compound = topic_sentiment.loc[topic_id, 'compound_mean']
                doc_count = int(topic_sentiment.loc[topic_id, 'document_count'])
                self.logger.info(f"  Topic {topic_id}: {mean_compound:.4f} ({doc_count} docs)")
            
            # Save
            output_path = os.path.join(self.processed_path, 'sentiment_by_topic.csv')
            topic_sentiment.to_csv(output_path)
            
            self.logger.info(f"Sentiment by topic saved to {output_path}")
            
            return topic_sentiment
            
        except Exception as e:
            self.logger.error(f"Error analyzing sentiment by topic: {e}", exc_info=True)
            return None
    
    def temporal_sentiment_analysis(self):
        """Analyze sentiment over time"""
        self.logger.info("Analyzing sentiment over time...")
        
        try:
            # Add year-month column
            self.df['year_month'] = self.df['created_utc'].dt.to_period('M')
            
            # Group by month
            temporal_sentiment = self.df.groupby('year_month').agg({
                'compound': ['mean', 'std'],
                'pos': 'mean',
                'neg': 'mean',
                'neu': 'mean',
                'doc_id': 'count'
            }).round(4)
            
            # Flatten column names
            temporal_sentiment.columns = ['_'.join(col).strip() for col in temporal_sentiment.columns.values]
            temporal_sentiment.rename(columns={'doc_id_count': 'document_count'}, inplace=True)
            
            # Reset index to make year_month a column
            temporal_sentiment = temporal_sentiment.reset_index()
            temporal_sentiment['year_month'] = temporal_sentiment['year_month'].astype(str)
            
            self.logger.info(f"Temporal analysis complete: {len(temporal_sentiment)} periods")
            
            # Save
            output_path = os.path.join(self.processed_path, 'sentiment_temporal.csv')
            temporal_sentiment.to_csv(output_path, index=False)
            
            self.logger.info(f"Temporal sentiment saved to {output_path}")
            
            return temporal_sentiment
            
        except Exception as e:
            self.logger.error(f"Error in temporal analysis: {e}", exc_info=True)
            return None
    
    def topic_sentiment_temporal(self):
        """Analyze sentiment by topic over time"""
        self.logger.info("Analyzing sentiment by topic over time...")
        
        try:
            # Group by topic and month
            topic_temporal = self.df.groupby(['dominant_topic', 'year_month']).agg({
                'compound': 'mean',
                'doc_id': 'count'
            }).round(4)
            
            topic_temporal.rename(columns={'doc_id': 'document_count'}, inplace=True)
            
            # Reset index
            topic_temporal = topic_temporal.reset_index()
            topic_temporal['year_month'] = topic_temporal['year_month'].astype(str)
            
            self.logger.info(f"Topic-temporal analysis complete")
            
            # Save
            output_path = os.path.join(self.processed_path, 'sentiment_topic_temporal.csv')
            topic_temporal.to_csv(output_path, index=False)
            
            self.logger.info(f"Topic-temporal sentiment saved to {output_path}")
            
            return topic_temporal
            
        except Exception as e:
            self.logger.error(f"Error in topic-temporal analysis: {e}", exc_info=True)
            return None
    
    def find_extreme_sentiments(self):
        """Find most positive and negative documents per topic"""
        self.logger.info("Finding extreme sentiment documents...")
        
        try:
            extreme_docs = []
            
            for topic_id in self.df['dominant_topic'].unique():
                topic_df = self.df[self.df['dominant_topic'] == topic_id]
                
                if len(topic_df) == 0:
                    continue
                
                # Most positive
                most_pos = topic_df.nlargest(3, 'compound')[
                    ['doc_id', 'doc_type', 'compound', 'cleaned_text']
                ]
                most_pos['extreme_type'] = 'most_positive'
                most_pos['topic'] = topic_id
                
                # Most negative
                most_neg = topic_df.nsmallest(3, 'compound')[
                    ['doc_id', 'doc_type', 'compound', 'cleaned_text']
                ]
                most_neg['extreme_type'] = 'most_negative'
                most_neg['topic'] = topic_id
                
                extreme_docs.append(most_pos)
                extreme_docs.append(most_neg)
            
            extreme_df = pd.concat(extreme_docs, ignore_index=True)
            
            # Save
            output_path = os.path.join(self.processed_path, 'extreme_sentiments.csv')
            extreme_df.to_csv(output_path, index=False)
            
            self.logger.info(f"Extreme sentiments saved to {output_path}")
            
            return extreme_df
            
        except Exception as e:
            self.logger.error(f"Error finding extreme sentiments: {e}", exc_info=True)
            return None
    
    def generate_sentiment_report(self):
        """Generate comprehensive sentiment report"""
        self.logger.info("Generating sentiment report...")
        
        try:
            # Overall statistics
            overall_stats = {
                'total_documents': int(len(self.df)),
                'compound': {
                    'mean': float(self.df['compound'].mean()),
                    'std': float(self.df['compound'].std()),
                    'min': float(self.df['compound'].min()),
                    'max': float(self.df['compound'].max()),
                    'median': float(self.df['compound'].median())
                },
                'sentiment_distribution': {
                    'positive': int((self.df['sentiment_class'] == 'positive').sum()),
                    'neutral': int((self.df['sentiment_class'] == 'neutral').sum()),
                    'negative': int((self.df['sentiment_class'] == 'negative').sum())
                },
                'sentiment_percentages': {
                    'positive': float((self.df['sentiment_class'] == 'positive').mean() * 100),
                    'neutral': float((self.df['sentiment_class'] == 'neutral').mean() * 100),
                    'negative': float((self.df['sentiment_class'] == 'negative').mean() * 100)
                }
            }
            
            # Sentiment by topic
            sentiment_by_topic_df = pd.read_csv(
                os.path.join(self.processed_path, 'sentiment_by_topic.csv')
            )
            sentiment_by_topic = sentiment_by_topic_df.to_dict('index')
            
            # Temporal trends
            temporal_df = pd.read_csv(
                os.path.join(self.processed_path, 'sentiment_temporal.csv')
            )
            
            # Key findings
            most_positive_topic = sentiment_by_topic_df['compound_mean'].idxmax()
            most_negative_topic = sentiment_by_topic_df['compound_mean'].idxmin()
            
            # Create report
            report = {
                'report_metadata': {
                    'generated_at': datetime.now().isoformat(),
                    'analyzer': 'VADER',
                    'total_documents': int(len(self.df)),
                    'positive_threshold': self.pos_threshold,
                    'negative_threshold': self.neg_threshold
                },
                'overall_sentiment': overall_stats,
                'sentiment_by_topic': {
                    str(k): v for k, v in sentiment_by_topic.items()
                },
                'temporal_summary': {
                    'periods_analyzed': int(len(temporal_df)),
                    'earliest_period': str(temporal_df['year_month'].iloc[0]),
                    'latest_period': str(temporal_df['year_month'].iloc[-1]),
                    'mean_sentiment_over_time': float(temporal_df['compound_mean'].mean())
                },
                'key_findings': [
                    f"Overall sentiment is {overall_stats['compound']['mean']:.4f} (slightly positive)" if overall_stats['compound']['mean'] > 0 else f"Overall sentiment is {overall_stats['compound']['mean']:.4f} (slightly negative)",
                    f"Most positive topic: Topic {most_positive_topic}",
                    f"Most negative topic: Topic {most_negative_topic}",
                    f"Sentiment distribution: {overall_stats['sentiment_percentages']['positive']:.1f}% positive, {overall_stats['sentiment_percentages']['neutral']:.1f}% neutral, {overall_stats['sentiment_percentages']['negative']:.1f}% negative"
                ]
            }
            
            # Save report
            report_path = os.path.join(self.metadata_path, 'sentiment_report.json')
            save_json(report, report_path)
            
            self.logger.info(f"Sentiment report saved to {report_path}")
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating report: {e}", exc_info=True)
            return {}


def main():
    """Main execution function"""
    print("\n" + "="*60)
    print("MODULE 5: SENTIMENT ANALYSIS WITH VADER")
    print("="*60 + "\n")
    
    # Initialize
    analyzer = SentimentAnalyzer()
    
    # Load data
    print("Step 1: Loading documents with topics...")
    if not analyzer.load_data():
        print("ERROR: Failed to load data")
        return
    
    # Analyze sentiment
    print("\nStep 2: Analyzing sentiment for all documents...")
    print("This may take a minute...\n")
    if not analyzer.analyze_all_documents():
        print("ERROR: Failed to analyze sentiment")
        return
    
    # Sentiment by topic
    print("\nStep 3: Analyzing sentiment by topic...")
    topic_sentiment = analyzer.sentiment_by_topic()
    
    # Temporal analysis
    print("\nStep 4: Analyzing sentiment over time...")
    temporal_sentiment = analyzer.temporal_sentiment_analysis()
    
    # Topic-temporal analysis
    print("\nStep 5: Analyzing sentiment by topic over time...")
    topic_temporal = analyzer.topic_sentiment_temporal()
    
    # Find extremes
    print("\nStep 6: Finding extreme sentiment documents...")
    extremes = analyzer.find_extreme_sentiments()
    
    # Generate report
    print("\nStep 7: Generating comprehensive report...")
    report = analyzer.generate_sentiment_report()
    
    # Print summary
    print("\n" + "="*60)
    print("SENTIMENT ANALYSIS COMPLETE!")
    print("="*60)
    
    overall = report['overall_sentiment']
    print(f"\nOverall Sentiment: {overall['compound']['mean']:.4f}")
    print(f"  Range: [{overall['compound']['min']:.4f}, {overall['compound']['max']:.4f}]")
    
    print(f"\nSentiment Distribution:")
    for sentiment, pct in report['overall_sentiment']['sentiment_percentages'].items():
        print(f"  {sentiment.capitalize()}: {pct:.1f}%")
    
    print(f"\nSentiment by Topic (Mean Compound):")
    for topic_id, stats in report['sentiment_by_topic'].items():
        if isinstance(stats, dict):
            mean = stats.get('compound_mean', 0)
            print(f"  Topic {topic_id}: {mean:.4f}")
    
    print(f"\nFiles saved:")
    print(f"  - Documents with sentiment: data/processed/documents_with_sentiment.csv")
    print(f"  - Sentiment by topic: data/processed/sentiment_by_topic.csv")
    print(f"  - Temporal sentiment: data/processed/sentiment_temporal.csv")
    print(f"  - Topic-temporal sentiment: data/processed/sentiment_topic_temporal.csv")
    print(f"  - Extreme sentiments: data/processed/extreme_sentiments.csv")
    print(f"  - Report: data/metadata/sentiment_report.json")
    
    print("\n✓ Module 5: Sentiment Analysis - COMPLETE\n")


if __name__ == "__main__":
    main()
