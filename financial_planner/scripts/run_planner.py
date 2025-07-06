"""Command line interface to run the financial planner."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from financial_planner.config import load_config
from financial_planner.models import CashFlowModel, ProfitAndLossModel
from financial_planner.sales import generate_goal_oriented_sales_plan
from financial_planner.visualization import Visualizer


def main() -> None:
    parser = argparse.ArgumentParser(description="Run financial planner")
    parser.add_argument(
        "--global-config",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "data" / "global_config.yaml",
        help="Path to global config YAML",
    )
    parser.add_argument(
        "--products-config",
        type=Path,
        default=Path(__file__).resolve().parents[1]
        / "data"
        / "productos_config.yaml",
        help="Path to products config YAML",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("output"),
        help="Directory to store CSV results",
    )
    args = parser.parse_args()

    cfg = load_config(args.global_config, args.products_config)
    horizonte = cfg["global"]["horizonte_plan_consolidado"]
    productos = cfg["productos"]

    objetivos = {1: 750000, 2: 1200000, 3: 2100000, 4: 3000000}
    distribucion = [1, 1, 1.5, 1, 1, 1.5, 1, 1, 1.5, 1, 1, 2]

    plan_de_ventas = generate_goal_oriented_sales_plan(
        annual_targets=objetivos,
        monthly_distribution=distribucion,
        product_config=productos,
    )

    cash_model = CashFlowModel(productos, horizonte)
    caja = cash_model.run_consolidation(plan_de_ventas)
    caja["Flujo Neto Mensual"] = caja.sum(axis=1)
    caja["Flujo Neto Acumulado"] = caja["Flujo Neto Mensual"].cumsum()

    capital_necesario = max(0.0, -caja["Flujo Neto Acumulado"].min())
    min_val = caja["Flujo Neto Acumulado"].min()
    min_month = int(caja["Flujo Neto Acumulado"].idxmin() + 1)

    pyg_model = ProfitAndLossModel(productos, horizonte)
    pyg = pyg_model.run_consolidation(plan_de_ventas)
    pyg["Margen Bruto"] = pyg["Total Ventas"] - pyg["Coste Mantenimiento"]
    pyg["EBIT"] = pyg["Margen Bruto"] - pyg["Amortizacion"]
    pyg["Año"] = (pyg.index) // 12 + 1
    pyg_anual = pyg.groupby("Año").sum().reset_index()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    plan_de_ventas.to_csv(args.output_dir / "ventas.csv", index=False)
    caja.to_csv(args.output_dir / "cashflow.csv")
    pyg_anual.to_csv(args.output_dir / "pnl_anual.csv", index=False)

    Visualizer.plot_pnl_annual(pyg_anual)
    Visualizer.plot_cash_flow_monthly(caja, capital_necesario, min_val, min_month)


if __name__ == "__main__":
    main()
