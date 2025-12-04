# Claude Code Plugin Installation - Quick Guide

## First Time Setup

### 1. Add Marketplace

```bash
# Add the 9yards marketplace
/plugin marketplace add jurgenmahn/9yards-dev-agents
```

### 2. Install Plugin

```bash
# Install the plugin
/plugin install 9yards-dev-agents@9yards-marketplace
```

### 3. Configure MCP Settings

Create `.claude/settings.local.json` in your project:

```bash
mkdir -p .claude
nano .claude/settings.local.json
```

Add configuration:

```json
{
  "env": {
    "PLAYWRIGHT_VIEWPORT": "1920,1080",
    "PLAYWRIGHT_BROWSER": "chrome",
    "PLAYWRIGHT_USER_AGENT": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
    "MYSQL_DSN": "mysql://user:password@localhost:3306/database?sslmode=disable",
    "POSTGRES_DSN": "postgres://user:password@localhost:5432/database?sslmode=disable"
  }
}
```

**Add to .gitignore:**
```bash
echo ".claude/settings.local.json" >> .gitignore
```

Done. Agents are ready to use.

---

## Using Agents

### Select Agent Set

```bash
# For Python work
use agents/python/*

# For Magento work
use agents/magento/*

# For PHP work
use agents/php/*

# For JavaScript work
use agents/javascript/*

# For sysadmin work
use agents/sysadmin/*
```

### Example Task

```
You: Create a Python script to sync products from Mplus POS to MySQL

Claude will automatically:
1. Use planner to break down task
2. Use developer to write code
3. Use database for schema/migrations
4. Use validator to test with sample data
5. Use git to commit when complete
```

---

## Marketplace Commands

### List Available Marketplaces
```bash
/plugin marketplace list
```

### Add Marketplace

**From GitHub:**
```bash
/plugin marketplace add github:username/repo-name
```

**From URL:**
```bash
/plugin marketplace add https://raw.githubusercontent.com/user/repo/main/.claude-plugin/marketplace.json
```

**From Local Path:**
```bash
/plugin marketplace add /path/to/marketplace
```

### Remove Marketplace
```bash
/plugin marketplace remove marketplace-name
```

---

## Plugin Management

### List All Plugins
```bash
/plugin list
```

### Install Plugin
```bash
/plugin install plugin-name@marketplace-name
```

### Update Plugin
```bash
/plugin update plugin-name@marketplace-name
```

### Uninstall Plugin
```bash
/plugin uninstall plugin-name@marketplace-name
```

### Enable/Disable Plugin
```bash
/plugin enable plugin-name@marketplace-name
/plugin disable plugin-name@marketplace-name
```

---

## Auto-Install for Team

Add to project's `.claude/settings.json` (can be committed to git):

```json
{
  "marketplaces": ["github:jurgenmahn/9yards-dev-agents"],
  "plugins": {
    "9yards-dev-agents@9yards-marketplace": "enabled"
  }
}
```


When teammates trust the folder, plugins install automatically.

---

## YOLO mode - Dangerous

`.claude/settings.json`

```json
{
  "permissions": {
    "allow": ["Read", "Write", "Edit", "Bash(*)"]
  }
}
```


## Check MCP Status

### View Connected MCPs
```bash
/mcp
```

### Debug MCP Issues
```bash
claude --mcp-debug
```

### Test MCP Connection

```bash
# In Claude Code, try:
use agents/python/validator
Navigate to http://localhost:8000 and take screenshot

# If Playwright works, MCP is configured correctly
```

---

## Troubleshooting

### Plugin Not Showing
```bash
# Reinstall
/plugin uninstall 9yards-dev-agents@9yards-marketplace
/plugin install 9yards-dev-agents@9yards-marketplace

# Verify installation
/plugin list
```

### MCP Not Connecting

**Check DSN format:**
```
MySQL:    mysql://user:pass@host:port/database?sslmode=disable
Postgres: postgres://user:pass@host:port/database?sslmode=disable
```

**Test manually:**
```bash
mysql -u user -p -h localhost -P 3306 database
psql "postgres://user:pass@localhost:5432/database"
```

### Agents Not Available

**Check loaded agents:**
```bash
# List available commands/agents
/help
```

**Verify plugin is enabled:**
```bash
/plugin list
# Should show: 9yards-dev-agents@9yards-marketplace [enabled]
```

---

## Per-Project Configuration

Each project can have different MCP settings:

**Project A (Magento):**
`.claude/settings.local.json`:
```json
{
  "env": {
    "MYSQL_DSN": "mysql://magento_user:pass@localhost:3306/magento_db?sslmode=disable"
  }
}
```

**Project B (Node.js + PostgreSQL):**
`.claude/settings.local.json`:
```json
{
  "env": {
    "POSTGRES_DSN": "postgres://app_user:pass@localhost:5432/app_db?sslmode=disable"
  }
}
```

Claude Code automatically uses the right settings per project.

---

## Common Workflows

### Daily Development
```bash
# Start Claude Code in project
cd /path/to/project
claude

# Select appropriate agents
use agents/magento/*

# Work normally - agents handle everything
```

### Switch Between Projects
```bash
# Agents and MCP settings automatically adjust per project
# No manual configuration needed if .claude/settings.local.json exists
```

### Share with Team
```bash
# Just commit .claude/settings.json (NOT settings.local.json)
git add .claude/settings.json
git commit -m "Add Claude Code plugin configuration"
git push

# Team members:
# 1. Pull repo
# 2. Trust folder in Claude Code
# 3. Create their own .claude/settings.local.json
# 4. Done
```

---

That's it. Direct and functional.