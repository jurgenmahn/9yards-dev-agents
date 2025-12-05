---
description: Index Slack messages into knowledge base
---

Run the Slack knowledge indexing script to update the Chroma database with recent team discussions.

**By default, only new messages since the last run are indexed (incremental mode).**

## What This Does

- Fetches messages from configured Slack channels
- Indexes them into Chroma MCP for semantic search
- Tracks progress to enable fast incremental updates
- Allows agents to query historical team discussions
- Helps find past solutions and decisions

## Requirements

- SLACK_BOT_TOKEN must be set in .env
- Python virtual environment must be activated
- Chroma MCP must be configured

## Usage

### Incremental Update (Default)
Only indexes new messages since last run:
```bash
source .venv/bin/activate
python scripts/index-slack-knowledge.py
```

### Full Reindex
Force complete reindexing from scratch:
```bash
source .venv/bin/activate
python scripts/index-slack-knowledge.py --full-reindex
```

## Configuration

Edit `.env` to configure:
- `SLACK_BOT_TOKEN` - Your Slack bot token (required)
- `SLACK_CHANNELS` - Comma-separated list (e.g., `dev,magento,general`). **Leave empty to index all accessible channels**
- `SLACK_DAYS_BACK` - How many days to index on first run (default: 90)
- `CHROMA_DATA_DIR` - Where to store Chroma data

**Example configurations:**
```bash
# Index specific channels
SLACK_CHANNELS=dev,magento,general

# Index all accessible channels (leave empty or unset)
SLACK_CHANNELS=
```

## Expected Output

**Incremental Mode (specific channels):**
```
🔍 Slack Knowledge Indexing
📅 Mode: incremental update
📂 Chroma path: ~/claude-code-data/chroma
📝 Channels (configured): dev, magento, general

📡 Processing #dev...
  📥 Fetching new messages from #dev (since 2025-12-04 10:30)... 12 messages
  ✅ Indexed 8 messages, skipped 4

✅ Slack indexing complete!
```

**Incremental Mode (all channels):**
```
📡 SLACK_CHANNELS not set - discovering all accessible channels...
🔍 Slack Knowledge Indexing
📅 Mode: incremental update
📂 Chroma path: ~/claude-code-data/chroma
📝 Channels (all accessible): dev, magento, general, design, support, sales

📡 Processing #dev...
...
```

**Full Reindex Mode:**
```
🔄 Full reindex requested - resetting state...
📅 Mode: last 90 days (FULL)
...
```

## How Incremental Indexing Works

- **State tracking**: Last indexed message timestamp stored in `scripts/.indexer-state.json`
- **First run**: Indexes last 90 days (or SLACK_DAYS_BACK value)
- **Subsequent runs**: Only fetches messages newer than last indexed timestamp
- **Performance**: Incremental runs are 10-100x faster than full reindex

## Troubleshooting

- **Channel not found**: Ensure bot has access to the channel
- **Authentication failed**: Check SLACK_BOT_TOKEN is correct
- **Import error**: Run `pip install chromadb requests`
- **State file corrupted**: Delete `scripts/.indexer-state.json` and run with `--full-reindex`

## When to Run

- **Initial setup**: Run with `--full-reindex` after installing the plugin
- **Regular updates**: Run daily (incremental mode is fast)
- **After state issues**: Run with `--full-reindex` if state is out of sync
- **Manual refresh**: Run incrementally when you need latest context
