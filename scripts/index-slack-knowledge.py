#!/usr/bin/env python3
"""
Index Slack messages into Chroma MCP for semantic search
Run: source .venv/bin/activate && python scripts/index-slack-knowledge.py

Supports incremental updates by default (only indexes new messages since last run).
Use --full-reindex to force complete reindexing from scratch.
"""

import os
import sys
import requests
import argparse
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import chromadb
except ImportError:
    print("❌ chromadb not installed. Run: pip install chromadb")
    sys.exit(1)

from scripts.indexer_state import IndexerState

# Configuration from environment
SLACK_TOKEN = os.getenv('SLACK_BOT_TOKEN')
CHANNELS = os.getenv('SLACK_CHANNELS', 'dev,magento,general').split(',')
DAYS_BACK = int(os.getenv('SLACK_DAYS_BACK', '90'))
CHROMA_PATH = os.path.expanduser(os.getenv('CHROMA_DATA_DIR', '~/claude-code-data/chroma'))

if not SLACK_TOKEN:
    print("❌ SLACK_BOT_TOKEN not set in environment")
    print("   Set it in .env file or export SLACK_BOT_TOKEN=xoxb-...")
    sys.exit(1)

def get_channel_id(channel_name):
    """Get channel ID from name"""
    resp = requests.get(
        'https://slack.com/api/conversations.list',
        headers={'Authorization': f'Bearer {SLACK_TOKEN}'},
        params={'types': 'public_channel,private_channel', 'limit': 1000}
    )
    
    if not resp.ok or not resp.json().get('ok'):
        print(f"❌ Failed to list channels: {resp.json().get('error')}")
        return None
    
    channels = resp.json()['channels']
    for ch in channels:
        if ch['name'] == channel_name:
            return ch['id']
    return None

def fetch_messages(channel_id, channel_name, oldest_timestamp=None, days_back=90):
    """Fetch messages from channel

    Args:
        channel_id: Slack channel ID
        channel_name: Channel name (for display)
        oldest_timestamp: Unix timestamp to fetch from (for incremental), or None for days_back
        days_back: Fallback days to go back if no timestamp provided
    """
    if oldest_timestamp:
        oldest = float(oldest_timestamp)
        print(f"  📥 Fetching new messages from #{channel_name} (since {datetime.fromtimestamp(oldest).strftime('%Y-%m-%d %H:%M')})...", end='', flush=True)
    else:
        oldest = (datetime.now() - timedelta(days=days_back)).timestamp()
        print(f"  📥 Fetching messages from #{channel_name} (last {days_back} days)...", end='', flush=True)

    messages = []
    cursor = None
    
    while True:
        params = {
            'channel': channel_id,
            'oldest': oldest,
            'limit': 200
        }
        if cursor:
            params['cursor'] = cursor
            
        resp = requests.get(
            'https://slack.com/api/conversations.history',
            headers={'Authorization': f'Bearer {SLACK_TOKEN}'},
            params=params
        )
        data = resp.json()
        
        if not data.get('ok'):
            print(f"\n❌ Error: {data.get('error')}")
            break
            
        messages.extend(data.get('messages', []))
        
        if not data.get('has_more'):
            break
        cursor = data['response_metadata']['next_cursor']
    
    print(f" {len(messages)} messages")
    return messages

def index_to_chroma(messages, channel_name):
    """Store messages in Chroma with metadata

    Returns:
        str: Latest message timestamp (for state tracking), or None if no messages indexed
    """
    client = chromadb.PersistentClient(path=CHROMA_PATH)

    # Get or create collection
    collection = client.get_or_create_collection(
        name="slack_knowledge",
        metadata={"description": "Indexed Slack messages for knowledge retrieval"}
    )

    indexed = 0
    skipped = 0
    latest_timestamp = None

    for msg in messages:
        # Skip bot messages, join/leave, simple reactions
        if msg.get('subtype') or msg.get('bot_id'):
            skipped += 1
            continue

        text = msg.get('text', '')

        # Skip very short messages (likely not useful)
        if len(text) < 20:
            skipped += 1
            continue

        doc_id = f"slack_{channel_name}_{msg['ts']}"

        # Check if already indexed (idempotent)
        try:
            existing = collection.get(ids=[doc_id])
            if existing and existing['ids']:
                skipped += 1
                continue
        except:
            pass

        # Track latest timestamp
        msg_ts = msg['ts']
        if not latest_timestamp or float(msg_ts) > float(latest_timestamp):
            latest_timestamp = msg_ts

        # Add context if it's a thread reply
        metadata = {
            'source': 'slack',
            'channel': channel_name,
            'timestamp': msg_ts,
            'user': msg.get('user', 'unknown'),
            'thread': 'yes' if msg.get('thread_ts') else 'no',
            'date': datetime.fromtimestamp(float(msg_ts)).isoformat()
        }

        try:
            collection.add(
                documents=[text],
                metadatas=[metadata],
                ids=[doc_id]
            )
            indexed += 1
        except Exception as e:
            print(f"\n⚠️  Failed to index message: {e}")
            skipped += 1

    print(f"  ✅ Indexed {indexed} messages, skipped {skipped}")
    return latest_timestamp

def main():
    # Parse CLI arguments
    parser = argparse.ArgumentParser(
        description='Index Slack messages into Chroma (incremental by default)'
    )
    parser.add_argument(
        '--full-reindex',
        action='store_true',
        help='Force full reindexing from scratch (ignores previous state)'
    )
    args = parser.parse_args()

    # Initialize state
    state = IndexerState()

    # Handle full reindex
    if args.full_reindex:
        print("🔄 Full reindex requested - resetting state...")
        state.reset()
        mode = f"last {DAYS_BACK} days (FULL)"
    else:
        mode = "incremental update"

    print("=" * 60)
    print("🔍 Slack Knowledge Indexing")
    print("=" * 60)
    print(f"📅 Mode: {mode}")
    print(f"📂 Chroma path: {CHROMA_PATH}")
    print(f"📝 Channels: {', '.join(CHANNELS)}")
    print()

    for channel_name in CHANNELS:
        print(f"📡 Processing #{channel_name}...")

        channel_id = get_channel_id(channel_name)

        if not channel_id:
            print(f"  ❌ Channel #{channel_name} not found (check bot has access)")
            continue

        # Get last indexed timestamp for incremental updates
        oldest_timestamp = None
        if not args.full_reindex:
            oldest_timestamp = state.get_slack_channel_timestamp(channel_name)

        messages = fetch_messages(
            channel_id,
            channel_name,
            oldest_timestamp=oldest_timestamp,
            days_back=DAYS_BACK
        )

        if not messages:
            print(f"  ℹ️  No new messages")
            continue

        latest_timestamp = index_to_chroma(messages, channel_name)

        # Update state with latest timestamp
        if latest_timestamp:
            state.update_slack_channel(channel_name, latest_timestamp)

    # Save state
    state.save()

    print()
    print("=" * 60)
    print("✅ Slack indexing complete!")
    print("=" * 60)

if __name__ == '__main__':
    main()
