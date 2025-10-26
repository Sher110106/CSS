"""
Module 7: Comprehensive Visualization Generation
Creates all visualizations for the research report
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import json
import os
from datetime import datetime
import pickle
import logging

from utils import setup_logger, load_config


class Visualizer:
    """Comprehensive Visualization Generator"""
    
    def __init__(self, config_path='config/config.yaml'):
        """Initialize visualizer"""
        self.config = load_config(config_path)
        self.logger = setup_logger(
            'visualization',
            'logs/visualization.log'
        )
        
        # Paths
        self.processed_path = self.config['paths']['processed_data']
        self.models_path = self.config['paths']['models']
        self.viz_path = self.config['paths']['visualizations']
        self.metadata_path = self.config['paths']['metadata']
        
        # Create visualization directories
        self.wordclouds_path = os.path.join(self.viz_path, 'wordclouds')
        self.charts_path = os.path.join(self.viz_path, 'charts')
        self.report_path = os.path.join(self.viz_path, 'report_figures')
        
        os.makedirs(self.wordclouds_path, exist_ok=True)
        os.makedirs(self.charts_path, exist_ok=True)
        os.makedirs(self.report_path, exist_ok=True)
        
        # Visualization settings
        self.dpi = self.config['visualization']['figure_dpi']
        self.format = self.config['visualization']['figure_format']
        
        # Set style
        plt.style.use('seaborn-v0_8-darkgrid')
        sns.set_palette("viridis")
        
        # Data containers
        self.df = None
        self.topic_names = {
            0: "Alternative Medications",
            1: "Weight Loss Experiences",
            2: "Insurance & Access",
            3: "Diet & Side Effects",
            4: "Community Support"
        }
        
        self.logger.info("Visualizer initialized")
        self.logger.info(f"DPI: {self.dpi}, Format: {self.format}")
    
    def load_data(self):
        """Load integrated dataset"""
        self.logger.info("Loading data...")
        
        try:
            # Load final dataset
            df_path = os.path.join(self.processed_path, 'documents_with_sentiment.csv')
            self.df = pd.read_csv(df_path)
            
            # Add topic names
            self.df['topic_name'] = self.df['dominant_topic'].map(self.topic_names)
            
            # Convert timestamp
            self.df['created_utc'] = pd.to_datetime(self.df['created_utc'])
            
            self.logger.info(f"Loaded {len(self.df)} documents")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading data: {e}", exc_info=True)
            return False
    
    # ==================== WORD CLOUDS ====================
    
    def create_overall_wordcloud(self):
        """Create overall word cloud"""
        self.logger.info("Creating overall word cloud...")
        
        try:
            # Combine all text
            text = ' '.join(self.df['cleaned_text'].astype(str))
            
            # Create word cloud
            wordcloud = WordCloud(
                width=1600,
                height=800,
                background_color='white',
                colormap='viridis',
                max_words=100,
                relative_scaling=0.5,
                min_font_size=10
            ).generate(text)
            
            # Plot
            fig, ax = plt.subplots(figsize=(16, 8), dpi=self.dpi)
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.axis('off')
            ax.set_title('Overall Word Cloud - Semaglutide Discussions', 
                        fontsize=20, fontweight='bold', pad=20)
            
            plt.tight_layout()
            
            # Save
            output_path = os.path.join(self.wordclouds_path, 'overall_wordcloud.png')
            plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
            plt.close()
            
            self.logger.info(f"Overall word cloud saved: {output_path}")
            
        except Exception as e:
            self.logger.error(f"Error creating overall word cloud: {e}", exc_info=True)
    
    def create_topic_wordclouds(self):
        """Create word cloud for each topic"""
        self.logger.info("Creating topic word clouds...")
        
        for topic_id, topic_name in self.topic_names.items():
            try:
                topic_df = self.df[self.df['dominant_topic'] == topic_id]
                
                if len(topic_df) < 10:
                    self.logger.warning(f"Skipping {topic_name} - too few documents")
                    continue
                
                # Combine text for topic
                text = ' '.join(topic_df['cleaned_text'].astype(str))
                
                # Create word cloud
                wordcloud = WordCloud(
                    width=1200,
                    height=600,
                    background_color='white',
                    colormap='viridis',
                    max_words=50,
                    relative_scaling=0.5,
                    min_font_size=8
                ).generate(text)
                
                # Plot
                fig, ax = plt.subplots(figsize=(12, 6), dpi=self.dpi)
                ax.imshow(wordcloud, interpolation='bilinear')
                ax.axis('off')
                ax.set_title(f'Topic {topic_id}: {topic_name}', 
                           fontsize=16, fontweight='bold', pad=15)
                
                plt.tight_layout()
                
                # Save
                output_path = os.path.join(
                    self.wordclouds_path, 
                    f'topic_{topic_id}_wordcloud.png'
                )
                plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
                plt.close()
                
                self.logger.info(f"Topic {topic_id} word cloud saved")
                
            except Exception as e:
                self.logger.error(f"Error creating word cloud for topic {topic_id}: {e}")
    
    # ==================== TOPIC VISUALIZATIONS ====================
    
    def plot_topic_distribution(self):
        """Bar chart of document counts per topic"""
        self.logger.info("Creating topic distribution chart...")
        
        try:
            topic_counts = self.df['topic_name'].value_counts().sort_index()
            
            fig, ax = plt.subplots(figsize=(12, 6), dpi=self.dpi)
            
            bars = ax.bar(range(len(topic_counts)), topic_counts.values, 
                         color=sns.color_palette("viridis", len(topic_counts)))
            
            ax.set_xticks(range(len(topic_counts)))
            ax.set_xticklabels(topic_counts.index, rotation=45, ha='right')
            ax.set_xlabel('Topic', fontsize=12, fontweight='bold')
            ax.set_ylabel('Number of Documents', fontsize=12, fontweight='bold')
            ax.set_title('Distribution of Documents Across Topics', 
                        fontsize=14, fontweight='bold', pad=15)
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{int(height):,}',
                       ha='center', va='bottom', fontsize=10)
            
            ax.grid(axis='y', alpha=0.3)
            plt.tight_layout()
            
            # Save
            output_path = os.path.join(self.charts_path, 'topic_distribution.png')
            plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
            plt.close()
            
            self.logger.info(f"Topic distribution saved: {output_path}")
            
        except Exception as e:
            self.logger.error(f"Error creating topic distribution: {e}", exc_info=True)
    
    def plot_topic_coherence_comparison(self):
        """Line plot comparing coherence scores"""
        self.logger.info("Creating coherence comparison chart...")
        
        try:
            coherence_path = os.path.join(
                self.models_path, 
                'evaluation', 
                'topic_coherence_comparison.csv'
            )
            coherence_df = pd.read_csv(coherence_path)
            
            fig, ax = plt.subplots(figsize=(10, 6), dpi=self.dpi)
            
            ax.plot(coherence_df['num_topics'], coherence_df['coherence_score'],
                   marker='o', linewidth=2, markersize=10, color='#2E86AB')
            
            # Highlight best model
            best_idx = coherence_df['coherence_score'].idxmax()
            best_topics = coherence_df.loc[best_idx, 'num_topics']
            best_score = coherence_df.loc[best_idx, 'coherence_score']
            
            ax.scatter([best_topics], [best_score], 
                      color='red', s=200, zorder=5, label='Best Model')
            
            ax.axhline(y=0.4, color='green', linestyle='--', 
                      alpha=0.5, label='Good Threshold (0.4)')
            
            ax.set_xlabel('Number of Topics', fontsize=12, fontweight='bold')
            ax.set_ylabel('Coherence Score (C_v)', fontsize=12, fontweight='bold')
            ax.set_title('Topic Model Coherence Comparison', 
                        fontsize=14, fontweight='bold', pad=15)
            ax.legend()
            ax.grid(alpha=0.3)
            
            plt.tight_layout()
            
            # Save
            output_path = os.path.join(self.charts_path, 'coherence_comparison.png')
            plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
            plt.close()
            
            self.logger.info(f"Coherence comparison saved: {output_path}")
            
        except Exception as e:
            self.logger.error(f"Error creating coherence comparison: {e}", exc_info=True)
    
    # ==================== SENTIMENT VISUALIZATIONS ====================
    
    def plot_sentiment_distribution(self):
        """Pie/bar chart of sentiment distribution"""
        self.logger.info("Creating sentiment distribution chart...")
        
        try:
            sentiment_counts = self.df['sentiment_class'].value_counts()
            
            # Create figure with two subplots
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), dpi=self.dpi)
            
            # Pie chart
            colors = {'positive': '#2E7D32', 'neutral': '#FBC02D', 'negative': '#C62828'}
            pie_colors = [colors[cat] for cat in sentiment_counts.index]
            
            wedges, texts, autotexts = ax1.pie(
                sentiment_counts.values,
                labels=sentiment_counts.index,
                autopct='%1.1f%%',
                startangle=90,
                colors=pie_colors,
                textprops={'fontsize': 11, 'fontweight': 'bold'}
            )
            
            ax1.set_title('Sentiment Distribution', 
                         fontsize=14, fontweight='bold', pad=15)
            
            # Bar chart
            bars = ax2.bar(sentiment_counts.index, sentiment_counts.values, 
                          color=pie_colors)
            
            ax2.set_xlabel('Sentiment', fontsize=12, fontweight='bold')
            ax2.set_ylabel('Number of Documents', fontsize=12, fontweight='bold')
            ax2.set_title('Sentiment Counts', fontsize=14, fontweight='bold', pad=15)
            
            # Add value labels
            for bar in bars:
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height,
                        f'{int(height):,}',
                        ha='center', va='bottom', fontsize=10)
            
            ax2.grid(axis='y', alpha=0.3)
            
            plt.tight_layout()
            
            # Save
            output_path = os.path.join(self.charts_path, 'sentiment_distribution.png')
            plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
            plt.close()
            
            self.logger.info(f"Sentiment distribution saved: {output_path}")
            
        except Exception as e:
            self.logger.error(f"Error creating sentiment distribution: {e}", exc_info=True)
    
    def plot_sentiment_by_topic(self):
        """Grouped bar chart of sentiment by topic"""
        self.logger.info("Creating sentiment by topic chart...")
        
        try:
            # Create crosstab
            sentiment_topic = pd.crosstab(
                self.df['topic_name'], 
                self.df['sentiment_class'],
                normalize='index'
            ) * 100
            
            # Reorder columns
            if 'positive' in sentiment_topic.columns:
                col_order = ['positive', 'neutral', 'negative']
                col_order = [c for c in col_order if c in sentiment_topic.columns]
                sentiment_topic = sentiment_topic[col_order]
            
            fig, ax = plt.subplots(figsize=(12, 7), dpi=self.dpi)
            
            colors = {'positive': '#2E7D32', 'neutral': '#FBC02D', 'negative': '#C62828'}
            
            sentiment_topic.plot(kind='bar', ax=ax, 
                                color=[colors.get(c, 'gray') for c in sentiment_topic.columns],
                                width=0.8)
            
            ax.set_xlabel('Topic', fontsize=12, fontweight='bold')
            ax.set_ylabel('Percentage (%)', fontsize=12, fontweight='bold')
            ax.set_title('Sentiment Distribution by Topic', 
                        fontsize=14, fontweight='bold', pad=15)
            ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
            ax.legend(title='Sentiment', title_fontsize=11, fontsize=10)
            ax.grid(axis='y', alpha=0.3)
            
            plt.tight_layout()
            
            # Save
            output_path = os.path.join(self.charts_path, 'sentiment_by_topic.png')
            plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
            plt.close()
            
            self.logger.info(f"Sentiment by topic saved: {output_path}")
            
        except Exception as e:
            self.logger.error(f"Error creating sentiment by topic: {e}", exc_info=True)
    
    def plot_sentiment_compound_boxplots(self):
        """Box plots of compound scores by topic"""
        self.logger.info("Creating sentiment compound box plots...")
        
        try:
            fig, ax = plt.subplots(figsize=(12, 7), dpi=self.dpi)
            
            # Prepare data
            topic_order = sorted(self.df['topic_name'].unique())
            data_to_plot = [
                self.df[self.df['topic_name'] == topic]['compound'].values
                for topic in topic_order
            ]
            
            bp = ax.boxplot(data_to_plot, labels=topic_order, patch_artist=True,
                           showmeans=True, meanline=True)
            
            # Color boxes
            colors = sns.color_palette("viridis", len(topic_order))
            for patch, color in zip(bp['boxes'], colors):
                patch.set_facecolor(color)
                patch.set_alpha(0.7)
            
            ax.set_xlabel('Topic', fontsize=12, fontweight='bold')
            ax.set_ylabel('Compound Sentiment Score', fontsize=12, fontweight='bold')
            ax.set_title('Sentiment Distribution by Topic (Box Plots)', 
                        fontsize=14, fontweight='bold', pad=15)
            ax.set_xticklabels(topic_order, rotation=45, ha='right')
            
            # Add reference line at 0
            ax.axhline(y=0, color='red', linestyle='--', alpha=0.5, label='Neutral (0)')
            ax.legend()
            ax.grid(axis='y', alpha=0.3)
            
            plt.tight_layout()
            
            # Save
            output_path = os.path.join(self.charts_path, 'sentiment_boxplots.png')
            plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
            plt.close()
            
            self.logger.info(f"Sentiment box plots saved: {output_path}")
            
        except Exception as e:
            self.logger.error(f"Error creating box plots: {e}", exc_info=True)
    
    def plot_sentiment_heatmap(self):
        """Heatmap of sentiment by topic"""
        self.logger.info("Creating sentiment heatmap...")
        
        try:
            # Create crosstab with counts
            sentiment_topic = pd.crosstab(
                self.df['topic_name'],
                self.df['sentiment_class']
            )
            
            # Reorder columns
            if 'positive' in sentiment_topic.columns:
                col_order = ['positive', 'neutral', 'negative']
                col_order = [c for c in col_order if c in sentiment_topic.columns]
                sentiment_topic = sentiment_topic[col_order]
            
            fig, ax = plt.subplots(figsize=(10, 8), dpi=self.dpi)
            
            sns.heatmap(sentiment_topic, annot=True, fmt='d', cmap='YlGnBu',
                       cbar_kws={'label': 'Document Count'},
                       linewidths=0.5, ax=ax)
            
            ax.set_xlabel('Sentiment Class', fontsize=12, fontweight='bold')
            ax.set_ylabel('Topic', fontsize=12, fontweight='bold')
            ax.set_title('Sentiment-Topic Heatmap', 
                        fontsize=14, fontweight='bold', pad=15)
            ax.set_yticklabels(ax.get_yticklabels(), rotation=0)
            
            plt.tight_layout()
            
            # Save
            output_path = os.path.join(self.charts_path, 'sentiment_heatmap.png')
            plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
            plt.close()
            
            self.logger.info(f"Sentiment heatmap saved: {output_path}")
            
        except Exception as e:
            self.logger.error(f"Error creating heatmap: {e}", exc_info=True)
    
    # ==================== TEMPORAL VISUALIZATIONS ====================
    
    def plot_temporal_sentiment(self):
        """Line plot of sentiment over time"""
        self.logger.info("Creating temporal sentiment chart...")
        
        try:
            # Load temporal data
            temporal_path = os.path.join(self.processed_path, 'sentiment_temporal.csv')
            temporal_df = pd.read_csv(temporal_path)
            
            fig, ax = plt.subplots(figsize=(14, 6), dpi=self.dpi)
            
            # Plot sentiment
            ax.plot(range(len(temporal_df)), temporal_df['compound_mean'],
                   marker='o', linewidth=2, markersize=6, color='#2E86AB',
                   label='Mean Sentiment')
            
            # Add confidence interval
            ax.fill_between(
                range(len(temporal_df)),
                temporal_df['compound_mean'] - temporal_df['compound_std'],
                temporal_df['compound_mean'] + temporal_df['compound_std'],
                alpha=0.2, color='#2E86AB', label='±1 Std Dev'
            )
            
            # Add reference line
            ax.axhline(y=0, color='red', linestyle='--', alpha=0.5, label='Neutral')
            
            ax.set_xlabel('Time Period', fontsize=12, fontweight='bold')
            ax.set_ylabel('Mean Compound Sentiment', fontsize=12, fontweight='bold')
            ax.set_title('Sentiment Trends Over Time', 
                        fontsize=14, fontweight='bold', pad=15)
            
            # Set x-axis labels (every 6 months)
            step = max(1, len(temporal_df) // 12)
            ax.set_xticks(range(0, len(temporal_df), step))
            ax.set_xticklabels(temporal_df['year_month'][::step], rotation=45, ha='right')
            
            ax.legend()
            ax.grid(alpha=0.3)
            
            plt.tight_layout()
            
            # Save
            output_path = os.path.join(self.charts_path, 'temporal_sentiment.png')
            plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
            plt.close()
            
            self.logger.info(f"Temporal sentiment saved: {output_path}")
            
        except Exception as e:
            self.logger.error(f"Error creating temporal sentiment: {e}", exc_info=True)
    
    def plot_posts_over_time(self):
        """Line plot of posting activity over time"""
        self.logger.info("Creating posting activity chart...")
        
        try:
            # Group by month
            self.df['year_month'] = self.df['created_utc'].dt.to_period('M')
            posts_over_time = self.df.groupby('year_month').size()
            
            fig, ax = plt.subplots(figsize=(14, 6), dpi=self.dpi)
            
            ax.plot(range(len(posts_over_time)), posts_over_time.values,
                   linewidth=2, color='#E63946')
            ax.fill_between(range(len(posts_over_time)), posts_over_time.values,
                           alpha=0.3, color='#E63946')
            
            ax.set_xlabel('Time Period', fontsize=12, fontweight='bold')
            ax.set_ylabel('Number of Posts', fontsize=12, fontweight='bold')
            ax.set_title('Posting Activity Over Time', 
                        fontsize=14, fontweight='bold', pad=15)
            
            # Set x-axis labels
            step = max(1, len(posts_over_time) // 12)
            ax.set_xticks(range(0, len(posts_over_time), step))
            ax.set_xticklabels([str(x) for x in posts_over_time.index[::step]], 
                              rotation=45, ha='right')
            
            ax.grid(alpha=0.3)
            
            plt.tight_layout()
            
            # Save
            output_path = os.path.join(self.charts_path, 'posts_over_time.png')
            plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
            plt.close()
            
            self.logger.info(f"Posting activity saved: {output_path}")
            
        except Exception as e:
            self.logger.error(f"Error creating posting activity: {e}", exc_info=True)
    
    # ==================== INTEGRATION VISUALIZATIONS ====================
    
    def plot_topic_sentiment_summary(self):
        """Combined summary chart"""
        self.logger.info("Creating topic-sentiment summary...")
        
        try:
            # Calculate mean sentiment per topic
            topic_sentiment = self.df.groupby('topic_name').agg({
                'compound': 'mean',
                'doc_id': 'count'
            }).reset_index()
            topic_sentiment.columns = ['topic_name', 'mean_sentiment', 'doc_count']
            topic_sentiment = topic_sentiment.sort_values('mean_sentiment', ascending=True)
            
            fig, ax = plt.subplots(figsize=(12, 7), dpi=self.dpi)
            
            # Create bars
            colors = ['#C62828' if x < 0 else '#2E7D32' for x in topic_sentiment['mean_sentiment']]
            bars = ax.barh(topic_sentiment['topic_name'], topic_sentiment['mean_sentiment'],
                          color=colors, alpha=0.7)
            
            # Add reference line
            ax.axvline(x=0, color='black', linestyle='-', linewidth=1)
            
            # Add value labels
            for i, (idx, row) in enumerate(topic_sentiment.iterrows()):
                ax.text(row['mean_sentiment'], i,
                       f" {row['mean_sentiment']:.3f} ({row['doc_count']:,} docs)",
                       va='center', fontsize=9)
            
            ax.set_xlabel('Mean Sentiment (Compound Score)', fontsize=12, fontweight='bold')
            ax.set_ylabel('Topic', fontsize=12, fontweight='bold')
            ax.set_title('Topic Sentiment Summary', 
                        fontsize=14, fontweight='bold', pad=15)
            ax.grid(axis='x', alpha=0.3)
            
            plt.tight_layout()
            
            # Save
            output_path = os.path.join(self.charts_path, 'topic_sentiment_summary.png')
            plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
            plt.close()
            
            self.logger.info(f"Topic-sentiment summary saved: {output_path}")
            
        except Exception as e:
            self.logger.error(f"Error creating summary: {e}", exc_info=True)
    
    def copy_to_report_figures(self):
        """Copy best figures to report folder"""
        self.logger.info("Copying figures to report folder...")
        
        import shutil
        
        # Key figures for report
        key_figures = [
            ('charts', 'topic_distribution.png'),
            ('charts', 'coherence_comparison.png'),
            ('charts', 'sentiment_distribution.png'),
            ('charts', 'sentiment_by_topic.png'),
            ('charts', 'sentiment_boxplots.png'),
            ('charts', 'topic_sentiment_summary.png'),
            ('charts', 'temporal_sentiment.png'),
            ('wordclouds', 'overall_wordcloud.png'),
        ]
        
        for folder, filename in key_figures:
            src = os.path.join(self.viz_path, folder, filename)
            dst = os.path.join(self.report_path, filename)
            
            try:
                if os.path.exists(src):
                    shutil.copy2(src, dst)
                    self.logger.info(f"Copied {filename} to report folder")
            except Exception as e:
                self.logger.error(f"Error copying {filename}: {e}")
    
    def generate_all_visualizations(self):
        """Main function to generate all visualizations"""
        self.logger.info("="*60)
        self.logger.info("Starting visualization generation")
        self.logger.info("="*60)
        
        # Word clouds
        self.logger.info("\n=== Word Clouds ===")
        self.create_overall_wordcloud()
        self.create_topic_wordclouds()
        
        # Topic visualizations
        self.logger.info("\n=== Topic Visualizations ===")
        self.plot_topic_distribution()
        self.plot_topic_coherence_comparison()
        
        # Sentiment visualizations
        self.logger.info("\n=== Sentiment Visualizations ===")
        self.plot_sentiment_distribution()
        self.plot_sentiment_by_topic()
        self.plot_sentiment_compound_boxplots()
        self.plot_sentiment_heatmap()
        
        # Temporal visualizations
        self.logger.info("\n=== Temporal Visualizations ===")
        self.plot_temporal_sentiment()
        self.plot_posts_over_time()
        
        # Integration visualizations
        self.logger.info("\n=== Integration Visualizations ===")
        self.plot_topic_sentiment_summary()
        
        # Copy to report folder
        self.logger.info("\n=== Finalizing ===")
        self.copy_to_report_figures()
        
        self.logger.info("\n" + "="*60)
        self.logger.info("All visualizations generated successfully!")
        self.logger.info("="*60)


def main():
    """Main execution function"""
    print("\n" + "="*60)
    print("MODULE 7: COMPREHENSIVE VISUALIZATION")
    print("="*60 + "\n")
    
    # Initialize
    visualizer = Visualizer()
    
    # Load data
    print("Step 1: Loading data...")
    if not visualizer.load_data():
        print("ERROR: Failed to load data")
        return
    
    # Generate all visualizations
    print("\nStep 2: Generating all visualizations...")
    print("This may take a minute...\n")
    
    visualizer.generate_all_visualizations()
    
    # Summary
    print("\n" + "="*60)
    print("VISUALIZATION GENERATION COMPLETE!")
    print("="*60)
    
    print(f"\nVisualizations created:")
    print(f"  - Word clouds: {visualizer.wordclouds_path}")
    print(f"  - Charts: {visualizer.charts_path}")
    print(f"  - Report figures: {visualizer.report_path}")
    
    print("\n✓ Module 7: Visualization - COMPLETE\n")


if __name__ == "__main__":
    main()
