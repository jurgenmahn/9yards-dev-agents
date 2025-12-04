---
description: Load system administration agents (planner, implementer, database, validator, git)
---

# SysAdmin Agent Set

Loading system administration agents...

use agents/sysadmin/*

You now have access to:
- **Planner**: Analyze infrastructure requirements and security
- **Implementer**: Create bash/Python scripts, configs, automation
- **Database**: Handle database admin tasks (backup, replication, tuning)
- **Validator**: Test scripts, verify services, check logs
- **Git**: Commit infrastructure changes

Ready for system administration tasks.
```

## Update Plugin Structure

Your plugin should look like:
```
9yards-dev-agents/
├── .claude-plugin/
│   ├── plugin.json
│   └── marketplace.json
├── commands/              # ADD THIS
│   ├── python.md
│   ├── magento.md
│   ├── php.md
│   ├── javascript.md
│   ├── js.md             # Alias
│   └── sysadmin.md
├── agents/
│   ├── python/
│   ├── magento/
│   ├── php/
│   ├── javascript/
│   └── sysadmin/
├── .mcp.json
└── README.md