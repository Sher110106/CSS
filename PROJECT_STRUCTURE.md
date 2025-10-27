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
│   │   └── documents_with_sentiment.csv
│   ├── anonymized/                # Final anonymized dataset
│   │   ├── final_dataset.csv
│   │   └── representative_posts.csv
│   └── metadata/                  # Reports and statistics
│       ├── collection_report.json
│       ├── preprocessing_report.json
│       ├── eda_report.json
│       ├── topic_modeling_report.json
│       ├── sentiment_report.json
│       ├── integration_report.json
│       └── key_insights.json
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
│   ├── 01_data_collection_main.py    # Main collection script
│   ├── 01_data_collection.py         # Original collection (archived)
│   ├── 02_data_preprocessing.py      # Data preprocessing
│   ├── 03_exploratory_analysis.py    # EDA
│   ├── 04_topic_modeling.py          # Topic modeling (LDA)
│   ├── 05_sentiment_analysis.py      # Sentiment analysis (VADER)
│   ├── 06_integration.py             # Integration & stats
│   ├── 07_visualization.py           # Visualization generation
│   ├── run_collection.py             # Collection runner (CLI)
│   ├── test_collection.py            # Test Reddit API
│   ├── validate_setup.py             # Setup validation
│   └── utils.py                      # Utility functions
│
├── 📂 visualizations/             # Generated visualizations
│   ├── wordclouds/                # Word cloud images
│   │   ├── overall_wordcloud.png
│   │   └── topic_*_wordcloud.png
│   ├── charts/                    # Statistical charts
│   │   ├── topic_distribution.png
│   │   ├── sentiment_distribution.png
│   │   └── temporal_sentiment.png
│   ├── eda/                       # EDA visualizations
│   └── report_figures/            # Publication-ready figures
│
├── 📂 docs/                       # Documentation
│   ├── COLLECTION_GUIDE.md        # Detailed collection guide
│   ├── CHECKLIST.md               # Pre-execution checklist
│   ├── COMPREHENSIVE_RESULTS.md   # Complete analysis results
│   ├── ANALYSIS_SUMMARY_2025-10-27.md  # Latest summary
│   ├── PIPELINE_EXECUTION_SUMMARY.md   # Pipeline execution log
│   ├── EXECUTION_INSTRUCTIONS.txt
│   ├── RUN_ME_FIRST.txt
│   └── module_reports/            # Individual module reports
│       ├── MODULE_0_COMPLETE.md
│       ├── MODULE_1_COMPLETE.md
│       └── ...
│
├── 📂 logs/                       # Execution logs
│   └── collection_*.log           # Collection logs
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
- **Quick Summary**: `docs/ANALYSIS_SUMMARY_2025-10-27.md`
- **Full Results**: `docs/COMPREHENSIVE_RESULTS.md`
- **Latest Report**: `docs/PIPELINE_EXECUTION_SUMMARY.md`
- **Visualizations**: `visualizations/report_figures/`

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
- `docs/CHECKLIST.md` - Pre-execution checklist

### For Developers
- `PROJECT_STRUCTURE.md` - This file (project layout)
- `scripts/utils.py` - Shared utility functions
- Individual module scripts have detailed docstrings

### Analysis Reports
- `docs/ANALYSIS_SUMMARY_2025-10-27.md` - Latest analysis summary
- `docs/COMPREHENSIVE_RESULTS.md` - Full results with details
- `docs/module_reports/` - Individual module completion reports

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

**Last Updated**: October 27, 2025  
**Project Version**: 1.0  
**Status**: Production Ready
