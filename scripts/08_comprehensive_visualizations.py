#!/usr/bin/env python3
"""
Module 8: Comprehensive Visualizations for Research Analysis
Creates publication-ready visualizations for all key findings.
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.labelsize'] = 12

# Output directory
VIZ_DIR = 'visualizations/research_analysis'
os.makedirs(VIZ_DIR, exist_ok=True)

print("="*80)
print("GENERATING COMPREHENSIVE VISUALIZATIONS")
print("="*80)

# Load data
print("\nLoading data...")
df = pd.read_csv('data/processed/documents_with_sentiment.csv')
df['created_datetime'] = pd.to_datetime(df['created_utc'])
df['year'] = df['created_datetime'].dt.year
df['year_month'] = df['created_datetime'].dt.to_period('M')

# Filter posts for engagement analysis
posts_df = df[df['doc_type'] == 'post'].copy()

print(f"Loaded {len(df)} documents ({len(posts_df)} posts)")

# ============================================================================
# 1. TEMPORAL EVOLUTION - Volume Growth
# ============================================================================
print("\n1. Creating temporal volume plot...")

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))

# Plot 1: Document volume by year
year_counts = df.groupby('year').size()
colors = plt.cm.viridis(np.linspace(0.3, 0.9, len(year_counts)))

bars1 = ax1.bar(year_counts.index, year_counts.values, color=colors, edgecolor='black', linewidth=1.5)
ax1.set_xlabel('Year', fontsize=12, fontweight='bold')
ax1.set_ylabel('Number of Documents', fontsize=12, fontweight='bold')
ax1.set_title('Semaglutide Reddit Discussion Volume (2019-2025)\n903x Growth Over 6 Years', 
              fontsize=14, fontweight='bold', pad=20)
ax1.grid(axis='y', alpha=0.3)

# Add value labels on bars
for bar in bars1:
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height,
            f'{int(height):,}',
            ha='center', va='bottom', fontsize=10, fontweight='bold')

# Add annotation for dramatic growth
ax1.annotate('903x increase!', 
            xy=(2025, 12655), xytext=(2023, 14000),
            arrowprops=dict(arrowstyle='->', lw=2, color='red'),
            fontsize=11, fontweight='bold', color='red',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.7))

# Plot 2: Posts vs Comments breakdown
post_counts = df[df['doc_type'] == 'post'].groupby('year').size()
comment_counts = df[df['doc_type'] == 'comment'].groupby('year').size()

x = np.arange(len(year_counts))
width = 0.35

bars2 = ax2.bar(x - width/2, post_counts, width, label='Posts', color='steelblue', edgecolor='black')
bars3 = ax2.bar(x + width/2, comment_counts, width, label='Comments', color='coral', edgecolor='black')

ax2.set_xlabel('Year', fontsize=12, fontweight='bold')
ax2.set_ylabel('Count', fontsize=12, fontweight='bold')
ax2.set_title('Posts vs Comments Distribution Over Time', fontsize=13, fontweight='bold', pad=15)
ax2.set_xticks(x)
ax2.set_xticklabels(year_counts.index)
ax2.legend(fontsize=11, loc='upper left')
ax2.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig(f'{VIZ_DIR}/01_temporal_volume.png', dpi=300, bbox_inches='tight')
print(f"   Saved: {VIZ_DIR}/01_temporal_volume.png")
plt.close()

# ============================================================================
# 2. SENTIMENT OVER TIME - The 2023 Mystery
# ============================================================================
print("\n2. Creating sentiment over time plot...")

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))

# Plot 1: Mean sentiment by year with trend line
sentiment_by_year = df.groupby('year')['compound'].mean()

ax1.plot(sentiment_by_year.index, sentiment_by_year.values, 
         marker='o', markersize=10, linewidth=3, color='darkblue', label='Mean Sentiment')
ax1.fill_between(sentiment_by_year.index, sentiment_by_year.values, 
                  alpha=0.3, color='skyblue')

# Highlight 2023 drop
ax1.axvspan(2022.5, 2023.5, alpha=0.2, color='red', label='2023 Sentiment Drop')
ax1.annotate('30% drop\n(Supply shortage?)', 
            xy=(2023, sentiment_by_year[2023]), 
            xytext=(2021.5, 0.25),
            arrowprops=dict(arrowstyle='->', lw=2, color='red'),
            fontsize=11, fontweight='bold', color='red',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.7))

ax1.set_xlabel('Year', fontsize=12, fontweight='bold')
ax1.set_ylabel('Mean Compound Sentiment', fontsize=12, fontweight='bold')
ax1.set_title('Sentiment Evolution: The 2023 Mystery\nDramatic Drop Followed by Recovery', 
              fontsize=14, fontweight='bold', pad=20)
ax1.legend(fontsize=11, loc='upper right')
ax1.grid(True, alpha=0.3)
ax1.set_ylim(0.2, 0.45)

# Plot 2: Sentiment distribution by year (stacked bar)
sentiment_dist = df.groupby(['year', 'sentiment_class']).size().unstack(fill_value=0)
sentiment_pct = sentiment_dist.div(sentiment_dist.sum(axis=1), axis=0) * 100

sentiment_pct.plot(kind='bar', stacked=True, ax=ax2, 
                   color=['#d62728', '#7f7f7f', '#2ca02c'],
                   edgecolor='black', linewidth=1)

ax2.set_xlabel('Year', fontsize=12, fontweight='bold')
ax2.set_ylabel('Percentage (%)', fontsize=12, fontweight='bold')
ax2.set_title('Sentiment Distribution Over Time (Stacked %)', fontsize=13, fontweight='bold', pad=15)
ax2.legend(title='Sentiment', fontsize=10, title_fontsize=11)
ax2.set_xticklabels(ax2.get_xticklabels(), rotation=0)
ax2.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig(f'{VIZ_DIR}/02_sentiment_over_time.png', dpi=300, bbox_inches='tight')
print(f"   Saved: {VIZ_DIR}/02_sentiment_over_time.png")
plt.close()

# ============================================================================
# 3. THE ENGAGEMENT PARADOX
# ============================================================================
print("\n3. Creating engagement paradox visualization...")

fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))

# Plot 1: Posts vs Engagement (dual axis)
post_counts_by_year = posts_df.groupby('year').size()
mean_score_by_year = posts_df.groupby('year')['score'].mean()
median_score_by_year = posts_df.groupby('year')['score'].median()

ax1_twin = ax1.twinx()
bars = ax1.bar(post_counts_by_year.index, post_counts_by_year.values, 
               alpha=0.6, color='steelblue', label='Number of Posts', edgecolor='black')
line1 = ax1_twin.plot(mean_score_by_year.index, mean_score_by_year.values, 
                      marker='o', markersize=8, linewidth=3, color='red', label='Mean Score')

ax1.set_xlabel('Year', fontsize=11, fontweight='bold')
ax1.set_ylabel('Number of Posts', fontsize=11, fontweight='bold', color='steelblue')
ax1_twin.set_ylabel('Mean Engagement Score', fontsize=11, fontweight='bold', color='red')
ax1.set_title('The Engagement Paradox:\nMore Posts, Lower Engagement', 
              fontsize=13, fontweight='bold', pad=15)
ax1.tick_params(axis='y', labelcolor='steelblue')
ax1_twin.tick_params(axis='y', labelcolor='red')
ax1.legend(loc='upper left', fontsize=9)
ax1_twin.legend(loc='upper right', fontsize=9)

# Plot 2: Median score collapse
ax2.plot(median_score_by_year.index, median_score_by_year.values, 
         marker='D', markersize=10, linewidth=3, color='darkred')
ax2.fill_between(median_score_by_year.index, median_score_by_year.values, 
                  alpha=0.3, color='lightcoral')

# Add dramatic annotation
ax2.annotate('99.3% collapse!', 
            xy=(2025, median_score_by_year[2025]), 
            xytext=(2023, 400),
            arrowprops=dict(arrowstyle='->', lw=2, color='darkred'),
            fontsize=11, fontweight='bold', color='darkred',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.7))

ax2.set_xlabel('Year', fontsize=11, fontweight='bold')
ax2.set_ylabel('Median Score', fontsize=11, fontweight='bold')
ax2.set_title('Median Score Collapse (2020: 888 → 2025: 6)', 
              fontsize=13, fontweight='bold', pad=15)
ax2.grid(True, alpha=0.3)

# Plot 3: Distribution of scores over time (boxplot)
years_for_box = [2020, 2021, 2022, 2023, 2024, 2025]
data_for_box = [posts_df[posts_df['year'] == y]['score'].values for y in years_for_box]

bp = ax3.boxplot(data_for_box, labels=years_for_box, patch_artist=True,
                 medianprops=dict(color='red', linewidth=2),
                 boxprops=dict(facecolor='lightblue', edgecolor='black'),
                 whiskerprops=dict(color='black'),
                 capprops=dict(color='black'))

ax3.set_xlabel('Year', fontsize=11, fontweight='bold')
ax3.set_ylabel('Score', fontsize=11, fontweight='bold')
ax3.set_title('Score Distribution by Year\n(Box Plot Shows Spread)', 
              fontsize=13, fontweight='bold', pad=15)
ax3.set_yscale('log')
ax3.grid(True, alpha=0.3, axis='y')

# Plot 4: Engagement rate over time (using score only as proxy)
# Note: num_comments not available in processed data, using score as engagement metric
engagement_by_year = posts_df.groupby('year')['score'].mean()

ax4.bar(engagement_by_year.index, engagement_by_year.values, 
        color=plt.cm.RdYlGn(np.linspace(0.8, 0.2, len(engagement_by_year))),
        edgecolor='black', linewidth=1.5)

ax4.set_xlabel('Year', fontsize=11, fontweight='bold')
ax4.set_ylabel('Mean Score', fontsize=11, fontweight='bold')
ax4.set_title('Total Engagement Score Trend', fontsize=13, fontweight='bold', pad=15)
ax4.grid(axis='y', alpha=0.3)

# Add values on bars
for i, (year, val) in enumerate(engagement_by_year.items()):
    ax4.text(year, val, f'{int(val)}', ha='center', va='bottom', 
            fontsize=9, fontweight='bold')

plt.tight_layout()
plt.savefig(f'{VIZ_DIR}/03_engagement_paradox.png', dpi=300, bbox_inches='tight')
print(f"   Saved: {VIZ_DIR}/03_engagement_paradox.png")
plt.close()

# ============================================================================
# 4. TOPIC ANALYSIS
# ============================================================================
print("\n4. Creating topic analysis visualizations...")

fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))

# Plot 1: Topic distribution (pie chart)
topic_counts = df['dominant_topic'].value_counts().sort_index()
topic_labels = ['Topic 0:\nWeight Loss &\nExperiences', 
                'Topic 1:\nDiet &\nNutrition',
                'Topic 2:\nCommunity\nSupport']
colors_pie = ['#ff9999', '#66b3ff', '#99ff99']

wedges, texts, autotexts = ax1.pie(topic_counts.values, 
                                     labels=topic_labels,
                                     colors=colors_pie,
                                     autopct='%1.1f%%',
                                     startangle=90,
                                     textprops={'fontsize': 11, 'fontweight': 'bold'},
                                     explode=(0.05, 0.05, 0.1))

for autotext in autotexts:
    autotext.set_color('black')
    autotext.set_fontsize(12)
    autotext.set_fontweight('bold')

ax1.set_title('Topic Distribution\n(3 Topics, Coherence: 0.682)', 
              fontsize=13, fontweight='bold', pad=15)

# Plot 2: Sentiment by topic
sentiment_by_topic = df.groupby('dominant_topic')['compound'].mean()
colors_sent = ['#ff6b6b', '#4ecdc4', '#95e1d3']

bars = ax2.bar(range(len(sentiment_by_topic)), sentiment_by_topic.values,
               color=colors_sent, edgecolor='black', linewidth=2)

ax2.set_xlabel('Topic', fontsize=11, fontweight='bold')
ax2.set_ylabel('Mean Compound Sentiment', fontsize=11, fontweight='bold')
ax2.set_title('Sentiment by Topic\n(Topic 2 Most Positive)', 
              fontsize=13, fontweight='bold', pad=15)
ax2.set_xticks(range(len(sentiment_by_topic)))
ax2.set_xticklabels(['Topic 0\nWeight Loss', 'Topic 1\nDiet', 'Topic 2\nSupport'])
ax2.axhline(y=df['compound'].mean(), color='red', linestyle='--', 
            linewidth=2, label='Overall Mean')
ax2.legend(fontsize=10)
ax2.grid(axis='y', alpha=0.3)

# Add value labels
for i, bar in enumerate(bars):
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height,
            f'{height:.3f}',
            ha='center', va='bottom', fontsize=11, fontweight='bold')

# Plot 3: Topic evolution over time (stacked area)
topic_by_year = df.groupby(['year', 'dominant_topic']).size().unstack(fill_value=0)

ax3.stackplot(topic_by_year.index, 
              topic_by_year[0], topic_by_year[1], topic_by_year[2],
              labels=['Topic 0: Weight Loss', 'Topic 1: Diet', 'Topic 2: Support'],
              colors=['#ff9999', '#66b3ff', '#99ff99'],
              alpha=0.8)

ax3.set_xlabel('Year', fontsize=11, fontweight='bold')
ax3.set_ylabel('Number of Documents', fontsize=11, fontweight='bold')
ax3.set_title('Topic Evolution Over Time\n(Stacked Area)', 
              fontsize=13, fontweight='bold', pad=15)
ax3.legend(loc='upper left', fontsize=10)
ax3.grid(True, alpha=0.3)

# Plot 4: Topic proportion over time
topic_pct_by_year = topic_by_year.div(topic_by_year.sum(axis=1), axis=0) * 100

topic_pct_by_year.plot(kind='bar', stacked=True, ax=ax4,
                        color=['#ff9999', '#66b3ff', '#99ff99'],
                        edgecolor='black', linewidth=1)

ax4.set_xlabel('Year', fontsize=11, fontweight='bold')
ax4.set_ylabel('Percentage (%)', fontsize=11, fontweight='bold')
ax4.set_title('Topic Proportion Over Time\n(Stacked %)', 
              fontsize=13, fontweight='bold', pad=15)
ax4.legend(title='Topic', fontsize=9, title_fontsize=10, loc='upper left')
ax4.set_xticklabels(ax4.get_xticklabels(), rotation=45, ha='right')
ax4.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig(f'{VIZ_DIR}/04_topic_analysis.png', dpi=300, bbox_inches='tight')
print(f"   Saved: {VIZ_DIR}/04_topic_analysis.png")
plt.close()

# ============================================================================
# 5. TOPIC × SENTIMENT HEATMAP
# ============================================================================
print("\n5. Creating topic-sentiment heatmap...")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# Heatmap 1: Topic × Sentiment Class
topic_sentiment_counts = df.groupby(['dominant_topic', 'sentiment_class']).size().unstack(fill_value=0)
topic_sentiment_pct = topic_sentiment_counts.div(topic_sentiment_counts.sum(axis=1), axis=0) * 100

sns.heatmap(topic_sentiment_pct, annot=True, fmt='.1f', cmap='RdYlGn', 
            cbar_kws={'label': 'Percentage (%)'}, ax=ax1,
            linewidths=2, linecolor='black',
            xticklabels=['Negative', 'Neutral', 'Positive'],
            yticklabels=['Topic 0: Weight Loss', 'Topic 1: Diet', 'Topic 2: Support'])

ax1.set_xlabel('Sentiment Class', fontsize=12, fontweight='bold')
ax1.set_ylabel('Topic', fontsize=12, fontweight='bold')
ax1.set_title('Topic × Sentiment Distribution\n(% within each topic)', 
              fontsize=13, fontweight='bold', pad=15)

# Heatmap 2: Year × Topic sentiment
year_topic_sentiment = df.groupby(['year', 'dominant_topic'])['compound'].mean().unstack()

sns.heatmap(year_topic_sentiment.T, annot=True, fmt='.3f', cmap='coolwarm', 
            cbar_kws={'label': 'Mean Sentiment'}, ax=ax2,
            linewidths=2, linecolor='black',
            yticklabels=['Topic 0: Weight Loss', 'Topic 1: Diet', 'Topic 2: Support'])

ax2.set_xlabel('Year', fontsize=12, fontweight='bold')
ax2.set_ylabel('Topic', fontsize=12, fontweight='bold')
ax2.set_title('Sentiment by Topic Over Time\n(Heatmap)', 
              fontsize=13, fontweight='bold', pad=15)

plt.tight_layout()
plt.savefig(f'{VIZ_DIR}/05_topic_sentiment_heatmap.png', dpi=300, bbox_inches='tight')
print(f"   Saved: {VIZ_DIR}/05_topic_sentiment_heatmap.png")
plt.close()

# ============================================================================
# 6. COMPREHENSIVE DASHBOARD
# ============================================================================
print("\n6. Creating comprehensive dashboard...")

fig = plt.figure(figsize=(20, 12))
gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

# Row 1: Volume, Sentiment, Topics
ax1 = fig.add_subplot(gs[0, 0])
ax2 = fig.add_subplot(gs[0, 1])
ax3 = fig.add_subplot(gs[0, 2])

# Row 2: Engagement, Topic evolution, Sentiment by topic
ax4 = fig.add_subplot(gs[1, 0])
ax5 = fig.add_subplot(gs[1, 1])
ax6 = fig.add_subplot(gs[1, 2])

# Row 3: Heatmaps
ax7 = fig.add_subplot(gs[2, :2])
ax8 = fig.add_subplot(gs[2, 2])

# 1. Volume growth
year_counts.plot(kind='bar', ax=ax1, color=colors, edgecolor='black')
ax1.set_title('Volume Growth', fontweight='bold')
ax1.set_xlabel('Year')
ax1.set_ylabel('Documents')
ax1.tick_params(axis='x', rotation=0)

# 2. Sentiment trend
sentiment_by_year.plot(ax=ax2, marker='o', linewidth=2, color='darkblue')
ax2.fill_between(sentiment_by_year.index, sentiment_by_year.values, alpha=0.3)
ax2.set_title('Sentiment Trend', fontweight='bold')
ax2.set_xlabel('Year')
ax2.set_ylabel('Mean Sentiment')
ax2.axvspan(2022.5, 2023.5, alpha=0.2, color='red')

# 3. Topic distribution
ax3.pie(topic_counts.values, labels=['T0: Weight Loss\n(76.7%)', 'T1: Diet\n(20.7%)', 'T2: Support\n(2.7%)'],
        colors=colors_pie, autopct='', startangle=90, textprops={'fontsize': 9})
ax3.set_title('Topic Distribution', fontweight='bold')

# 4. Engagement paradox
ax4_twin = ax4.twinx()
ax4.bar(post_counts_by_year.index, post_counts_by_year.values, alpha=0.6, color='steelblue')
ax4_twin.plot(median_score_by_year.index, median_score_by_year.values, 
              marker='o', linewidth=2, color='red')
ax4.set_title('Engagement Paradox', fontweight='bold')
ax4.set_xlabel('Year')
ax4.set_ylabel('Posts', color='steelblue')
ax4_twin.set_ylabel('Median Score', color='red')
ax4.tick_params(axis='y', labelcolor='steelblue')
ax4_twin.tick_params(axis='y', labelcolor='red')

# 5. Topic evolution
topic_by_year.plot(kind='area', stacked=True, ax=ax5, 
                   color=['#ff9999', '#66b3ff', '#99ff99'], alpha=0.7)
ax5.set_title('Topic Evolution', fontweight='bold')
ax5.set_xlabel('Year')
ax5.set_ylabel('Documents')
ax5.legend(['T0', 'T1', 'T2'], fontsize=8, loc='upper left')

# 6. Sentiment by topic
sentiment_by_topic.plot(kind='barh', ax=ax6, color=colors_sent, edgecolor='black')
ax6.set_title('Sentiment by Topic', fontweight='bold')
ax6.set_xlabel('Mean Sentiment')
ax6.set_yticklabels(['T0: Weight', 'T1: Diet', 'T2: Support'])

# 7. Year-Topic-Sentiment heatmap
sns.heatmap(year_topic_sentiment.T, annot=True, fmt='.2f', cmap='coolwarm', 
            ax=ax7, cbar_kws={'label': 'Sentiment'},
            yticklabels=['T0: Weight', 'T1: Diet', 'T2: Support'])
ax7.set_title('Sentiment by Year & Topic', fontweight='bold')
ax7.set_xlabel('Year')

# 8. Key stats
stats_text = f"""
KEY STATISTICS
==============
Total Documents: {len(df):,}
Posts: {len(posts_df):,}
Comments: {len(df[df['doc_type']=='comment']):,}

