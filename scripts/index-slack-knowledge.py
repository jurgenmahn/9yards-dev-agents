#!/usr/bin/env python3
"""
Index Slack messages into Chroma MCP for semantic search
Run: source .venv/bin/activate && python scripts/index-slack-knowledge.py
"""

import os
import sys
import requests
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import chromadb
except ImportError:
    print("❌ chromadb not installed. Run: pip install chromadb")
    sys.exit(1)

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

def fetch_messages(channel_id, channel_name, days_back=90):
    """Fetch messages from channel"""
    oldest = (datetime.now() - timedelta(days=days_back)).timestamp()
    messages = []
    cursor = None
    
    print(f"  📥 Fetching messages from #{channel_name}...", end='', flush=True)
    
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
    """Store messages in Chroma with metadata"""
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    
    # Get or create collection
    collection = client.get_or_create_collection(
        name="slack_knowledge",
        metadata={"description": "Indexed Slack messages for knowledge retrieval"}
    )
    
    indexed = 0
    skipped = 0
    
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
        
        # Add context if it's a thread reply
        metadata = {
            'source': 'slack',
            'channel': channel_name,
            'timestamp': msg['ts'],
            'user': msg.get('user', 'unknown'),
            'thread': 'yes' if msg.get('thread_ts') else 'no',
            'date': datetime.fromtimestamp(float(msg['ts'])).isoformat()
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

def main():
    print("=" * 60)
    print("🔍 Slack Knowledge Indexing")
    print("=" * 60)
    print(f"📅 Indexing last {DAYS_BACK} days")
    print(f"📂 Chroma path: {CHROMA_PATH}")
    print(f"📝 Channels: {', '.join(CHANNELS)}")
    print()
    
    for channel_name in CHANNELS:
        print(f"📡 Processing #{channel_name}...")
        
        channel_id = get_channel_id(channel_name)
        
        if not channel_id:
            print(f"  ❌ Channel #{channel_name} not found (check bot has access)")
            continue
        
        messages = fetch_messages(channel_id, channel_name, DAYS_BACK)
        
        if not messages:
            print(f"  ⚠️  No messages found")
            continue
        
        index_to_chroma(messages, channel_name)
    
    print()
    print("=" * 60)
    print("✅ Slack indexing complete!")
    print("=" * 60)

if __name__ == '__main__':
    main()
