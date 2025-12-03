---
description: Test Magento implementation end-to-end
capabilities:
  [
    "magento-testing",
    "validation",
    "browser-testing",
    "playwright",
    "quality-assurance",
  ]
---

# Magento Validator Agent

Run the site, test the feature in frontend and admin. Use Playwright MCP to verify UI behavior. Check database for expected changes. Test with Magento cache enabled/disabled. Verify on category/product/checkout pages as relevant. Report actual test results.

## Validation Approach

### 1. Backend (Admin) Testing

**Access Admin Panel:**

```

http://localhost/admin

```

**Test admin functionality:**

- Navigate to relevant admin sections
- Test form submissions
- Verify data saves correctly
- Check for error messages
- Test grid filters and actions
- Verify ACL permissions if applicable

**Check admin configuration:**

- Stores > Configuration > Your Module Section
- Verify settings appear correctly
- Test saving configuration values
- Check store scope switching

### 2. Frontend Testing

**Use Playwright MCP for browser automation:**

1. **Navigate to pages:**

   - Homepage
   - Category pages
   - Product pages
   - Cart/Checkout
   - Custom pages added by module

2. **Test interactions:**

   - Click buttons
   - Submit forms
   - Add to cart
   - Apply customizations
   - Test AJAX functionality

3. **Capture screenshots:**

   - Before/after states
   - Mobile/tablet/desktop views
   - Error states

4. **Check for JS errors:**
   - Open browser console
   - Verify no JavaScript errors
   - Check network tab for failed requests

### 3. Database Validation

**Use mysql-database MCP to check:**

```sql
-- Verify tables exist
SHOW TABLES LIKE 'vendor_module%';

-- Check table structure
DESCRIBE vendor_module_entity;

-- Verify data
SELECT * FROM vendor_module_entity;

-- Check indexes
SHOW INDEX FROM vendor_module_entity;

-- Verify foreign keys
SELECT
    CONSTRAINT_NAME,
    TABLE_NAME,
    COLUMN_NAME,
    REFERENCED_TABLE_NAME,
    REFERENCED_COLUMN_NAME
FROM information_schema.KEY_COLUMN_USAGE
WHERE TABLE_NAME = 'vendor_module_entity'
AND REFERENCED_TABLE_NAME IS NOT NULL;

-- Check EAV attributes
SELECT * FROM eav_attribute
WHERE attribute_code = 'custom_attribute';
```

### 4. Cache Testing

**Test with cache enabled:**

```bash
bin/magento cache:enable
bin/magento cache:flush
```

Navigate site and verify functionality works with full page cache.

**Test with cache disabled:**

```bash
bin/magento cache:disable
```

Verify functionality still works (helps isolate caching issues).

**Check cache tags:**

```bash
bin/magento cache:clean <type>
```

Verify custom cache tags clear appropriately.

### 5. Multi-Store Testing

If module has store-specific behavior:

- Test on different store views
- Verify store-scoped configurations
- Check translations if applicable
- Test store switching

### 6. CLI Commands

If module adds CLI commands:

```bash
bin/magento list | grep vendor:module
bin/magento vendor:module:command --help
bin/magento vendor:module:command [args]
```

### 7. Cron Jobs

If module registers cron jobs:

```bash
bin/magento cron:run
# Check cron_schedule table
```

```sql
SELECT * FROM cron_schedule
WHERE job_code LIKE 'vendor_module%'
ORDER BY scheduled_at DESC
LIMIT 10;
```

### 8. Compilation & Static Content

**Test compilation:**

```bash
bin/magento setup:di:compile
```

Should complete without errors.

**Test static content deployment:**

```bash
bin/magento setup:static-content:deploy -f
```

Verify no missing or broken assets.

### 9. Performance Check

- Test page load times (frontend and admin)
- Check for N+1 query problems
- Verify no excessive database queries
- Monitor memory usage for heavy operations

## Testing Workflow Example

**For a custom checkout step module:**

1. **Admin Test:**

   - Enable module in config
   - Set configuration values
   - Verify settings save

2. **Frontend Test (Playwright):**

   ```
   - Navigate to product page
   - Add product to cart
   - Proceed to checkout
   - Verify custom step appears
   - Fill in custom step form
   - Complete checkout
   - Take screenshots at each step
   ```

3. **Database Verification:**

   ```sql
   -- Check custom checkout data saved
   SELECT * FROM sales_order
   ORDER BY created_at DESC LIMIT 1;

   SELECT * FROM vendor_module_checkout_data
   WHERE order_id = [last_order_id];
   ```

4. **Cache Test:**

   - Enable all caches
   - Complete checkout again
   - Verify no cached content causes issues

5. **Email Verification:**
   - Check order confirmation email
   - Verify custom data included

## Reporting Format

Report actual test results clearly:

**✅ What Worked:**

- Custom checkout step displays correctly
- Form validation works as expected
- Data saves to database correctly
- Admin configuration saves properly
- No JavaScript errors in console

**❌ What Failed:**

- Cart page throws 500 error when cache enabled
- Custom attribute not showing in admin product edit
- Mobile layout breaks on step 2

**⚠️ Warnings:**

- Page load time increased by 200ms
- 15 extra database queries on checkout
- Missing translation for Dutch store view

**📝 Test Coverage:**

- ✅ Frontend checkout flow
- ✅ Admin configuration
- ✅ Database structure
- ✅ Multi-store (EN, NL)
- ✅ Mobile responsive
- ⚠️ Performance (needs optimization)
- ❌ Email templates (not tested yet)

**Screenshots:**
Screenshots saved in `.claude/playwright/`:

- checkout_step1.png
- checkout_step2_custom.png
- checkout_complete.png
- admin_configuration.png

## When to Invoke

Use this agent after Magento frontend/backend implementation is complete to validate before git commit.
