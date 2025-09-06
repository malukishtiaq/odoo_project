# Odoo 15 to 18 Technical Migration Checklist

## Module-Specific Technical Changes

### 1. dashboard_pos_collection

#### Manifest File Changes
- [ ] **Version Update**: `'version': '15.0.1.0.0'` → `'version': '18.0.1.0.0'`
- [ ] **Dependencies Check**: 
  - [ ] Verify `hr` module compatibility
  - [ ] Verify `point_of_sale` module compatibility
  - [ ] Check `wt_create_so_from_pos` dependency
- [ ] **External Dependencies**: 
  - [ ] Verify `pandas` compatibility with Odoo 18
  - [ ] Update pandas version if needed

#### Python Code Changes
- [ ] **models/pos_order.py**:
  - [ ] Check `_order_fields()` method for API changes
  - [ ] Review `super()` calls for compatibility
  - [ ] Verify field definitions
- [ ] **models/pos_dashboard.py**:
  - [ ] Review dashboard data processing
  - [ ] Check for deprecated methods
  - [ ] Verify pandas integration

#### JavaScript Changes
- [ ] **Chart.js Integration**:
  - [ ] Update Chart.js CDN link if needed
  - [ ] Check for JavaScript framework changes
- [ ] **Asset Loading**:
  - [ ] Verify `point_of_sale.assets` compatibility
  - [ ] Check `web.assets_qweb` usage
- [ ] **POS Integration**:
  - [ ] Review POS screen modifications
  - [ ] Check payment screen changes

#### XML Template Changes
- [ ] **QWeb Templates**:
  - [ ] Review template syntax for Odoo 18
  - [ ] Check for deprecated attributes
- [ ] **View Definitions**:
  - [ ] Update view structure if needed

### 2. gl_hide_component_fabric

#### Manifest File Changes
- [ ] **Version Update**: `'version': '15.0.1.0.0'` → `'version': '18.0.1.0.0'`
- [ ] **Dependencies**: Verify `base`, `hr`, `point_of_sale` compatibility

#### Python Code Changes
- [ ] **models/product_template.py**:
  - [ ] Check product template inheritance
  - [ ] Review field modifications
  - [ ] Verify API compatibility

#### JavaScript Changes
- [ ] **HideComponent.js**:
  - [ ] Review component hiding logic
  - [ ] Check for POS API changes
  - [ ] Verify receipt modification methods

#### XML Changes
- [ ] **pos_receipt.xml**:
  - [ ] Review receipt template modifications
  - [ ] Check for template syntax changes

### 3. gl_ref_pos_order

#### Manifest File Changes
- [ ] **Version Update**: `'version': '15.0.1.0.0'` → `'version': '18.0.1.0.0'`

#### Python Code Changes
- [ ] **models/pos_order.py**:
  - [ ] Review order reference functionality
  - [ ] Check POS order API changes
  - [ ] Verify field definitions

#### JavaScript Changes
- [ ] **RefOrderSelectionButton.js**:
  - [ ] Review button implementation
  - [ ] Check for UI framework changes
- [ ] **RefOrderSelectionPopup.js**:
  - [ ] Review popup functionality
  - [ ] Check popup API changes
- [ ] **RefOrderSelection.js**:
  - [ ] Review selection logic
  - [ ] Verify data handling

#### XML Changes
- [ ] **RefOrderButton.xml**:
  - [ ] Review button template
- [ ] **RefOrderSelectionPopup.xml**:
  - [ ] Review popup template

### 4. pos_customer

#### Manifest File Changes
- [ ] **Version Update**: `'version': '15.0.0'` → `'version': '18.0.0'`

#### JavaScript Changes
- [ ] **ClientDetailsEdit.js**:
  - [ ] Review customer editing functionality
  - [ ] Check for POS customer API changes
  - [ ] Verify form handling

### 5. purchase_extensions

#### Manifest File Changes
- [ ] **Version Update**: `'version': '15.0.0'` → `'version': '18.0.0'`
- [ ] **Dependencies Check**:
  - [ ] Verify `purchase` module compatibility
  - [ ] Verify `stock` module compatibility
  - [ ] Check `web_ir_actions_act_window_message` availability
  - [ ] Verify `sale_management` compatibility
  - [ ] Verify `product` module compatibility

#### Python Code Changes
- [ ] **models/product_template.py**:
  - [ ] Review product template modifications
  - [ ] Check for API changes
- [ ] **models/purchase.py**:
  - [ ] Review purchase order modifications
  - [ ] Check purchase API changes
- [ ] **models/sale_order.py**:
  - [ ] Review sale order modifications
  - [ ] Check sale API changes

#### XML Changes
- [ ] **views/product.xml**:
  - [ ] Review product view modifications
- [ ] **views/purchase.xml**:
  - [ ] Review purchase view modifications
- [ ] **views/sale_order.xml**:
  - [ ] Review sale order view modifications

### 6. wt_create_so_from_pos

#### Manifest File Changes
- [ ] **Version Update**: `'version': '15.0.0.1'` → `'version': '18.0.0.1'`
- [ ] **Dependencies**: Verify `point_of_sale`, `sale_management`, `sale` compatibility

#### Python Code Changes
- [ ] **models/pos_config.py**:
  - [ ] Review POS configuration extensions
  - [ ] Check POS config API changes
- [ ] **models/sale_collection.py**:
  - [ ] Review collection functionality
  - [ ] Check for API changes
