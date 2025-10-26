# Semaglutide Reddit Analysis Project

A comprehensive NLP research project analyzing patient experiences with semaglutide (Ozempic, Wegovy) on Reddit using topic modeling (LDA) and sentiment analysis (VADER).

## 📊 Project Overview

This project collects and analyzes Reddit posts and comments from communities discussing semaglutide, a medication used for diabetes and weight management. Using natural language processing techniques, we identify key topics and sentiment patterns in patient experiences.

### Key Results Achieved
- ✅ **19,204 documents** analyzed (posts + comments)
- ✅ **7 distinct topics** identified using LDA
- ✅ **5.8 years** of data (2020-2025)
- ✅ **72.1% coherence score** achieved
- ✅ **20+ visualizations** generated
- ✅ **Comprehensive statistical analysis** completed

### Research Objectives
- Collect and analyze Reddit discussions about semaglutide
- Identify main topics using Latent Dirichlet Allocation (LDA)
- Analyze sentiment patterns using VADER
- Generate publication-ready visualizations
- Provide real-world evidence for healthcare research

## 🏗️ Project Structure

```
semaglutide-reddit-analysis/
├── config/                      # Configuration files
│   ├── config.yaml             # Main configuration
│   └── config_loader.py        # Config loader utility
├── data/
│   ├── raw/                    # Raw scraped data
│   ├── processed/              # Cleaned and processed data
│   ├── anonymized/             # Final anonymized dataset
│   └── metadata/               # Reports and statistics
├── models/
│   ├── lda/                    # Trained LDA models
│   ├── evaluation/             # Model evaluation metrics
│   └── checkpoints/            # Model checkpoints
├── visualizations/
│   ├── wordclouds/            # Word cloud images
│   ├── charts/                # Statistical charts
│   ├── interactive/           # Interactive visualizations
│   ├── eda/                   # Exploratory analysis plots
│   └── report_figures/        # Publication-ready figures
├── scripts/                    # Analysis scripts
│   ├── 01_data_collection.py
│   ├── 02_data_preprocessing.py
│   ├── 03_exploratory_analysis.py
│   ├── 04_topic_modeling.py
│   ├── 05_sentiment_analysis.py
│   ├── 06_integration.py
│   ├── 07_visualization.py
│   ├── 08_report_generation.py
│   ├── 09_final_validation.py
│   ├── utils.py               # Utility functions
│   └── validate_setup.py      # Setup validation
├── notebooks/                  # Jupyter notebooks
├── logs/                      # Execution logs
├── report/                    # Research paper sections
└── venv/                      # Python virtual environment
```

## 🚀 Getting Started

### Prerequisites
- Python 3.13 or higher
- Reddit API credentials (free)
- 5GB+ free disk space

### Installation

1. **Clone/Navigate to project directory**
```bash
cd semaglutide-reddit-analysis
```

2. **Activate virtual environment**
```bash
source venv/bin/activate
```

3. **Verify installation**
```bash
python scripts/validate_setup.py
```

### Reddit API Setup

1. Go to https://www.reddit.com/prefs/apps
2. Click "Create App" or "Create Another App"
3. Select "script" as the app type
4. Fill in the form:
   - **name**: semaglutide-research
   - **description**: Academic research on patient experiences
   - **redirect uri**: http://localhost:8080
5. Copy the **client_id** (under your app name) and **client_secret**
6. Create `.env` file from template:
```bash
cp .env.template .env
```
7. Edit `.env` and add your credentials:
```
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
REDDIT_USER_AGENT=semaglutide_research_v1.0
```

## 📝 Usage

### Run Complete Pipeline
```bash
# Module 1: Data Collection
python scripts/01_data_collection.py

# Module 2: Preprocessing
python scripts/02_data_preprocessing.py

# Module 3: Exploratory Analysis
python scripts/03_exploratory_analysis.py

# Module 4: Topic Modeling
python scripts/04_topic_modeling.py

# Module 5: Sentiment Analysis
python scripts/05_sentiment_analysis.py

# Module 6: Integration
python scripts/06_integration.py

# Module 7: Visualization
python scripts/07_visualization.py

# Module 8: Report Generation
python scripts/08_report_generation.py

# Module 9: Final Validation
python scripts/09_final_validation.py
```

### Run Individual Scripts
Each script can be run independently if previous modules are complete:
```bash
python scripts/04_topic_modeling.py  # Run topic modeling only
```

## 🔧 Configuration

Edit `config/config.yaml` to customize:
- **Subreddits**: Communities to scrape
- **Keywords**: Search terms
- **Target posts**: Number of posts to collect
- **LDA parameters**: Number of topics, iterations
- **Preprocessing rules**: Stopwords, filters
- **Visualization settings**: DPI, color schemes

## 📊 Key Findings & Results

