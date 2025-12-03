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

## Installation

### 1. Install the Plugin

```bash
# Clone into your plugins directory (or install via marketplace if available)
git clone https://github.com/9yards/9yards-dev-agents.git
```

### 2. Configure MCP Servers

Copy the example environment file and update with your local settings:

```bash
cp .mcp-env-example.json .mcp-env.json
```

Edit `.mcp-env.json` to provide:

- Database connection strings (DSN)
- Playwright configuration

## Usage

### invoking an Agent

Ask Claude to use a specific agent set for your task.

**Example Prompts:**

- "Use the **Python agents** to create a script that parses CSV files and inserts them into MySQL."
- "I need to create a new **Magento module** for custom checkout steps. Please use the Magento architect agent to plan it."
- "Use the **SysAdmin agents** to set up a new Nginx server with SSL."

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
- Playwright requirements:

```bash
npm install -g playwright
npm install -g @playwright/mcp@0.0.33
npx playwright install chromium firefox webkit
npx playwright install-deps
```
