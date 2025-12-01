# Semaglutide Reddit Discourse Analysis

**Analysis Period**: March 2019 - October 2025 (6.6 years)  
**Dataset**: 23,405 Reddit documents  
**Status**: ✅ COMPLETE

---

## 📊 Project Overview

Comprehensive NLP analysis of Reddit discussions about semaglutide (Ozempic/Wegovy) using:
- **Data Collection**: BAScraper for enhanced temporal sampling
- **Topic Modeling**: LDA with coherence-based model selection (K=3 optimal)
- **Sentiment Analysis**: VADER temporal tracking
- **Research Questions**: 8 data-driven questions with findings

### Key Results
- **23,405 documents** analyzed from 6 major health subreddits
- **3 distinct topics** identified (coherence: 0.682)
- **68.7% positive sentiment** overall
- **903x growth** in discussion volume (2019→2025)
- **Engagement paradox** discovered: More posts, less engagement

---

## 🚀 Quick Start

### Prerequisites
- Python 3.13+
- Reddit API credentials (free from https://www.reddit.com/prefs/apps)
- 5GB+ disk space

### Installation

```bash
# Navigate to project
cd /Users/sher/project/sema/CSS

# Activate virtual environment
source venv/bin/activate

# Install dependencies (if needed)
pip install -r requirements.txt
```

### Reddit API Setup

1. Go to https://www.reddit.com/prefs/apps
2. Create app (type: script)
3. Copy client_id and client_secret
4. Create `.env` file:
```bash
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
REDDIT_USER_AGENT=semaglutide_research_v1.0
```

---

## 📁 Project Structure

```
CSS/
├── data/
│   ├── raw/                           # Original scraped data
│   │   ├── posts.csv                  # 1,402 posts
│   │   └── comments.csv               # 53,332 comments
│   ├── processed/                     # Cleaned data
│   │   ├── combined_processed.csv     # 23,405 documents
│   │   ├── documents_with_topics.csv  # With topic assignments
│   │   └── documents_with_sentiment.csv  # Final dataset
│   └── metadata/                      # Analysis reports (JSON)
├── models/
│   ├── lda/                          # Topic models
│   │   ├── lda_model_2_topics        # K=2 model
│   │   ├── lda_model_3_topics        # K=3 model (best)
│   │   ├── lda_model_4_topics        # K=4 model
│   │   ├── lda_model_5_topics        # K=5 model
│   │   └── lda_model_best            # Symlink to best
│   └── evaluation/
│       └── topic_coherence_comparison.csv
├── scripts/
│   ├── 01_bascraper_collection.py    # Data collection
│   ├── 02_data_preprocessing.py       # Text cleaning
│   ├── 03_exploratory_analysis.py     # EDA
│   ├── 04_enhanced_topic_modeling.py  # LDA with model selection
│   ├── 05_sentiment_analysis.py       # VADER sentiment
│   ├── 08_comprehensive_visualizations.py  # Plots
│   └── utils.py                       # Utility functions
├── visualizations/
│   ├── eda/                          # Exploratory plots
│   ├── wordclouds/                   # Topic word clouds
│   └── research_analysis/            # Research figures
├── logs/                             # Execution logs
├── RESEARCH_ANALYSIS_REPORT.md       # 📊 MAIN REPORT (15 pages)
├── FINAL_PROJECT_SUMMARY.md          # Executive summary
└── PROJECT_COMPLETION_SUMMARY.md     # Detailed completion status
```

---

## 🔬 Analysis Pipeline

### Step 1: Data Collection
```bash
python scripts/01_bascraper_collection.py
```
- **Tool**: BAScraper (enhanced temporal sampling)
- **Subreddits**: r/Ozempic, r/Semaglutide, r/WeightLossAdvice, r/diabetes_t2, r/diabetes, r/loseit
- **Output**: `data/raw/posts.csv`, `data/raw/comments.csv`

### Step 2: Preprocessing
```bash
python scripts/02_data_preprocessing.py
```
- **Tasks**: Tokenization, stopword removal, lemmatization, filtering (<10 tokens)
- **Output**: `data/processed/combined_processed.csv` (23,405 docs)

### Step 3: Exploratory Analysis
```bash
python scripts/03_exploratory_analysis.py
```
- **Tasks**: Temporal distribution, vocabulary analysis, word clouds
- **Output**: `visualizations/eda/`, `data/metadata/eda_report.json`

### Step 4: Topic Modeling
```bash
python scripts/04_enhanced_topic_modeling.py
```
- **Method**: LDA with coherence-based selection (tested K=2,3,4,5)
- **Best Model**: K=3 (coherence: 0.682)
- **Output**: `models/lda/lda_model_best`, `data/processed/documents_with_topics.csv`

### Step 5: Sentiment Analysis
```bash
python scripts/05_sentiment_analysis.py
```
- **Tool**: VADER (social media optimized)
- **Output**: `data/processed/documents_with_sentiment.csv`

### Step 6: Visualizations
```bash
python scripts/08_comprehensive_visualizations.py
```
- **Output**: 10 publication-ready figures in `visualizations/research_analysis/`

---

## 📈 Key Findings

### 1. Three Distinct Topics Identified

| Topic | Label | Distribution | Top Keywords |
|-------|-------|--------------|--------------|
| **0** | Weight Loss & Experiences | 76.7% | weight, lose, start, take, week, month, dose |
| **1** | Diet & Nutrition | 20.7% | eat, food, protein, calorie, feel, meal, water |
| **2** | Community Support | 2.7% | help, question, thank, doctor, advice, share |

**Model Selection**:
- K=2: Coherence 0.565
- K=3: Coherence 0.682 ← **BEST**
- K=4: Coherence 0.623
- K=5: Coherence 0.613

### 2. Overall Positive Sentiment (68.7%)

- **Positive**: 16,090 documents (68.7%)
- **Neutral**: 1,311 documents (5.6%)
- **Negative**: 6,004 documents (25.7%)

**Sentiment by Topic**:
- Topic 2 (Community Support): 0.370 (highest)
- Topic 1 (Diet): 0.342
- Topic 0 (Weight Loss): 0.320

### 3. Dramatic Growth Over Time

```
Year   | Documents | Growth vs 2019
-------|-----------|---------------
2019   |        14 |     1x (baseline)
2020   |       148 |    11x
2021   |       515 |    37x
2022   |     1,485 |   106x
2023   |     4,588 |   328x
2024   |     3,992 |   285x
2025   |    12,655 |   903x
```

### 4. The Engagement Paradox

**Discovery**: Volume increased 903x, but engagement collapsed 99%

```
Year   | Median Post Score | Mean Score
-------|-------------------|------------
2020   |             888   |      1,144
2021   |             240   |        509
2022   |              75   |        352
2023   |              16   |        180
2024   |              10   |        218
2025   |               6   |        317
```

**Hypothesis**: Content saturation + demographic shift + novelty depreciation

### 5. The 2023 Sentiment Mystery

- Sentiment **dropped 30%** from 2020 (0.39) to 2023 (0.27)
- **Likely causes**: Supply shortage, negative media, cost/access issues
- Recovery in 2024-2025 suggests stabilization

---

## 📊 Main Deliverable

### **RESEARCH_ANALYSIS_REPORT.md** (15 pages)

Comprehensive analysis including:

**Section 1: Research Questions**
- RQ1: How has discourse evolved 2019-2025?
- RQ2: Why does volume increase correlate with engagement decrease?
- RQ3: How does sentiment vary across topics?
- RQ4: How do users frame semaglutide experiences?
- RQ5: What caused the 2023 sentiment decline?
- RQ6-8: Secondary questions on engagement, subreddits, sampling

**Section 2: Methodology**
- Data collection procedures
- Preprocessing pipeline
- LDA model selection rationale
- VADER sentiment analysis
- Temporal analysis approach

**Section 3: Detailed Findings**
- Topic distribution and keywords
- Sentiment patterns (overall, by topic, by year)
- Engagement paradox analysis
- Temporal evolution insights
- Framing analysis

**Section 4: Implications**
- Healthcare communication insights
- Policy implications
- Platform dynamics understanding
- Patient experience documentation

**Section 5: Limitations**
- 2019 undersampling due to Reddit API behavior
- Platform-specific biases
- Self-selected population
- Causal inference limitations

**Section 6: Future Research**
- Causal inference methods
- Cross-platform comparison
- Real-time monitoring
- Engagement prediction modeling

---

## 📉 Available Visualizations

All figures in `visualizations/research_analysis/`:

1. **01_temporal_volume.png** - Document volume over time
2. **02_sentiment_over_time.png** - Sentiment trends (2019-2025)
3. **03_engagement_paradox.png** - 4-panel engagement analysis
4. **04_topic_distribution.png** - Topic prevalence pie chart
5. **05_topic_sentiment.png** - Sentiment by topic boxplots
6. **06_sentiment_distribution.png** - Overall sentiment histogram
7. **07_sentiment_by_class.png** - Positive/neutral/negative counts
8. **08_topic_sentiment_heatmap.png** - Topic × sentiment heatmap
9. **09_document_length.png** - Token count distribution
10. **10_subreddit_distribution.png** - Documents by subreddit

Word clouds in `visualizations/wordclouds/`:
- `overall_wordcloud.png` - All documents
- `topic_0_wordcloud.png` - Weight Loss
- `topic_1_wordcloud.png` - Diet & Nutrition
- `topic_2_wordcloud.png` - Community Support

---

## 🔍 Data Access

### Load Final Dataset
```python
import pandas as pd

# Load complete dataset with topics & sentiment
df = pd.read_csv('data/processed/documents_with_sentiment.csv')

# Columns:
# - doc_id, doc_type, author, score, created_utc
# - text, cleaned_text, tokens, token_count, subreddit
# - dominant_topic, topic_0, topic_1, topic_2
# - compound, pos, neu, neg, sentiment_class

# Filter by topic
topic_0 = df[df['dominant_topic'] == 0]

# Filter by sentiment
positive = df[df['sentiment_class'] == 'positive']

# Filter by year
df['year'] = pd.to_datetime(df['created_utc']).dt.year
df_2025 = df[df['year'] == 2025]
```

### Load Models
```python
from gensim.models import LdaMulticore
from gensim.corpora import Dictionary

# Load best LDA model
lda = LdaMulticore.load('models/lda/lda_model_best')

# Load dictionary
dictionary = Dictionary.load('models/lda/dictionary.dict')

# Get topics
for idx, topic in lda.print_topics(-1):
    print(f"Topic {idx}: {topic}")
```

---

## 📚 Technical Stack

- **Python**: 3.13
- **Data Collection**: PRAW, BAScraper
- **NLP**: spaCy (en_core_web_sm), NLTK
- **Topic Modeling**: Gensim (LdaMulticore)
- **Sentiment**: VADER (vaderSentiment)
- **Analysis**: pandas, numpy, scipy
- **Visualization**: matplotlib, seaborn, wordcloud

---

## ⚠️ Important Limitations

### 2019 Data Undersampling

Due to Reddit API behavior with relevance-based sorting:
- **Only 14 documents** collected from 2019 (vs 12,655 in 2025)
- API prioritizes recent, popular content even with `time_filter="all"`
- **Impact**: Pre-2020 temporal analysis is limited; focus on 2020-2025

### Sample Representativeness
- Data represents Reddit users discussing semaglutide (self-selected)
- May not represent all patients using semaglutide
- Skewed toward weight loss discussions vs diabetes management
- English-language posts only

### Platform Specifics
- Reddit community demographics may shift over time
- Moderation policies affect discussion content
- Upvote/downvote mechanics influence visibility

---

## 🎯 Research Contributions

1. **Methodological**:
   - Demonstrated importance of model selection (not assuming K)
   - Coherence-based selection yielded K=3 > K=5
   - Temporal sampling crucial for trend analysis

2. **Empirical**:
   - **Engagement paradox**: Novel finding about volume-engagement inverse relationship
   - **2023 sentiment drop**: Connected to real-world supply shortage
   - **Topic-sentiment relationship**: Community support highest sentiment but rarest

3. **Practical**:
   - Real-world evidence for healthcare providers
   - Social media monitoring for public health surveillance
   - Understanding online health community dynamics

---

## 📧 Citation

If using this analysis, please reference:

```
Semaglutide Reddit Discourse Analysis (2025)
Dataset: 23,405 Reddit documents (2019-2025)
Topics: 3 (LDA, coherence: 0.682)
Sentiment: VADER
GitHub: [Your repository]
```

---

## 📄 License

MIT License - Academic research use

---

## 🏁 Status

**Project**: ✅ COMPLETE  
**Last Updated**: December 1, 2025  
**Main Report**: `RESEARCH_ANALYSIS_REPORT.md`

---

**For Questions**: Refer to `RESEARCH_ANALYSIS_REPORT.md` for methodology details and `FINAL_PROJECT_SUMMARY.md` for executive summary.