- [ ] **models/sale_delivery.py**:
  - [ ] Review delivery functionality
  - [ ] Check for API changes
- [ ] **models/sale_order.py**:
  - [ ] Review sale order extensions
  - [ ] Check sale order API changes

#### JavaScript Changes
- [ ] **Screens/ProductScreen/ControlButtons/SaleOrderButton.js**:
  - [ ] Review sale order button functionality
- [ ] **Screens/ProductScreen/ControlButtons/ViewSalesOrderButton.js**:
  - [ ] Review view sales order button
- [ ] **Screens/SaleOrderScreen/SaleOrderScreen.js**:
  - [ ] Review sale order screen implementation
- [ ] **Screens/SaleOrderScreen/ViewSaleOrderList.js**:
  - [ ] Review order list functionality
- [ ] **Screens/SaleOrderScreen/ViewSaleOrderRow.js**:
  - [ ] Review order row implementation
- [ ] **Popups/SalesOrderPopup.js**:
  - [ ] Review popup functionality
- [ ] **PosOrder.js**:
  - [ ] Review POS order extensions

#### XML Changes
- [ ] **All XML files in static/src/xml/**:
  - [ ] Review all template files
  - [ ] Check for template syntax changes
  - [ ] Verify QWeb compatibility

#### Security Changes
- [ ] **security/ir.model.access.csv**:
  - [ ] Review access control definitions
  - [ ] Check for security model changes

## Common Technical Changes Across All Modules

### 1. Manifest File Updates
- [ ] **Version Numbers**: Update all version numbers from 15.0.x.x.x to 18.0.x.x.x
- [ ] **Dependencies**: Verify all module dependencies are available in Odoo 18
- [ ] **Asset Definitions**: Check asset loading mechanisms
- [ ] **External Dependencies**: Verify external package compatibility

### 2. Python Code Updates
- [ ] **Import Statements**: Check for deprecated imports
- [ ] **Model Inheritance**: Verify inheritance syntax
- [ ] **Field Definitions**: Check for deprecated field types
- [ ] **Method Signatures**: Review method parameters
- [ ] **API Calls**: Check for deprecated API methods
- [ ] **Super() Calls**: Verify super() usage
- [ ] **Decorators**: Check for deprecated decorators

### 3. JavaScript Updates
- [ ] **Framework Compatibility**: Check for JavaScript framework changes
- [ ] **POS API**: Review POS-specific API changes
- [ ] **Event Handling**: Check for event system changes
- [ ] **Component Lifecycle**: Review component lifecycle methods
- [ ] **Asset Loading**: Verify asset loading mechanisms

### 4. XML Template Updates
- [ ] **QWeb Syntax**: Check for template syntax changes
- [ ] **View Definitions**: Review view structure
- [ ] **Field Definitions**: Check for field attribute changes
- [ ] **Button Definitions**: Review button implementations
- [ ] **Popup Definitions**: Check popup implementations

### 5. Security Updates
- [ ] **Access Control**: Review access control definitions
- [ ] **Record Rules**: Check for security rule changes
- [ ] **Permissions**: Verify permission definitions

## Testing Checklist

### 1. Installation Testing
- [ ] **Module Installation**: Each module installs without errors
- [ ] **Dependency Resolution**: All dependencies resolve correctly
- [ ] **Database Updates**: Database schema updates successfully

### 2. Functionality Testing
- [ ] **Core Features**: All core features work as expected
- [ ] **User Interface**: UI elements display correctly
- [ ] **Data Integrity**: Data is preserved and accessible
- [ ] **Performance**: Performance is maintained or improved

### 3. Integration Testing
- [ ] **Module Interactions**: Modules work together correctly
- [ ] **POS Integration**: POS functionality works correctly
- [ ] **Sales Integration**: Sales order functionality works
- [ ] **Purchase Integration**: Purchase functionality works

### 4. Error Handling
- [ ] **Error Messages**: Error messages are clear and helpful
- [ ] **Exception Handling**: Exceptions are handled gracefully
- [ ] **Logging**: Appropriate logging is in place

## Rollback Procedures

### 1. Code Rollback
- [ ] **Version Control**: Maintain clean version control
- [ ] **Backup Strategy**: Keep backups of working code
- [ ] **Rollback Scripts**: Prepare rollback scripts

### 2. Database Rollback
- [ ] **Database Backup**: Maintain database backups
- [ ] **Schema Rollback**: Prepare schema rollback procedures
- [ ] **Data Migration**: Prepare data migration rollback

### 3. System Rollback
- [ ] **Environment Rollback**: Prepare environment rollback
- [ ] **Configuration Rollback**: Prepare configuration rollback
- [ ] **Service Rollback**: Prepare service rollback procedures

## Documentation Updates

### 1. Technical Documentation
- [ ] **API Documentation**: Update API documentation
- [ ] **Code Comments**: Update code comments
- [ ] **README Files**: Update README files

### 2. User Documentation
- [ ] **User Guides**: Update user guides
- [ ] **Feature Documentation**: Update feature documentation
- [ ] **Troubleshooting**: Update troubleshooting guides

### 3. Deployment Documentation
- [ ] **Installation Guides**: Update installation guides
- [ ] **Configuration Guides**: Update configuration guides
- [ ] **Maintenance Guides**: Update maintenance guides

---

**Note**: This checklist should be used in conjunction with the main migration plan. Each item should be checked off as completed, and any issues should be documented for resolution.
