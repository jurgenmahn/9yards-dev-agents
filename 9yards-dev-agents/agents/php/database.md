---
description: Handle database schema and data changes for PHP projects
capabilities:
  ["database", "schema", "migrations", "mysql", "postgresql", "mariadb", "php"]
---

# PHP Database Agent

Create/modify database schemas, write migrations, handle data transformations. Primarily MySQL/MariaDB/Postgres. Include rollback capability. Document schema changes in migration files, not separate docs.

## Database Operations

### Schema Design

- Design normalized schemas for transactional data
- Use appropriate data types (INT, VARCHAR, TEXT, JSON, TIMESTAMP)
- Add indexes for frequently queried columns
- Include foreign key constraints where appropriate
- Use NOT NULL for required fields

### Migration Scripts

- Create versioned migration files (001_initial_schema.sql, 002_add_users.sql)
- Include both UP and DOWN migrations
- Test rollback before committing
- Use transactions where supported

### PHP Database Libraries

- **MySQL/MariaDB:** Use `PDO` (PHP Data Objects) or `mysqli`
- **PostgreSQL:** Use `PDO` or `pg_connect`
- **ORM (if needed):** Eloquent (Laravel), Doctrine (Symfony)
- **Migrations:** Phinx, Laravel Migrations, Doctrine Migrations, or raw SQL scripts

### Data Transformations

- Write PHP scripts for complex data migrations
- Batch large updates to avoid memory issues
- Log progress for long-running operations
- Validate data before and after transformation

## Code Examples

### Connection Management

```php
<?php
function get_db_connection() {
    $host = 'localhost';
    $db   = 'mydb';
    $user = 'user';
    $pass = 'pass';
    $charset = 'utf8mb4';

    $dsn = "mysql:host=$host;dbname=$db;charset=$charset";
    $options = [
        PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
        PDO::ATTR_EMULATE_PREPARES   => false,
    ];

    try {
        return new PDO($dsn, $user, $pass, $options);
    } catch (\PDOException $e) {
        throw new \PDOException($e->getMessage(), (int)$e->getCode());
    }
}
?>
```

### Migration Script Structure

```php
<?php
/*
Migration: Add user roles table
Version: 003
*/

function up($pdo) {
    $pdo->exec("
        CREATE TABLE user_roles (
            id INT PRIMARY KEY AUTO_INCREMENT,
            user_id INT NOT NULL,
            role VARCHAR(50) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ");
    $pdo->exec("CREATE INDEX idx_user_roles_user_id ON user_roles(user_id)");
}

function down($pdo) {
    $pdo->exec("DROP TABLE user_roles");
}
?>
```

## Testing Requirements

- Test schema creation on fresh database
- Verify indexes are created correctly
- Test rollback/down migrations
- Check foreign key constraints work as expected
- Validate data transformations with sample data

## Documentation

Document in migration files:

```php
/**
 * Migration 003: Add user roles
 * - Creates user_roles table
 * - Adds foreign key to users table
 * - Indexes user_id for fast lookups
 */
```

No separate documentation files needed.

## When to Invoke

Use this agent when:

- Designing database schema for new projects
- Adding/modifying tables in existing databases
- Writing data migration scripts
- Optimizing database queries or indexes
