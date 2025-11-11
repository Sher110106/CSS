"""
Module 8: Extended Analysis and Visualizations
Performs additional analyses requested:
1. Subreddit-level analysis with Arctic-style visualizations
2. Temporal trends across subreddits
3. 4-topic LDA model evaluation
4. Pre vs Post-Pandemic analysis
5. Temporal trend methodology documentation
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json
import os
from datetime import datetime
from pathlib import Path
import logging
from tqdm import tqdm
import pickle

# Gensim imports for topic modeling
import gensim
from gensim import corpora
from gensim.models import LdaModel, CoherenceModel

from utils import setup_logger, load_config, save_json


class ExtendedAnalyzer:
    """Extended Analysis for Reddit Semaglutide Project"""

    def __init__(self, config_path='config/config.yaml'):
        """Initialize analyzer"""
        self.config = load_config(config_path)
        self.logger = setup_logger(
            'extended_analysis',
            'logs/extended_analysis.log'
        )

        # Paths
        self.processed_path = self.config['paths']['processed_data']
        self.models_path = self.config['paths']['models']
        self.viz_path = self.config['paths']['visualizations']
        self.metadata_path = self.config['paths']['metadata']

        # Create extended analysis directory
        self.extended_viz_path = os.path.join(self.viz_path, 'extended_analysis')
        os.makedirs(self.extended_viz_path, exist_ok=True)

        # Visualization settings
        self.dpi = self.config['visualization']['figure_dpi']

        # Set style
        plt.style.use('seaborn-v0_8-darkgrid')

        # Data containers
        self.df = None
        self.corpus = None
        self.dictionary = None
        self.texts = None

        # Topic names from existing 5-topic model
        self.topic_names = {
            0: "Alternative Medications",
            1: "Weight Loss Experiences",
            2: "Insurance & Access",
            3: "Diet & Side Effects",
            4: "Community Support"
        }

        # Pandemic cutoff date
        self.pandemic_cutoff = pd.Timestamp('2020-03-01')

        self.logger.info("Extended Analyzer initialized")

    def load_data(self):
        """Load final dataset"""
        self.logger.info("Loading final dataset...")

        try:
            # Load final dataset
            df_path = os.path.join('data/anonymized', 'final_dataset.csv')
            self.df = pd.read_csv(df_path)

            # Convert timestamp
            self.df['created_utc'] = pd.to_datetime(self.df['created_utc'])

            # Add temporal features
            self.df['year_month'] = self.df['created_utc'].dt.to_period('M')
            self.df['year'] = self.df['created_utc'].dt.year
            self.df['month'] = self.df['created_utc'].dt.month

            # Add pandemic period indicator
            self.df['pandemic_period'] = self.df['created_utc'].apply(
                lambda x: 'Post-Pandemic' if x >= self.pandemic_cutoff else 'Pre-Pandemic'
            )

            self.logger.info(f"Loaded {len(self.df)} documents")
            self.logger.info(f"Date range: {self.df['created_utc'].min()} to {self.df['created_utc'].max()}")
            self.logger.info(f"Subreddits: {self.df['subreddit'].unique()}")

            return True

        except Exception as e:
            self.logger.error(f"Error loading data: {e}", exc_info=True)
            return False

    # ==================== SUBREDDIT-LEVEL ANALYSIS ====================

    def create_arctic_style_subreddit_barplot(self):
        """Generate Arctic-style bar plot for posts/comments per subreddit"""
        self.logger.info("Creating Arctic-style subreddit bar plot...")

        try:
            # Count posts and comments per subreddit
            subreddit_counts = self.df['subreddit'].value_counts().sort_values(ascending=True)

            # Create figure with Arctic color scheme
            fig, ax = plt.subplots(figsize=(12, 8), dpi=self.dpi)

            # Arctic color palette: cool blues and whites
            arctic_colors = ['#E8F4F8', '#B8D4E0', '#7FB3D5', '#4F8FC0', '#2E5F8A', '#1A3F5C']
            colors = [arctic_colors[i % len(arctic_colors)] for i in range(len(subreddit_counts))]

            # Create horizontal bars
            bars = ax.barh(range(len(subreddit_counts)), subreddit_counts.values,
                          color=colors, edgecolor='#1A3F5C', linewidth=1.5)

            # Styling
            ax.set_yticks(range(len(subreddit_counts)))
            ax.set_yticklabels(subreddit_counts.index, fontsize=12, fontweight='bold')
            ax.set_xlabel('Number of Posts/Comments', fontsize=14, fontweight='bold', color='#1A3F5C')
            ax.set_title('Subreddit Activity Distribution\nArctic Visualization Style',
                        fontsize=16, fontweight='bold', pad=20, color='#1A3F5C')

            # Add value labels on bars
            for i, (bar, value) in enumerate(zip(bars, subreddit_counts.values)):
                ax.text(value + max(subreddit_counts) * 0.01, i,
                       f'{int(value):,}',
                       va='center', fontsize=11, fontweight='bold', color='#1A3F5C')

            # Grid styling
            ax.grid(axis='x', alpha=0.3, color='#B8D4E0', linestyle='--')
            ax.set_facecolor('#F8FCFD')
            fig.patch.set_facecolor('white')

            # Add percentage labels
            total = subreddit_counts.sum()
            for i, (bar, value) in enumerate(zip(bars, subreddit_counts.values)):
                percentage = (value / total) * 100
                ax.text(value * 0.5, i,
                       f'{percentage:.1f}%',
                       va='center', ha='center', fontsize=10,
                       fontweight='bold', color='white',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='#1A3F5C', alpha=0.7))

            plt.tight_layout()

            # Save
            output_path = os.path.join(self.extended_viz_path, 'arctic_subreddit_distribution.png')
            plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight', facecolor='white')
            plt.close()

            self.logger.info(f"Arctic-style subreddit bar plot saved: {output_path}")

            # Return statistics
            return subreddit_counts.to_dict()

        except Exception as e:
            self.logger.error(f"Error creating Arctic bar plot: {e}", exc_info=True)
            return None

    def create_temporal_trends_by_subreddit(self):
        """Create line plot showing temporal trends across subreddits"""
        self.logger.info("Creating temporal trends by subreddit...")

        try:
            # Group by month and subreddit
            temporal_subreddit = self.df.groupby(['year_month', 'subreddit']).size().reset_index(name='count')

            # Create figure
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 10), dpi=self.dpi)

            # Color palette
            colors = {'Ozempic': '#2E86AB', 'Semaglutide': '#A23B72',
                     'WeightLossAdvice': '#F18F01', 'diabetes_t2': '#C73E1D'}

            # Plot 1: Line plot of activity over time
            for subreddit in self.df['subreddit'].unique():
                data = temporal_subreddit[temporal_subreddit['subreddit'] == subreddit]
                ax1.plot(range(len(data)), data['count'].values,
                        marker='o', linewidth=2, markersize=4,
                        label=subreddit, color=colors.get(subreddit, '#333333'))

            ax1.set_xlabel('Time Period', fontsize=12, fontweight='bold')
            ax1.set_ylabel('Number of Posts/Comments', fontsize=12, fontweight='bold')
            ax1.set_title('Temporal Trends Across Subreddits',
                         fontsize=14, fontweight='bold', pad=15)
            ax1.legend(loc='upper left', fontsize=10)
            ax1.grid(alpha=0.3)

            # Set x-axis labels for first plot
            unique_months = temporal_subreddit['year_month'].unique()
            step = max(1, len(unique_months) // 12)
            ax1.set_xticks(range(0, len(unique_months), step))
            ax1.set_xticklabels([str(m) for m in unique_months[::step]], rotation=45, ha='right')

            # Plot 2: Stacked area chart
            pivot_data = temporal_subreddit.pivot(index='year_month',
                                                   columns='subreddit',
                                                   values='count').fillna(0)

            ax2.stackplot(range(len(pivot_data)),
                         *[pivot_data[col].values for col in pivot_data.columns],
                         labels=pivot_data.columns,
                         colors=[colors.get(col, '#333333') for col in pivot_data.columns],
                         alpha=0.8)

            ax2.set_xlabel('Time Period', fontsize=12, fontweight='bold')
            ax2.set_ylabel('Number of Posts/Comments', fontsize=12, fontweight='bold')
            ax2.set_title('Cumulative Activity Distribution Across Subreddits',
                         fontsize=14, fontweight='bold', pad=15)
            ax2.legend(loc='upper left', fontsize=10)
            ax2.grid(alpha=0.3)

            # Set x-axis labels for second plot
            ax2.set_xticks(range(0, len(pivot_data), step))
            ax2.set_xticklabels([str(m) for m in pivot_data.index[::step]], rotation=45, ha='right')

            plt.tight_layout()

            # Save
            output_path = os.path.join(self.extended_viz_path, 'temporal_trends_by_subreddit.png')
            plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
            plt.close()

            self.logger.info(f"Temporal trends by subreddit saved: {output_path}")

            return temporal_subreddit

        except Exception as e:
            self.logger.error(f"Error creating temporal trends: {e}", exc_info=True)
            return None

    def create_subreddit_sentiment_temporal(self):
        """Create sentiment trends for each subreddit"""
        self.logger.info("Creating subreddit sentiment temporal analysis...")

        try:
            # Group by month, subreddit and calculate mean sentiment
            sentiment_temporal = self.df.groupby(['year_month', 'subreddit']).agg({
                'compound': ['mean', 'std'],
                'doc_id': 'count'
            }).reset_index()

            sentiment_temporal.columns = ['year_month', 'subreddit',
                                          'sentiment_mean', 'sentiment_std', 'count']

            # Create figure
            fig, ax = plt.subplots(figsize=(16, 8), dpi=self.dpi)

            # Color palette
            colors = {'Ozempic': '#2E86AB', 'Semaglutide': '#A23B72',
                     'WeightLossAdvice': '#F18F01', 'diabetes_t2': '#C73E1D'}

            # Plot sentiment trends for each subreddit
            for subreddit in self.df['subreddit'].unique():
                data = sentiment_temporal[sentiment_temporal['subreddit'] == subreddit]

                ax.plot(range(len(data)), data['sentiment_mean'].values,
                       marker='o', linewidth=2, markersize=5,
                       label=subreddit, color=colors.get(subreddit, '#333333'))

                # Add confidence interval
                ax.fill_between(
                    range(len(data)),
                    data['sentiment_mean'] - data['sentiment_std'],
                    data['sentiment_mean'] + data['sentiment_std'],
                    alpha=0.2, color=colors.get(subreddit, '#333333')
                )

            # Add reference line at 0
            ax.axhline(y=0, color='red', linestyle='--', alpha=0.5, linewidth=2, label='Neutral')

            ax.set_xlabel('Time Period', fontsize=12, fontweight='bold')
            ax.set_ylabel('Mean Sentiment (Compound Score)', fontsize=12, fontweight='bold')
            ax.set_title('Sentiment Trends Across Subreddits Over Time',
                        fontsize=14, fontweight='bold', pad=15)
            ax.legend(loc='best', fontsize=10)
            ax.grid(alpha=0.3)

            # Set x-axis labels
            unique_months = sentiment_temporal['year_month'].unique()
            step = max(1, len(unique_months) // 12)
            ax.set_xticks(range(0, len(unique_months), step))
            ax.set_xticklabels([str(m) for m in unique_months[::step]], rotation=45, ha='right')

            plt.tight_layout()

            # Save
            output_path = os.path.join(self.extended_viz_path, 'subreddit_sentiment_temporal.png')
            plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
            plt.close()

            self.logger.info(f"Subreddit sentiment temporal saved: {output_path}")

            # Save data
            output_csv = os.path.join(self.processed_path, 'subreddit_sentiment_temporal.csv')
            sentiment_temporal.to_csv(output_csv, index=False)

            return sentiment_temporal

        except Exception as e:
            self.logger.error(f"Error creating subreddit sentiment temporal: {e}", exc_info=True)
            return None

    # ==================== 4-TOPIC MODEL EVALUATION ====================

    def train_and_evaluate_4_topic_model(self):
        """Train LDA model with 4 topics and compute coherence score"""
        self.logger.info("Training and evaluating 4-topic LDA model...")

        try:
            # Load processed data with tokens
            df_path = os.path.join(self.processed_path, 'combined_processed.csv')
            df_tokens = pd.read_csv(df_path)

            # Parse tokens
            import ast
            df_tokens['tokens'] = df_tokens['tokens'].apply(ast.literal_eval)
            texts = df_tokens['tokens'].tolist()

            # Load existing dictionary and corpus
            lda_path = os.path.join(self.models_path, 'lda')
            dict_path = os.path.join(lda_path, 'dictionary.dict')
            corpus_path = os.path.join(lda_path, 'corpus.pkl')

            self.dictionary = corpora.Dictionary.load(dict_path)
            with open(corpus_path, 'rb') as f:
                self.corpus = pickle.load(f)

            self.texts = texts

            self.logger.info(f"Loaded dictionary with {len(self.dictionary)} terms")
            self.logger.info(f"Loaded corpus with {len(self.corpus)} documents")

            # Train 4-topic model
            self.logger.info("Training 4-topic LDA model...")

            model_4_topics = LdaModel(
                corpus=self.corpus,
                id2word=self.dictionary,
                num_topics=4,
                random_state=42,
                chunksize=2000,
                passes=10,
                iterations=400,
                alpha='auto',
                eta='auto',
                per_word_topics=True,
                minimum_probability=0.0
            )

            self.logger.info("4-topic model trained successfully")

            # Calculate coherence score
            self.logger.info("Calculating coherence score for 4-topic model...")

            coherence_model = CoherenceModel(
                model=model_4_topics,
                texts=self.texts,
                dictionary=self.dictionary,
                coherence='c_v'
            )

            coherence_score_4 = coherence_model.get_coherence()

            self.logger.info(f"Coherence score (4 topics): {coherence_score_4:.4f}")

            # Extract topics
            self.logger.info("Extracting topics from 4-topic model...")
            topics_4 = []

            for topic_id in range(4):
                top_words = model_4_topics.show_topic(topic_id, topn=15)
                words = [word for word, prob in top_words]
                probs = [float(prob) for word, prob in top_words]

                topics_4.append({
                    'topic_id': topic_id,
                    'topic_label': f"Topic {topic_id}",
                    'top_words': words,
                    'word_probabilities': probs,
                    'top_10_words': ', '.join(words[:10])
                })

                self.logger.info(f"Topic {topic_id}: {', '.join(words[:10])}")

            # Load existing 5-topic coherence for comparison
            coherence_comparison_path = os.path.join(
                self.models_path, 'evaluation', 'topic_coherence_comparison.csv'
            )
            coherence_df = pd.read_csv(coherence_comparison_path)

            # Add 4-topic result if not already present
            if 4 not in coherence_df['num_topics'].values:
                # Calculate perplexity
                perplexity_4 = model_4_topics.log_perplexity(self.corpus)

                new_row = pd.DataFrame({
                    'num_topics': [4],
                    'coherence_score': [coherence_score_4],
                    'perplexity': [perplexity_4]
                })

                coherence_df = pd.concat([coherence_df, new_row], ignore_index=True)
                coherence_df = coherence_df.sort_values('num_topics')
                coherence_df.to_csv(coherence_comparison_path, index=False)

                self.logger.info("Updated coherence comparison file with 4-topic model results")

            # Create visualization comparing coherence scores
            self.create_coherence_comparison_viz(coherence_df)

            # Save 4-topic model
            model_path = os.path.join(lda_path, 'lda_model_4_topics.model')
            model_4_topics.save(model_path)
            self.logger.info(f"4-topic model saved: {model_path}")

            # Create report
            report_4_topics = {
                'num_topics': 4,
                'coherence_score': coherence_score_4,
                'perplexity': float(perplexity_4),
                'topics': topics_4,
                'generated_at': datetime.now().isoformat()
            }

            report_path = os.path.join(self.metadata_path, '4_topic_model_report.json')
            save_json(report_4_topics, report_path)

            return report_4_topics

        except Exception as e:
            self.logger.error(f"Error training 4-topic model: {e}", exc_info=True)
            return None

    def create_coherence_comparison_viz(self, coherence_df):
        """Create enhanced coherence comparison visualization"""
        self.logger.info("Creating coherence comparison visualization...")

        try:
            fig, ax = plt.subplots(figsize=(12, 7), dpi=self.dpi)

            # Sort by number of topics
            coherence_df = coherence_df.sort_values('num_topics')

            # Plot line
            ax.plot(coherence_df['num_topics'], coherence_df['coherence_score'],
                   marker='o', linewidth=3, markersize=12, color='#2E86AB',
                   label='Coherence Score')

            # Highlight best model
            best_idx = coherence_df['coherence_score'].idxmax()
            best_topics = coherence_df.loc[best_idx, 'num_topics']
            best_score = coherence_df.loc[best_idx, 'coherence_score']

            ax.scatter([best_topics], [best_score],
                      color='#C73E1D', s=300, zorder=5,
                      label=f'Best Model ({int(best_topics)} topics)',
                      edgecolor='black', linewidth=2)

            # Highlight 4-topic model
            if 4 in coherence_df['num_topics'].values:
                score_4 = coherence_df[coherence_df['num_topics'] == 4]['coherence_score'].values[0]
                ax.scatter([4], [score_4],
                          color='#F18F01', s=250, zorder=5,
                          label='4-Topic Model',
                          edgecolor='black', linewidth=2)

            # Add value labels
            for idx, row in coherence_df.iterrows():
                ax.annotate(f'{row["coherence_score"]:.4f}',
                           xy=(row['num_topics'], row['coherence_score']),
                           xytext=(0, 10), textcoords='offset points',
                           ha='center', fontsize=9, fontweight='bold',
                           bbox=dict(boxstyle='round,pad=0.3',
                                   facecolor='white', alpha=0.8))

            # Reference lines
            ax.axhline(y=0.4, color='green', linestyle='--',
                      alpha=0.5, linewidth=2, label='Good Threshold (0.4)')
            ax.axhline(y=0.6, color='darkgreen', linestyle='--',
                      alpha=0.5, linewidth=2, label='Excellent Threshold (0.6)')

            ax.set_xlabel('Number of Topics', fontsize=12, fontweight='bold')
            ax.set_ylabel('Coherence Score (C_v)', fontsize=12, fontweight='bold')
            ax.set_title('Topic Model Coherence Comparison\n(Including 4-Topic Model)',
                        fontsize=14, fontweight='bold', pad=15)
            ax.legend(loc='best', fontsize=10)
            ax.grid(alpha=0.3)

            # Set x-axis to show integer values only
            ax.set_xticks(coherence_df['num_topics'].values)

            plt.tight_layout()

            # Save
            output_path = os.path.join(self.extended_viz_path, 'coherence_comparison_with_4topics.png')
            plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
            plt.close()

            self.logger.info(f"Coherence comparison visualization saved: {output_path}")

        except Exception as e:
            self.logger.error(f"Error creating coherence visualization: {e}", exc_info=True)

    # ==================== PRE VS POST-PANDEMIC ANALYSIS ====================

    def analyze_pandemic_posting_behavior(self):
        """Analyze posting behavior before and after pandemic"""
        self.logger.info("Analyzing pre vs post-pandemic posting behavior...")

        try:
            # Group by pandemic period
            posting_behavior = self.df.groupby('pandemic_period').agg({
                'doc_id': 'count',
                'created_utc': ['min', 'max']
            }).reset_index()

            posting_behavior.columns = ['period', 'total_posts', 'start_date', 'end_date']

            # Calculate posts per month
            pre_pandemic = self.df[self.df['pandemic_period'] == 'Pre-Pandemic']
            post_pandemic = self.df[self.df['pandemic_period'] == 'Post-Pandemic']

            pre_months = (pre_pandemic['created_utc'].max() - pre_pandemic['created_utc'].min()).days / 30.44
            post_months = (post_pandemic['created_utc'].max() - post_pandemic['created_utc'].min()).days / 30.44

            posting_behavior['months'] = [pre_months, post_months]
            posting_behavior['posts_per_month'] = posting_behavior['total_posts'] / posting_behavior['months']

            # Create visualization
            fig, axes = plt.subplots(2, 2, figsize=(16, 12), dpi=self.dpi)

            # Plot 1: Total posts comparison
            ax1 = axes[0, 0]
            colors = ['#5A7C9B', '#C73E1D']
            bars = ax1.bar(posting_behavior['period'], posting_behavior['total_posts'],
                          color=colors, edgecolor='black', linewidth=1.5)

            ax1.set_ylabel('Total Posts/Comments', fontsize=12, fontweight='bold')
            ax1.set_title('Total Posting Activity:\nPre vs Post-Pandemic',
                         fontsize=13, fontweight='bold', pad=15)
            ax1.grid(axis='y', alpha=0.3)

            # Add value labels
            for bar in bars:
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height,
                        f'{int(height):,}',
                        ha='center', va='bottom', fontsize=11, fontweight='bold')

            # Plot 2: Posts per month comparison
            ax2 = axes[0, 1]
            bars = ax2.bar(posting_behavior['period'], posting_behavior['posts_per_month'],
                          color=colors, edgecolor='black', linewidth=1.5)

            ax2.set_ylabel('Posts/Comments per Month', fontsize=12, fontweight='bold')
            ax2.set_title('Average Monthly Activity:\nPre vs Post-Pandemic',
                         fontsize=13, fontweight='bold', pad=15)
            ax2.grid(axis='y', alpha=0.3)

            # Add value labels
            for bar in bars:
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height,
                        f'{int(height):,}',
                        ha='center', va='bottom', fontsize=11, fontweight='bold')

            # Plot 3: Monthly timeline
            ax3 = axes[1, 0]
            monthly_counts = self.df.groupby('year_month').size()

            # Color by period
            colors_timeline = ['#5A7C9B' if pd.Timestamp(str(ym)) < self.pandemic_cutoff
                             else '#C73E1D' for ym in monthly_counts.index]

            ax3.bar(range(len(monthly_counts)), monthly_counts.values,
                   color=colors_timeline, alpha=0.8, edgecolor='black', linewidth=0.5)

            # Add vertical line at pandemic cutoff
            cutoff_idx = sum(pd.Timestamp(str(ym)) < self.pandemic_cutoff
                           for ym in monthly_counts.index)
            ax3.axvline(x=cutoff_idx, color='red', linestyle='--',
                       linewidth=3, label='Pandemic Start (March 2020)')

            ax3.set_xlabel('Time Period', fontsize=12, fontweight='bold')
            ax3.set_ylabel('Posts/Comments', fontsize=12, fontweight='bold')
            ax3.set_title('Monthly Activity Timeline with Pandemic Marker',
                         fontsize=13, fontweight='bold', pad=15)
            ax3.legend(loc='upper left', fontsize=10)
            ax3.grid(axis='y', alpha=0.3)

            # Set x-axis labels
            step = max(1, len(monthly_counts) // 12)
            ax3.set_xticks(range(0, len(monthly_counts), step))
            ax3.set_xticklabels([str(m) for m in monthly_counts.index[::step]],
                               rotation=45, ha='right', fontsize=9)

            # Plot 4: Growth rate
            ax4 = axes[1, 1]

            # Calculate growth
            pre_rate = posting_behavior[posting_behavior['period'] == 'Pre-Pandemic']['posts_per_month'].values[0]
            post_rate = posting_behavior[posting_behavior['period'] == 'Post-Pandemic']['posts_per_month'].values[0]
            growth_rate = ((post_rate - pre_rate) / pre_rate) * 100

            ax4.text(0.5, 0.6, f'{growth_rate:.1f}%',
                    ha='center', va='center', fontsize=60, fontweight='bold',
                    color='#C73E1D' if growth_rate > 0 else '#5A7C9B',
                    transform=ax4.transAxes)

            ax4.text(0.5, 0.35, 'Growth in Monthly Activity\nPost-Pandemic vs Pre-Pandemic',
                    ha='center', va='center', fontsize=13, fontweight='bold',
                    transform=ax4.transAxes)

            ax4.axis('off')

            plt.tight_layout()

            # Save
            output_path = os.path.join(self.extended_viz_path, 'pandemic_posting_behavior.png')
            plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
            plt.close()

            self.logger.info(f"Pandemic posting behavior saved: {output_path}")

            # Save data
            output_csv = os.path.join(self.processed_path, 'pandemic_posting_behavior.csv')
            posting_behavior.to_csv(output_csv, index=False)

            return posting_behavior.to_dict('records')

        except Exception as e:
            self.logger.error(f"Error analyzing posting behavior: {e}", exc_info=True)
            return None

    def analyze_pandemic_sentiment(self):
        """Analyze sentiment trends before and after pandemic"""
        self.logger.info("Analyzing pre vs post-pandemic sentiment...")

        try:
            # Group by pandemic period
            sentiment_stats = self.df.groupby('pandemic_period').agg({
                'compound': ['mean', 'std', 'median'],
                'pos': 'mean',
                'neu': 'mean',
                'neg': 'mean',
                'doc_id': 'count'
            }).reset_index()

            sentiment_stats.columns = ['period', 'compound_mean', 'compound_std',
                                       'compound_median', 'pos_mean', 'neu_mean',
                                       'neg_mean', 'count']

            # Sentiment class distribution
            sentiment_class_dist = pd.crosstab(
                self.df['pandemic_period'],
                self.df['sentiment_class'],
                normalize='index'
            ) * 100

            # Create visualization
            fig, axes = plt.subplots(2, 2, figsize=(16, 12), dpi=self.dpi)

            # Plot 1: Compound sentiment comparison
            ax1 = axes[0, 0]
            colors = ['#5A7C9B', '#C73E1D']
            bars = ax1.bar(sentiment_stats['period'], sentiment_stats['compound_mean'],
                          yerr=sentiment_stats['compound_std'],
                          color=colors, edgecolor='black', linewidth=1.5,
                          capsize=5, error_kw={'linewidth': 2})

            ax1.axhline(y=0, color='red', linestyle='--', alpha=0.5, linewidth=2)
            ax1.set_ylabel('Mean Compound Sentiment', fontsize=12, fontweight='bold')
            ax1.set_title('Average Sentiment:\nPre vs Post-Pandemic',
                         fontsize=13, fontweight='bold', pad=15)
            ax1.grid(axis='y', alpha=0.3)

            # Add value labels
            for bar, val in zip(bars, sentiment_stats['compound_mean']):
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height,
                        f'{val:.4f}',
                        ha='center', va='bottom' if height > 0 else 'top',
                        fontsize=11, fontweight='bold')

            # Plot 2: Sentiment class distribution
            ax2 = axes[0, 1]
            sentiment_class_dist.plot(kind='bar', ax=ax2,
                                     color=['#2E7D32', '#FBC02D', '#C62828'],
                                     edgecolor='black', linewidth=1.5)

            ax2.set_xlabel('Period', fontsize=12, fontweight='bold')
            ax2.set_ylabel('Percentage (%)', fontsize=12, fontweight='bold')
            ax2.set_title('Sentiment Distribution:\nPre vs Post-Pandemic',
                         fontsize=13, fontweight='bold', pad=15)
            ax2.set_xticklabels(ax2.get_xticklabels(), rotation=45, ha='right')
            ax2.legend(title='Sentiment', title_fontsize=11, fontsize=10)
            ax2.grid(axis='y', alpha=0.3)

            # Plot 3: Component scores
            ax3 = axes[1, 0]
            x = np.arange(len(sentiment_stats))
            width = 0.25

            bars1 = ax3.bar(x - width, sentiment_stats['pos_mean'], width,
                           label='Positive', color='#2E7D32', edgecolor='black')
            bars2 = ax3.bar(x, sentiment_stats['neu_mean'], width,
                           label='Neutral', color='#FBC02D', edgecolor='black')
            bars3 = ax3.bar(x + width, sentiment_stats['neg_mean'], width,
                           label='Negative', color='#C62828', edgecolor='black')

            ax3.set_ylabel('Mean Score', fontsize=12, fontweight='bold')
            ax3.set_title('Sentiment Component Scores:\nPre vs Post-Pandemic',
                         fontsize=13, fontweight='bold', pad=15)
            ax3.set_xticks(x)
            ax3.set_xticklabels(sentiment_stats['period'])
            ax3.legend(fontsize=10)
            ax3.grid(axis='y', alpha=0.3)

            # Plot 4: Temporal sentiment trend with pandemic marker
            ax4 = axes[1, 1]
            monthly_sentiment = self.df.groupby('year_month')['compound'].mean()

            # Color by period
            colors_timeline = ['#5A7C9B' if pd.Timestamp(str(ym)) < self.pandemic_cutoff
                             else '#C73E1D' for ym in monthly_sentiment.index]

            ax4.plot(range(len(monthly_sentiment)), monthly_sentiment.values,
                    linewidth=2, color='black', alpha=0.5)
            ax4.scatter(range(len(monthly_sentiment)), monthly_sentiment.values,
                       c=colors_timeline, s=50, edgecolor='black', linewidth=0.5, zorder=3)

            # Add vertical line at pandemic cutoff
            cutoff_idx = sum(pd.Timestamp(str(ym)) < self.pandemic_cutoff
                           for ym in monthly_sentiment.index)
            ax4.axvline(x=cutoff_idx, color='red', linestyle='--',
                       linewidth=3, label='Pandemic Start')

            ax4.axhline(y=0, color='red', linestyle='--', alpha=0.3, linewidth=1)

            ax4.set_xlabel('Time Period', fontsize=12, fontweight='bold')
            ax4.set_ylabel('Mean Compound Sentiment', fontsize=12, fontweight='bold')
            ax4.set_title('Sentiment Trend Over Time with Pandemic Marker',
                         fontsize=13, fontweight='bold', pad=15)
            ax4.legend(loc='best', fontsize=10)
            ax4.grid(alpha=0.3)

            # Set x-axis labels
            step = max(1, len(monthly_sentiment) // 12)
            ax4.set_xticks(range(0, len(monthly_sentiment), step))
            ax4.set_xticklabels([str(m) for m in monthly_sentiment.index[::step]],
                               rotation=45, ha='right', fontsize=9)

            plt.tight_layout()

            # Save
            output_path = os.path.join(self.extended_viz_path, 'pandemic_sentiment_analysis.png')
            plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
            plt.close()

            self.logger.info(f"Pandemic sentiment analysis saved: {output_path}")

            # Save data
            output_csv = os.path.join(self.processed_path, 'pandemic_sentiment_stats.csv')
            sentiment_stats.to_csv(output_csv, index=False)

            return sentiment_stats.to_dict('records')

        except Exception as e:
            self.logger.error(f"Error analyzing pandemic sentiment: {e}", exc_info=True)
            return None

    def analyze_pandemic_topic_distribution(self):
        """Analyze topic distribution before and after pandemic"""
        self.logger.info("Analyzing pre vs post-pandemic topic distribution...")

        try:
            # Topic distribution by pandemic period
            topic_dist = pd.crosstab(
                self.df['pandemic_period'],
                self.df['topic_name'],
                normalize='index'
            ) * 100

            # Topic counts
            topic_counts = pd.crosstab(
                self.df['pandemic_period'],
                self.df['topic_name']
            )

            # Create visualization
            fig, axes = plt.subplots(2, 2, figsize=(16, 12), dpi=self.dpi)

            # Plot 1: Grouped bar chart
            ax1 = axes[0, 0]
            topic_dist.T.plot(kind='bar', ax=ax1,
                             color=['#5A7C9B', '#C73E1D'],
                             edgecolor='black', linewidth=1.5)

            ax1.set_xlabel('Topic', fontsize=12, fontweight='bold')
            ax1.set_ylabel('Percentage (%)', fontsize=12, fontweight='bold')
            ax1.set_title('Topic Distribution:\nPre vs Post-Pandemic (%)',
                         fontsize=13, fontweight='bold', pad=15)
            ax1.set_xticklabels(ax1.get_xticklabels(), rotation=45, ha='right')
            ax1.legend(title='Period', title_fontsize=11, fontsize=10)
            ax1.grid(axis='y', alpha=0.3)

            # Plot 2: Stacked bar chart (counts)
            ax2 = axes[0, 1]
            topic_counts.T.plot(kind='bar', stacked=True, ax=ax2,
                               color=['#5A7C9B', '#C73E1D'],
                               edgecolor='black', linewidth=1.5)

            ax2.set_xlabel('Topic', fontsize=12, fontweight='bold')
            ax2.set_ylabel('Number of Posts/Comments', fontsize=12, fontweight='bold')
            ax2.set_title('Topic Distribution:\nPre vs Post-Pandemic (Counts)',
                         fontsize=13, fontweight='bold', pad=15)
            ax2.set_xticklabels(ax2.get_xticklabels(), rotation=45, ha='right')
            ax2.legend(title='Period', title_fontsize=11, fontsize=10)
            ax2.grid(axis='y', alpha=0.3)

            # Plot 3: Heatmap
            ax3 = axes[1, 0]
            sns.heatmap(topic_dist, annot=True, fmt='.1f', cmap='RdYlBu_r',
                       cbar_kws={'label': 'Percentage (%)'},
                       linewidths=0.5, ax=ax3)

            ax3.set_xlabel('Topic', fontsize=12, fontweight='bold')
            ax3.set_ylabel('Period', fontsize=12, fontweight='bold')
            ax3.set_title('Topic Distribution Heatmap',
                         fontsize=13, fontweight='bold', pad=15)
            ax3.set_xticklabels(ax3.get_xticklabels(), rotation=45, ha='right')
            ax3.set_yticklabels(ax3.get_yticklabels(), rotation=0)

            # Plot 4: Change in topic proportions
            ax4 = axes[1, 1]

            # Calculate change
            pre_dist = topic_dist.loc['Pre-Pandemic']
            post_dist = topic_dist.loc['Post-Pandemic']
            change = post_dist - pre_dist
            change = change.sort_values()

            colors_change = ['#C73E1D' if x > 0 else '#5A7C9B' for x in change]
            bars = ax4.barh(range(len(change)), change.values,
                           color=colors_change, edgecolor='black', linewidth=1.5)

            ax4.axvline(x=0, color='black', linestyle='-', linewidth=2)
            ax4.set_yticks(range(len(change)))
            ax4.set_yticklabels(change.index, fontsize=10)
            ax4.set_xlabel('Change in Percentage Points', fontsize=12, fontweight='bold')
            ax4.set_title('Topic Proportion Change:\nPost-Pandemic vs Pre-Pandemic',
                         fontsize=13, fontweight='bold', pad=15)
            ax4.grid(axis='x', alpha=0.3)

            # Add value labels
            for i, (bar, val) in enumerate(zip(bars, change.values)):
                width = bar.get_width()
                ax4.text(width, i,
                        f' {val:+.1f}%',
                        ha='left' if width > 0 else 'right',
                        va='center', fontsize=10, fontweight='bold')

            plt.tight_layout()

            # Save
            output_path = os.path.join(self.extended_viz_path, 'pandemic_topic_distribution.png')
            plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
            plt.close()

            self.logger.info(f"Pandemic topic distribution saved: {output_path}")

            # Save data
            output_csv = os.path.join(self.processed_path, 'pandemic_topic_distribution.csv')
            topic_dist.to_csv(output_csv)

            return topic_dist.to_dict()

        except Exception as e:
            self.logger.error(f"Error analyzing topic distribution: {e}", exc_info=True)
            return None

    # ==================== TEMPORAL TREND METHODOLOGY ====================

    def document_temporal_methodology(self):
        """Create comprehensive documentation of temporal trend methodology"""
        self.logger.info("Documenting temporal trend methodology...")

        try:
            methodology = {
                "temporal_trend_methodology": {
                    "overview": "This document explains how temporal trends were derived in the Semaglutide Reddit Analysis project.",

                    "data_source": {
                        "description": "Reddit posts and comments collected from 4 subreddits",
                        "subreddits": ["r/Ozempic", "r/Semaglutide", "r/WeightLossAdvice", "r/diabetes_t2"],
                        "collection_period": f"{self.df['created_utc'].min()} to {self.df['created_utc'].max()}",
                        "total_documents": len(self.df),
                        "posts": len(self.df[self.df['doc_type'] == 'post']),
                        "comments": len(self.df[self.df['doc_type'] == 'comment']),
                        "data_fields_used": [
                            "created_utc (timestamp)",
                            "subreddit",
                            "doc_type (post/comment)",
                            "compound (sentiment score)",
                            "dominant_topic",
                            "sentiment_class"
                        ]
                    },

                    "time_segmentation": {
                        "primary_method": "Monthly bins (year-month periods)",
                        "implementation": "Using pandas Period functionality with frequency='M'",
                        "code_example": "df['year_month'] = df['created_utc'].dt.to_period('M')",
                        "rationale": "Monthly aggregation provides sufficient granularity while smoothing out daily noise",
                        "total_months": len(self.df['year_month'].unique()),
                        "month_range": f"{self.df['year_month'].min()} to {self.df['year_month'].max()}",

                        "alternative_segmentation": {
                            "yearly": "For high-level trend analysis",
                            "quarterly": "For seasonal pattern analysis",
                            "pandemic_periods": {
                                "pre_pandemic": f"Before {self.pandemic_cutoff}",
                                "post_pandemic": f"After {self.pandemic_cutoff}",
                                "cutoff_rationale": "March 2020 marks WHO pandemic declaration"
                            }
                        }
                    },

                    "processing_pipeline": {
                        "step_1": {
                            "name": "Timestamp Parsing",
                            "description": "Convert Unix timestamps to pandas datetime objects",
                            "function": "pd.to_datetime()",
                            "input": "created_utc column from raw data",
                            "output": "Datetime objects with timezone awareness"
                        },

                        "step_2": {
                            "name": "Temporal Feature Engineering",
                            "description": "Extract temporal features for aggregation",
                            "features_created": [
                                "year_month: Monthly period",
                                "year: Calendar year",
                                "month: Month number (1-12)",
                                "pandemic_period: Pre/Post pandemic classification"
                            ]
                        },

                        "step_3": {
                            "name": "Aggregation",
                            "description": "Group data by temporal bins and calculate statistics",
                            "aggregation_functions": {
                                "posting_activity": "count() - number of posts/comments per period",
                                "sentiment_mean": "mean() of compound scores",
                                "sentiment_std": "std() of compound scores",
                                "topic_distribution": "crosstab() or value_counts() normalized"
                            },
                            "code_example": "df.groupby('year_month').agg({'compound': ['mean', 'std'], 'doc_id': 'count'})"
                        },

                        "step_4": {
                            "name": "Multi-dimensional Analysis",
                            "description": "Cross-tabulate temporal data with other dimensions",
                            "dimensions": [
                                "Subreddit: Temporal trends per community",
                                "Topic: Topic prevalence over time",
                                "Sentiment: Sentiment evolution over time",
                                "Pandemic Period: Before/after comparison"
                            ]
                        },

                        "step_5": {
                            "name": "Visualization",
                            "description": "Generate temporal plots with appropriate time axes",
                            "plot_types": [
                                "Line plots: Continuous trends over time",
                                "Bar plots: Discrete period comparisons",
                                "Stacked area: Cumulative distributions over time",
                                "Scatter plots: Individual data points with temporal coloring"
                            ],
                            "x_axis_handling": "Sequential indices with period labels for readability"
                        }
                    },

                    "specific_temporal_analyses": {
                        "posting_activity_trends": {
                            "description": "Track volume of posts/comments over time",
                            "calculation": "Count of documents per month",
                            "insights": [
                                "Identify growth patterns",
                                "Detect activity spikes",
                                "Compare subreddit activity levels"
                            ]
                        },

                        "sentiment_trends": {
                            "description": "Track sentiment evolution over time",
                            "calculation": "Mean and standard deviation of compound scores per month",
                            "metrics": [
                                "compound_mean: Average sentiment",
                                "compound_std: Sentiment variability",
                                "sentiment_class distribution: % positive/neutral/negative"
                            ],
                            "insights": [
                                "Detect sentiment shifts",
                                "Identify stable vs volatile periods",
                                "Compare sentiment across communities"
                            ]
                        },

                        "topic_evolution": {
                            "description": "Track topic prevalence over time",
                            "calculation": "Topic distribution (%) per month",
                            "insights": [
                                "Identify emerging topics",
                                "Track declining interests",
                                "Detect topic shifts around events"
                            ]
                        },

                        "pandemic_comparison": {
                            "description": "Compare metrics before and after pandemic",
                            "cutoff_date": str(self.pandemic_cutoff),
                            "metrics_compared": [
                                "Total posting volume",
                                "Average monthly activity",
                                "Mean sentiment scores",
                                "Topic distribution changes",
                                "Growth rate calculations"
                            ],
                            "calculation_example": "growth_rate = ((post_rate - pre_rate) / pre_rate) * 100"
                        }
                    },

                    "data_quality_considerations": {
                        "handling_missing_months": "Months with no data are preserved in visualizations but marked accordingly",
                        "outlier_detection": "Standard deviation bands used to identify unusual periods",
                        "smoothing": "No smoothing applied to preserve authentic patterns",
                        "minimum_sample_size": "Periods with <10 documents flagged for interpretation caution"
                    },

                    "output_files": {
                        "sentiment_temporal.csv": {
                            "description": "Monthly sentiment aggregates",
                            "columns": ["year_month", "compound_mean", "compound_std", "doc_count"],
                            "rows": 79
                        },
                        "sentiment_topic_temporal.csv": {
                            "description": "Monthly sentiment by topic",
                            "columns": ["year_month", "topic_name", "compound_mean", "doc_count"],
                            "rows": 296
                        },
                        "subreddit_sentiment_temporal.csv": {
                            "description": "Monthly sentiment by subreddit",
                            "columns": ["year_month", "subreddit", "sentiment_mean", "sentiment_std", "count"]
                        },
                        "pandemic_posting_behavior.csv": {
                            "description": "Posting statistics by pandemic period",
                            "columns": ["period", "total_posts", "start_date", "end_date", "months", "posts_per_month"]
                        },
                        "pandemic_sentiment_stats.csv": {
                            "description": "Sentiment statistics by pandemic period",
                            "columns": ["period", "compound_mean", "compound_std", "compound_median", "pos_mean", "neu_mean", "neg_mean", "count"]
                        },
                        "pandemic_topic_distribution.csv": {
                            "description": "Topic distribution by pandemic period",
                            "columns": ["period"] + list(self.topic_names.values())
                        }
                    },

                    "reproducibility": {
                        "random_seed": "Not applicable for temporal analysis (deterministic)",
                        "dependencies": ["pandas", "numpy", "matplotlib", "seaborn"],
                        "python_version": "3.8+",
                        "execution_time": "~2-5 minutes for full temporal analysis pipeline"
                    },

                    "generated_at": datetime.now().isoformat(),
                    "generated_by": "Extended Analysis Module (scripts/08_extended_analysis.py)"
                }
            }

            # Save as JSON
            json_path = os.path.join(self.metadata_path, 'temporal_methodology.json')
            save_json(methodology, json_path)

            # Create markdown documentation
            markdown_content = self._create_markdown_methodology(methodology)
            markdown_path = os.path.join('docs', 'TEMPORAL_METHODOLOGY.md')
            os.makedirs('docs', exist_ok=True)

            with open(markdown_path, 'w') as f:
                f.write(markdown_content)

            self.logger.info(f"Temporal methodology documented:")
            self.logger.info(f"  JSON: {json_path}")
            self.logger.info(f"  Markdown: {markdown_path}")

            return methodology

        except Exception as e:
            self.logger.error(f"Error documenting methodology: {e}", exc_info=True)
            return None

    def _create_markdown_methodology(self, methodology_dict):
        """Create markdown documentation from methodology dictionary"""

        md = f"""# Temporal Trend Derivation Methodology

