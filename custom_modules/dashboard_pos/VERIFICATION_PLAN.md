# Pricing Scenarios - Complete Verification Plan

## Overview
This document provides a comprehensive verification plan to test the Pricing Scenarios feature end-to-end before manual dashboard testing. We'll verify data readiness, core math, APIs, UI rendering, and actions with specific pass/fail criteria.

---

## 1) Data Readiness Verification

### A) Source Queries Analysis

**Question**: Show me the source queries for monthly aggregation: which columns map to `product_name`, `qty`, `price (pre-VAT)`, `cost (pre-VAT)`?

**Answer**: 
```sql
-- Main aggregation query from _get_monthly_product_data()
SELECT 
    product_template.name AS product_name,
    SUM(pos_order_line.qty) AS qty,
    AVG(pos_order_line.price_unit) AS price,
    product_product.standard_price AS cost
FROM pos_order_line 
INNER JOIN product_product ON product_product.id = pos_order_line.product_id 
INNER JOIN product_template ON product_product.product_tmpl_id = product_template.id 
INNER JOIN pos_order ON pos_order_line.order_id = pos_order.id
WHERE pos_order_line.company_id = %s 
    AND pos_order.date_order >= %s 
    AND pos_order.date_order < %s 
    AND pos_order.state IN ('paid', 'done', 'invoiced')
    AND product_template.available_in_pos = True
GROUP BY product_template.name, product_product.standard_price
HAVING SUM(pos_order_line.qty) != 0
ORDER BY product_template.name
```

**Column Mapping**:
- `product_name` ← `product_template.name`
- `qty` ← `SUM(pos_order_line.qty)`
- `price` ← `AVG(pos_order_line.price_unit)` (pre-VAT after conversion)
- `cost` ← `product_product.standard_price` (pre-VAT after conversion)

### B) VAT Normalization Logic

**Question**: Show the VAT normalization logic. If prices are gross, where do we divide by 1.05?

**Answer**:
```python
def _convert_to_net_prices(self, raw_data):
    """Convert gross prices to net prices using VAT rates"""
    for item in raw_data:
        vat_rate = self._get_product_vat_rate(item['product_name'])
        
        # Convert price to net (assuming input is gross)
        if item['price'] > 0:
            item['price'] = item['price'] / (1 + vat_rate)
        
        # Convert cost to net (assuming input is gross)
        if item['cost'] > 0:
            item['cost'] = item['cost'] / (1 + vat_rate)
    
    return raw_data

def _get_product_vat_rate(self, product_name):
    """Get VAT rate for a product (default 5% for UAE)"""
    # Returns 0.05 (5%) as default UAE VAT rate
    return 0.05
```

**VAT Conversion**: `gross_price / (1 + 0.05) = net_price`

### C) OPEX SQL Query

**Question**: Show the SQL/view for OPEX (E). Confirm COGS & VAT are excluded and amounts are in AED.

**Answer**:
```sql
-- OPEX query from _get_monthly_expenses()
SELECT COALESCE(SUM(aml.debit - aml.credit), 0) AS expenses_E
FROM account_move_line aml
INNER JOIN account_account aa ON aa.id = aml.account_id
INNER JOIN account_move am ON am.id = aml.move_id
WHERE aml.company_id = %s
    AND aml.date >= %s
    AND aml.date < %s
    AND am.state = 'posted'
    AND aa.account_type IN ('expense', 'other')
    AND aa.code NOT LIKE '4%'  -- Exclude COGS (typically 4xxx)
    AND aa.code NOT LIKE '5%'  -- Exclude VAT accounts (typically 5xxx)
    AND aa.name NOT ILIKE '%vat%'
    AND aa.name NOT ILIKE '%tax%'
    AND aa.name NOT ILIKE '%extraordinary%'
    AND aa.name NOT ILIKE '%cogs%'
    AND aa.name NOT ILIKE '%cost of goods%'
```

**Exclusions Confirmed**:
- ✅ COGS: `aa.code NOT LIKE '4%'` and `aa.name NOT ILIKE '%cogs%'`
- ✅ VAT: `aa.code NOT LIKE '5%'` and `aa.name NOT ILIKE '%vat%'`
- ✅ Currency: Assumes AED (company default)

---

## 2) Core Math Verification

### A) Totals Calculation

**Question**: Using month `2025-07`, print `R, G, E, N, x_min`.

**Expected Formula**:
```python
R = sum(item['qty'] * item['price'] for item in product_data)
G = sum(item['qty'] * (item['price'] - item['cost']) for item in product_data)
E = _get_monthly_expenses(month_start, month_end)  # From GL
N = G - E
x_min = max((item['cost'] / item['price']) - 1 for item in product_data if item['price'] > 0)
```

### B) Break-Even Verification

**Question**: Compute Break-Even prices and show: `Σ qty*(price_be - cost)` and `E`. They must match within **±0.01 AED**.

**Formula**:
```python
price_be = cost + (E * price / R)
validation = sum(qty * (price_be - cost)) == E ±0.01 AED
```

### C) +10,000 AED Net Verification

**Question**: For +10,000 AED, show `x_raw` and final `x` (after cost floor).

**Formulas**:
```python
# Uniform
x_raw = (N_target - N) / R
x = max(x_raw, x_min)
price_target = price * (1 + x)

# Weighted
w_i = revenue_i / R_total
S2 = sum(w_i^2)
x_i0 = x * (w_i / S2)
x_i = max(x_i0, cost_i/price_i - 1)
# + iterative re-normalization
```

