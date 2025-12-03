Structure
9yards-dev-agents/
├── .claude-plugin/
│ ├── plugin.json
│ └── marketplace.json
├── agents/
│ ├── python/
│ │ ├── planner.md
│ │ ├── developer.md
│ │ ├── database.md
│ │ ├── validator.md
│ │ └── git.md
│ ├── magento/
│ │ ├── architect.md
│ │ ├── backend.md
│ │ ├── frontend.md
│ │ ├── database.md
│ │ ├── validator.md
│ │ └── git.md
│ ├── php/
│ │ └── [same structure]
│ ├── javascript/
│ │ └── [same structure]
│ └── sysadmin/
│ └── [same structure]
├── .mcp.json
└── README.md
Files
.claude-plugin/plugin.json:
json{
"name": "9yards-dev-agents",
"version": "1.0.0",
"description": "Development agent sets for Python, Magento, PHP, JavaScript, and SysAdmin workflows with integrated testing and git automation",
"author": {
"name": "9Yards",
"email": "info@nine-yards.nl",
"url": "https://nine-yards.nl"
},
"homepage": "https://github.com/YOUR_USERNAME/9yards-dev-agents",
"repository": "https://github.com/YOUR_USERNAME/9yards-dev-agents",
"license": "MIT",
"keywords": ["development", "magento", "python", "php", "javascript", "sysadmin", "agents"],
"agents": [
"agents/python/*.md",
"agents/magento/*.md",
"agents/php/*.md",
"agents/javascript/*.md",
"agents/sysadmin/*.md"
]
}
.claude-plugin/marketplace.json:
json{
"name": "9yards-marketplace",
"owner": {
"name": "9Yards",
"email": "info@nine-yards.nl"
},
"metadata": {
"description": "9Yards development agent collections",
"version": "1.0.0"
},
"plugins": [
{
"name": "9yards-dev-agents",
"version": "1.0.0",
"source": {
"type": "git",
"url": "https://github.com/YOUR_USERNAME/9yards-dev-agents.git"
}
}
]
}
.mcp.json (bundled MCP servers):
json{
"mcpServers": {
"puppeteer": {
"command": "npx",
"args": ["-y", "@modelcontextprotocol/server-puppeteer"]
},
"filesystem": {
"command": "npx",
"args": ["-y", "@modelcontextprotocol/server-filesystem", "${workspaceFolder}"]
},
"brave-search": {
"command": "npx",
"args": ["-y", "@modelcontextprotocol/server-brave-search"],
"env": {
"BRAVE_API_KEY": "${env:BRAVE_API_KEY}"
}
}
}
}
Example agent file (agents/python/developer.md):
markdown---
description: Write Python code for scripts and internal tools
capabilities: ["python-development", "scripting", "automation", "internal-tools"]

---

# Python Developer Agent

Implement solutions using modern Python (3.10+). Prioritize clarity and ease of modification. Include basic error handling and logging. Use type hints.

## Key Instructions

- Place all test scripts in `workroot/dev/claude/`
- Keep documentation minimal - README should cover: what it does, how to run it, CLI params, and any gotchas. That's it.
- Focus on maintainability for internal tools over premature optimization
- Use standard library when possible
- Add type hints for all function signatures

## When to Invoke

Use this agent when implementing Python code after planning phase is complete.
Example validator agent (agents/python/validator.md):
markdown---
description: Test and validate Python implementations
capabilities: ["testing", "validation", "quality-assurance", "browser-testing"]

---

# Python Validator Agent

Actually run the script/tool with realistic inputs. Verify outputs (files created, database entries, API responses). Check error handling with bad inputs.

## Testing Requirements

- Run the script/tool with realistic test data
- Verify all outputs (files, database entries, API calls)
- Test error handling with invalid inputs
- If there's a web UI, use Puppeteer MCP to test browser functionality
- Check for common issues (permissions, missing dependencies, race conditions)

## Reporting

Report what you tested and actual results:

- ✅ What worked
- ❌ What failed (with error messages)
- ⚠️ Edge cases that need attention
- 📝 Suggestions for improvements

## When to Invoke

Use after implementation is complete to validate functionality before git commit.
Example git agent (agents/python/git.md):
markdown---
description: Commit completed work with clear messages
capabilities: ["git", "version-control", "commit"]

---

# Git Agent

After user's task is complete, commit all changes. Write concise commit messages: what changed and why in 1-2 lines.

## Commit Message Format

Format: `verb: short description`

Examples:

- `Add: user import script with CSV validation`
- `Fix: handle missing email fields in data processor`
- `Update: improve error messages in API client`
- `Refactor: extract database logic to separate module`

## Process

1. Check `git status` to see what changed
2. Review changes to understand scope
3. `git add` relevant files
4. Commit with clear, concise message
5. Confirm commit was successful

## When to Invoke

Use when the user's requested task is complete and code is validated.
Installation for Team

1. Create GitHub repo:
   bash# Initialize and push
   git init
   git add .
   git commit -m "Initial commit: 9Yards development agents"
   git remote add origin git@github.com:YOUR_USERNAME/9yards-dev-agents.git
   git push -u origin main
2. Team members install:
   bash# Add marketplace
   /plugin marketplace add github:YOUR_USERNAME/9yards-dev-agents

# Install plugin

/plugin install 9yards-dev-agents@9yards-marketplace 3. Use specific agent set:
bash# For Python work
use agents/python/\*

# For Magento work

use agents/magento/\*

# Mix and match if needed

use agents/python/validator agents/javascript/frontend
Auto-install in Projects
Add to project's .claude/settings.json:
json{
"marketplaces": ["github:YOUR_USERNAME/9yards-dev-agents"],
"plugins": {
"9yards-dev-agents@9yards-marketplace": "enabled"
}
}
When teammates trust the folder, agents install automatically.
MCP Server Notes
The bundled MCPs:

puppeteer: For validator agents to test web UIs
filesystem: Access project files (already available by default, but explicit)
brave-search: Optional web search for documentation lookup

Team members need BRAVE_API_KEY env var if using brave-search. Add to ~/.zshrc or ~/.bashrc:
bashexport BRAVE_API_KEY="your-key-here"
Now you have a single repo URL to share. Team members run one command and get all agent sets + MCP servers configured.
