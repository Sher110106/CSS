# Project Structure

## 📁 Directory Organization

```
semaglutide-reddit-analysis/
├── 📄 README.md                    # Main project documentation
├── 📄 QUICK_START.md              # Quick start guide
├── 📄 PROJECT_STRUCTURE.md        # This file
│
├── 📂 config/                     # Configuration files
│   ├── config.yaml                # Main configuration
│   └── config_loader.py           # Config loader utility
│
├── 📂 data/                       # Data directory
│   ├── raw/                       # Raw scraped data
│   │   ├── posts.csv             # Reddit posts
│   │   └── comments.csv          # Reddit comments
│   ├── processed/                 # Cleaned and processed data
│   │   ├── combined_processed.csv
│   │   ├── documents_with_topics.csv
│   │   ├── documents_with_sentiment.csv
│   │   ├── period_posting_behavior.csv
│   │   ├── period_sentiment_stats.csv
│   │   └── period_topic_distribution.csv
│   ├── anonymized/                # Final anonymized dataset
│   │   ├── final_dataset.csv
│   │   └── representative_posts.csv
│   └── metadata/                  # Reports and statistics
│       ├── collection_report.json
│       ├── preprocessing_report.json
│       ├── eda_report.json
│       ├── topic_modeling_report.json
│       ├── 4_topic_model_report.json
│       ├── sentiment_report.json
│       ├── integration_report.json
│       ├── key_insights.json
│       ├── extended_analysis_summary.json
│       └── temporal_methodology.json
│
├── 📂 models/                     # Trained models
│   ├── lda/                       # LDA topic models
│   │   ├── lda_model_5_topics.model
│   │   ├── lda_model_best.model
│   │   ├── dictionary.dict
│   │   └── corpus.mm
│   └── evaluation/                # Model evaluation
│       └── topic_coherence_comparison.csv
│
├── 📂 scripts/                    # Analysis scripts
│   ├── 01_data_collection.py         # Enhanced data collection
│   ├── 02_data_preprocessing.py      # Data preprocessing
│   ├── 03_exploratory_analysis.py    # EDA
│   ├── 04_topic_modeling.py          # Topic modeling (LDA)
│   ├── 05_sentiment_analysis.py      # Sentiment analysis (VADER)
│   ├── 06_integration.py             # Integration & stats
│   ├── 07_visualization.py           # Visualization generation
│   ├── 08_extended_analysis.py       # Extended analysis & period comparison
│   ├── run_collection.py             # Collection runner (CLI)
│   ├── test_collection.py            # Test Reddit API
│   ├── validate_setup.py             # Setup validation
│   ├── utils.py                      # Utility functions
│   └── archive/                      # Archived old scripts
│
├── 📂 visualizations/             # Generated visualizations (300 DPI)
│   ├── wordclouds/                # Word cloud images (6 total)
│   │   ├── overall_wordcloud.png
│   │   └── topic_*_wordcloud.png (0-4)
│   ├── charts/                    # Statistical charts
│   │   ├── topic_distribution.png
│   │   ├── sentiment_distribution.png
│   │   ├── temporal_sentiment.png
│   │   └── sentiment_heatmap.png
│   ├── eda/                       # EDA visualizations
│   │   ├── temporal_analysis.png
│   │   ├── subreddit_analysis.png
│   │   └── vocabulary_analysis.png
│   ├── extended_analysis/         # Extended analysis visualizations
│   │   ├── period_posting_behavior.png
│   │   ├── period_sentiment_analysis.png
│   │   └── period_topic_distribution.png
│   └── report_figures/            # Publication-ready figures
│
├── 📂 docs/                       # Documentation
│   ├── COLLECTION_GUIDE.md        # Detailed collection guide
│   ├── TEMPORAL_METHODOLOGY.md    # Temporal analysis methodology
│   └── module_reports/            # Module completion reports
│       ├── PROJECT_SUMMARY.md     # 📌 Complete project summary
│       ├── MODULE_0_COMPLETE.md   # Setup & configuration
│       ├── MODULE_1_COMPLETE.md   # Data collection
│       ├── MODULE_2_COMPLETE.md   # Data preprocessing
│       ├── MODULE_3_COMPLETE.md   # Exploratory analysis
│       ├── MODULE_4_COMPLETE.md   # Topic modeling
│       ├── MODULE_5_COMPLETE.md   # Sentiment analysis
│       ├── MODULE_6_COMPLETE.md   # Integration & stats
│       └── MODULE_7_COMPLETE.md   # Visualization
│
├── 📂 logs/                       # Execution logs
│   ├── collection_*.log           # Collection logs
│   ├── extended_analysis.log      # Extended analysis logs
│   ├── topic_modeling.log         # Topic modeling logs
│   ├── sentiment_analysis.log     # Sentiment analysis logs
│   └── archive/                   # Archived old logs
│
├── 📂 notebooks/                  # Jupyter notebooks (if any)
│
├── 📂 venv/                       # Python virtual environment
│
├── 📄 .env                        # Environment variables (credentials)
├── 📄 .env.template               # Template for .env
├── 📄 .gitignore                  # Git ignore rules
└── 📄 requirements.txt            # Python dependencies

```

## 🎯 Quick Navigation

