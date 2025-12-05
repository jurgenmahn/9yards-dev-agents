# 9Yards Development Agents

Specialized development agent teams for Claude Code with knowledge integration, automated testing, and GitLab workflows.

## What This Does

Provides structured agent teams for **Python**, **Magento**, **PHP**, **JavaScript/Node.js**, and **SysAdmin** work. Each team has architects, developers, validators, and automation.

**Key Features:**
- **Knowledge System** - Agents search Slack/GitLab history before coding to reuse existing patterns
- **Orchestration** - Coordinator routes tasks, enforces testing, creates MRs automatically
- **Comprehensive Testing** - Playwright E2E tests including security checks (XSS, SQL injection)
- **Learning** - Stores solutions for future reference

## Quick Start

### 1. Add Marketplace & Install

```bash
/plugin marketplace add github:jurgenmahn/9yards-dev-agents
/plugin install 9yards-dev-agents@9yards-marketplace
```

### 2. Configure Environment

Edit `.claude/settings.json` in your project (or `~/.claude/settings.json` globally):

```json
{
  "env": {
    "PLAYWRIGHT_VIEWPORT": "1920x1080",
    "PLAYWRIGHT_BROWSER": "chromium",
    "MYSQL_DSN": "mysql://user:pass@localhost:3306/db?sslmode=disable",
    "POSTGRES_DSN": "postgres://user:pass@localhost:5432/db?sslmode=disable",
    "SLACK_MCP_XOXC_TOKEN": "xoxc-...",
    "SLACK_MCP_XOXD_TOKEN": "xoxd-...",
    "GITLAB_PERSONAL_ACCESS_TOKEN": "glpat-...",
    "GITLAB_API_URL": "https://git.9yards.nl/api/v4"
  },
  "enabledPlugins": {
    "9yards-dev-agents@9yards-marketplace": true
  }
}
```

**Optional YOLO Mode** (bypass all permissions):
```json
{
  "permissions": {
    "defaultMode": "bypassPermissions"
  },
  "alwaysThinkingEnabled": true
}
```

### 3. Setup Knowledge Indexing (Optional)

If you want agents to learn from Slack/GitLab history:

```bash
# Clone plugin source for indexing scripts
git clone https://github.com/jurgenmahn/9yards-dev-agents.git
cd 9yards-dev-agents

# Run installer (Ubuntu 24+)
./install.sh

# Configure tokens
cp .env.example .env
nano .env  # Add your tokens

# Index knowledge (first run - full reindex)
source .venv/bin/activate
python scripts/index-slack-knowledge.py --full-reindex
python scripts/index-gitlab-repos.py --full-reindex

# Setup automated indexing (runs incrementally)
./scripts/setup-cron.sh
```

Or use slash commands:
```bash
/index-slack    # Index Slack messages (incremental)
/index-gitlab   # Index GitLab repos (incremental)
```

**Note**: Indexing is incremental by default - only new/changed content is indexed, making subsequent runs very fast.

## Usage

### Load Agent Teams

```bash
/python      # Python development
/magento     # Magento 2 development
/php         # PHP development
/js          # JavaScript/Node.js
/sysadmin    # Infrastructure
```

### Example Workflow

```
You: "Add email validation to contact form"

Agent: 🔍 Checking knowledge base...
       Found: Utils/Validator.php pattern from MR #234
       Reuse this pattern? [Yes/No]

You: Yes

Agent: ✅ Implemented using existing pattern
       Run Playwright tests? [Yes/No]

You: Yes

Agent: ✅ Tests passed (12/12)
       🎯 Created GitLab MR: feature/contact-validation
       💾 Stored learning for future use
```

### Direct Task Assignment

```
"Use Python agents to create a CSV parser"
"Use Magento validator to run comprehensive tests"
"Have we implemented checkout customization before?"
"Show me similar implementations of X"
```

## Agent Teams

Each stack includes:

- **Architect** - Plans implementation, asks clarifying questions
- **Developer/Backend/Frontend** - Writes code
- **Database** - Handles schema changes
- **Validator** - Runs tests (unit, integration, E2E with Playwright)
- **Git** - Commits work when complete

**Orchestration Agents:**
- **Coordinator** - Routes tasks, queries knowledge, enforces checkpoints
- **Interrogative Planner** - Question-first planning for complex tasks

## MCP Servers

Configured automatically when environment variables are set:

| Server | Purpose | Required Env Vars |
|--------|---------|------------------|
| Memory | Agent memory/state | None |
| Chroma | Knowledge search | None |
| Playwright | Browser automation | `PLAYWRIGHT_*` |
| MySQL | Database queries | `MYSQL_DSN` |
| PostgreSQL | Database queries | `POSTGRES_DSN` |
| Slack | Team communication | `SLACK_MCP_*` (see below) |
| GitLab | MR automation | `GITLAB_*` |

## Getting Slack Tokens (Non-Standard)

Slack MCP requires browser session tokens:

### Get SLACK_MCP_XOXC_TOKEN:
1. Open Slack in browser, open Developer Console
2. Go to Console tab
3. Type `allow pasting` and press Enter
4. Paste and execute:
```javascript
JSON.parse(localStorage.localConfig_v2).teams[document.location.pathname.match(/^\/client\/([A-Z0-9]+)/)[1]].token
```
5. Copy the `xoxc-...` token

