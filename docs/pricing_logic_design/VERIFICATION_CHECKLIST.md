# Cursor Verification Plan

## Unit Tests
1. **Break-Even Equality**: Sum(qty*(price_be - cost)) == E ±0.01 AED.
2. **Uniform Target Hit**: With no floors engaged, computed net equals N_target ±0.5 AED.
3. **Weighted Budget Equality**: Sum(revenue * x_i) == x * R ±0.01 AED.
4. **Cost Floors**: All target prices >= cost.
5. **Unrealistic Flags**: Trigger on x_raw>0.30 and on +50% cap shortfall.
6. **Insufficient Sales**: R==0 returns InsufficientSales with message.

## Integration Tests
- API returns schema-compliant JSON.
- UI renders tables with correct columns and badges.
- Month picker restricts to past months.
- [x] **Real OPEX integration from GL accounts**
- [x] **VAT conversion for gross-to-net prices**
- [x] **Price list creation and activation**
- [x] **Action buttons functionality**

## Manual QA
- Try Custom Net = extremely high number → see "unrealistic" guidance.
- Try Custom Net = current N_total → expect tiny/no changes.
- Try dataset with many near-cost items → see warnings and higher uplifts concentrated on high-weight items.
- [x] **Test expense integration with real GL data**
- [x] **Test VAT conversion with different tax rates**
- [x] **Test price list creation and activation workflow**
- [x] **Test RBAC permissions for pricing administrators**

## New Test Coverage
- [x] **Expense Integration Tests** - OPEX calculation, COGS/VAT exclusion, negative expense handling
- [x] **VAT Conversion Tests** - Gross-to-net conversion, different tax rates, precision handling
- [x] **Action Button Tests** - Price list creation, activation, idempotency, RBAC validation


docs/pricing_logic_design

docs/pricing_logic_design/IMPLEMENTATION_GUIDE.md
docs/pricing_logic_design/pricing_scenarios_spec.json
docs/pricing_logic_design/VERIFICATION_CHECKLIST.md