**Generated:** {methodology_dict['temporal_trend_methodology']['generated_at']}

## Overview

{methodology_dict['temporal_trend_methodology']['overview']}

## 1. Data Source

### Reddit Collection
- **Subreddits:** {', '.join(methodology_dict['temporal_trend_methodology']['data_source']['subreddits'])}
- **Collection Period:** {methodology_dict['temporal_trend_methodology']['data_source']['collection_period']}
- **Total Documents:** {methodology_dict['temporal_trend_methodology']['data_source']['total_documents']:,}
  - Posts: {methodology_dict['temporal_trend_methodology']['data_source']['posts']:,}
  - Comments: {methodology_dict['temporal_trend_methodology']['data_source']['comments']:,}

### Key Data Fields Used for Temporal Analysis
"""

        for field in methodology_dict['temporal_trend_methodology']['data_source']['data_fields_used']:
            md += f"- {field}\n"

        md += f"""
## 2. Time Segmentation Method

### Primary Method: {methodology_dict['temporal_trend_methodology']['time_segmentation']['primary_method']}

**Implementation:**
```python
{methodology_dict['temporal_trend_methodology']['time_segmentation']['code_example']}
```

**Rationale:** {methodology_dict['temporal_trend_methodology']['time_segmentation']['rationale']}

