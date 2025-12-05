#!/bin/bash
# Setup cron jobs for indexing

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_PYTHON="$PROJECT_DIR/.venv/bin/python"

# Create cron entries
CRON_ENTRIES=$(cat <<CRONEOF
# 9Yards Agent Knowledge Indexing
# Slack indexing - nightly at 2 AM
0 2 * * * cd $PROJECT_DIR && $VENV_PYTHON scripts/index-slack-knowledge.py >> logs/slack-index.log 2>&1

# GitLab indexing - weekly on Sunday at 3 AM
0 3 * * 0 cd $PROJECT_DIR && $VENV_PYTHON scripts/index-gitlab-repos.py >> logs/gitlab-index.log 2>&1
CRONEOF
)

echo "📅 Setting up cron jobs..."
echo "$CRON_ENTRIES"
echo ""
echo "Add these to your crontab? (y/n)"
read -r response

if [[ "$response" =~ ^[Yy]$ ]]; then
    (crontab -l 2>/dev/null; echo "$CRON_ENTRIES") | crontab -
    echo "✅ Cron jobs installed"
    echo ""
    echo "View with: crontab -l"
else
    echo "⏭️  Skipped. Add manually with: crontab -e"
fi
