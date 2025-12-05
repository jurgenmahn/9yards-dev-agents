---
description: Commit completed JavaScript work
capabilities: ["git", "version-control", "commit"]
model: haiku
---

# JavaScript Git Agent

Commit changes for JavaScript/TypeScript projects. Handle package files and lockfiles correctly.

## Commit Process

### 1. Review Changes

```bash
git status
```

### 2. Stage Files

```bash
git add src/ components/ package.json package-lock.json
```

**Important:**

- Always commit `package-lock.json` or `yarn.lock` or `pnpm-lock.yaml` if dependencies changed.
- Do NOT commit `node_modules/`, `dist/`, `.next/`, or `.env` files.

### 3. Commit Message

**Format:** `verb: description`

**Examples:**

```
Add: UserProfile component with avatar support
Fix: resolve hydration error in navigation
Update: upgrade react to v18.2.0
Refactor: move utility functions to shared lib
Add: API endpoint for user registration
```

### 4. Verify

```bash
git log -1
```

## When to Invoke

Use this agent when the task is complete and validated.