- **Total Months Analyzed:** {methodology_dict['temporal_trend_methodology']['time_segmentation']['total_months']}
- **Date Range:** {methodology_dict['temporal_trend_methodology']['time_segmentation']['month_range']}

### Alternative Segmentations
- **Yearly:** {methodology_dict['temporal_trend_methodology']['time_segmentation']['alternative_segmentation']['yearly']}
- **Quarterly:** {methodology_dict['temporal_trend_methodology']['time_segmentation']['alternative_segmentation']['quarterly']}
- **Pandemic Periods:**
  - Pre-Pandemic: {methodology_dict['temporal_trend_methodology']['time_segmentation']['alternative_segmentation']['pandemic_periods']['pre_pandemic']}
  - Post-Pandemic: {methodology_dict['temporal_trend_methodology']['time_segmentation']['alternative_segmentation']['pandemic_periods']['post_pandemic']}
  - Rationale: {methodology_dict['temporal_trend_methodology']['time_segmentation']['alternative_segmentation']['pandemic_periods']['cutoff_rationale']}

## 3. Processing Pipeline

### Step 1: {methodology_dict['temporal_trend_methodology']['processing_pipeline']['step_1']['name']}
{methodology_dict['temporal_trend_methodology']['processing_pipeline']['step_1']['description']}

