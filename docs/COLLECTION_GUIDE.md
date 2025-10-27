# Overnight Data Collection Guide

This guide explains how to use the enhanced overnight data collection system to gather large amounts of Reddit data.

## 🌟 Features

- **Robust Error Handling**: Automatically recovers from API errors, rate limits, and network issues
- **Checkpoint System**: Auto-saves progress every 5 minutes - can resume after interruption
- **Adaptive Rate Limiting**: Dynamically adjusts request speed to avoid hitting Reddit's limits
- **Multiple Collection Methods**: Uses search, hot, top, and new sorting to maximize data diversity
- **Graceful Shutdown**: Press Ctrl+C anytime to stop cleanly and save all progress
- **Comprehensive Logging**: Detailed logs track every step for debugging and monitoring
- **Progress Tracking**: Real-time updates on collection rate, errors, and estimated completion

## 📋 Prerequisites

1. **Reddit API Credentials**: 
   - Go to https://www.reddit.com/prefs/apps
   - Click "Create App" or "Create Another App"
   - Choose "script" type
   - Note your client_id and client_secret

2. **Environment Setup**:
   ```bash
   # Make sure you're in the project directory
   cd semaglutide-reddit-analysis
   
   # Activate virtual environment (if using one)
   source venv/bin/activate  # On Mac/Linux
   # or
   venv\Scripts\activate     # On Windows
   ```

3. **Configure Credentials**:
   Edit `.env` file:
   ```bash
   REDDIT_CLIENT_ID=your_actual_client_id_here
   REDDIT_CLIENT_SECRET=your_actual_client_secret_here
   REDDIT_USER_AGENT=semaglutide_research_v1.0
   ```

## 🧪 Step 1: Test Collection (IMPORTANT - Do This First!)

Before running overnight, test that everything works:

```bash
python scripts/test_collection.py
```

This will:
- Verify your Reddit credentials work
- Collect ~50 posts in 2-3 minutes
- Validate the collection system
- Confirm data is being saved correctly

**Expected output:**
```
✅ TEST PASSED - Collection system working!
✓ Posts collected: 50+
✓ Comments collected: 200+
```

## 🚀 Step 2: Run Overnight Collection

### Option A: Interactive Mode (Recommended)
```bash
python scripts/run_overnight_collection.py
```

You'll be prompted for:
- Target number of posts (default: 10,000)
- Maximum runtime in hours (default: 8)
- Confirmation before starting

### Option B: Command Line Arguments
```bash
# Collect 20,000 posts with 12-hour limit
python scripts/run_overnight_collection.py --target 20000 --hours 12

# Quick run for testing (100 posts, 30 minutes)
python scripts/run_overnight_collection.py --target 100 --hours 0.5

# Resume from last checkpoint
python scripts/run_overnight_collection.py --resume

# Start immediately without confirmation
python scripts/run_overnight_collection.py --no-confirm
```

### Full Command Options:
```bash
python scripts/run_overnight_collection.py \
  --target 15000 \      # Target number of posts
  --hours 10 \          # Maximum runtime in hours
  --resume \            # Resume from checkpoint
  --no-confirm          # Skip confirmation prompt
```

## 📊 What to Expect

### Typical Collection Rates
- **Fast**: 50-100 posts/hour (when lots of data available)
- **Moderate**: 20-50 posts/hour (normal conditions)
- **Slow**: 5-20 posts/hour (rate limiting, fewer results)

### Example Timeline for 10,000 Posts
- **Best case**: 2-4 hours
- **Typical**: 4-8 hours  
- **Worst case**: 8-12 hours

### Console Output
```
================================================================================
PROGRESS UPDATE
================================================================================
Posts collected: 2,547 / 10,000 (25.5%)
Comments collected: 12,384
Runtime: 1.23 hours
Collection rate: 45.3 posts/hour
Total errors: 3
Current delay: 1.2s
================================================================================
```

## ⚠️ Handling Issues

### If Collection Stops or Errors Occur

**The script automatically:**
1. Saves progress every 5 minutes
2. Retries failed requests
3. Backs off when hitting rate limits
4. Saves data before exiting on errors

**To resume:**
```bash
python scripts/run_overnight_collection.py --resume
```

Your collected data is preserved in:
- `data/raw/posts_checkpoint.csv`
- `data/raw/comments_checkpoint.csv`
- `data/raw/checkpoint.json`

### Common Issues and Solutions

#### 1. Rate Limiting Errors
**Symptoms**: "Rate limit hit" messages, slow collection
**Solution**: Script handles automatically - just let it run. It will slow down and retry.

#### 2. "403 Forbidden" or Authentication Errors
**Problem**: Invalid Reddit credentials
**Solution**: 
- Check your `.env` file has correct client_id and client_secret
- Verify credentials at https://www.reddit.com/prefs/apps
- Make sure app type is "script"

#### 3. Very Slow Collection (<5 posts/hour)
**Possible causes**:
- Reddit API being slow (peak hours)
- Keywords not matching many posts
- Already collected most available posts

**Solutions**:
- Try different keywords in `config/config.yaml`
- Add more subreddits to search
- Run during off-peak hours (US nighttime)

#### 4. Network Timeout Errors
**Solution**: Script auto-retries. If persistent:
```bash
# Stop with Ctrl+C, wait a few minutes, then resume
python scripts/run_overnight_collection.py --resume
```

## 🛑 Stopping Collection

### Graceful Stop (Recommended)
Press `Ctrl+C` once - the script will:
1. Finish current request
2. Save all collected data
3. Create checkpoint for resuming
4. Exit cleanly

