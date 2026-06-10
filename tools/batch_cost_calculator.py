# ============================================================
#  batch_cost_calculator.py
#  Craft Brewery Batch Cost Calculator
#  Inspired by: tfrayner/beerfestdb — tool_dashboard/CBF_beer_price_calculator.py
#  (https://github.com/tfrayner/beerfestdb)
# ============================================================
"""
Craft Brewery Batch Cost Calculator
====================================
Calculates total batch cost, cost-per-barrel, and recommended
selling price per barrel for a given craft beer batch.

Inputs
------
  Ingredient costs
    - grain_cost_per_lb    : float  — cost of grain in $/lb
    - grain_lbs            : float  — total grain weight used (lbs)
    - hops_cost_per_oz     : float  — cost of hops in $/oz
    - hops_oz              : float  — total hops weight used (oz)
    - yeast_cost_per_unit  : float  — cost per yeast packet/vial ($)
    - yeast_units          : int    — number of yeast units used
    - packaging_cost_per_unit : float — cost per package unit (bottle/can/keg) ($)
    - packaging_units      : int    — total packaging units in batch

  Batch parameters
    - batch_size_barrels   : float  — batch size in US barrels (1 bbl = 31 gal)
    - margin_pct           : float  — desired profit margin percentage (e.g. 40.0 for 40%)

Outputs
-------
  - Total ingredient cost ($)
  - Total packaging cost ($)
  - Total batch cost ($)
  - Cost per barrel ($/bbl)
  - Recommended selling price per barrel ($/bbl) at the configured margin
"""

import math


# ── helpers ──────────────────────────────────────────────────────────────────

def calculate_ingredient_cost(
    grain_cost_per_lb: float,
    grain_lbs: float,
    hops_cost_per_oz: float,
    hops_oz: float,
    yeast_cost_per_unit: float,
    yeast_units: int,
) -> dict:
    """Return a breakdown of raw ingredient costs."""
    grain_total = grain_cost_per_lb * grain_lbs
    hops_total  = hops_cost_per_oz  * hops_oz
    yeast_total = yeast_cost_per_unit * yeast_units
    return {
        "grain": round(grain_total, 2),
        "hops":  round(hops_total,  2),
        "yeast": round(yeast_total, 2),
    }


def calculate_packaging_cost(
    packaging_cost_per_unit: float,
    packaging_units: int,
) -> float:
    """Return total packaging cost."""
    return round(packaging_cost_per_unit * packaging_units, 2)


def calculate_batch_totals(
    ingredient_costs: dict,
    packaging_cost: float,
    batch_size_barrels: float,
    margin_pct: float,
) -> dict:
    """
    Aggregate costs and derive per-barrel and selling-price figures.

    Selling price uses a cost-plus margin formula (inspired by the
    ABV/cost-floor logic in CBF_beer_price_calculator.py):

        selling_price_per_bbl = cost_per_bbl / (1 - margin_pct/100)

    The result is rounded up to the nearest whole dollar (ceiling),
    mirroring the 20-pence rounding used in the reference script.
    """
    total_ingredient_cost = sum(ingredient_costs.values())
    total_cost            = round(total_ingredient_cost + packaging_cost, 2)
    cost_per_barrel       = round(total_cost / batch_size_barrels, 2)

    # Cost-plus margin -> recommended sell price, rounded up to nearest $1
    raw_sell_price        = cost_per_barrel / (1 - margin_pct / 100)
    sell_price_per_barrel = math.ceil(raw_sell_price)   # round-up, like reference

    return {
        "total_ingredient_cost":  total_ingredient_cost,
        "total_packaging_cost":   packaging_cost,
        "total_batch_cost":       total_cost,
        "cost_per_barrel":        cost_per_barrel,
        "margin_pct":             margin_pct,
        "sell_price_per_barrel":  sell_price_per_barrel,
    }


def run_batch_cost_calculator(
    grain_cost_per_lb:        float,
    grain_lbs:                float,
    hops_cost_per_oz:         float,
    hops_oz:                  float,
    yeast_cost_per_unit:      float,
    yeast_units:              int,
    packaging_cost_per_unit:  float,
    packaging_units:          int,
    batch_size_barrels:       float,
    margin_pct:               float = 40.0,
    batch_name:               str   = "Sample Batch",
) -> dict:
    """
    High-level entry point.  Runs all calculations and prints a
    formatted report.  Returns the full results dict.
    """
    ingredient_costs = calculate_ingredient_cost(
        grain_cost_per_lb, grain_lbs,
        hops_cost_per_oz,  hops_oz,
        yeast_cost_per_unit, yeast_units,
    )
    packaging_cost = calculate_packaging_cost(packaging_cost_per_unit, packaging_units)
    results        = calculate_batch_totals(
        ingredient_costs, packaging_cost, batch_size_barrels, margin_pct
    )

    # ── formatted report ─────────────────────────────────────────────────────
    sep = "=" * 52
    print(sep)
    print(f"  CRAFT BREWERY BATCH COST REPORT")
    print(f"      Batch : {batch_name}")
    print(f"      Size  : {batch_size_barrels} barrel(s)")
    print(sep)
    print(f"  INGREDIENT COSTS")
    print(f"    Grain          : ${ingredient_costs['grain']:>10,.2f}")
    print(f"    Hops           : ${ingredient_costs['hops']:>10,.2f}")
    print(f"    Yeast          : ${ingredient_costs['yeast']:>10,.2f}")
    print(f"  {'─'*46}")
    print(f"    Subtotal (ingr): ${results['total_ingredient_cost']:>10,.2f}")
    print()
    print(f"  PACKAGING COSTS")
    print(f"    Packaging      : ${results['total_packaging_cost']:>10,.2f}")
    print(f"  {'─'*46}")
    print(f"  TOTAL BATCH COST : ${results['total_batch_cost']:>9,.2f}")
    print()
    print(f"  COST PER BARREL  : ${results['cost_per_barrel']:>9,.2f} / bbl")
    print()
    print(f"  MARGIN TARGET    : {results['margin_pct']}%")
    print(f"  RECOMMENDED SELL : ${results['sell_price_per_barrel']:>9,.2f} / bbl  <- selling price")
    print(sep)

    return results


# ── sample run ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    results = run_batch_cost_calculator(
        # Grain: 400 lbs @ $0.85/lb  (base malt + specialty)
        grain_cost_per_lb       = 0.85,
        grain_lbs               = 400,
        # Hops: 48 oz @ $2.50/oz
        hops_cost_per_oz        = 2.50,
        hops_oz                 = 48,
        # Yeast: 3 units @ $12.00 each
        yeast_cost_per_unit     = 12.00,
        yeast_units             = 3,
        # Packaging: 744 cans @ $0.18 each  (~2 bbl x 31 gal x 128 fl-oz / 16 fl-oz)
        packaging_cost_per_unit = 0.18,
        packaging_units         = 744,
        # Batch: 2 barrels
        batch_size_barrels      = 2.0,
        # Target margin: 45%
        margin_pct              = 45.0,
        batch_name              = "Cascade IPA -- Batch #001",
    )

    print("\n  Raw results dict:")
    for k, v in results.items():
        print(f"    {k:<30} = {v}")
