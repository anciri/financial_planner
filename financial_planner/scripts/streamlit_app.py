"""Streamlit interface for the financial planner."""

from __future__ import annotations

from pathlib import Path

import streamlit as st
import pandas as pd

from financial_planner.config import load_config
from financial_planner.models import CashFlowModel, ProfitAndLossModel
from financial_planner.sales import generate_goal_oriented_sales_plan
from financial_planner.visualization import Visualizer


DEFAULT_GLOBAL = Path(__file__).resolve().parents[1] / "data" / "global_config.yaml"
DEFAULT_PRODUCTS = Path(__file__).resolve().parents[1] / "data" / "productos_config.yaml"


def run_planner() -> None:
    cfg = load_config(DEFAULT_GLOBAL, DEFAULT_PRODUCTS)
    horizonte = cfg["global"]["horizonte_plan_consolidado"]
    productos = cfg["productos"]

    objetivos = {1: 750000, 2: 1200000, 3: 2100000, 4: 3000000}
    distribucion = [1, 1, 1.5, 1, 1, 1.5, 1, 1, 1.5, 1, 1, 2]

    plan = generate_goal_oriented_sales_plan(objetivos, distribucion, productos)
    st.subheader("Plan de Ventas")
    st.dataframe(plan)

    cash_model = CashFlowModel(productos, horizonte)
    caja = cash_model.run_consolidation(plan)
    caja["Flujo Neto Mensual"] = caja.sum(axis=1)
    caja["Flujo Neto Acumulado"] = caja["Flujo Neto Mensual"].cumsum()

    capital_necesario = max(0.0, -caja["Flujo Neto Acumulado"].min())
    min_val = caja["Flujo Neto Acumulado"].min()
    min_month = int(caja["Flujo Neto Acumulado"].idxmin() + 1)

    pyg_model = ProfitAndLossModel(productos, horizonte)
    pyg = pyg_model.run_consolidation(plan)
    pyg["Margen Bruto"] = pyg["Total Ventas"] - pyg["Coste Mantenimiento"]
    pyg["EBIT"] = pyg["Margen Bruto"] - pyg["Amortizacion"]
    pyg["Año"] = (pyg.index) // 12 + 1
    pyg_anual = pyg.groupby("Año").sum().reset_index()

    st.subheader("PyG Anual")
    st.dataframe(pyg_anual[["Año", "Total Ventas", "Coste Mantenimiento", "Amortizacion", "EBIT"]])

    fig_pnl = Visualizer.plot_pnl_annual(pyg_anual, show=False)
    st.plotly_chart(fig_pnl, use_container_width=True)

    fig_cf = Visualizer.plot_cash_flow_monthly(caja, capital_necesario, min_val, min_month, show=False)
    st.plotly_chart(fig_cf, use_container_width=True)


st.title("Financial Planner")
if st.button("Ejecutar Planner"):
    run_planner()
