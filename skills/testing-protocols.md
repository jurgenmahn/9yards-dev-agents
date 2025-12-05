# Testing Protocols Skill

**PURPOSE**: Comprehensive test patterns and edge cases reference

## Test Categories

### 1. Happy Path Tests
Normal user flow, everything works

```javascript
test('user completes checkout successfully', async ({ page }) => {
  await page.goto('/checkout');
  await page.fill('#email', 'user@example.com');
  await page.click('button[type=submit]');
  await expect(page).toHaveURL(/order-success/);
});
```

### 2. Input Validation Tests
Invalid/malicious input handling - CRITICAL

```javascript
// Empty fields
test('form rejects empty fields', async ({ page }) => {
  await page.goto('/contact');
  await page.click('button[type=submit]');
  await expect(page.locator('.error-required')).toBeVisible();
});

// Invalid format
test('form rejects invalid email', async ({ page }) => {
  await page.fill('#email', 'notanemail');
  await page.click('button[type=submit]');
  await expect(page.locator('.error-email')).toContainText('valid email');
});

// XSS attempts
test('form sanitizes script tags', async ({ page }) => {
  await page.fill('#message', "<script>alert('xss')</script>");
  await page.click('button[type=submit]');
  await expect(page.locator('.success-message')).toBeVisible();
});

// SQL injection
test('search prevents SQL injection', async ({ page }) => {
  await page.fill('#search', "'; DROP TABLE users; --");
  await page.click('button[type=submit]');
  await expect(page.locator('.search-results')).toBeVisible();
});

// Max length
test('form enforces max length', async ({ page }) => {
  const longText = 'a'.repeat(10000);
  await page.fill('#message', longText);
  const value = await page.inputValue('#message');
  expect(value.length).toBeLessThanOrEqual(5000);
});
```

### 3. Concurrent Action Tests
Race condition detection

```javascript
test('prevents double form submission', async ({ page }) => {
  await page.goto('/checkout');
  const submitButton = page.locator('button[type=submit]');
  await Promise.all([
    submitButton.click(),
    submitButton.click(),
    submitButton.click()
  ]);
  // Should only process once
});
```

### 4. Error Condition Tests
Network failures, timeouts

```javascript
test('handles API timeout', async ({ page, context }) => {
  await context.route('**/api/**', route => {
    setTimeout(() => route.abort(), 10000);
  });
  await page.goto('/products');
  await expect(page.locator('.error-loading')).toBeVisible();
});

test('handles 500 server error', async ({ page, context }) => {
  await context.route('**/api/cart/add', route => {
    route.fulfill({ status: 500 });
  });
  await page.goto('/product/123');
  await page.click('.add-to-cart');
  await expect(page.locator('.error-message')).toContainText('try again');
});
```

### 5. Console Error Tests
JavaScript quality assurance

```javascript
test('page loads without console errors', async ({ page }) => {
  const errors = [];
  page.on('console', msg => {
    if (msg.type() === 'error') errors.push(msg.text());
  });
  await page.goto('/');
  await page.waitForLoadState('networkidle');
  expect(errors).toHaveLength(0);
});
```

### 6. Responsive/Mobile Tests
Different viewport sizes

```javascript
test('works on mobile', async ({ page }) => {
  await page.setViewportSize({ width: 375, height: 667 });
  await page.goto('/');
  await expect(page.locator('.mobile-menu-toggle')).toBeVisible();
});

test('form usable on mobile', async ({ page }) => {
  await page.setViewportSize({ width: 375, height: 667 });
  await page.goto('/contact');
  await page.tap('#name');
  await page.fill('#name', 'Test');
  const submitButton = page.locator('button[type=submit]');
  await expect(submitButton).toBeVisible();
});
```

### 7. Performance Tests
Load times, large datasets

```javascript
test('page loads within 3 seconds', async ({ page }) => {
  const start = Date.now();
  await page.goto('/');
  await page.waitForLoadState('domcontentloaded');
  const loadTime = Date.now() - start;
  expect(loadTime).toBeLessThan(3000);
});
```

### 8. Accessibility Tests
WCAG compliance, keyboard navigation

```javascript
test('form navigable by keyboard', async ({ page }) => {
  await page.goto('/contact');
  await page.keyboard.press('Tab');
  await expect(page.locator('#name')).toBeFocused();
  await page.keyboard.press('Tab');
  await expect(page.locator('#email')).toBeFocused();
});
```

## Security Testing Checklist

```markdown
✅ XSS Prevention - Script tags sanitized
✅ SQL Injection Prevention - Parameterized queries
✅ CSRF Protection - Tokens present on forms
✅ Authentication - Session timeout works
✅ Authorization - Users can't access others' data
```

## Running Tests

```bash
# All tests
npx playwright test

# Specific suite
npx playwright test tests/checkout/

# With UI
npx playwright test --ui

# Debug mode
npx playwright test --debug

# Headed (see browser)
npx playwright test --headed

# Specific browser
npx playwright test --project=chromium
```

## Best Practices

1. **Test isolation**: Each test independent
2. **Clear test names**: Describe what's being tested
3. **Arrange-Act-Assert**: Clear structure
4. **Wait properly**: Use Playwright's auto-waiting
5. **Screenshot failures**: Automatic with Playwright
6. **Test data**: Use fixtures, not production data
7. **Cleanup**: Reset state between tests

## When Tests Fail

1. Check screenshot: artifacts/<test-name>.png
2. Check trace: playwright-report/
3. Run with --debug flag
4. Check browser console logs
5. Verify test data setup
