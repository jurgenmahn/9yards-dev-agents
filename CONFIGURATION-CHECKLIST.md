# Configuration Checklist

Use this checklist after running `./install.sh`.

## Environment Setup

- [ ] Copied `.env.example` to `.env`
- [ ] Set `GITLAB_PERSONAL_ACCESS_TOKEN`
- [ ] Set `GITLAB_API_URL` (https://git.9yards.nl/api/v4)
- [ ] Set `SLACK_BOT_TOKEN` (for indexing)
- [ ] Set `SLACK_MCP_XOXC_TOKEN` (for agent communication)
- [ ] Set `SLACK_MCP_XOXD_TOKEN` (for agent communication)
- [ ] Set `MYSQL_DSN` (if using MySQL)
- [ ] Set `POSTGRES_DSN` (if using PostgreSQL)
- [ ] Set `GITLAB_REPOS` (comma-separated list)
- [ ] Set `SLACK_CHANNELS` (default: dev,magento,general)
- [ ] Set `PLAYWRIGHT_VIEWPORT`, `PLAYWRIGHT_BROWSER`, `PLAYWRIGHT_USER_AGENT`

## MCP Server Verification

Test each MCP server:

```bash
# Memory
npx -y @modelcontextprotocol/server-memory --help

# Chroma
uvx chroma-mcp --help

# Playwright
npx @playwright/mcp@latest --help

# Database
npx @bytebase/dbhub --help

# Slack
npx slack-mcp-server@latest --help

# GitLab
npx @zereight/mcp-gitlab --help
```

- [ ] All MCP servers respond without errors

## Initial Indexing

Run indexers manually first:

```bash
source .venv/bin/activate

# Slack indexing
python scripts/index-slack-knowledge.py

# GitLab indexing
python scripts/index-gitlab-repos.py
```

- [ ] Slack indexing completed without errors
- [ ] GitLab indexing completed without errors
- [ ] No errors in logs/slack-index.log
- [ ] No errors in logs/gitlab-index.log

## Verify Chroma Data

```bash
# Check Chroma directory
ls -lh ~/claude-code-data/chroma/

# Should see database files
```

- [ ] Chroma database files exist
- [ ] Collections created (slack_knowledge, codebase_knowledge)

## Cron Jobs

```bash
./scripts/setup-cron.sh

# Verify
crontab -l
```

- [ ] Cron jobs installed
- [ ] Slack indexing scheduled: nightly at 2 AM
- [ ] GitLab indexing scheduled: weekly on Sunday at 3 AM

## Docker Verification

```bash
docker --version
docker compose version

# Test BuildKit
DOCKER_BUILDKIT=1 docker build --help
```

- [ ] Docker installed and working
- [ ] Docker Compose v2+ installed
- [ ] User in docker group (may need logout/login)
- [ ] BuildKit enabled

## Claude Code Plugin

- [ ] `.claude-plugin/plugin.json` has all MCP servers configured
- [ ] Environment variables referenced with `${VAR_NAME}`
- [ ] No syntax errors in JSON
- [ ] Agents array includes `./agents/orchestration/*.md`
- [ ] Skills array includes `./skills/*.md`

## Test Agent Workflow

Try a simple task with coordinator:

```
"Add a console.log to test.js"
```

Expected flow:
1. Coordinator queries Chroma for context
2. Routes to JavaScript developer
3. Makes change
4. Offers testing
5. Stores learning

- [ ] Coordinator agent activates
- [ ] Knowledge query happens
- [ ] Task completes successfully
- [ ] Learning stored in Chroma

## Logs

Check log files:

```bash
ls -lh logs/
tail logs/slack-index.log
tail logs/gitlab-index.log
```

- [ ] Log directory exists
- [ ] Logs are being written
- [ ] No critical errors in logs

## Permissions

```bash
# All scripts executable
chmod +x install.sh
chmod +x scripts/*.sh
chmod +x scripts/*.py
```

- [ ] Scripts are executable

## Documentation

- [ ] Read `README.md`
- [ ] Read `MCP-README.md`
- [ ] Read `CODING-AGENT-TASK-DESCRIPTION.md`
- [ ] Reviewed agent files in `./agents/orchestration/`
- [ ] Reviewed skills in `./skills/`

## Optional: Playwright Browsers

If using Playwright MCP extensively:

```bash
npx playwright install
npx playwright install-deps
```

- [ ] Chromium installed
- [ ] Firefox installed
- [ ] WebKit installed (optional)

## Troubleshooting

If issues:

1. Check `.env` file exists and is loaded
2. Verify tokens have correct permissions
3. Check logs in `./logs/`
4. Test MCP servers individually
5. Ensure Docker services running
6. Verify Python venv activated
7. Run `./install.sh` again if packages missing

## Ready!

Once all checkboxes are complete, you're ready to use the enhanced agent system.

Test with:
```
"Show me what you know about checkout customization"
```

Agent should query Chroma and present findings.
