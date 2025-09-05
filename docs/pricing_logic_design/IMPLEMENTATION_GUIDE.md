# Cursor Implementation Guide — Pricing Scenarios (POS Dashboard)

## Goal
Compute and render **Break-Even**, **+10,000 AED Net**, and **+Custom Net** prices for each Product Name for **previous months** only, using the business logic in `pricing_scenarios_spec.json`.

---

## Steps

1. **Data Aggregation (Backend)**
   - Aggregate per `product_name` for the selected past month:
     - `qty` (net of returns), `price` (pre-VAT effective), `cost` (pre-VAT per-unit).
   - Compute per-item `revenue = qty * price` and totals `R, G, N = G - E`.
   - Ensure `E` (expenses) is the month’s OPEX (exclude COGS & VAT).

2. **Scenarios**
   - **Break-Even**: `price_be = cost + (E * price / R)` with revenue weights.
   - **Net +10k**:
     - Uniform: `x = max((N_target - N)/R, x_min)`; `price_target = price*(1+x)`.
     - Weighted: Use weights `w = revenue/R` and `S2 = sum(w^2)`; `x_i = x*(w/S2)`, apply floors and re-normalize to keep uplift budget.
   - **Net +Custom**: Copy net+10k flow with `N_target = input`.

3. **Unrealistic/Insufficient Handling**
   - Unrealistic if `x_raw > 0.30`, or even at `+50%` cap net < target, or many items need >2x, or `R<=0`.
   - Show guidance text (branches, marketing, acquisition, basket size, mix, overheads).

4. **UI Rendering (POS Dashboard)**
   - Controls: month picker (past only); tabs (Break Even, +10k, +Custom); toggle Uniform/Weighted for target tabs; numeric input for custom target.
   - Summary card: R, G, E, N, x_min.
   - Tables per spec; highlight below-cost / near-cost rows.
   - Action chips: Apply Uniform; Apply Weighted.
   - Banners for required uplifts and warnings.

5. **Precision & Rounding**
   - Internal: double precision.
   - UI prices: 2 decimals, AED currency format.
   - Totals validation tolerance: ±0.01 AED.

6. **APIs**
   - `GET /api/pricing-scenarios?month=YYYY-MM` returns the response schema in the JSON spec.
   - Backend must pre-validate data completeness and respond with `status` and `message` for errors.

---

## What We Implemented
- Business logic for break-even and target net scenarios (uniform and weighted).
- Cost-floor enforcement and redistribution.
- Unrealistic target detection with actionable guidance.
- Dashboard UI contract with consistent tables and banners.
- JSON API contract for frontend consumption.

---

## Verification Checklist
- ✅ Break-even total margin equals E (±0.01 AED).
- ✅ Uniform scenario reaches N_target when no floors bind (±0.5 AED).
- ✅ Weighted scenario total uplift equals uniform uplift budget (±0.01 AED).
- ✅ No target price below cost.
- ✅ Unrealistic messaging appears for extreme inputs.

---

## Notes for Cursor
- Keep logic in a pure module so it’s testable.
- Write unit tests with the sample dataset in the JSON file.
- Add a small iterative loop for weighted uplift re-normalization; cap iterations (e.g., 20) and break on convergence by uplift budget gap < 0.01 AED.
- Respect VAT handling (use pre-VAT). If upstream sends gross, convert using 5% VAT.