### Get SLACK_MCP_XOXD_TOKEN:
1. Switch to Application/Storage tab
2. Find cookie named `d`
3. Copy its value (that's the token)

**Alternative:** Create a Slack App with User OAuth token (`xoxp-...`) - see [Slack App Setup](https://api.slack.com/apps)

## Knowledge Indexing

### What Gets Indexed

**From Slack:**
- Messages from configured channels (last 90 days)
- Excludes: Bot messages, very short messages
- Stored with metadata: channel, timestamp, thread info

**From GitLab:**
- Code files (.php, .js, .vue, .py, .md, .xml)
- Commit messages (meaningful ones, last 500)
- Merge request descriptions (last 100)
- Excludes: vendor/, node_modules/, very large files

### Incremental Indexing

**Default Behavior** (fast, incremental updates):
- Only indexes new/changed content since last run
- Tracks state in `scripts/.indexer-state.json`
- Removes deleted files from knowledge base
- 10-1000x faster than full reindex

**First Run**:
```bash
python scripts/index-slack-knowledge.py --full-reindex
python scripts/index-gitlab-repos.py --full-reindex
```

**Subsequent Runs** (automatic or manual):
```bash
python scripts/index-slack-knowledge.py    # Only new messages
python scripts/index-gitlab-repos.py       # Only changed files
```

**When to Full Reindex**:
- After git force-push or history rewrite
- If state file becomes corrupted
- When switching to new Chroma database

### Configuration

Edit `.env`:
```bash
SLACK_BOT_TOKEN=xoxb-...
SLACK_CHANNELS=dev,magento,general  # Leave empty to index all accessible channels
SLACK_DAYS_BACK=90

GITLAB_PERSONAL_ACCESS_TOKEN=glpat-...
GITLAB_REPOS=group/project1,group/project2
```

### Automated Updates

```bash
# Setup cron jobs
./scripts/setup-cron.sh

# Schedules:
# - Slack: Nightly at 2 AM
# - GitLab: Weekly on Sunday at 3 AM
```

## Requirements

**Minimum:**
- Claude Code v2.0.0+
- Node.js 18+
- Git

**For Knowledge Indexing:**
- Python 3.12+
- Ubuntu 24+ (for install.sh)
- Docker (if testing with containers)

**MCP Dependencies:**
```bash
# Installed automatically by Claude Code
npx @playwright/mcp@latest --help
uvx chroma-mcp --help
```

## Troubleshooting

### Plugin Not Found
```bash
/plugin marketplace list  # Verify marketplace added
/plugin list             # Check installation
```

### MCP Not Working
```bash
/mcp                     # View MCP status
```

Check `.claude/settings.json` has environment variables set correctly.

### Agents Not Loading
```bash
/plugin list
# Should show: 9yards-dev-agents@9yards-marketplace [enabled]

# If disabled:
/plugin enable 9yards-dev-agents@9yards-marketplace
```

### Knowledge Indexing Fails

**Slack:** Check `SLACK_BOT_TOKEN` has `channels:history`, `channels:read` permissions
**GitLab:** Check `GITLAB_PERSONAL_ACCESS_TOKEN` has `read_repository` scope

**Test manually:**
```bash
source .venv/bin/activate
python scripts/index-slack-knowledge.py  # Check output
tail logs/slack-index.log               # View errors
```

### Database Connection Issues

**Format:**
```
MySQL:    mysql://user:pass@host:port/database?sslmode=disable
Postgres: postgres://user:pass@host:port/database?sslmode=disable
```

**Test:**
```bash
mysql -u user -p -h host -P port database
psql "postgres://user:pass@host:port/database"
```

## Team Setup

**Commit to git** (`.claude/settings.json`):
```json
{
  "enabledPlugins": {
    "9yards-dev-agents@9yards-marketplace": true
  }
}
```

**Personal config** (`.claude/settings.local.json` - NOT committed):
```json
{
  "env": {
    "MYSQL_DSN": "mysql://...",
    "SLACK_MCP_XOXC_TOKEN": "xoxc-..."
  }
}
```

Add to `.gitignore`:
```
.claude/settings.local.json
```

Team members: Pull repo → Trust folder in Claude Code → Create their own `settings.local.json` → Done.

## Project Structure

```
9yards-dev-agents/
├── .claude-plugin/         # Plugin metadata
│   ├── plugin.json        # MCP servers, agents, commands
│   └── marketplace.json   # Publishing info
├── .claude/
│   └── settings.json      # Environment variables
├── agents/
│   ├── orchestration/     # Coordinator, planner
│   ├── python/           # Architect, developer, validator, git
│   ├── magento/          # Architect, backend, frontend, database, validator, git
│   ├── php/              # Architect, backend, frontend, database, validator, git
│   ├── javascript/       # Architect, backend, frontend, database, validator, git
│   └── sysadmin/         # Planner, implementer, database, validator, git
├── skills/               # Reusable knowledge
│   ├── docker-operations.md
│   ├── query-knowledge.md
│   └── testing-protocols.md
├── commands/             # Slash commands
│   ├── /python, /magento, /php, /js, /sysadmin
│   ├── /index-slack
│   └── /index-gitlab
├── scripts/              # Knowledge indexing
│   ├── index-slack-knowledge.py
│   ├── index-gitlab-repos.py
│   └── setup-cron.sh
└── install.sh           # Ubuntu 24+ setup
```

## License

MIT
