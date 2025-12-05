---
description: Index Slack messages into knowledge base
---

Run the Slack knowledge indexing script to update the Chroma database with recent team discussions.

## What This Does

- Fetches messages from configured Slack channels (last 90 days by default)
- Indexes them into Chroma MCP for semantic search
- Allows agents to query historical team discussions
- Helps find past solutions and decisions

## Requirements

- SLACK_BOT_TOKEN must be set in .env
- Python virtual environment must be activated
- Chroma MCP must be configured

## Usage

```bash
source .venv/bin/activate
python scripts/index-slack-knowledge.py
```

## Configuration

Edit `.env` to configure:
- `SLACK_BOT_TOKEN` - Your Slack bot token
- `SLACK_CHANNELS` - Comma-separated list (default: dev,magento,general)
- `SLACK_DAYS_BACK` - How many days to index (default: 90)
- `CHROMA_DATA_DIR` - Where to store Chroma data

## Expected Output

```
🔍 Slack Knowledge Indexing
📅 Indexing last 90 days
📂 Chroma path: ~/claude-code-data/chroma
📝 Channels: dev, magento, general

📡 Processing #dev...
  📥 Fetching messages from #dev... 245 messages
  ✅ Indexed 178 messages, skipped 67

✅ Slack indexing complete!
```

## Troubleshooting

- **Channel not found**: Ensure bot has access to the channel
- **Authentication failed**: Check SLACK_BOT_TOKEN is correct
- **Import error**: Run `pip install chromadb requests`

## When to Run

- Initial setup: After installing the plugin
- Regular updates: Automatically via cron (nightly at 2 AM)
- Manual refresh: When you need latest discussions indexed
