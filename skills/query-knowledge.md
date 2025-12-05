# Query Knowledge Skill

**PURPOSE**: How and when to query Chroma MCP for historical context

## When to Query

### ALWAYS Query Before:
- Implementing any new feature
- Fixing a bug (might be solved before)
- Making architectural decisions
- Writing significant code (>100 LOC)

### Query for:
- Similar implementations
- Known gotchas
- Team patterns/conventions
- Past decisions and reasoning
- Error resolutions

## Chroma Collections

### 1. slack_knowledge
**Content**: Indexed Slack messages (90 days)
**Channels**: #dev, #magento, #general

```bash
# Query via Chroma MCP
COLLECTION: slack_knowledge
QUERY: "<search terms>"
LIMIT: 5

# Example queries:
- "Magento cache issues"
- "Vue composable patterns"
- "checkout customization"
```

### 2. codebase_knowledge
**Content**: Code files, commits, merge requests
**Sources**: GitLab repositories

```bash
# Query via Chroma MCP
COLLECTION: codebase_knowledge
QUERY: "<what you're looking for>"
FILTER:
  metadata.type = "code" | "commit" | "merge_request"
  metadata.language = "php" | "js" | "vue"
LIMIT: 5

# Example queries:
- QUERY: "checkout observer" FILTER: type="code", language="php"
- QUERY: "Vue API composable" FILTER: type="code", language="js"
- QUERY: "payment method" FILTER: type="merge_request"
```

## Query Workflow

### Step 1: Extract Key Terms
From task: "Add email validation to contact form"
Key terms: email validation, contact form, form validation

### Step 2: Query Both Collections
```markdown
# Slack query
QUERY: "email validation form"
RESULT: Discussion about regex patterns, bug fixes

# Codebase query
QUERY: "email validation" FILTER: type="code", language="php"
RESULT: Utils/Validator.php::validateEmail()
```

### Step 3: Present to User
```markdown
🔍 Found Related Context:

**From Slack (#dev):**
"Use filter_var with FILTER_VALIDATE_EMAIL plus regex for international domains"

**From Codebase:**
- Utils/Validator.php has reusable validateEmail() method
- Used in MR #234 for checkout validation

**Suggested Approach:**
Reuse Utils/Validator.php pattern from MR #234

👉 Should we follow this approach?
```

### Step 4: Store After Implementation
```markdown
STORE IN: codebase_knowledge

DOCUMENT: |
  Implemented email validation for contact form using Utils/Validator.php.
  Client-side validation on blur, server-side in Controller/ContactPost.php.

METADATA:
  type: "learning"
  project: "website"
  feature: "contact_form_validation"
  patterns_used: ["Utils.Validator", "inline validation"]
  date: "2024-12-05T10:30:00Z"
```

## Query Patterns by Task Type

### Feature Implementation
1. Query: "<feature_name> implementation"
2. Query: "<technology> patterns"
3. Review: MRs with similar features

### Bug Fix
1. Query: "<error_message>"
2. Query: "<component> issues"
3. Filter: Recent commits with "fix"

### Refactoring
1. Query: "<current_pattern> refactor"
2. Review: Architecture decisions in Slack

### Performance Optimization
1. Query: "<component> performance"
2. Check: Slack for performance discussions

## Query Tips

### Effective Search Terms
✅ **Good:**
- "checkout discount observer"
- "Vue form validation"
- "PayPal redirect timeout"

❌ **Avoid:**
- Too generic: "code"
- Single words: "validation"

### Using Filters
```markdown
# Narrow by type
FILTER: type="code"       # Find implementations
FILTER: type="commit"     # Find fixes
FILTER: type="merge_request"  # Find full features

# Narrow by language
FILTER: language="php"
FILTER: language="vue"

# Combine filters
FILTER: type="code" AND language="php"
```

## Common Queries
```markdown
# Architecture patterns
"Magento observer pattern"
"Vue composable structure"

# Integration help
"payment gateway integration"
"shipping method custom"

# Bug patterns
"cache not clearing"
"Docker permission errors"

# Performance
"slow query optimization"
"page load improvement"

# Testing
"Playwright test patterns"
"unit test setup"
```