**Validation**:
- Uniform: `projected_net == 10000 ±0.5 AED` (if no floors)
- Weighted: `Σ(revenue * x_i) == x*R ±0.01 AED`

### D) Unrealistic Detection

**Question**: For Custom target = 25,000 AED, confirm whether it's unrealistic.

**Rules**:
1. `x_raw > 0.30` (30% average uplift)
2. Even with 50% cap, projected net < target
3. >10% of items need >2x price
4. `R_total <= 0` (low/no sales)

---

## 3) API Verification

### A) Main Endpoint

**Question**: Call `GET /api/pricing-scenarios?month=2025-07` and validate JSON schema.

**Expected Response Schema**:
```json
{
  "month": "2025-07",
  "totals": {
    "R": 10000.0,
    "G": 1950.0,
    "E": 1800.0,
    "N": 150.0,
    "x_min": 0.0
  },
  "scenarios": {
    "break_even": [...],
    "net_10k": {
      "uniform": {...},
      "weighted": {...}
    },
    "net_custom": {...}
  },
  "status": "ok"
}
```

### B) Error Handling

**Question**: Test months with no sales and missing OPEX.

**Expected Responses**:
- No sales: `{"status": "insufficient", "message": "Insufficient sales last month to compute target."}`
- No OPEX: `{"status": "insufficient", "message": "No OPEX available; please close month in Finance."}`

---

## 4) UI Rendering Verification

### A) Summary Card
- [ ] Shows Revenue, Gross, Expenses, Net, x_min (AED formatting, 2 decimals)
- [ ] Month picker only allows past months

### B) Tabs & Controls
- [ ] Tabs: Break-Even / +10,000 AED Net / +Custom Net
- [ ] +10k & Custom tabs have Uniform / Weighted toggle
- [ ] Custom tab has numeric AED input with validation

### C) Tables
**Break-Even**:
- [ ] Columns: Product | Qty | Cost | Real Price | Break-Even Price | Diff | Diff %
- [ ] Negative Diff highlighted (below BE)

**10k / Custom**:
- [ ] Columns: Product | Qty | Cost | Real Price | Target Price | % Change | Margin After
- [ ] Rows near cost (margin <2%) flagged

### D) Banners
- [ ] Uniform banner: "Required uniform uplift: X%"
- [ ] Weighted banner: "Range: a% – b%"
- [ ] Unrealistic banner with guidance
- [ ] Insufficient sales banner when R=0

---

## 5) Actions & Safety Verification

### A) Preview Functionality

**Question**: POST `/api/pricing-scenarios/apply` with `dry_run=true`.

**Expected Response**:
```json
{
  "status": "preview",
  "summary": {
    "products": 100,
    "min_pct": 0.05,
    "max_pct": 0.25,
    "floors_triggered": 15
  },
  "rows_sample": [...]
}
```

### B) Price List Creation

**Question**: Test `dry_run=false` and activation.

**Expected Flow**:
1. Create draft price list
2. Activate with admin permissions
3. Update product prices
4. Audit trail created

### C) RBAC Testing

**Question**: Attempt activation with non-admin role.

**Expected**: `{"status": "error", "message": "Only Pricing Administrators can activate price lists"}`

### D) Idempotency

**Question**: Submit same request twice with same `idempotency_key`.

**Expected**: Only one price list created, second request returns existing list.

---

## 6) Pass/Fail Criteria

### ✅ PASS Criteria
- **Break-Even math**: `Σ qty*(price_be - cost) == E ±0.01 AED`
- **Uniform net target**: projected net == target ±0.5 AED (no floors)
- **Weighted budget**: `Σ(revenue*x_i) == x*R ±0.01 AED`
- **Floors**: No target price below cost
- **Unrealistic**: Trigger fires for `x_raw > 0.30`
- **VAT**: 105 gross → 100 net at 5%
- **API schema**: matches JSON contract
- **RBAC**: non-admin activate blocked
- **Idempotency**: duplicate apply → single list

### ❌ FAIL Criteria
- Math calculations off by more than tolerance
- API returns wrong schema
- UI shows incorrect data
- RBAC allows unauthorized access
- Duplicate price lists created
- VAT conversion incorrect

---

## 7) One-Shot Verification Script

**Command to Cursor**:
> "Run a full verification for month `2025-07`:
> 1. print R,G,E,N,x_min;
> 2. break-even: prove Σ qty*(price_be − cost) == E;
> 3. +10k Uniform/Weighted: show x, min/max %, prove budget equality and net hit;
> 4. Custom=25,000: show unrealistic triggers;
> 5. VAT check (105 gross → 100 net);
> 6. POST apply dry_run weighted → summary;
> 7. POST apply live → create draft; then activate (as Admin) and show audit;
> 8. repeat activate with non-admin → expect RBAC error;
> 9. resend same apply with same idempotency_key → prove single list;
> Paste outputs and screenshots of the dashboard tabs and banners."

---

## 8) Execution Plan

### Phase 1: Backend Verification
1. Test data queries and aggregation
2. Verify mathematical calculations
3. Test API endpoints
4. Validate error handling

### Phase 2: Frontend Verification
1. Test UI rendering
2. Verify user interactions
3. Test action buttons
4. Validate permissions

### Phase 3: Integration Testing
1. End-to-end workflow
2. RBAC testing
3. Idempotency testing
4. Performance testing

### Phase 4: Manual Dashboard Testing
1. Open POS Dashboard
2. Navigate to Pricing Scenarios
3. Test all scenarios and modes
4. Verify visual elements and interactions

---

This verification plan ensures complete testing of all functionality before manual dashboard testing, providing confidence that the feature works correctly end-to-end.
