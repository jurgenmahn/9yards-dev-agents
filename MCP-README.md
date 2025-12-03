# 9Yards MCP Servers

This plugin bundles several Model Context Protocol (MCP) servers to provide agents with necessary capabilities.

## Included Servers

### 1. Memory (`@modelcontextprotocol/server-memory`)

- **Purpose:** Persist knowledge across sessions
- **Usage:** Agents store project context, decisions, and learnings
- **Storage:** `.claude/memory-storage.json`

### 2. Filesystem (`@modelcontextprotocol/server-filesystem`)

- **Purpose:** Read/write files in the project
- **Usage:** Agents create code files, read configs, and manage project structure
- **Scope:** Restricted to the project directory

### 3. Git (`@cyanheads/git-mcp-server`)

- **Purpose:** Git operations
- **Usage:** Agents check status, stage files, and commit changes
- **Capabilities:** status, add, commit, log, diff

### 4. Fetch (`@tokenizin/mcp-npx-fetch`)

- **Purpose:** Web access
- **Usage:** Agents can read documentation, check external APIs, or download resources
- **Privacy:** Runs locally via npx

### 5. Playwright (`@playwright/mcp`)

- **Purpose:** Browser automation and testing
- **Usage:** Validator agents run end-to-end tests, take screenshots, and verify UI behavior
- **Config:** Headless by default, saves artifacts to `.claude/playwright/`

### 6. Database Servers (`@bytebase/dbhub`)

- **MySQL:** Connects to MySQL/MariaDB databases
- **PostgreSQL:** Connects to PostgreSQL databases
- **Usage:** Database agents manage schema; Validator agents verify data

## Configuration

Configuration is handled in `.mcp.json`. Environment variables (like database DSNs) should be set in your Claude desktop configuration or `.mcp-env.json` (gitignored).

See `.mcp-env-example.json` for required environment variables.
