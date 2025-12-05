---
description: Index GitLab repositories into knowledge base
---

Run the GitLab indexing script to update the Chroma database with code, commits, and merge requests.

## What This Does

- Clones/pulls configured GitLab repositories
- Indexes code files (PHP, JS, Vue, Python, etc.)
- Indexes meaningful commit messages
- Indexes merge request descriptions
- Allows agents to find similar implementations and patterns

## Requirements

- GITLAB_PERSONAL_ACCESS_TOKEN must be set in .env
- Python virtual environment must be activated
- Chroma MCP must be configured
- Git must be installed

## Usage

```bash
source .venv/bin/activate
python scripts/index-gitlab-repos.py
```

## Configuration

Edit `.env` to configure:
- `GITLAB_PERSONAL_ACCESS_TOKEN` - Your GitLab access token
- `GITLAB_API_URL` - Your GitLab API URL (default: https://git.9yards.nl/api/v4)
- `GITLAB_REPOS` - Comma-separated list (e.g., group/project1,group/project2)
- `CHROMA_DATA_DIR` - Where to store Chroma data

## Expected Output

```
🔍 GitLab Codebase Indexing
📂 Chroma path: ~/claude-code-data/chroma
📦 Repositories: 2

📦 Processing group/project1...
  📥 Cloning repository...
  📄 Indexing code files... indexed 245, skipped 89
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

## Troubleshooting

- **Project not found**: Check GITLAB_PERSONAL_ACCESS_TOKEN has access
- **Clone failed**: Verify repository path and network access
- **Import error**: Run `pip install chromadb gitpython python-gitlab requests`
- **Permission denied**: Check token has read_repository scope

## When to Run

- Initial setup: After installing the plugin
- Regular updates: Automatically via cron (weekly on Sunday at 3 AM)
- After major development: When significant code changes are merged
- Manual refresh: When you need latest code patterns indexed