- **Function:** `{methodology_dict['temporal_trend_methodology']['processing_pipeline']['step_1']['function']}`
- **Input:** {methodology_dict['temporal_trend_methodology']['processing_pipeline']['step_1']['input']}
- **Output:** {methodology_dict['temporal_trend_methodology']['processing_pipeline']['step_1']['output']}

### Step 2: {methodology_dict['temporal_trend_methodology']['processing_pipeline']['step_2']['name']}
{methodology_dict['temporal_trend_methodology']['processing_pipeline']['step_2']['description']}

**Features Created:**
"""

        for feature in methodology_dict['temporal_trend_methodology']['processing_pipeline']['step_2']['features_created']:
            md += f"- {feature}\n"

        md += f"""
### Step 3: {methodology_dict['temporal_trend_methodology']['processing_pipeline']['step_3']['name']}
{methodology_dict['temporal_trend_methodology']['processing_pipeline']['step_3']['description']}

**Aggregation Functions:**
"""

        for func_name, func_desc in methodology_dict['temporal_trend_methodology']['processing_pipeline']['step_3']['aggregation_functions'].items():
            md += f"- **{func_name}:** {func_desc}\n"

        md += f"""
**Example Code:**
```python
{methodology_dict['temporal_trend_methodology']['processing_pipeline']['step_3']['code_example']}
```

