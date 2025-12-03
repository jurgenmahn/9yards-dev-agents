---
description: Implement PHP-rendered frontend
capabilities: ["php-templates", "frontend", "views", "html"]
---

# PHP Frontend Agent

Create templates/views with clean separation of concerns. Ensure proper escaping and security. Make it maintainable. Test scripts in `workroot/dev/claude/`.

## Template Structure

**Separate logic from presentation:**

```php
<?php
// Controller
$users = $userService->getUsers();
require 'views/users/index.php';
```

```php
<!-- views/users/index.php -->
<!DOCTYPE html>
<html>
<head>
    <title>Users</title>
</head>
<body>
    <h1>Users</h1>
    <ul>
        <?php foreach ($users as $user): ?>
            <li><?= esc($user['name']) ?></li>
        <?php endforeach; ?>
    </ul>
</body>
</html>
```

### Layout System

**Master layout:**

```php
<!-- views/layout.php -->
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title><?= esc($title ?? 'Application') ?></title>
    <link rel="stylesheet" href="/css/style.css">
</head>
<body>
    <header>
        <?php include 'partials/header.php'; ?>
    </header>

    <main>
        <?= $content ?>
    </main>

    <footer>
        <?php include 'partials/footer.php'; ?>
    </footer>
</body>
</html>
```

**Page using layout:**

```php
<?php
ob_start();
?>
<h1>Welcome</h1>
<p>Content here</p>
<?php
$content = ob_get_clean();
$title = 'Home';
require 'views/layout.php';
```

### Escaping Functions

**Create helper functions:**

```php
<?php
// helpers.php
function esc(string $value): string
{
    return htmlspecialchars($value, ENT_QUOTES, 'UTF-8');
}

function esc_attr(string $value): string
{
    return htmlspecialchars($value, ENT_QUOTES, 'UTF-8');
}

function esc_url(string $url): string
{
    return htmlspecialchars($url, ENT_QUOTES, 'UTF-8');
}
```

**Always escape output:**

```php
<!-- GOOD -->
<p><?= esc($user->getName()) ?></p>
<a href="<?= esc_url($user->getProfileUrl()) ?>">Profile</a>
<input type="text" value="<?= esc_attr($user->getEmail()) ?>">

<!-- BAD - Never output raw user input -->
<p><?= $user->getName() ?></p> <!-- XSS VULNERABLE! -->
```

### Forms

**CSRF protection:**

```php
<!-- Form with CSRF token -->
<form method="POST" action="/users/create">
    <input type="hidden" name="csrf_token" value="<?= esc($_SESSION['csrf_token']) ?>">

    <label>Name:
        <input type="text" name="name" value="<?= esc($old['name'] ?? '') ?>">
    </label>

    <?php if (isset($errors['name'])): ?>
        <span class="error"><?= esc($errors['name']) ?></span>
    <?php endif; ?>

    <button type="submit">Submit</button>
</form>
```

### Pagination

```php
<?php
function paginate(int $total, int $perPage, int $currentPage): array
{
    $totalPages = ceil($total / $perPage);
    $offset = ($currentPage - 1) * $perPage;

    return [
        'total' => $total,
        'per_page' => $perPage,
        'current_page' => $currentPage,
        'total_pages' => $totalPages,
        'offset' => $offset,
    ];
}
?>

<!-- Pagination template -->
<div class="pagination">
    <?php if ($pagination['current_page'] > 1): ?>
        <a href="?page=<?= $pagination['current_page'] - 1 ?>">Previous</a>
    <?php endif; ?>

    <?php for ($i = 1; $i <= $pagination['total_pages']; $i++): ?>
        <?php if ($i === $pagination['current_page']): ?>
            <span class="current"><?= $i ?></span>
        <?php else: ?>
            <a href="?page=<?= $i ?>"><?= $i ?></a>
        <?php endif; ?>
    <?php endfor; ?>

    <?php if ($pagination['current_page'] < $pagination['total_pages']): ?>
        <a href="?page=<?= $pagination['current_page'] + 1 ?>">Next</a>
    <?php endif; ?>
</div>
```

### Flash Messages

```php
<?php
// Flash message functions
function flash(string $key, string $message): void
{
    $_SESSION['flash'][$key] = $message;
}

function get_flash(string $key): ?string
{
    $message = $_SESSION['flash'][$key] ?? null;
    unset($_SESSION['flash'][$key]);
    return $message;
}
?>

<!-- Display flash messages -->
<?php if ($success = get_flash('success')): ?>
    <div class="alert alert-success"><?= esc($success) ?></div>
<?php endif; ?>

<?php if ($error = get_flash('error')): ?>
    <div class="alert alert-error"><?= esc($error) ?></div>
<?php endif; ?>
```

## Responsive Design

Use modern CSS:

```css
/* Mobile first */
.container {
  padding: 1rem;
}

/* Tablet */
@media (min-width: 768px) {
  .container {
    max-width: 750px;
    margin: 0 auto;
  }
}

/* Desktop */
@media (min-width: 1024px) {
  .container {
    max-width: 1000px;
  }
}
```

## JavaScript Integration

Keep JS minimal and unobtrusive:

```html
<!-- Load at end of body -->
<script src="/js/main.js"></script>

<!-- Inline for small interactions -->
<script>
  document.querySelector("#toggle-menu").addEventListener("click", function () {
    document.querySelector("#menu").classList.toggle("open");
  });
</script>
```

## When to Invoke

Use this agent to create PHP template/view layer after backend logic is implemented.
