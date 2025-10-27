# Quick Start Guide

## 🚀 Three Simple Steps

### 1. Set Up Credentials (One-time setup)

Edit your `.env` file:
```bash
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_secret  
REDDIT_USER_AGENT=semaglutide_research_v1.0
```

Get credentials: https://www.reddit.com/prefs/apps (Create "script" app)

### 2. Test Collection (2-3 minutes)

```bash
python scripts/test_collection.py
```

Should see: `✅ TEST PASSED`

### 3. Run Data Collection

```bash
python scripts/run_collection.py
```

Follow prompts or use flags:
```bash
# Collect 20,000 posts with 12 hour limit
python scripts/run_collection.py --target 20000 --hours 12
```

## 📊 What You'll Get

- `data/raw/posts.csv` - All posts
- `data/raw/comments.csv` - All comments  
- `data/metadata/collection_report.json` - Statistics
- `logs/collection_*.log` - Detailed log

## ⚡ Key Features

- ✅ Auto-saves every 5 minutes
- ✅ Resume after interruption: `--resume`
- ✅ Press Ctrl+C to stop gracefully
- ✅ Handles rate limits automatically
- ✅ Multiple collection strategies

## 🔧 Common Commands

```bash
# Default collection (10k posts, 8 hours max)
python scripts/run_collection.py

# Large collection
python scripts/run_collection.py --target 20000 --hours 12

# Quick test collection
python scripts/run_collection.py --target 100 --hours 0.5

# Resume interrupted collection
python scripts/run_collection.py --resume

# Skip confirmation prompt
python scripts/run_collection.py --no-confirm
```

## 🆘 Troubleshooting

| Problem | Solution |
|---------|----------|
| Authentication error | Check `.env` credentials |
| Rate limit messages | Normal - script handles automatically |
| Very slow (<5 posts/hr) | Adjust keywords in `config/config.yaml` |
| Script stuck | Check log file, may be waiting on rate limit |
| Resume after crash | `python scripts/run_collection.py --resume` |

## 📈 Expected Performance

- **Typical**: 20-50 posts/hour
- **10,000 posts**: 4-8 hours
- **20,000 posts**: 8-16 hours

## ✅ Pre-flight Checklist

- [ ] Reddit credentials in `.env`
- [ ] Test script passed
- [ ] Stable internet
- [ ] Computer won't sleep
- [ ] Enough disk space (~10MB per 1k posts)

---

For detailed guide: See `docs/COLLECTION_GUIDE.md`