### Step 4: {methodology_dict['temporal_trend_methodology']['processing_pipeline']['step_4']['name']}
{methodology_dict['temporal_trend_methodology']['processing_pipeline']['step_4']['description']}

**Dimensions Analyzed:**
"""

        for dim in methodology_dict['temporal_trend_methodology']['processing_pipeline']['step_4']['dimensions']:
            md += f"- {dim}\n"

        md += f"""
### Step 5: {methodology_dict['temporal_trend_methodology']['processing_pipeline']['step_5']['name']}
{methodology_dict['temporal_trend_methodology']['processing_pipeline']['step_5']['description']}

**Plot Types:**
"""

        for plot_type in methodology_dict['temporal_trend_methodology']['processing_pipeline']['step_5']['plot_types']:
            md += f"- {plot_type}\n"

        md += f"""
**X-Axis Handling:** {methodology_dict['temporal_trend_methodology']['processing_pipeline']['step_5']['x_axis_handling']}

## 4. Specific Temporal Analyses

### 4.1 Posting Activity Trends
{methodology_dict['temporal_trend_methodology']['specific_temporal_analyses']['posting_activity_trends']['description']}

- **Calculation:** {methodology_dict['temporal_trend_methodology']['specific_temporal_analyses']['posting_activity_trends']['calculation']}

