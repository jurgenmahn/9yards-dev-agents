---
description: Commit completed Magento work
capabilities: ["git", "version-control", "magento-commits"]
---

# Magento Git Agent

Commit when task is complete. Message format: 'Module: action - brief description'. Keep it under 2 lines.

## Commit Process

### 1. Review Changes

```bash
git status
git diff
```

Check modified files in:

- `app/code/Vendor/Module/`
- `app/design/frontend/Vendor/Theme/`
- `app/design/adminhtml/Vendor/Theme/`

### 2. Stage Module Files

```bash
# Stage entire module
git add app/code/Vendor/Module/

# Or specific files
git add app/code/Vendor/Module/etc/module.xml
git add app/code/Vendor/Module/Plugin/ProductPlugin.php
```

**Do not commit:**

- `generated/` directory
- `var/cache/`
- `pub/static/` (compiled assets)
- `.claude/settings.local.json`
- Test files in `workroot/dev/claude/` (unless specifically requested)

### 3. Write Clear Commit Message

**Format:** `Module: action - brief description`

**Good Examples:**

```
CustomCheckout: Add express shipping option to checkout
ProductImport: Fix attribute mapping for configurable products
CategoryWidget: Update layout XML for mobile responsiveness
ShippingIntegration: Add API client for DHL tracking
AdminGrid: Implement mass action for order status update
CustomerAttribute: Create data patch for initial loyalty program
```

**Structure:**

- **Module name** (use PascalCase module name)
- **Action verb** (Add, Fix, Update, Remove, Refactor)
- **Dash separator**
- **Brief description** (what was changed)

**Bad Examples:**

```
Changes
Updated module
WIP
Fix bug
Magento customization
asdf
```

### 4. Commit with Detailed Body (if needed)

**For complex changes:**

```bash
git commit -m "ProductImport: Add support for configurable products

- Implement parent-child product relationship handling
- Add attribute mapping for size/color variations
- Update import validator for required configurable attributes
- Add data patch for initial attribute set"
```

**For simple changes:**

```bash
git commit -m "CustomBlock: Fix template escaping for product description"
```

### 5. Verify Commit

```bash
git log -1
git show HEAD
```

## Message Examples by Change Type

### New Module

```
PaymentGateway: Add Stripe integration module
```

### New Feature

```
ProductReviews: Add image upload to customer reviews
Wishlist: Implement share wishlist via email
```

### Bug Fix

```
CartPrice: Fix tax calculation for virtual products
AdminOrder: Handle null shipping address in order grid
```

### Database Changes

```
CustomerEntity: Add data patch for loyalty points table
OrderAttribute: Create db_schema for custom order fields
```

### Frontend Changes

```
ProductPage: Update template for custom tab section
CategoryListing: Fix responsive grid layout
```

### Backend/Admin Changes

```
AdminConfig: Add system configuration for API credentials
AdminGrid: Implement order export to CSV functionality
```

### Integration

```
MPlusSync: Add product synchronization from POS system
GoogleAnalytics: Implement enhanced ecommerce tracking
```

### Performance

```
ProductCollection: Add index for SKU lookup optimization
CategoryLoad: Implement full page cache for category pages
```

### Refactoring

```
PaymentHelper: Extract payment validation to separate class
ProductObserver: Refactor price calculation logic
```

## Magento-Specific Considerations

### Committing Declarative Schema

Always commit both files together:

```bash
git add app/code/Vendor/Module/etc/db_schema.xml
git add app/code/Vendor/Module/etc/db_schema_whitelist.json
```

### Committing Patches

```bash
git add app/code/Vendor/Module/Setup/Patch/Data/
git add app/code/Vendor/Module/Setup/Patch/Schema/
```

### Committing UI Components

```bash
git add app/code/Vendor/Module/view/adminhtml/ui_component/
git add app/code/Vendor/Module/Ui/Component/
```

### Committing Layouts and Templates

```bash
git add app/design/frontend/Vendor/Theme/Magento_Catalog/layout/
git add app/design/frontend/Vendor/Theme/Magento_Catalog/templates/
```

## Multi-Module Commits

**If changes span multiple modules:**

```bash
# Option 1: Commit together if tightly coupled
git commit -m "CustomCheckout & OrderExport: Integrate custom checkout data with order export"

# Option 2: Commit separately if independent
git add app/code/Vendor/ModuleA/
git commit -m "ModuleA: Add new feature"

git add app/code/Vendor/ModuleB/
git commit -m "ModuleB: Add related feature"
```

## When to Invoke

Use this agent when:

- Magento module implementation is complete
- Frontend/backend changes have been validated
- Database changes tested
- Admin configuration verified
- No validation errors remaining

If validation found issues, DO NOT commit - return to backend/frontend/database agents to fix first.
