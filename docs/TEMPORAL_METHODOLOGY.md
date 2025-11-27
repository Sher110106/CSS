# Temporal Trend Derivation Methodology

**Generated:** 2025-11-11T16:10:59.235578

## Overview

This document explains how temporal trends were derived in the Semaglutide Reddit Analysis project.

## 1. Data Source

### Reddit Collection
- **Subreddits:** r/Ozempic, r/Semaglutide, r/WeightLossAdvice, r/diabetes_t2
- **Collection Period:** 2019-03-20 16:13:21 to 2025-10-27 21:05:08
- **Total Documents:** 23,405
  - Posts: 1,221
  - Comments: 22,184

### Key Data Fields Used for Temporal Analysis
- created_utc (timestamp)
- subreddit
- doc_type (post/comment)
- compound (sentiment score)
- dominant_topic
- sentiment_class

## 2. Time Segmentation Method

### Primary Method: Monthly bins (year-month periods)

**Implementation:**
```python
df['year_month'] = df['created_utc'].dt.to_period('M')
```

**Rationale:** Monthly aggregation provides sufficient granularity while smoothing out daily noise

- **Total Months Analyzed:** 70
- **Date Range:** 2019-03 to 2025-10

### Alternative Segmentations
- **Yearly:** For high-level trend analysis
- **Quarterly:** For seasonal pattern analysis
- **Pandemic Periods:**
  - Pre-Pandemic: Before 2020-03-01 00:00:00
  - Post-Pandemic: After 2020-03-01 00:00:00
  - Rationale: March 2020 marks WHO pandemic declaration

## 3. Processing Pipeline

### Step 1: Timestamp Parsing
Convert Unix timestamps to pandas datetime objects

- **Function:** `pd.to_datetime()`
- **Input:** created_utc column from raw data
- **Output:** Datetime objects with timezone awareness

### Step 2: Temporal Feature Engineering
Extract temporal features for aggregation

**Features Created:**
- year_month: Monthly period
- year: Calendar year
- month: Month number (1-12)
- pandemic_period: Pre/Post pandemic classification

### Step 3: Aggregation
Group data by temporal bins and calculate statistics

**Aggregation Functions:**
- **posting_activity:** count() - number of posts/comments per period
- **sentiment_mean:** mean() of compound scores
- **sentiment_std:** std() of compound scores
- **topic_distribution:** crosstab() or value_counts() normalized

**Example Code:**
```python
df.groupby('year_month').agg({'compound': ['mean', 'std'], 'doc_id': 'count'})
```

### Step 4: Multi-dimensional Analysis
Cross-tabulate temporal data with other dimensions

**Dimensions Analyzed:**
- Subreddit: Temporal trends per community
- Topic: Topic prevalence over time
- Sentiment: Sentiment evolution over time
- Pandemic Period: Before/after comparison

### Step 5: Visualization
Generate temporal plots with appropriate time axes

**Plot Types:**
- Line plots: Continuous trends over time
- Bar plots: Discrete period comparisons
- Stacked area: Cumulative distributions over time
- Scatter plots: Individual data points with temporal coloring

**X-Axis Handling:** Sequential indices with period labels for readability

## 4. Specific Temporal Analyses

### 4.1 Posting Activity Trends
Track volume of posts/comments over time

- **Calculation:** Count of documents per month

**Insights:**
- Identify growth patterns
- Detect activity spikes
- Compare subreddit activity levels

### 4.2 Sentiment Trends
Track sentiment evolution over time

- **Calculation:** Mean and standard deviation of compound scores per month

**Metrics:**
- compound_mean: Average sentiment
- compound_std: Sentiment variability
- sentiment_class distribution: % positive/neutral/negative

**Insights:**
- Detect sentiment shifts
- Identify stable vs volatile periods
- Compare sentiment across communities

### 4.3 Topic Evolution
Track topic prevalence over time

- **Calculation:** Topic distribution (%) per month

**Insights:**
- Identify emerging topics
- Track declining interests
- Detect topic shifts around events

### 4.4 Pandemic Comparison Analysis
Compare metrics before and after pandemic

- **Cutoff Date:** 2020-03-01 00:00:00

**Metrics Compared:**
- Total posting volume
- Average monthly activity
- Mean sentiment scores
- Topic distribution changes
- Growth rate calculations

**Example Calculation:**
```python
growth_rate = ((post_rate - pre_rate) / pre_rate) * 100
```

## 5. Output Files

The temporal analysis pipeline generates the following CSV files:

### sentiment_temporal.csv
Monthly sentiment aggregates

**Columns:** year_month, compound_mean, compound_std, doc_count

**Rows:** 79

### sentiment_topic_temporal.csv
Monthly sentiment by topic

**Columns:** year_month, topic_name, compound_mean, doc_count

**Rows:** 296

### subreddit_sentiment_temporal.csv
Monthly sentiment by subreddit

**Columns:** year_month, subreddit, sentiment_mean, sentiment_std, count

### pandemic_posting_behavior.csv
Posting statistics by pandemic period

**Columns:** period, total_posts, start_date, end_date, months, posts_per_month

### pandemic_sentiment_stats.csv
Sentiment statistics by pandemic period

**Columns:** period, compound_mean, compound_std, compound_median, pos_mean, neu_mean, neg_mean, count

### pandemic_topic_distribution.csv
Topic distribution by pandemic period

**Columns:** period, Alternative Medications, Weight Loss Experiences, Insurance & Access, Diet & Side Effects, Community Support


## 6. Data Quality Considerations

- **Handling Missing Months:** Months with no data are preserved in visualizations but marked accordingly
- **Outlier Detection:** Standard deviation bands used to identify unusual periods
- **Smoothing:** No smoothing applied to preserve authentic patterns
- **Minimum Sample Size:** Periods with <10 documents flagged for interpretation caution

## 7. Reproducibility

- **Random Seed:** Not applicable for temporal analysis (deterministic)
- **Dependencies:** pandas, numpy, matplotlib, seaborn
- **Python Version:** 3.8+
- **Execution Time:** ~2-5 minutes for full temporal analysis pipeline

---

*This methodology document ensures transparency and reproducibility of all temporal trend analyses in the Semaglutide Reddit Analysis project.*