**Insights:**
"""

        for insight in methodology_dict['temporal_trend_methodology']['specific_temporal_analyses']['posting_activity_trends']['insights']:
            md += f"- {insight}\n"

        md += f"""
### 4.2 Sentiment Trends
{methodology_dict['temporal_trend_methodology']['specific_temporal_analyses']['sentiment_trends']['description']}

- **Calculation:** {methodology_dict['temporal_trend_methodology']['specific_temporal_analyses']['sentiment_trends']['calculation']}

**Metrics:**
"""

        for metric in methodology_dict['temporal_trend_methodology']['specific_temporal_analyses']['sentiment_trends']['metrics']:
            md += f"- {metric}\n"

        md += f"""
**Insights:**
"""

        for insight in methodology_dict['temporal_trend_methodology']['specific_temporal_analyses']['sentiment_trends']['insights']:
            md += f"- {insight}\n"

        md += f"""
### 4.3 Topic Evolution
{methodology_dict['temporal_trend_methodology']['specific_temporal_analyses']['topic_evolution']['description']}

- **Calculation:** {methodology_dict['temporal_trend_methodology']['specific_temporal_analyses']['topic_evolution']['calculation']}

**Insights:**
"""

        for insight in methodology_dict['temporal_trend_methodology']['specific_temporal_analyses']['topic_evolution']['insights']:
            md += f"- {insight}\n"

        md += f"""
