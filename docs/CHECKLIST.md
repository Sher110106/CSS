# Pre-Execution Checklist

Use this checklist before running overnight data collection.

## ☑️ Setup Checklist (One-time)

- [ ] **Reddit API Credentials Obtained**
  - Registered at https://www.reddit.com/prefs/apps
  - Created "script" type application
  - Have client_id and client_secret

- [ ] **Environment File Configured**
  - `.env` file exists in project root
  - Contains valid REDDIT_CLIENT_ID
  - Contains valid REDDIT_CLIENT_SECRET
  - Contains REDDIT_USER_AGENT

- [ ] **Dependencies Installed**
  - Virtual environment activated (if using)
  - All packages from requirements.txt installed
  - `praw` package available

- [ ] **Configuration Reviewed**
  - Checked `config/config.yaml`
  - Subreddits list is appropriate
  - Keywords list is comprehensive
  - Target posts is realistic

## ☑️ Pre-Run Checklist (Every time)

- [ ] **Test Collection Passed**
  - Ran `python scripts/test_collection.py`
  - Saw "✅ TEST PASSED" message
  - At least 10 posts collected in test
  - No authentication errors

- [ ] **System Requirements Met**
  - Stable internet connection
  - Computer won't sleep during run
  - Sufficient disk space (500MB+ free)
  - No other Reddit scripts running

- [ ] **Monitoring Setup**
  - Know log file location: `logs/`
  - Can check progress: `tail -f logs/overnight_collection_*.log`
  - Understand output files location: `data/raw/`

- [ ] **Execution Plan Clear**
  - Know target post count
  - Know max runtime in hours
  - Understand it can be stopped with Ctrl+C
  - Know how to resume: `--resume` flag

## ☑️ During Collection

- [ ] **Initial Verification (first 30 min)**
  - Collection started successfully
  - Posts being collected (check console output)
  - No continuous errors in log
  - Collection rate is reasonable (>5 posts/hour)

- [ ] **Mid-Run Check (if awake)**
  - Progress updates showing in console
  - Post count increasing
  - Error count is low (<10% of attempts)
  - Checkpoint files being created

## ☑️ Post-Collection Checklist

- [ ] **Output Files Created**
  - `data/raw/posts.csv` exists
  - `data/raw/comments.csv` exists
  - `data/metadata/overnight_collection_report.json` exists
  - Log file exists in `logs/`

- [ ] **Data Quality Check**
  - Post count meets minimum requirements (>1000)
  - No excessive duplicates
  - Multiple subreddits represented
  - Date range is reasonable
  - Comments collected (ratio ~3-5 per post)

- [ ] **Review Collection Report**
  - Checked `overnight_collection_report.json`
  - Runtime is reasonable
  - Error count is acceptable
  - Posts by subreddit looks balanced
  - Statistics make sense

- [ ] **Backup Created (Recommended)**
  - Copied `data/raw/` to backup location
  - Or committed to git (if using)
  - Have recovery plan if preprocessing fails

- [ ] **Ready for Next Step**
  - Data validated
  - Can proceed to preprocessing
  - Know next command: `python scripts/02_data_preprocessing.py`

## 🚨 Troubleshooting Checklist

If collection fails or has issues:

- [ ] **Check Authentication**
  - Verify `.env` credentials are correct
  - Test at reddit.com/prefs/apps
  - Regenerate secret if needed

- [ ] **Check Network**
  - Internet connection stable
  - Reddit is accessible
  - Check https://www.redditstatus.com

- [ ] **Check Logs**
  - Read latest log file in `logs/`
  - Look for specific error messages
  - Check for rate limit patterns

- [ ] **Check Disk Space**
  - Sufficient space available
  - No disk write errors

- [ ] **Try Recovery Steps**
  - Resume with `--resume` flag
  - Reduce target posts
  - Adjust keywords in config
  - Try test collection again

## 📋 Quick Reference Commands

```bash
# Navigate to project
cd /Users/sher/project/css/semaglutide-reddit-analysis

# Activate environment (if needed)
source venv/bin/activate

# Test
python scripts/test_collection.py

# Run overnight
python scripts/run_overnight_collection.py

# Run with options
python scripts/run_overnight_collection.py --target 15000 --hours 10

# Resume
python scripts/run_overnight_collection.py --resume

# Check progress (in another terminal)
tail -f logs/overnight_collection_*.log
wc -l data/raw/posts_checkpoint.csv
```

## ✅ Success Criteria

Collection is successful if:
- ✅ Collected at least 1,000 posts
- ✅ Collected at least 3,000 comments
- ✅ Multiple subreddits represented
- ✅ No authentication failures
- ✅ Error rate <20%
- ✅ Data files are valid CSV format
- ✅ Can load data with pandas without errors

---

**Tip**: Print this checklist or keep it open while running collection!
