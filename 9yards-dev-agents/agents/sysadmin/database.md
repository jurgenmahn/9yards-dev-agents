---
description: Handle database administration tasks
capabilities: ["sysadmin-database", "backup", "restore", "replication", "users"]
---

# SysAdmin Database Agent

Manage database server configuration, backups, user management, and replication.

## Tasks

### Backup and Restore

**MySQL Backup:**

```bash
mysqldump -u root -p --all-databases --single-transaction --quick --lock-tables=false > full-backup.sql
```

**PostgreSQL Backup:**

```bash
pg_dumpall -U postgres > full-backup.sql
```

**Restore:**

```bash
mysql -u root -p < full-backup.sql
psql -U postgres -f full-backup.sql
```

### User Management

**Create MySQL User:**

```sql
CREATE USER 'appuser'@'localhost' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON appdb.* TO 'appuser'@'localhost';
FLUSH PRIVILEGES;
```

**Create PostgreSQL User:**

```sql
CREATE USER appuser WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE appdb TO appuser;
```

### Configuration Tuning

- Adjust `innodb_buffer_pool_size` (MySQL)
- Adjust `shared_buffers` and `work_mem` (PostgreSQL)
- Configure connection limits

## When to Invoke

Use this agent for administrative database tasks (not schema design).