**DO NOT** press Ctrl+C multiple times - let it finish saving!

### Emergency Stop
If you must force quit:
- Data is auto-saved every 5 minutes
- You'll lose at most 5 minutes of collection
- Resume with `--resume` flag

## 📁 Output Files

After collection completes:

```
data/raw/
├── posts.csv                          # All collected posts
├── comments.csv                       # All collected comments
└── checkpoint.json                    # Progress checkpoint (cleaned up after success)

data/metadata/
└── overnight_collection_report.json   # Detailed collection statistics

logs/
└── overnight_collection_YYYYMMDD_HHMMSS.log  # Full execution log
```

## 📈 Monitoring Progress

### During Collection
1. **Console**: Shows progress updates every checkpoint (5 min)
2. **Log File**: Real-time details in `logs/overnight_collection_*.log`
3. **Data Files**: Check `data/raw/posts_checkpoint.csv` anytime

### To Check Progress While Running
```bash
# In another terminal, count current posts
wc -l data/raw/posts_checkpoint.csv

# Or check the log
tail -f logs/overnight_collection_*.log
```

## 🎯 Recommended Strategy for Maximum Data

### For Truly Large Collection (20,000+ posts):

1. **Day 1 - Initial Run**:
   ```bash
   python scripts/run_overnight_collection.py --target 10000 --hours 8
   ```

2. **Day 2 - Continue Collection**:
   - DON'T use `--resume` (that continues the same run)
   - Instead, backup first batch:
   ```bash
   cp data/raw/posts.csv data/raw/posts_batch1.csv
   cp data/raw/comments.csv data/raw/comments_batch1.csv
   ```
   
3. **Run Again**:
   ```bash
   python scripts/run_overnight_collection.py --target 15000 --hours 10
   ```

4. **Combine Batches** (if needed):
   ```python
   import pandas as pd
   
   # Load both batches
   batch1 = pd.read_csv('data/raw/posts_batch1.csv')
   batch2 = pd.read_csv('data/raw/posts.csv')
   
   # Combine and remove duplicates
   combined = pd.concat([batch1, batch2])
   combined = combined.drop_duplicates(subset=['post_id'])
   
   # Save
   combined.to_csv('data/raw/posts_combined.csv', index=False)
   ```

## 🔍 Post-Collection Validation

After collection completes, verify your data:

```bash
# Run validation
python scripts/validate_collection.py  # (if exists)

# Or manually check with Python:
python
>>> import pandas as pd
>>> posts = pd.read_csv('data/raw/posts.csv')
>>> comments = pd.read_csv('data/raw/comments.csv')
>>> print(f"Posts: {len(posts):,}")
>>> print(f"Comments: {len(comments):,}")
>>> print(f"Subreddits: {posts['subreddit'].unique()}")
>>> print(f"Date range: {posts['created_utc'].min()} to {posts['created_utc'].max()}")
```

## 🎓 Tips for Best Results

1. **Run During Off-Peak Hours**: Reddit API is faster at night (US timezone)

2. **Adjust Keywords**: Edit `config/config.yaml` to add more relevant keywords:
   ```yaml
   keywords:
     - "semaglutide"
     - "ozempic"
     - "wegovy"
     - "mounjaro"      # Add comparisons
     - "weight loss"    # Broader terms
   ```

3. **Add More Subreddits**:
   ```yaml
   subreddits:
     - "Ozempic"
     - "Semaglutide"
     - "WeightLossAdvice"
     - "loseit"
     - "progresspics"
     - "diabetes"
   ```

4. **Monitor Your First Hour**: 
   - Check logs after 30-60 minutes
   - Verify data is being collected
   - Adjust if needed before full overnight run

5. **Use Screen/Tmux for Remote Servers**:
   ```bash
   # Start a screen session
   screen -S reddit_collection
   
   # Run collection
   python scripts/run_overnight_collection.py --no-confirm
   
   # Detach: Ctrl+A, then D
   # Reattach later: screen -r reddit_collection
   ```

## ❓ FAQ

**Q: Can I run this on my laptop and close the lid?**
A: Depends on your OS settings. Better to keep it open or use a server/desktop.

**Q: How much will this cost in Reddit API calls?**
A: Reddit API is free for reasonable use. This script respects all limits.

**Q: What if I lose internet connection?**
A: Script saves every 5 minutes. Resume with `--resume` when back online.

**Q: Can I collect from private subreddits?**
A: No, only public subreddits. Reddit API doesn't allow private subreddit access in script mode.

**Q: The script seems stuck, is it working?**
A: Check the log file. If requests are timing out, it's working but slow. If no activity for 10+ minutes, stop and restart.

## 🆘 Getting Help

If you encounter issues:

1. Check the log file: `logs/overnight_collection_*.log`
2. Verify credentials in `.env`
3. Try the test script first: `python scripts/test_collection.py`
4. Check Reddit's status: https://www.redditstatus.com/

## ✅ Success Checklist

Before starting overnight collection:
- [ ] Tested credentials with `test_collection.py`
- [ ] Reviewed and adjusted `config/config.yaml` if needed
- [ ] Have stable internet connection
- [ ] Computer won't sleep/shutdown
- [ ] Enough disk space (10,000 posts ≈ 50-100MB)
- [ ] Noted the log file location for monitoring

After collection:
- [ ] Check data files exist: `posts.csv`, `comments.csv`
- [ ] Verify post count meets target
- [ ] Review collection report JSON
- [ ] Backup data if needed
- [ ] Ready to run preprocessing: `python scripts/02_data_preprocessing.py`

---

**Good luck with your data collection! 🚀**