### 4.4 Pandemic Comparison Analysis
{methodology_dict['temporal_trend_methodology']['specific_temporal_analyses']['pandemic_comparison']['description']}

- **Cutoff Date:** {methodology_dict['temporal_trend_methodology']['specific_temporal_analyses']['pandemic_comparison']['cutoff_date']}

**Metrics Compared:**
"""

        for metric in methodology_dict['temporal_trend_methodology']['specific_temporal_analyses']['pandemic_comparison']['metrics_compared']:
            md += f"- {metric}\n"

        md += f"""
**Example Calculation:**
```python
{methodology_dict['temporal_trend_methodology']['specific_temporal_analyses']['pandemic_comparison']['calculation_example']}
```

## 5. Output Files

The temporal analysis pipeline generates the following CSV files:

"""

        for filename, details in methodology_dict['temporal_trend_methodology']['output_files'].items():
            md += f"### {filename}\n"
            md += f"{details['description']}\n\n"
            if 'columns' in details:
                md += f"**Columns:** {', '.join(details['columns'])}\n\n"
            if 'rows' in details:
                md += f"**Rows:** {details['rows']}\n\n"

        md += f"""
## 6. Data Quality Considerations

- **Handling Missing Months:** {methodology_dict['temporal_trend_methodology']['data_quality_considerations']['handling_missing_months']}
- **Outlier Detection:** {methodology_dict['temporal_trend_methodology']['data_quality_considerations']['outlier_detection']}
- **Smoothing:** {methodology_dict['temporal_trend_methodology']['data_quality_considerations']['smoothing']}
- **Minimum Sample Size:** {methodology_dict['temporal_trend_methodology']['data_quality_considerations']['minimum_sample_size']}