### Dataset Summary
- **Total Documents**: 19,204 (13,867 posts + 5,337 comments)
- **Time Period**: 2020-01-11 to 2025-10-26 (5.8 years)
- **Subreddits**: r/Ozempic, r/Semaglutide, r/WeightLossAdvice, r/diabetes_t2
- **Average Token Count**: 52.8 tokens/document
- **Vocabulary Size**: 10,827 unique terms

### Topic Analysis (7 Topics Identified)

**Best Model Performance**: 
- Coherence Score (C_v): **0.721** (72.1% - Excellent)
- Perplexity: -9.13
- Log Likelihood: -129,827

**Topics Discovered**:
1. **Topic 0 - Weight Loss Success** (24.9%)
   - Keywords: weight, lose, loss, pound, month
   
2. **Topic 1 - Side Effects** (16.3%)
   - Keywords: nausea, sick, feel, stomach, bad
   
3. **Topic 2 - Dosage & Medication** (15.1%)
   - Keywords: dose, pen, week, injection, start
   
4. **Topic 3 - Medical Experience** (13.8%)
   - Keywords: doctor, insurance, pharmacy, prescription
   
5. **Topic 4 - Appetite & Food** (11.2%)
   - Keywords: food, eat, appetite, hungry, craving
   
6. **Topic 5 - Community Questions** (10.4%)
   - Keywords: anyone, know, try, thing, question
   
7. **Topic 6 - Treatment Experience** (8.3%)
   - Keywords: help, try, work, time, good

### Sentiment Analysis Results

**Overall Sentiment Distribution**:
- Positive: 42.7% (8,194 documents)
- Neutral: 32.9% (6,311 documents)
- Negative: 24.5% (4,699 documents)

**Sentiment by Topic** (Average Compound Scores):
- Topic 0 (Weight Loss): 0.215 (Most Positive)
- Topic 6 (Treatment Experience): 0.178
- Topic 4 (Appetite & Food): 0.144
- Topic 5 (Community): 0.131
- Topic 2 (Dosage): 0.098
- Topic 3 (Medical): 0.091
- Topic 1 (Side Effects): -0.052 (Most Negative)

**Statistical Significance**: ANOVA F=89.47, p<0.001 (highly significant differences between topics)

### Visualizations Generated
- ✅ 8 word clouds (overall + 7 topics)
- ✅ Topic distribution charts
- ✅ Sentiment analysis visualizations
- ✅ Time series plots
- ✅ Interactive pyLDAvis HTML
- ✅ Statistical heatmaps
- ✅ All figures at 300 DPI (publication-ready)

### Data Outputs
- Raw data: 19,204 documents
- Processed dataset with topics and sentiment
- Anonymized final dataset (3.1 MB)
- 500+ representative posts extracted
- Complete statistical reports

## 🔬 Technical Details

### NLP Techniques
- **Topic Modeling**: Latent Dirichlet Allocation (LDA) via Gensim
- **Sentiment Analysis**: VADER (Valence Aware Dictionary and sEntiment Reasoner)
- **Preprocessing**: spaCy + NLTK
- **Evaluation**: Coherence scores (C_v metric)

### Key Libraries
- `praw`: Reddit API wrapper
- `gensim`: Topic modeling
- `vaderSentiment`: Sentiment analysis
- `spacy`: NLP preprocessing
- `nltk`: Text processing
- `pandas`: Data manipulation
- `matplotlib/seaborn`: Visualization
- `pyLDAvis`: Interactive topic visualization

## 📈 Key Research Insights

### Main Patient Concerns
1. **Weight Loss Journey** (24.9% of discussions)
   - Most positive topic (0.215 average sentiment)
   - Focus on success stories and measurable results
   - Strong community support and encouragement

2. **Side Effects Management** (16.3% of discussions)
   - Only negative-leaning topic (-0.052 sentiment)
   - Common concerns: nausea, stomach issues
   - Important for patient education

3. **Medication Access** (13.8% of discussions)
   - Insurance coverage challenges
   - Pharmacy availability issues
   - Prescription process discussions

### Temporal Trends
- Increasing discussion volume over time
- Consistent sentiment patterns across years
- Growing community engagement

### Clinical Implications
- Real-world evidence of treatment experiences
- Patient priorities: weight loss success > side effect concerns
- Need for better patient education on side effects
- Access barriers remain a significant concern

## ⚠️ Ethics & Privacy

- All data is anonymized (usernames hashed/removed)
- Public Reddit data only (no private messages)
- Research use only
- Complies with Reddit API terms of service
- No personal identifiable information (PII) in outputs

## 🐛 Troubleshooting

### Common Issues

**Rate Limiting**
- Reddit API: Max 60 requests/minute
- Script implements automatic delays

**Missing Credentials**
```bash
# Check your .env file exists and has valid credentials
cat .env
```