Volume Growth: 903x
(2019→2025)

Best Topic Model: K=3
Coherence: 0.682

Overall Sentiment: 68.7% Positive

Engagement Drop: 99.3%
(Median: 888→6)

2023 Sentiment Drop: 30%
(Likely supply shortage)
"""

ax8.text(0.1, 0.5, stats_text, fontsize=10, family='monospace',
         verticalalignment='center', bbox=dict(boxstyle='round', 
         facecolor='wheat', alpha=0.5))
ax8.axis('off')

plt.suptitle('Semaglutide Reddit Analysis: Comprehensive Dashboard (2019-2025)', 
             fontsize=16, fontweight='bold', y=0.98)

plt.savefig(f'{VIZ_DIR}/06_comprehensive_dashboard.png', dpi=300, bbox_inches='tight')
print(f"   Saved: {VIZ_DIR}/06_comprehensive_dashboard.png")
plt.close()

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "="*80)
print("✓ VISUALIZATION GENERATION COMPLETE!")
print("="*80)
print(f"\nGenerated 6 comprehensive visualizations in: {VIZ_DIR}/")
print("\nFiles created:")
print("  1. 01_temporal_volume.png - Volume growth analysis")
print("  2. 02_sentiment_over_time.png - Sentiment evolution & 2023 mystery")
print("  3. 03_engagement_paradox.png - Engagement collapse analysis")
print("  4. 04_topic_analysis.png - Topic distribution & evolution")
print("  5. 05_topic_sentiment_heatmap.png - Topic-sentiment relationships")
print("  6. 06_comprehensive_dashboard.png - All-in-one dashboard")
print("\nAll visualizations are publication-ready (300 DPI)")
print("="*80)
