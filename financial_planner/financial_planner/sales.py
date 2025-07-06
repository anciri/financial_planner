"""Sales plan utilities."""

from __future__ import annotations

from typing import Any, Dict, List

import numpy as np
import pandas as pd


def generate_goal_oriented_sales_plan(
    annual_targets: Dict[int, float],
    monthly_distribution: List[float],
    product_config: Dict[str, Any],
) -> pd.DataFrame:
    """Generate a sales plan that tries to meet annual revenue goals."""
    all_sales: List[Dict[str, Any]] = []
    sale_counter = 1
    distribution = np.array(monthly_distribution, dtype=float)
    distribution /= distribution.sum()
    product_names = list(product_config.keys())
    product_prices = np.array([p["valor_venta"] for p in product_config.values()], dtype=float)
    weights = 1 / product_prices
    weights /= weights.sum()

    for year, target in annual_targets.items():
        revenue = 0
        while revenue < target:
            product = np.random.choice(product_names, p=weights)
            month = np.random.choice(range(1, 13), p=distribution)
            absolute_month = (year - 1) * 12 + month
            all_sales.append(
                {
                    "ID Venta": f"Venta-{sale_counter:03d}",
                    "Mes de Inicio": int(absolute_month),
                    "Categoría Producto": product,
                }
            )
            revenue += product_config[product]["valor_venta"]
            sale_counter += 1

    return pd.DataFrame(all_sales)