**Package Issues**
```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

**NLTK Data Missing**
```bash
python -c "import nltk; nltk.download('all')"
```

**spaCy Model Missing**
```bash
python -m spacy download en_core_web_sm
```

## 📂 Accessing Results

### Quick Start for Reviewing Results

**View Complete Analysis**:
```bash
# Open comprehensive results document
open COMPREHENSIVE_RESULTS.md
```

**Load Data in Python**:
```python
import pandas as pd

# Load final dataset with topics and sentiment
df = pd.read_csv('data/anonymized/final_dataset.csv')

# View summary
print(df.info())
print(df[['dominant_topic', 'sentiment_class', 'compound']].describe())

# Load representative posts
samples = pd.read_csv('data/anonymized/representative_posts.csv')
```

**View Visualizations**:
```bash
# Open interactive topic visualization in browser
open visualizations/interactive/lda_visualization.html

# View all word clouds
open visualizations/wordclouds/

# View publication-ready figures
open visualizations/report_figures/
```

**Load Statistical Reports**:
```python
import json

# Load topic analysis report
with open('models/evaluation/topic_report.json', 'r') as f:
    topic_report = json.load(f)

# Load sentiment analysis report  
with open('data/metadata/sentiment_report.json', 'r') as f:
    sentiment_report = json.load(f)

# Load integration insights
with open('data/metadata/key_insights.json', 'r') as f:
    insights = json.load(f)
```

### Dataset Schema

The final dataset (`data/anonymized/final_dataset.csv`) contains:
- **post_id**: Unique identifier (hashed)
- **text**: Original post/comment text
- **cleaned_text**: Preprocessed text
- **created_utc**: Timestamp
- **subreddit**: Source subreddit
- **score**: Reddit score
- **dominant_topic**: Assigned topic (0-6)
- **topic_0 to topic_6**: Topic probabilities
- **compound**: VADER compound sentiment score (-1 to 1)
- **pos, neg, neu**: VADER component scores
- **sentiment_class**: Positive/Neutral/Negative
- **doc_type**: Post or comment

## 📚 References

1. Somani et al. (2023) - Topic modeling for public health research
2. Goel et al. (2022) - VADER sentiment analysis applications
3. Blei et al. (2003) - Latent Dirichlet Allocation
4. Hutto & Gilbert (2014) - VADER: A Parsimonious Rule-based Model for Sentiment Analysis
5. Reddit API Documentation: https://www.reddit.com/dev/api/

## 📄 License

MIT License - Academic research use

## 👥 Contact

For questions about this project, please refer to the project documentation or raise an issue.

## 🎯 Project Status

**Project Phase**: Analysis Complete ✅

### Completed Modules
- [x] **Module 0**: Setup & Configuration ✓
- [x] **Module 1**: Data Collection (19,204 documents) ✓
- [x] **Module 2**: Data Preprocessing ✓
- [x] **Module 3**: Exploratory Data Analysis ✓
- [x] **Module 4**: Topic Modeling (7 topics, 72.1% coherence) ✓
- [x] **Module 5**: Sentiment Analysis (VADER) ✓
- [x] **Module 6**: Integration & Statistical Analysis ✓
- [x] **Module 7**: Visualization (20+ figures) ✓
- [ ] **Module 8**: Report Generation (in progress)
- [ ] **Module 9**: Final Validation

### Available Outputs

**Data Files**:
- `data/raw/posts.csv` - Raw Reddit posts (13,867)
- `data/raw/comments.csv` - Raw comments (5,337)
- `data/processed/combined_processed.csv` - Cleaned data
- `data/anonymized/final_dataset.csv` - Complete dataset with topics & sentiment
- `data/anonymized/representative_posts.csv` - 500+ sample posts

**Model Files**:
- `models/lda/lda_model_7_topics.model` - Best LDA model
- `models/evaluation/topic_coherence_comparison.csv` - Model comparison
- `models/evaluation/topic_report.json` - Detailed topic analysis

**Visualizations**:
- `visualizations/wordclouds/` - 8 word clouds (300 DPI)
- `visualizations/charts/` - Topic & sentiment charts
- `visualizations/interactive/lda_visualization.html` - pyLDAvis
- `visualizations/report_figures/` - Publication-ready figures

**Reports**:
- `COMPREHENSIVE_RESULTS.md` - Complete analysis results
- `data/metadata/` - All statistical reports (JSON)
- Individual module completion reports (MODULE_X_COMPLETE.md)

### File Locations

All project files are organized in:
```
/Users/sher/project/css/semaglutide-reddit-analysis/
```

For detailed results, see `COMPREHENSIVE_RESULTS.md` (67KB, 2,367 lines)

---

**Project Completion**: ~90%  
**Last Updated**: 2025-10-26  
**Analysis Date**: October 26, 2025
