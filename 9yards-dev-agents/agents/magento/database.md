---
description: Handle Magento database changes
capabilities:
  ["magento-database", "schema", "data-patches", "db_schema", "mysql"]
---

# Magento Database Agent

Create setup/upgrade scripts following Magento declarative schema. Handle data patches for content/config changes. Primarily MySQL/MariaDB. Test rollback. Keep schema.xml clean and documented inline.

## Declarative Schema (Magento 2.3+)

### db_schema.xml

**Location:** `app/code/Vendor/Module/etc/db_schema.xml`

```xml
<?xml version="1.0"?>
<schema xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <table name="vendor_module_entity" resource="default" engine="innodb"
           comment="Custom Entity Table">
        <column xsi:type="int" name="entity_id" unsigned="true" nullable="false"
                identity="true" comment="Entity ID"/>
        <column xsi:type="varchar" name="name" nullable="false" length="255"
                comment="Entity Name"/>
        <column xsi:type="text" name="description" nullable="true"
                comment="Description"/>
        <column xsi:type="timestamp" name="created_at" nullable="false"
                default="CURRENT_TIMESTAMP" comment="Created At"/>
        <column xsi:type="timestamp" name="updated_at" nullable="false"
                default="CURRENT_TIMESTAMP" on_update="true" comment="Updated At"/>
        <column xsi:type="int" name="store_id" unsigned="true" nullable="false"
                comment="Store ID"/>

        <constraint xsi:type="primary" referenceId="PRIMARY">
            <column name="entity_id"/>
        </constraint>

        <constraint xsi:type="foreign" referenceId="FK_VENDOR_ENTITY_STORE"
                    table="vendor_module_entity" column="store_id"
                    referenceTable="store" referenceColumn="store_id"
                    onDelete="CASCADE"/>

        <index referenceId="VENDOR_MODULE_ENTITY_NAME" indexType="btree">
            <column name="name"/>
        </index>

        <index referenceId="VENDOR_MODULE_ENTITY_STORE_ID" indexType="btree">
            <column name="store_id"/>
        </index>
    </table>
</schema>
```

### Column Types

- `int` - Integer
- `smallint` - Small integer
- `bigint` - Big integer
- `varchar` - Variable character (specify length)
- `text` - Long text
- `decimal` - Decimal (precision, scale)
- `timestamp` - Timestamp
- `datetime` - Datetime
- `boolean` - Boolean (0/1)

### Generate db_schema_whitelist.json

After creating db_schema.xml:

```bash
bin/magento setup:db-declaration:generate-whitelist --module-name=Vendor_Module
```

This creates: `app/code/Vendor/Module/etc/db_schema_whitelist.json`

## Data Patches

### Create Data Patch

**Location:** `app/code/Vendor/Module/Setup/Patch/Data/AddInitialData.php`

```php
<?php
namespace Vendor\Module\Setup\Patch\Data;

use Magento\Framework\Setup\Patch\DataPatchInterface;
use Magento\Framework\Setup\ModuleDataSetupInterface;

class AddInitialData implements DataPatchInterface
{
    private $moduleDataSetup;

    public function __construct(ModuleDataSetupInterface $moduleDataSetup)
    {
        $this->moduleDataSetup = $moduleDataSetup;
    }

    public function apply()
    {
        $this->moduleDataSetup->getConnection()->startSetup();

        // Your data manipulation here
        $table = $this->moduleDataSetup->getTable('vendor_module_entity');
        $this->moduleDataSetup->getConnection()->insert($table, [
            'name' => 'Default Item',
            'description' => 'Initial data',
            'store_id' => 0
        ]);

        $this->moduleDataSetup->getConnection()->endSetup();
    }

    public static function getDependencies()
    {
        // Return array of patch class names this patch depends on
        return [];
    }

    public function getAliases()
    {
        return [];
    }
}
```

### Schema Patches

**Location:** `app/code/Vendor/Module/Setup/Patch/Schema/AddCustomColumn.php`

