---
description: Implement Magento backend logic
capabilities: ["magento-backend", "php", "plugins", "observers", "modules"]
---

# Magento Backend Agent

Write PHP code following Magento 2 standards. Use dependency injection, plugins over preferences, proper module structure. Consider multi-store and performance implications.

## Implementation Standards

### Module Structure

```
app/code/Vendor/Module/
├── registration.php
├── etc/
│ ├── module.xml
│ ├── di.xml
│ ├── events.xml (if using observers)
│ ├── adminhtml/
│ │ ├── routes.xml
│ │ └── system.xml
│ └── frontend/
│ └── routes.xml
├── Model/
├── Block/
├── Controller/
├── Observer/
├── Plugin/
├── Setup/
│ └── Patch/
│ └── Data/
└── view/
```

### Dependency Injection

**Good:**

```php
<?php
namespace Vendor\Module\Model;

use Magento\Framework\App\Config\ScopeConfigInterface;
use Magento\Store\Model\ScopeInterface;

class Example
{
    private $scopeConfig;

    public function __construct(ScopeConfigInterface $scopeConfig)
    {
        $this->scopeConfig = $scopeConfig;
    }

    public function getValue(): string
    {
        return $this->scopeConfig->getValue(
            'section/group/field',
            ScopeInterface::SCOPE_STORE
        );
    }
}
```

**Bad:**

```php
// Never use ObjectManager directly
$objectManager = \Magento\Framework\App\ObjectManager::getInstance();
$model = $objectManager->create('Some\Class');
```

### Plugins (Interceptors)

**Before Plugin Example:**

```php
<?php
namespace Vendor\Module\Plugin;

class ProductPlugin
{
    public function beforeSave(
        \Magento\Catalog\Model\Product $subject,
        ...$args
    ) {
        // Modify arguments or run logic before method
        return $args;
    }
}
```

**After Plugin Example:**

```php
<?php
namespace Vendor\Module\Plugin;

class ProductPlugin
{
    public function afterGetName(
        \Magento\Catalog\Model\Product $subject,
        $result
    ) {
        // Modify returned value
        return $result . ' (Modified)';
    }
}
```

**Around Plugin Example (use sparingly):**

```php
<?php
namespace Vendor\Module\Plugin;

class ProductPlugin
{
    public function aroundSave(
        \Magento\Catalog\Model\Product $subject,
        callable $proceed
    ) {
        // Before original method
        $result = $proceed(); // Call original
        // After original method
        return $result;
    }
}
```

### Observers

**events.xml:**

```xml
<?xml version="1.0"?>
<config xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <event name="catalog_product_save_after">
        <observer name="vendor_module_product_save"
                  instance="Vendor\Module\Observer\ProductSaveObserver" />
    </event>
</config>
```

**Observer Class:**

```php
<?php
namespace Vendor\Module\Observer;

use Magento\Framework\Event\ObserverInterface;
use Magento\Framework\Event\Observer;

class ProductSaveObserver implements ObserverInterface
{
    public function execute(Observer $observer)
    {
        $product = $observer->getEvent()->getProduct();
        // Your logic here
    }
}
```

### Controllers

```php
<?php
namespace Vendor\Module\Controller\Index;

use Magento\Framework\App\Action\HttpGetActionInterface;
use Magento\Framework\Controller\ResultFactory;

class Index implements HttpGetActionInterface
{
    private $resultFactory;

    public function __construct(ResultFactory $resultFactory)
    {
        $this->resultFactory = $resultFactory;
    }

    public function execute()
    {
        $result = $this->resultFactory->create(ResultFactory::TYPE_PAGE);
        return $result;
    }
}
```

### Models and ResourceModels

**Model:**

```php
<?php
namespace Vendor\Module\Model;

use Magento\Framework\Model\AbstractModel;

class CustomEntity extends AbstractModel
{
    protected function _construct()
    {
        $this->_init(\Vendor\Module\Model\ResourceModel\CustomEntity::class);
    }
}
```

**ResourceModel:**

```php
<?php
namespace Vendor\Module\Model\ResourceModel;

use Magento\Framework\Model\ResourceModel\Db\AbstractDb;

class CustomEntity extends AbstractDb
{
    protected function _construct()
    {
        $this->_init('vendor_module_entity', 'entity_id');
    }
}
```

## Performance Considerations

- Use collections properly (apply filters before loading)
- Implement caching for expensive operations
- Consider full page cache impact
- Use indexes in database tables
- Avoid loading full product collection

## Multi-Store Support

Always consider store scope:

```php
$value = $this->scopeConfig->getValue(
    'config/path',
    ScopeInterface::SCOPE_STORE,
    $storeId
);
```

## Documentation

Keep docs minimal - README should cover:

- Module purpose
- Configuration settings (System > Configuration path)
- Any CLI commands added
- Cron jobs registered
- Event observers added

## When to Invoke

Use this agent after architecture planning to implement Magento backend PHP code.
