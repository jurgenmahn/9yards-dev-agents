---
description: Index GitLab repositories into knowledge base
---

Run the GitLab indexing script to update the Chroma database with code, commits, and merge requests.

**By default, only changed files since the last run are indexed (incremental mode).**

## What This Does

- Clones/pulls configured GitLab repositories
- Indexes code files (PHP, JS, Vue, Python, etc.)
- Tracks changes to index only modified files
- Removes deleted files from Chroma
- Indexes commits and MRs (on first run or full reindex)
- Allows agents to find similar implementations and patterns

## Requirements

- GITLAB_PERSONAL_ACCESS_TOKEN must be set in .env
- Python virtual environment must be activated
- Chroma MCP must be configured
- Git must be installed

## Usage

### Incremental Update (Default)
Only indexes changed files since last run:
```bash
source .venv/bin/activate
python scripts/index-gitlab-repos.py
```

### Full Reindex
Force complete reindexing from scratch:
```bash
source .venv/bin/activate
python scripts/index-gitlab-repos.py --full-reindex
```

## Configuration

Edit `.env` to configure:
- `GITLAB_PERSONAL_ACCESS_TOKEN` - Your GitLab access token
- `GITLAB_API_URL` - Your GitLab API URL (default: https://git.9yards.nl/api/v4)
- `GITLAB_REPOS` - Comma-separated list (e.g., group/project1,group/project2)
- `CHROMA_DATA_DIR` - Where to store Chroma data

## Expected Output

**Incremental Mode:**
```
🔍 GitLab Codebase Indexing
📅 Mode: incremental update
📂 Chroma path: ~/claude-code-data/chroma
📦 Repositories: 2

📦 Processing group/project1...
  📥 Pulling latest changes...
  📄 Indexing 8 changed files... indexed 5, skipped 3
  🗑️  Removing 2 deleted files... removed 2
  ℹ️  Skipping commits/MRs (incremental mode)

✅ GitLab indexing complete!
```

**Full Reindex Mode:**
```
🔄 Full reindex requested - resetting state...
📅 Mode: FULL reindex
📂 Chroma path: ~/claude-code-data/chroma
📦 Repositories: 2

📦 Processing group/project1...
  📥 Cloning repository...
  📄 Indexing all code files... indexed 245, skipped 89
  📝 Indexing commits... indexed 387, skipped 113
  🔀 Indexing merge requests... indexed 42, skipped 8

✅ GitLab indexing complete!
```

## What Gets Indexed

**Code Files:**
- Extensions: .php, .js, .vue, .py, .md, .xml, .json
- Excludes: vendor/, node_modules/, .git/, var/, pub/static/
- Size limits: 100 bytes minimum, 100KB maximum

**Commits:**
- Last 500 commits on main branch
- Excludes merge commits and trivial messages
- Minimum message length: 20 characters

**Merge Requests:**
- Last 100 merged MRs
- Includes title and description
- Links to original MR for reference

## How Incremental Indexing Works

- **State tracking**: Last indexed commit SHA stored in `scripts/.indexer-state.json`
- **First run**: Indexes all code files, commits, and MRs
- **Subsequent runs**:
  - Uses `git diff` to find changed/deleted files since last commit
  - Only indexes those changed files
  - Removes deleted files from Chroma
  - Skips commits/MRs indexing (they rarely change)
- **Performance**: Incremental runs are 50-1000x faster than full reindex
- **Deletion handling**: Automatically removes deleted files from knowledge base

## Troubleshooting

- **Project not found**: Check GITLAB_PERSONAL_ACCESS_TOKEN has access
- **Clone failed**: Verify repository path and network access
- **Import error**: Run `pip install chromadb gitpython python-gitlab requests`
- **Permission denied**: Check token has read_repository scope
- **Git history changed**: Run with `--full-reindex` after force-push
- **State file corrupted**: Delete `scripts/.indexer-state.json` and run with `--full-reindex`

## When to Run

- **Initial setup**: Run with `--full-reindex` after installing the plugin
- **Regular updates**: Run daily or on every push (incremental mode is fast)
- **After force-push**: Run with `--full-reindex` if git history was rewritten
- **After state issues**: Run with `--full-reindex` if state is out of sync
- **Manual refresh**: Run incrementally when you need latest code patterns
