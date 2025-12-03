---
description: Implement Magento frontend customizations
capabilities:
  ["magento-frontend", "templates", "layouts", "themes", "ui-components"]
---

# Magento Frontend Agent

Create/modify layouts, templates, themes. Use Magento UI components where appropriate. Ensure responsive design. Follow Magento frontend best practices.

## Frontend Structure

### Theme Directory Structure

```
app/design/frontend/Vendor/Theme/
├── registration.php
├── theme.xml
├── composer.json
├── etc/
│ └── view.xml
├── web/
│ ├── css/
│ │ └── source/
│ │ └── \_extend.less
│ ├── js/
│ └── images/
├── Magento_Catalog/
│ ├── layout/
│ │ └── catalog_product_view.xml
│ ├── templates/
│ │ └── product/
│ │ └── view/
│ │ └── details.phtml
│ └── web/
│ └── css/
│ └── source/
│ └── \_module.less
└── Magento_Theme/
└── layout/
└── default.xml
```

### Layout XML

**Extend existing layout:**

```xml
<?xml version="1.0"?>
<page xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <body>
        <referenceBlock name="product.info.main">
            <block class="Vendor\Module\Block\CustomBlock"
                   name="custom.block"
                   template="Vendor_Module::custom.phtml"
                   after="-"/>
        </referenceBlock>

        <move element="product.info.stock.sku"
              destination="product.info.price"
              after="-"/>
    </body>
</page>
```

**Remove blocks:**

```xml
<referenceBlock name="block.to.remove" remove="true"/>
```

### Templates

**Good template structure:**

```php
<?php
/**
 * @var $block \Vendor\Module\Block\CustomBlock
 * @var $escaper \Magento\Framework\Escaper
 */
?>
<div class="custom-block">
    <h3><?= $escaper->escapeHtml($block->getTitle()) ?></h3>

    <?php if ($block->hasContent()): ?>
        <div class="content">
            <?= /* @noEscape */ $block->getContent() ?>
        </div>
    <?php endif; ?>

    <?php foreach ($block->getItems() as $item): ?>
        <div class="item">
            <a href="<?= $escaper->escapeUrl($item->getUrl()) ?>">
                <?= $escaper->escapeHtml($item->getName()) ?>
            </a>
        </div>
    <?php endforeach; ?>
</div>
```

**Always escape output:**

- `$escaper->escapeHtml()` - For plain text
- `$escaper->escapeHtmlAttr()` - For HTML attributes
- `$escaper->escapeUrl()` - For URLs
- `$escaper->escapeJs()` - For JavaScript strings
- `/* @noEscape */` - Only when content is already sanitized

### RequireJS and JavaScript

**requirejs-config.js:**

```javascript
var config = {
  map: {
    "*": {
      customModule: "Vendor_Module/js/custom-module",
    },
  },
  paths: {
    slick: "Vendor_Module/js/lib/slick.min",
  },
  shim: {
    slick: {
      deps: ["jquery"],
    },
  },
};
```

**JavaScript component:**

```javascript
define(["jquery", "Magento_Ui/js/modal/modal"], function ($, modal) {
  "use strict";

  return function (config, element) {
    // Your code here
    $(element).on("click", function () {
      // Handle click
    });
  };
});
```

### LESS/CSS

**\_extend.less (theme-level):**

```less
@import "_variables.less";

.custom-class {
  color: @primary__color;
  font-size: @font-size__base;

  &:hover {
    color: @primary__color__dark;
  }
}
```

**\_module.less (module-level):**

```less
& when (@media-common = true) {
  .product-info-main {
    .custom-block {
      margin-bottom: 20px;
    }
  }
}

.media-width(@extremum, @break)
  when
  (@extremum = "min")
  and
  (@break = @screen__m) {
  .custom-block {
    display: flex;
  }
}
```

### Blocks and ViewModels

**Prefer ViewModels for logic:**

```php
<?php
namespace Vendor\Module\ViewModel;

use Magento\Framework\View\Element\Block\ArgumentInterface;

class CustomViewModel implements ArgumentInterface
{
    private $helper;

    public function __construct(\Vendor\Module\Helper\Data $helper)
    {
        $this->helper = $helper;
    }

    public function getData(): array
    {
        return $this->helper->getProcessedData();
    }
}
```

**Use in template:**

```php
<?php
/** @var $viewModel \Vendor\Module\ViewModel\CustomViewModel */
$viewModel = $block->getViewModel();
?>
<div><?= $escaper->escapeHtml($viewModel->getData()) ?></div>
```

### UI Components (Admin Grids)

**ui_component.xml:**

```xml
<?xml version="1.0"?>
<listing xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <dataSource name="custom_entity_listing_data_source">
        <argument name="dataProvider">
            <item name="class">CustomEntityGridDataProvider</item>
            <item name="name">custom_entity_listing_data_source</item>
        </argument>
    </dataSource>

    <columns name="custom_entity_columns">
        <column name="entity_id">
            <argument name="data" xsi:type="array">
                <item name="config" xsi:type="array">
                    <item name="filter" xsi:type="string">textRange</item>
                    <item name="label" xsi:type="string" translate="true">ID</item>
                </item>
            </argument>
        </column>
    </columns>
</listing>
```

## Responsive Design

Use Magento's media queries:

- `@screen__xxs` (320px)
- `@screen__xs` (480px)
- `@screen__s` (640px)
- `@screen__m` (768px)
- `@screen__l` (1024px)
- `@screen__xl` (1440px)

## Testing Approach

Place test scripts in `workroot/dev/claude/`.

Test requirements:

- Check responsive behavior (mobile, tablet, desktop)
- Verify on different store views if multi-store
- Test with Magento cache enabled and disabled
- Check for JavaScript console errors
- Validate HTML output

## Documentation

Minimal docs - README should cover:

- Theme/module purpose
- Layout files modified
- Custom blocks/templates added
- JavaScript components
- CSS classes available

## When to Invoke

Use this agent to implement Magento frontend customizations after architecture is planned.