```php
<?php
namespace Vendor\Module\Setup\Patch\Schema;

use Magento\Framework\Setup\Patch\SchemaPatchInterface;
use Magento\Framework\Setup\SchemaSetupInterface;
use Magento\Framework\DB\Ddl\Table;

class AddCustomColumn implements SchemaPatchInterface
{
    private $schemaSetup;

    public function __construct(SchemaSetupInterface $schemaSetup)
    {
        $this->schemaSetup = $schemaSetup;
    }

    public function apply()
    {
        $this->schemaSetup->startSetup();

        $this->schemaSetup->getConnection()->addColumn(
            $this->schemaSetup->getTable('vendor_module_entity'),
            'status',
            [
                'type' => Table::TYPE_SMALLINT,
                'nullable' => false,
                'default' => 1,
                'comment' => 'Entity Status'
            ]
        );

        $this->schemaSetup->endSetup();
    }

    public static function getDependencies()
    {
        return [];
    }

    public function getAliases()
    {
        return [];
    }
}
```

## EAV Attributes

### Add Product Attribute

```php
<?php
namespace Vendor\Module\Setup\Patch\Data;

use Magento\Eav\Setup\EavSetupFactory;
use Magento\Framework\Setup\Patch\DataPatchInterface;
use Magento\Framework\Setup\ModuleDataSetupInterface;

class AddCustomAttribute implements DataPatchInterface
{
    private $moduleDataSetup;
    private $eavSetupFactory;

    public function __construct(
        ModuleDataSetupInterface $moduleDataSetup,
        EavSetupFactory $eavSetupFactory
    ) {
        $this->moduleDataSetup = $moduleDataSetup;
        $this->eavSetupFactory = $eavSetupFactory;
    }

    public function apply()
    {
        $eavSetup = $this->eavSetupFactory->create(['setup' => $this->moduleDataSetup]);

        $eavSetup->addAttribute(
            \Magento\Catalog\Model\Product::ENTITY,
            'custom_attribute',
            [
                'type' => 'varchar',
                'label' => 'Custom Attribute',
                'input' => 'text',
                'required' => false,
                'sort_order' => 100,
                'global' => \Magento\Eav\Model\Entity\Attribute\ScopedAttributeInterface::SCOPE_STORE,
                'visible' => true,
                'user_defined' => true,
                'searchable' => true,
                'filterable' => true,
                'comparable' => true,
                'visible_on_front' => true,
                'used_in_product_listing' => true,
                'unique' => false
            ]
        );
    }

    public static function getDependencies()
    {
        return [];
    }

    public function getAliases()
    {
        return [];
    }
}
```

## Running Migrations

```bash
# Apply all pending patches and schema changes
bin/magento setup:upgrade

# Regenerate db_schema_whitelist
bin/magento setup:db-declaration:generate-whitelist

# Check database status
bin/magento setup:db:status
```

## Rollback Testing

Magento doesn't support automatic rollback. Document manual rollback steps:

```sql
-- Rollback for AddCustomColumn patch
ALTER TABLE vendor_module_entity DROP COLUMN status;

-- Rollback for table creation
DROP TABLE IF EXISTS vendor_module_entity;
```

## Best Practices

- Use declarative schema (db_schema.xml) over InstallSchema/UpgradeSchema
- Create data patches for initial data or configuration
- Use schema patches only when declarative schema can't handle it
- Add proper indexes for foreign keys and frequently queried columns
- Include ON DELETE CASCADE for dependent tables
- Use unsigned integers for IDs
- Add timestamps (created_at, updated_at) to entity tables

## Documentation

Document in patch files:

```php
/**
 * Data Patch: Add initial categories
 *
 * Creates default product categories:
 * - Electronics
 * - Clothing
 * - Home & Garden
 */
```

No separate documentation files needed.

## When to Invoke

Use this agent when:

- Creating new database tables for Magento modules
- Adding columns to existing tables
- Creating EAV attributes
- Inserting initial/default data
- Modifying database schema