### Getting Started
- **Setup**: See `.env.template` and `docs/CHECKLIST.md`
- **Quick Start**: Read `QUICK_START.md`
- **Testing**: Run `python scripts/test_collection.py`

### Data Collection
- **Main Script**: `scripts/run_collection.py`
- **Test Run**: `python scripts/run_collection.py --target 100 --hours 0.5`
- **Full Run**: `python scripts/run_collection.py --target 10000 --hours 8`

### Analysis Pipeline
Run in order:
1. `python scripts/02_data_preprocessing.py`
2. `python scripts/03_exploratory_analysis.py`
3. `python scripts/04_topic_modeling.py`
4. `python scripts/05_sentiment_analysis.py`
5. `python scripts/06_integration.py`
6. `python scripts/07_visualization.py`

### Results
- **📌 Complete Summary**: `docs/module_reports/PROJECT_SUMMARY.md`
- **Module Reports**: `docs/module_reports/MODULE_*.md`
- **Methodology**: `docs/TEMPORAL_METHODOLOGY.md`
- **Visualizations**: `visualizations/` (organized by type)

## 📊 Key Files

### Configuration
- `config/config.yaml` - Edit to change subreddits, keywords, model parameters
- `.env` - Reddit API credentials (never commit!)

### Input Data
- `data/raw/posts.csv` - Raw Reddit posts
- `data/raw/comments.csv` - Raw Reddit comments

### Final Output
- `data/anonymized/final_dataset.csv` - Complete dataset with topics & sentiment
- `data/metadata/key_insights.json` - Key research insights

### Models
- `models/lda/lda_model_best.model` - Best performing LDA model

## 🔧 Common Tasks

### Run Data Collection
```bash
python scripts/run_collection.py
```

### Run Full Pipeline
```bash
# With virtual environment
source venv/bin/activate
python scripts/02_data_preprocessing.py
python scripts/03_exploratory_analysis.py
python scripts/04_topic_modeling.py
python scripts/05_sentiment_analysis.py
python scripts/06_integration.py
python scripts/07_visualization.py
```

### View Results
```python
import pandas as pd

# Load final dataset
df = pd.read_csv('data/anonymized/final_dataset.csv')

# View summary
print(df.info())
print(df[['dominant_topic', 'sentiment_class', 'compound']].describe())
```

### Check Logs
```bash
# Latest collection log
tail -f logs/collection_*.log

# View all logs
ls -lh logs/
```

## 📝 Documentation

### For Users
- `README.md` - Complete project overview
- `QUICK_START.md` - Get started quickly
- `docs/COLLECTION_GUIDE.md` - Detailed collection instructions
- `docs/module_reports/PROJECT_SUMMARY.md` - **Complete project summary**

### For Developers
- `PROJECT_STRUCTURE.md` - This file (project layout)
- `scripts/utils.py` - Shared utility functions
- Individual module scripts have detailed docstrings

### Analysis Reports
- `docs/module_reports/PROJECT_SUMMARY.md` - **📌 Master summary document**
- `docs/module_reports/MODULE_*.md` - Individual module reports (0-7)
- `docs/TEMPORAL_METHODOLOGY.md` - Temporal analysis methodology

## 🎨 Visualization Files

All visualizations are saved at 300 DPI (publication-ready):

- **Word Clouds**: `visualizations/wordclouds/`
- **Charts**: `visualizations/charts/`
- **Report Figures**: `visualizations/report_figures/` (copied for easy access)

## 💾 Data Files

### Raw Data (after collection)
- Posts: ~1,400
- Comments: ~53,000
- Total: ~54,700 documents

### Processed Data (after preprocessing)
- Filtered documents: ~23,400
- With topics: 5 topics identified
- With sentiment: VADER scores

### Final Dataset
- Complete analysis: Topics + Sentiment + Metadata
- Representative samples extracted
- Fully anonymized

## ⚙️ Configuration Files

### config/config.yaml
Main configuration file - edit to customize:
- Subreddits to scrape
- Search keywords
- Target post count
- LDA parameters (topic count, iterations)
- Preprocessing rules

### .env
Reddit API credentials:
```
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=semaglutide_research_v1.0
```

## 🚀 Workflow Summary

1. **Setup** → Configure `.env` and `config/config.yaml`
2. **Test** → `python scripts/test_collection.py`
3. **Collect** → `python scripts/run_collection.py`
4. **Process** → Run modules 2-7 in sequence
5. **Analyze** → Review results in `docs/` and `visualizations/`

---

## 📌 Important Notes

### Study Limitations
- **Pre-2020 data insufficient**: Only 3 posts collected before March 2020
- **Valid comparisons**: Early Period (2020-2022) vs Recent Period (2023-2025)
- **Sample bias**: Reddit users may not represent all semaglutide patients
- See `docs/module_reports/PROJECT_SUMMARY.md` for full limitations discussion

### Key Changes (Nov 27, 2025)
- ✅ Removed redundant documentation files (consolidated into PROJECT_SUMMARY.md)
- ✅ Updated analysis to period-based comparison (deprecated pandemic comparison)
- ✅ Cleaned up logs folder (archived old logs)
- ✅ All metadata JSON files retained (each serves unique purpose)

---

**Last Updated**: November 27, 2025  
**Project Version**: 1.1  
**Status**: Production Ready - Cleaned & Consolidated
