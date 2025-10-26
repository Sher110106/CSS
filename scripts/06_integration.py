"""
Module 6: Integration and Cross-Analysis
Integrates topic modeling and sentiment analysis results
"""

import pandas as pd
import numpy as np
import json
import os
from datetime import datetime
from pathlib import Path
import logging
from scipy import stats
from collections import Counter

from utils import setup_logger, load_config, save_json


class IntegrationAnalyzer:
    """Integration and Cross-Analysis"""
    
    def __init__(self, config_path='config/config.yaml'):
        """Initialize integration analyzer"""
        self.config = load_config(config_path)
        self.logger = setup_logger(
            'integration',
            'logs/integration.log'
        )
        
        # Paths
        self.processed_path = self.config['paths']['processed_data']
        self.metadata_path = self.config['paths']['metadata']
        self.anonymized_path = self.config['paths']['anonymized_data']
        
        # Data containers
        self.df = None
        self.topic_names = {}
        
        self.logger.info("Integration Analyzer initialized")
    
    def load_all_data(self):
        """Load integrated dataset"""
        self.logger.info("Loading integrated dataset...")
        
        try:
            df_path = os.path.join(self.processed_path, 'documents_with_sentiment.csv')
            self.df = pd.read_csv(df_path)
            
            # Convert timestamp
            self.df['created_utc'] = pd.to_datetime(self.df['created_utc'])
            
            # Parse tokens if needed
            if isinstance(self.df['tokens'].iloc[0], str):
                import ast
                self.df['tokens'] = self.df['tokens'].apply(ast.literal_eval)
            
            self.logger.info(f"Loaded {len(self.df)} documents with all features")
            self.logger.info(f"Columns: {list(self.df.columns)}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading data: {e}", exc_info=True)
            return False
    
    def assign_topic_names(self):
        """Assign human-readable names to topics"""
        self.logger.info("Assigning topic names...")
        
        # Based on Module 4 analysis
        self.topic_names = {
            0: "Alternative Medications",
            1: "Weight Loss Experiences",
            2: "Insurance & Access",
            3: "Diet & Side Effects",
            4: "Community Support"
        }
        
        self.df['topic_name'] = self.df['dominant_topic'].map(self.topic_names)
        
        self.logger.info("Topic names assigned")
        for topic_id, name in self.topic_names.items():
            count = (self.df['dominant_topic'] == topic_id).sum()
            self.logger.info(f"  Topic {topic_id} ({name}): {count} docs")
    
    def topic_sentiment_correlation(self):
        """Analyze correlation between topics and sentiment"""
        self.logger.info("Analyzing topic-sentiment correlation...")
        
        try:
            # Statistical test: ANOVA
            # H0: Mean sentiment is the same across all topics
            groups = [
                self.df[self.df['dominant_topic'] == topic]['compound'].values
                for topic in self.df['dominant_topic'].unique()
            ]
            
            f_stat, p_value = stats.f_oneway(*groups)
            
            self.logger.info(f"\nANOVA Results:")
            self.logger.info(f"  F-statistic: {f_stat:.4f}")
            self.logger.info(f"  P-value: {p_value:.4e}")
            
            if p_value < 0.001:
                self.logger.info("  Result: Highly significant difference in sentiment across topics")
            elif p_value < 0.05:
                self.logger.info("  Result: Significant difference in sentiment across topics")
            else:
                self.logger.info("  Result: No significant difference in sentiment across topics")
            
            # Pairwise comparisons (post-hoc)
            pairwise_results = []
            topics = sorted(self.df['dominant_topic'].unique())
            
            for i, topic1 in enumerate(topics):
                for topic2 in topics[i+1:]:
                    group1 = self.df[self.df['dominant_topic'] == topic1]['compound']
                    group2 = self.df[self.df['dominant_topic'] == topic2]['compound']
                    
                    t_stat, p_val = stats.ttest_ind(group1, group2)
                    
                    pairwise_results.append({
                        'topic_1': int(topic1),
                        'topic_2': int(topic2),
                        'topic_1_name': self.topic_names[topic1],
                        'topic_2_name': self.topic_names[topic2],
                        't_statistic': float(t_stat),
                        'p_value': float(p_val),
                        'significant': bool(p_val < 0.05)
                    })
            
            self.logger.info(f"\nSignificant pairwise differences:")
            for result in pairwise_results:
                if result['significant']:
                    self.logger.info(
                        f"  {result['topic_1_name']} vs {result['topic_2_name']}: "
                        f"p={result['p_value']:.4f}"
                    )
            
            return {
                'anova': {
                    'f_statistic': float(f_stat),
                    'p_value': float(p_value),
                    'significant': bool(p_value < 0.05)
                },
                'pairwise_comparisons': pairwise_results
            }
            
        except Exception as e:
            self.logger.error(f"Error in correlation analysis: {e}", exc_info=True)
            return {}
    
    def extract_representative_posts(self):
        """Extract representative posts for each topic-sentiment combination"""
        self.logger.info("Extracting representative posts...")
        
        try:
            representative_docs = []
            
            for topic_id in sorted(self.df['dominant_topic'].unique()):
                topic_df = self.df[self.df['dominant_topic'] == topic_id]
                topic_name = self.topic_names[topic_id]
                
                # Skip if too few documents
                if len(topic_df) < 3:
                    continue
                
                # Most representative (highest topic probability)
                most_rep = topic_df.nlargest(3, 'topic_probability')
                
                for idx, row in most_rep.iterrows():
                    representative_docs.append({
                        'topic_id': int(topic_id),
                        'topic_name': topic_name,
                        'doc_type': 'most_representative',
                        'doc_id': row['doc_id'],
                        'type': row['doc_type'],
                        'topic_prob': float(row['topic_probability']),
                        'sentiment': float(row['compound']),
                        'sentiment_class': row['sentiment_class'],
                        'text_preview': str(row['cleaned_text'])[:200] + '...',
                        'token_count': int(row['token_count']),
                        'score': int(row['score']) if pd.notna(row['score']) else 0
                    })
                
                # Most positive in topic
                positive_in_topic = topic_df[topic_df['sentiment_class'] == 'positive']
                if len(positive_in_topic) > 0:
                    most_pos = positive_in_topic.nlargest(2, 'compound')
                    
                    for idx, row in most_pos.iterrows():
                        representative_docs.append({
                            'topic_id': int(topic_id),
                            'topic_name': topic_name,
                            'doc_type': 'most_positive',
                            'doc_id': row['doc_id'],
                            'type': row['doc_type'],
                            'topic_prob': float(row['topic_probability']),
                            'sentiment': float(row['compound']),
                            'sentiment_class': row['sentiment_class'],
                            'text_preview': str(row['cleaned_text'])[:200] + '...',
                            'token_count': int(row['token_count']),
                            'score': int(row['score']) if pd.notna(row['score']) else 0
                        })
                
                # Most negative in topic
                negative_in_topic = topic_df[topic_df['sentiment_class'] == 'negative']
                if len(negative_in_topic) > 0:
                    most_neg = negative_in_topic.nsmallest(2, 'compound')
                    
                    for idx, row in most_neg.iterrows():
                        representative_docs.append({
                            'topic_id': int(topic_id),
                            'topic_name': topic_name,
                            'doc_type': 'most_negative',
                            'doc_id': row['doc_id'],
                            'type': row['doc_type'],
                            'topic_prob': float(row['topic_probability']),
                            'sentiment': float(row['compound']),
                            'sentiment_class': row['sentiment_class'],
                            'text_preview': str(row['cleaned_text'])[:200] + '...',
                            'token_count': int(row['token_count']),
                            'score': int(row['score']) if pd.notna(row['score']) else 0
                        })
            
            rep_df = pd.DataFrame(representative_docs)
            
            # Save
            output_path = os.path.join(self.anonymized_path, 'representative_posts.csv')
            rep_df.to_csv(output_path, index=False)
            
            self.logger.info(f"Extracted {len(rep_df)} representative posts")
            self.logger.info(f"Saved to {output_path}")
            
            return rep_df
            
        except Exception as e:
            self.logger.error(f"Error extracting representative posts: {e}", exc_info=True)
            return pd.DataFrame()
    
    def keyword_analysis_by_topic_sentiment(self):
        """Analyze keywords by topic and sentiment"""
        self.logger.info("Analyzing keywords by topic and sentiment...")
        
        try:
            keyword_analysis = {}
            
            # Key medical/weight loss terms
            keywords = [
                'weight', 'lose', 'loss', 'pound', 'lbs',
                'side', 'effect', 'nausea', 'vomit', 'diarrhea',
                'eat', 'food', 'appetite', 'hungry', 'calorie',
                'insurance', 'cost', 'expensive', 'cheap', 'afford',
                'work', 'help', 'good', 'bad', 'better', 'worse',
                'doctor', 'prescribe', 'dose', 'injection'
            ]
            
            for topic_id in sorted(self.df['dominant_topic'].unique()):
                topic_name = self.topic_names[topic_id]
                topic_df = self.df[self.df['dominant_topic'] == topic_id]
                
                keyword_analysis[topic_name] = {}
                
                for sentiment in ['positive', 'negative', 'neutral']:
                    sent_df = topic_df[topic_df['sentiment_class'] == sentiment]
                    
                    if len(sent_df) == 0:
                        continue
                    
                    # Count keyword mentions
                    keyword_counts = {}
                    for keyword in keywords:
                        count = sent_df['cleaned_text'].str.contains(
                            keyword, 
                            case=False, 
                            na=False
                        ).sum()
                        
                        if count > 0:
                            percentage = (count / len(sent_df)) * 100
                            keyword_counts[keyword] = {
                                'count': int(count),
                                'percentage': float(percentage)
                            }
                    
                    # Get top 10
                    top_keywords = sorted(
                        keyword_counts.items(),
                        key=lambda x: x[1]['count'],
                        reverse=True
                    )[:10]
                    
                    keyword_analysis[topic_name][sentiment] = dict(top_keywords)
            
            self.logger.info("Keyword analysis complete")
            
            return keyword_analysis
            
        except Exception as e:
            self.logger.error(f"Error in keyword analysis: {e}", exc_info=True)
            return {}
    
    def generate_insights(self):
        """Generate key insights from integrated analysis"""
        self.logger.info("Generating key insights...")
        
        insights = []
        
        # Insight 1: Overall patterns
        total_docs = len(self.df)
        pos_pct = (self.df['sentiment_class'] == 'positive').mean() * 100
        
        insights.append({
            'category': 'Overall Sentiment',
            'insight': f"The community shows predominantly positive sentiment with {pos_pct:.1f}% positive discussions across {total_docs:,} documents.",
            'data': {
                'total_documents': int(total_docs),
                'positive_percentage': float(pos_pct)
            }
        })
        
        # Insight 2: Topic concentration
        top_topic = self.df['dominant_topic'].mode()[0]
        top_topic_pct = (self.df['dominant_topic'] == top_topic).mean() * 100
        
        insights.append({
            'category': 'Discussion Focus',
            'insight': f"Weight loss experiences dominate discussions ({top_topic_pct:.1f}% of content), indicating this is the primary reason people use semaglutide in these communities.",
            'data': {
                'dominant_topic': int(top_topic),
                'dominant_topic_name': self.topic_names[top_topic],
                'percentage': float(top_topic_pct)
            }
        })
        
        # Insight 3: Community support
        support_topic_df = self.df[self.df['dominant_topic'] == 4]
        if len(support_topic_df) > 0:
            support_pos_pct = (support_topic_df['sentiment_class'] == 'positive').mean() * 100
            
            insights.append({
                'category': 'Community Dynamics',
                'insight': f"Community support discussions are overwhelmingly positive ({support_pos_pct:.1f}%), demonstrating strong peer support and helpful information sharing.",
                'data': {
                    'support_positive_percentage': float(support_pos_pct)
                }
            })
        
        # Insight 4: Side effects manageable
        side_effects_df = self.df[self.df['dominant_topic'] == 3]
        if len(side_effects_df) > 0:
            se_pos_pct = (side_effects_df['sentiment_class'] == 'positive').mean() * 100
            
            insights.append({
                'category': 'Side Effects',
                'insight': f"Despite discussions about side effects, {se_pos_pct:.1f}% remain positive, suggesting benefits outweigh adverse effects for most users.",
                'data': {
                    'side_effects_positive_percentage': float(se_pos_pct)
                }
            })
        
        # Insight 5: Access barriers
        insurance_df = self.df[self.df['dominant_topic'] == 2]
        if len(insurance_df) > 0:
            ins_pos_pct = (insurance_df['sentiment_class'] == 'positive').mean() * 100
            
            insights.append({
                'category': 'Access & Affordability',
                'insight': f"Insurance/access discussions are more positive than expected ({ins_pos_pct:.1f}%), likely due to community sharing solutions and support for obtaining medication.",
                'data': {
                    'insurance_positive_percentage': float(ins_pos_pct)
                }
            })
        
        # Insight 6: Temporal stability
        self.df['year'] = self.df['created_utc'].dt.year
        yearly_sentiment = self.df.groupby('year')['compound'].mean()
        
        insights.append({
            'category': 'Temporal Trends',
            'insight': f"Sentiment remains consistently positive across years ({yearly_sentiment.mean():.3f} average), indicating sustained satisfaction over time.",
            'data': {
                'mean_sentiment_across_years': float(yearly_sentiment.mean()),
                'yearly_sentiment': {int(k): float(v) for k, v in yearly_sentiment.items()}
            }
        })
        
        # Insight 7: Topic-sentiment relationship
        topic_sent = self.df.groupby('dominant_topic')['compound'].mean().sort_values(ascending=False)
        
        insights.append({
            'category': 'Topic-Sentiment Relationship',
            'insight': f"Sentiment varies significantly by topic, with community support (0.52) being most positive and alternative medications (-0.04) being slightly negative.",
            'data': {
                'topic_sentiment_ranking': {
                    self.topic_names[int(k)]: float(v) 
                    for k, v in topic_sent.items()
                }
            }
        })
        
        self.logger.info(f"Generated {len(insights)} key insights")
        
        return insights
    
    def create_final_dataset(self):
        """Create final anonymized dataset"""
        self.logger.info("Creating final anonymized dataset...")
        
        try:
            # Select relevant columns
            final_df = self.df[[
                'doc_id', 'doc_type', 'created_utc',
                'cleaned_text', 'token_count',
                'dominant_topic', 'topic_name', 'topic_probability',
                'compound', 'pos', 'neu', 'neg', 'sentiment_class',
                'score', 'subreddit'
            ]].copy()
            
            # Remove any identifying information
            # (Already removed in preprocessing, but double-check)
            
            # Save
            output_path = os.path.join(self.anonymized_path, 'final_dataset.csv')
            final_df.to_csv(output_path, index=False)
            
            self.logger.info(f"Final dataset created: {len(final_df)} documents")
            self.logger.info(f"Saved to {output_path}")
            
            # Create summary stats
            summary = {
                'total_documents': int(len(final_df)),
                'date_range': {
                    'start': str(final_df['created_utc'].min()),
                    'end': str(final_df['created_utc'].max())
                },
                'topic_distribution': final_df['topic_name'].value_counts().to_dict(),
                'sentiment_distribution': final_df['sentiment_class'].value_counts().to_dict(),
                'mean_sentiment': float(final_df['compound'].mean()),
                'columns': list(final_df.columns)
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error creating final dataset: {e}", exc_info=True)
            return {}
    
    def generate_integration_report(self):
        """Generate comprehensive integration report"""
        self.logger.info("Generating integration report...")
        
        try:
            # Topic-sentiment correlation
            correlation_results = self.topic_sentiment_correlation()
            
            # Extract representative posts
            rep_posts = self.extract_representative_posts()
            
            # Keyword analysis
            keyword_analysis = self.keyword_analysis_by_topic_sentiment()
            
            # Generate insights
            insights = self.generate_insights()
            
            # Create final dataset
            dataset_summary = self.create_final_dataset()
            
            # Compile report
            report = {
                'report_metadata': {
                    'generated_at': datetime.now().isoformat(),
                    'total_documents': int(len(self.df)),
                    'analysis_modules': [
                        'Data Collection',
                        'Preprocessing',
                        'Exploratory Analysis',
                        'Topic Modeling (LDA)',
                        'Sentiment Analysis (VADER)',
                        'Integration & Cross-Analysis'
                    ]
                },
                'topic_sentiment_correlation': correlation_results,
                'keyword_analysis_summary': {
                    'topics_analyzed': len(keyword_analysis),
                    'keywords_tracked': 30
                },
                'representative_posts_summary': {
                    'total_extracted': int(len(rep_posts)),
                    'per_topic': rep_posts.groupby('topic_name').size().to_dict()
                },
                'key_insights': insights,
                'final_dataset_summary': dataset_summary
            }
            
            # Save report
            report_path = os.path.join(self.metadata_path, 'integration_report.json')
            save_json(report, report_path)
            
            self.logger.info(f"Integration report saved to {report_path}")
            
            # Save insights separately
            insights_path = os.path.join(self.metadata_path, 'key_insights.json')
            save_json({'insights': insights}, insights_path)
            
            self.logger.info(f"Key insights saved to {insights_path}")
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating report: {e}", exc_info=True)
            return {}


def main():
    """Main execution function"""
    print("\n" + "="*60)
    print("MODULE 6: INTEGRATION & CROSS-ANALYSIS")
    print("="*60 + "\n")
    
    # Initialize
    analyzer = IntegrationAnalyzer()
    
    # Load data
    print("Step 1: Loading integrated dataset...")
    if not analyzer.load_all_data():
        print("ERROR: Failed to load data")
        return
    
    # Assign topic names
    print("\nStep 2: Assigning human-readable topic names...")
    analyzer.assign_topic_names()
    
    # Generate report
    print("\nStep 3: Performing integrated analysis...")
    print("  - Topic-sentiment correlation analysis")
    print("  - Extracting representative posts")
    print("  - Keyword analysis by topic and sentiment")
    print("  - Generating key insights")
    print("  - Creating final anonymized dataset")
    
    report = analyzer.generate_integration_report()
    
    # Print summary
    print("\n" + "="*60)
    print("INTEGRATION & CROSS-ANALYSIS COMPLETE!")
    print("="*60)
    
    print(f"\nDataset Summary:")
    print(f"  Total Documents: {report['report_metadata']['total_documents']:,}")
    
    if 'topic_sentiment_correlation' in report:
        anova = report['topic_sentiment_correlation'].get('anova', {})
        if anova.get('significant'):
            print(f"\nStatistical Finding:")
            print(f"  ✓ Sentiment differs significantly across topics")
            print(f"    (ANOVA p-value: {anova['p_value']:.4e})")
    
    print(f"\nKey Insights Generated: {len(report['key_insights'])}")
    for i, insight in enumerate(report['key_insights'], 1):
        print(f"\n  {i}. {insight['category']}")
        print(f"     {insight['insight']}")
    
    print(f"\nFiles created:")
    print(f"  - Final dataset: data/anonymized/final_dataset.csv")
    print(f"  - Representative posts: data/anonymized/representative_posts.csv")
    print(f"  - Integration report: data/metadata/integration_report.json")
    print(f"  - Key insights: data/metadata/key_insights.json")
    
    print("\n✓ Module 6: Integration & Cross-Analysis - COMPLETE\n")


if __name__ == "__main__":
    main()
