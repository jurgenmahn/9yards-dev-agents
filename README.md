# 9Yards Development Agents Plugin

A collection of specialized development agent sets for Claude, designed to streamline workflows across different technology stacks.

## Overview

This plugin provides structured agent teams for:

- **Python:** Scripting, automation, and internal tools
- **Magento:** Module development, frontend customization, and architecture
- **PHP:** General backend/frontend development
- **JavaScript:** React/Vue frontend and Node.js backend
- **SysAdmin:** Infrastructure planning, implementation, and maintenance

Each discipline has a dedicated team of agents (Planner/Architect, Developer/Backend/Frontend, Database, Validator, Git) to handle the full lifecycle of a task.

## ✨ New Features (v1.3.0)

### Orchestration Layer
- **Coordinator Agent**: Routes tasks, enforces checkpoints, integrates knowledge
- **Interrogative Planner**: Question-first planning with historical context
- **Enhanced Validators**: Comprehensive testing with Playwright E2E tests

### Knowledge System
- **Slack Indexing**: Search 90 days of team discussions
- **GitLab Indexing**: Code, commits, and MR history
- **Semantic Search**: Find similar implementations and solutions automatically
- **Automatic Learning**: Stores patterns and decisions for future reference

### MCP Servers
- **Memory**: Persistent knowledge graph for agent memory
- **Chroma**: Vector database with full-text search
- **Playwright**: Browser automation for E2E testing
- **Database**: MySQL/PostgreSQL query and management
- **Slack**: Team communication integration
- **GitLab**: Repository and MR management

### Skills Library
- **Docker Operations**: Container management and debugging
- **Query Knowledge**: How to search historical context
- **Testing Protocols**: Comprehensive test patterns and security checks

## Installation

### Quick Setup (Ubuntu 24+)

```bash
# 1. Clone the repository
git clone https://github.com/jurgenmahn/9yards-dev-agents.git
cd 9yards-dev-agents

# 2. Run the installer (installs dependencies, MCP servers, etc.)
./install.sh

# 3. Configure environment
cp .env.example .env
nano .env  # Add your API tokens and configuration

# 4. Run initial indexing
source .venv/bin/activate
python scripts/index-slack-knowledge.py
python scripts/index-gitlab-repos.py

# 5. Setup automated indexing (optional)
./scripts/setup-cron.sh
```

See `INSTALL.md` for detailed instructions and troubleshooting.

### Configuration

Edit `.env` to provide:
- GitLab personal access token
- Slack bot tokens
- Database connection strings
- Repository and channel lists for indexing

## Usage

### Development Workflow

The enhanced workflow automatically:

1. **Coordinator Agent** assesses task complexity
2. **Queries knowledge base** for similar work and past solutions
3. **Routes to specialist agent** (Magento, PHP, JS, Python, SysAdmin)
4. **Enforces testing checkpoints** before commits
5. **Creates GitLab MR** automatically
6. **Stores learnings** for future use

**Example Prompts:**

- "Add email validation to the contact form" ← Coordinator will search for existing patterns first
- "Create a new Magento module for custom checkout steps" ← Planner will ask clarifying questions
- "Fix the cache warming bug in production" ← Will search for similar past issues
- "Optimize the product listing page performance" ← Will check past performance work

### Querying Knowledge

Ask agents to search historical context:

- "Have we implemented this before?"
- "What's our pattern for X?"
- "Show me similar code"
- "Find discussions about Y problem"

Agents automatically search before coding.

### Direct Agent Invocation

You can also directly request specific agent sets:

- "Use the **Python agents** to create a CSV parser script"
- "Use the **Magento validator** to run comprehensive tests"
- "Use the **SysAdmin agents** to set up a new Nginx server"

### Workflow

1. **Plan/Architect:** The first agent analyzes requirements and creates a plan.
2. **Develop/Implement:** Developer agents write the code/config.
3. **Database:** Database agents handle schema changes if needed.
4. **Validate:** Validator agents run tests and verify functionality.
5. **Git:** The Git agent commits the work once validated.

## Directory Structure

```
9yards-dev-agents/
├── .claude-plugin/       # Plugin metadata
├── agents/               # Agent definitions
│   ├── python/
│   ├── magento/
│   ├── php/
│   ├── javascript/
│   └── sysadmin/
├── .mcp.json             # MCP server configuration
├── MCP-README.md         # MCP documentation
└── README.md             # This file
```

## Requirements

- Claude Code v2.0.0+
- Node.js 18+ (for MCP servers)
- Git
- Relevant runtime environments (Python, PHP, etc.) for the code you generate
- uv & uvw 
```bash
pip install uv
```
- Playwright requirements:
```bash
npm install -g playwright
npm install -g @playwright/mcp@0.0.33
npx playwright install chromium firefox webkit
npx playwright install-deps
```

## Quick Start with Slash Commands

Load agent sets instantly:
```bash
/python      # Load Python agents
/magento     # Load Magento agents
/php         # Load PHP agents
/js          # Load JavaScript/Node.js agents
/sysadmin    # Load SysAdmin agents
```

All commands have autocomplete - just type `/` and start typing.

### Example Workflow
```bash
$ claude
> /magento
# Magento agents loaded

> Create a custom checkout step for express shipping

# Claude uses:
# - Architect to plan the module
# - Backend to implement PHP
# - Frontend to create templates
# - Database for schema
# - Validator to test in browser
# - Git to commit when done
```