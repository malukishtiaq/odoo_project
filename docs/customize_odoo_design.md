# 🎨 Customize Odoo Design - Complete Guide

## 📋 Table of Contents
1. [Quick Start Guide](#quick-start-guide)
2. [Understanding Odoo Design Structure](#understanding-odoo-design-structure)
3. [Creating Custom Modules](#creating-custom-modules)
4. [Common Design Customization Patterns](#common-design-customization-patterns)
5. [Troubleshooting Common Issues](#troubleshooting-common-issues)
6. [Best Practices](#best-practices)

---

## 🚀 Quick Start Guide

### Step 1: Create Custom Module Structure
```bash
# Create module directory
mkdir -p custom_modules/gl_[module_name]/{static/src/{xml,scss,js},views}

# Create basic files
touch custom_modules/gl_[module_name]/__manifest__.py
touch custom_modules/gl_[module_name]/__init__.py
touch custom_modules/gl_[module_name]/views/[module_name]_views.xml
touch custom_modules/gl_[module_name]/static/src/xml/[module_name]_templates.xml
touch custom_modules/gl_[module_name]/static/src/scss/[module_name]_styles.scss
```

### Step 2: Basic Manifest Template
```python
# __manifest__.py
{
    'name': 'GL [Module Name]',
    'version': '18.0.1.0.0',
    'category': '[Category]',
    'summary': 'Custom [description]',
    'description': """
        Custom module for [purpose]
    """,
    'author': 'GreenLines',
    'depends': ['[base_module]', 'web'],
    'data': [
        'views/[module_name]_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'gl_[module_name]/static/src/xml/[module_name]_templates.xml',
            'gl_[module_name]/static/src/scss/[module_name]_styles.scss',
        ],
    },
    'installable': True,
    'auto_install': False,
}
```

### Step 3: Basic Init File
```python
# __init__.py
# -*- coding: utf-8 -*-
```

---

## 🏗️ Understanding Odoo Design Structure

### Core Odoo Design Components

#### 1. **Views (XML)**
- **Location**: `odoo-18/addons/[module]/views/`
- **Purpose**: Define UI structure and layout
- **Key Files**: `*_views.xml`, `*_templates.xml`

#### 2. **Styles (SCSS/CSS)**
- **Location**: `odoo-18/addons/[module]/static/src/scss/`
- **Purpose**: Visual styling and theming
- **Key Files**: `*.scss`, `*.css`

#### 3. **JavaScript**
- **Location**: `odoo-18/addons/[module]/static/src/js/`
- **Purpose**: Interactive behavior and logic
- **Key Files**: `*.js`

#### 4. **Templates (QWeb)**
- **Location**: `odoo-18/addons/[module]/static/src/xml/`
- **Purpose**: Dynamic UI components
- **Key Files**: `*.xml`

### Common View Types to Customize

| View Type | File Pattern | Purpose |
|-----------|--------------|---------|
| **Kanban** | `*_kanban_view.xml` | Card-based layouts |
| **List** | `*_tree_view.xml` | Table/list layouts |
| **Form** | `*_form_view.xml` | Detail/edit forms |
| **Search** | `*_search_view.xml` | Search and filters |

---

## 🛠️ Creating Custom Modules

### Method 1: Inherit Existing Views (Recommended)

#### Step 1: Find the Target View
```bash
# Search for existing views
grep -r "kanban.*view" odoo-18/addons/[module]/views/
grep -r "product.*template.*kanban" odoo-18/addons/product/views/
```

#### Step 2: Create View Inheritance
```xml
<!-- views/[module_name]_views.xml -->
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="[module_name]_[view_name]_inherit" model="ir.ui.view">
        <field name="name">[module_name].[view_name].inherit</field>
        <field name="model">[model_name]</field>
        <field name="inherit_id" ref="[base_module].[view_id]"/>
        <field name="arch" type="xml">
            <!-- Add custom CSS class -->
            <xpath expr="//kanban" position="attributes">
                <attribute name="class">gl-custom-[view-name]</attribute>
            </xpath>
            <!-- Modify specific elements -->
            <xpath expr="//t[@t-name='card']" position="attributes">
                <attribute name="class">gl-custom-card</attribute>
            </xpath>
        </field>
    </record>
</odoo>
```

#### Step 3: Create Custom Styles
```scss
/* static/src/scss/[module_name]_styles.scss */

// CSS Variables for theming
:root {
    --gl-primary-color: #667eea;
    --gl-primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    --gl-border-radius: 16px;
    --gl-box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
    --gl-transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

// Custom styling
.gl-custom-[view-name] {
    padding: 20px !important;
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%) !important;
}

.gl-custom-card {
    background: rgba(255, 255, 255, 0.95) !important;
    backdrop-filter: blur(10px) !important;
    border-radius: var(--gl-border-radius) !important;
    box-shadow: var(--gl-box-shadow) !important;
    transition: var(--gl-transition) !important;
    
    &:hover {
        transform: translateY(-8px) scale(1.02) !important;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2) !important;
    }
}
```

### Method 2: Override Templates

#### Step 1: Create Template Inheritance
```xml
<!-- static/src/xml/[module_name]_templates.xml -->
<?xml version="1.0" encoding="UTF-8"?>
<templates id="template" xml:space="preserve">
    <!-- Inherit existing template -->
    <t t-name="[base_module].[template_name]" 
       t-inherit="[base_module].[template_name]" 
       t-inherit-mode="primary">
        <xpath expr="//[element]" position="replace">
            <!-- Your custom template content -->
        </xpath>
    </t>
</templates>
```

---

## 🎯 Common Design Customization Patterns

### 1. **Modern Card Design**
```scss
.modern-card {
    background: rgba(255, 255, 255, 0.95) !important;
    backdrop-filter: blur(10px) !important;
    border-radius: 16px !important;
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1) !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    
    &:hover {
        transform: translateY(-8px) scale(1.02) !important;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2) !important;
    }
}
```

### 2. **Gradient Backgrounds**
```scss
.gradient-bg {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
}

.glassmorphism {
    background: rgba(255, 255, 255, 0.1) !important;
    backdrop-filter: blur(10px) !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
}
```

### 3. **Hover Animations**
```scss
.hover-lift {
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    
    &:hover {
        transform: translateY(-8px) !important;
    }
}

.hover-scale {
    transition: transform 0.3s ease !important;
    
    &:hover {
        transform: scale(1.05) !important;
    }
}
```

### 4. **Responsive Design**
```scss
// Mobile first approach
@media (max-width: 768px) {
    .responsive-card {
        min-height: 180px !important;
        padding: 15px !important;
        margin: 5px !important;
    }
}

@media (min-width: 1200px) {
    .responsive-card {
        min-height: 280px !important;
        padding: 25px !important;
        margin: 15px !important;
    }
}
```

---

## 🔧 Troubleshooting Common Issues

### Issue 1: "External ID not found" Error
**Problem**: `ValueError: External ID not found: [module].[view_id]`

**Solution**:
1. Find the correct XML ID:
   ```bash
   grep -r "view_id.*ref" odoo-18/addons/[module]/views/
   ```
2. Check the actual view structure:
   ```bash
   grep -r "kanban\|list\|form" odoo-18/addons/[module]/views/
   ```

### Issue 2: "Element cannot be located" Error
**Problem**: `Element '<xpath expr="...">' cannot be located in parent view`

**Solution**:
1. Examine the actual view structure:
   ```bash
   cat odoo-18/addons/[module]/views/[view_file].xml
   ```
2. Use correct XPath expressions:
   - For kanban: `//kanban`
   - For list: `//list`
   - For form: `//form`
   - For specific elements: `//t[@t-name='card']`

### Issue 3: CSS Not Applying
**Problem**: Custom styles not showing up

**Solution**:
1. Check asset loading in manifest:
   ```python
   'assets': {
       'web.assets_backend': [
           'gl_[module]/static/src/scss/[module]_styles.scss',
       ],
   },
   ```
2. Use `!important` for specificity:
   ```scss
   .custom-style {
       background: red !important;
   }
   ```
3. Clear browser cache and restart Odoo

### Issue 4: Template Inheritance Issues
**Problem**: Template not inheriting correctly

**Solution**:
1. Check template name:
   ```bash
   grep -r "t-name.*template" odoo-18/addons/[module]/static/src/xml/
   ```
2. Use correct inheritance mode:
   ```xml
   <t t-name="[base_module].[template_name]" 
      t-inherit="[base_module].[template_name]" 
      t-inherit-mode="primary">
   ```

---

## 📚 Best Practices

### 1. **Module Naming Convention**
- Use prefix: `gl_` (GreenLines)
- Descriptive names: `gl_pos_products_redesign`
- Version format: `18.0.1.0.0`

### 2. **File Organization**
```
custom_modules/gl_[module_name]/
├── __manifest__.py
├── __init__.py
├── views/
│   └── [module_name]_views.xml
├── static/
│   └── src/
│       ├── xml/
│       │   └── [module_name]_templates.xml
│       ├── scss/
│       │   └── [module_name]_styles.scss
│       └── js/
│           └── [module_name]_scripts.js
└── README.md
```

### 3. **CSS Best Practices**
- Use CSS variables for consistency
- Use `!important` sparingly
- Implement responsive design
- Add dark mode support
- Use modern CSS features (backdrop-filter, etc.)

### 4. **Testing Checklist**
- [ ] Module installs without errors
- [ ] Styles apply correctly
- [ ] Responsive design works
- [ ] Hover effects function
- [ ] No console errors
- [ ] Works in different browsers

### 5. **Performance Considerations**
- Minimize CSS file size
- Use efficient selectors
- Avoid heavy animations
- Optimize images
- Use CSS transforms for animations

---

## 🚀 Quick Commands Reference

### Create New Module
```bash
# Create module structure
mkdir -p custom_modules/gl_[name]/{static/src/{xml,scss,js},views}
cd custom_modules/gl_[name]

# Create basic files
touch __manifest__.py __init__.py
touch views/[name]_views.xml
touch static/src/xml/[name]_templates.xml
touch static/src/scss/[name]_styles.scss
```

### Find Existing Views
```bash
# Search for views
grep -r "kanban.*view" odoo-18/addons/[module]/views/
grep -r "list.*view" odoo-18/addons/[module]/views/
grep -r "form.*view" odoo-18/addons/[module]/views/
```

### Install Module
```bash
# Via command line
python3.11 odoo-18/odoo-bin --addons-path=odoo-18/addons,custom_modules --data-dir=odoo-data --http-port=8069 -i gl_[module_name]

# Via Odoo interface
# Apps → Search → Install
```

### Debug Issues
```bash
# Check logs
tail -f odoo.log

# Clear cache
rm -rf odoo-data/filestore/[database]/web_assets/

# Restart server
./start_odoo.sh
```

---

## 📝 Example: Complete Module

### `gl_example_redesign/__manifest__.py`
```python
{
    'name': 'GL Example Redesign',
    'version': '18.0.1.0.0',
    'category': 'Customization',
    'summary': 'Example of Odoo design customization',
    'description': """
        Example module showing how to customize Odoo design
    """,
    'author': 'GreenLines',
    'depends': ['product', 'web'],
    'data': [
        'views/example_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'gl_example_redesign/static/src/xml/example_templates.xml',
            'gl_example_redesign/static/src/scss/example_styles.scss',
        ],
    },
    'installable': True,
    'auto_install': False,
}
```

### `gl_example_redesign/views/example_views.xml`
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="example_product_kanban_inherit" model="ir.ui.view">
        <field name="name">example.product.kanban.inherit</field>
        <field name="model">product.template</field>
        <field name="inherit_id" ref="product.product_template_kanban_view"/>
        <field name="arch" type="xml">
            <xpath expr="//kanban" position="attributes">
                <attribute name="class">gl-example-grid</attribute>
            </xpath>
            <xpath expr="//t[@t-name='card']" position="attributes">
                <attribute name="class">flex-row gl-example-card</attribute>
            </xpath>
        </field>
    </record>
</odoo>
```

### `gl_example_redesign/static/src/scss/example_styles.scss`
```scss
:root {
    --gl-primary-color: #667eea;
    --gl-border-radius: 16px;
    --gl-transition: all 0.3s ease;
}

.gl-example-grid {
    padding: 20px !important;
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%) !important;
}

.gl-example-card {
    background: rgba(255, 255, 255, 0.95) !important;
    backdrop-filter: blur(10px) !important;
    border-radius: var(--gl-border-radius) !important;
    transition: var(--gl-transition) !important;
    
    &:hover {
        transform: translateY(-8px) !important;
    }
}
```

---

## 🎯 Next Steps

1. **Practice**: Create a simple module following this guide
2. **Experiment**: Try different design patterns
3. **Document**: Keep notes of what works for your specific use cases
4. **Share**: Contribute improvements to this guide

---

*Last updated: 2025-01-05*
*Version: 1.0*