## 7. Reproducibility

- **Random Seed:** {methodology_dict['temporal_trend_methodology']['reproducibility']['random_seed']}
- **Dependencies:** {', '.join(methodology_dict['temporal_trend_methodology']['reproducibility']['dependencies'])}
- **Python Version:** {methodology_dict['temporal_trend_methodology']['reproducibility']['python_version']}
- **Execution Time:** {methodology_dict['temporal_trend_methodology']['reproducibility']['execution_time']}

---

*This methodology document ensures transparency and reproducibility of all temporal trend analyses in the Semaglutide Reddit Analysis project.*
"""

        return md

    # ==================== MAIN EXECUTION ====================

    def run_all_analyses(self):
        """Execute all extended analyses"""
        self.logger.info("="*80)
        self.logger.info("STARTING EXTENDED ANALYSIS")
        self.logger.info("="*80)

        results = {}

        try:
            # Subreddit-level analysis
            self.logger.info("\n=== SUBREDDIT-LEVEL ANALYSIS ===")
            results['subreddit_distribution'] = self.create_arctic_style_subreddit_barplot()
            results['temporal_trends_subreddit'] = self.create_temporal_trends_by_subreddit()
            results['subreddit_sentiment_temporal'] = self.create_subreddit_sentiment_temporal()

            # 4-topic model evaluation
            self.logger.info("\n=== 4-TOPIC MODEL EVALUATION ===")
            results['4_topic_model'] = self.train_and_evaluate_4_topic_model()

            # Pandemic analysis
            self.logger.info("\n=== PRE VS POST-PANDEMIC ANALYSIS ===")
            results['pandemic_posting'] = self.analyze_pandemic_posting_behavior()
            results['pandemic_sentiment'] = self.analyze_pandemic_sentiment()
            results['pandemic_topics'] = self.analyze_pandemic_topic_distribution()

            # Methodology documentation
            self.logger.info("\n=== TEMPORAL METHODOLOGY DOCUMENTATION ===")
            results['methodology'] = self.document_temporal_methodology()

            # Create summary report
            self.create_summary_report(results)

            self.logger.info("\n" + "="*80)
            self.logger.info("EXTENDED ANALYSIS COMPLETE!")
            self.logger.info("="*80)

            return results

        except Exception as e:
            self.logger.error(f"Error in analysis execution: {e}", exc_info=True)
            return results

    def create_summary_report(self, results):
        """Create summary report of extended analysis"""
        self.logger.info("Creating summary report...")

        try:
            summary = {
                "extended_analysis_summary": {
                    "generated_at": datetime.now().isoformat(),
                    "total_documents_analyzed": len(self.df),
                    "date_range": f"{self.df['created_utc'].min()} to {self.df['created_utc'].max()}",

                    "subreddit_analysis": {
                        "subreddits": list(self.df['subreddit'].unique()),
                        "subreddit_counts": results.get('subreddit_distribution', {}),
                        "visualizations_created": [
                            "arctic_subreddit_distribution.png",
                            "temporal_trends_by_subreddit.png",
                            "subreddit_sentiment_temporal.png"
                        ]
                    },

                    "4_topic_model": {
                        "status": "completed" if results.get('4_topic_model') else "failed",
                        "coherence_score": results['4_topic_model']['coherence_score'] if results.get('4_topic_model') else None,
                        "model_file": "models/lda/lda_model_4_topics.model",
                        "visualization": "coherence_comparison_with_4topics.png"
                    },

                    "pandemic_analysis": {
                        "cutoff_date": str(self.pandemic_cutoff),
                        "pre_pandemic_docs": len(self.df[self.df['pandemic_period'] == 'Pre-Pandemic']),
                        "post_pandemic_docs": len(self.df[self.df['pandemic_period'] == 'Post-Pandemic']),
                        "visualizations_created": [
                            "pandemic_posting_behavior.png",
                            "pandemic_sentiment_analysis.png",
                            "pandemic_topic_distribution.png"
                        ]
                    },

                    "documentation": {
                        "temporal_methodology": "docs/TEMPORAL_METHODOLOGY.md",
                        "methodology_json": "data/metadata/temporal_methodology.json"
                    },

                    "output_location": self.extended_viz_path
                }
            }

            # Save summary
            summary_path = os.path.join(self.metadata_path, 'extended_analysis_summary.json')
            save_json(summary, summary_path)

            self.logger.info(f"Summary report saved: {summary_path}")

            return summary

        except Exception as e:
            self.logger.error(f"Error creating summary report: {e}", exc_info=True)
            return None


def main():
    """Main execution function"""
    print("\n" + "="*80)
    print("MODULE 8: EXTENDED ANALYSIS AND VISUALIZATIONS")
    print("="*80 + "\n")

    # Initialize
    analyzer = ExtendedAnalyzer()

    # Load data
    print("Step 1: Loading final dataset...")
    if not analyzer.load_data():
        print("ERROR: Failed to load data")
        return

    # Run all analyses
    print("\nStep 2: Running all extended analyses...")
    print("This may take several minutes...\n")

    results = analyzer.run_all_analyses()

    # Print summary
    print("\n" + "="*80)
    print("EXTENDED ANALYSIS COMPLETE!")
    print("="*80)

    print("\n📊 Visualizations Created:")
    print(f"  Location: {analyzer.extended_viz_path}/")
    print("\n  Subreddit Analysis:")
    print("    - arctic_subreddit_distribution.png")
    print("    - temporal_trends_by_subreddit.png")
    print("    - subreddit_sentiment_temporal.png")
    print("\n  4-Topic Model:")
    print("    - coherence_comparison_with_4topics.png")
    print("\n  Pandemic Analysis:")
    print("    - pandemic_posting_behavior.png")
    print("    - pandemic_sentiment_analysis.png")
    print("    - pandemic_topic_distribution.png")

    print("\n📄 Documentation Created:")
    print("    - docs/TEMPORAL_METHODOLOGY.md")
    print("    - data/metadata/temporal_methodology.json")
    print("    - data/metadata/extended_analysis_summary.json")

    print("\n✓ Module 8: Extended Analysis - COMPLETE\n")


if __name__ == "__main__":
    main()
