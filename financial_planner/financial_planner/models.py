"""Financial models to compute cash flow and P&L."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

import numpy as np
import pandas as pd


@dataclass
class FinancialModel:
    """Base class for financial models."""

    config_productos: Dict[str, Any]
    horizonte_meses: int

    def __post_init__(self) -> None:
        self.templates = self._generate_all_templates()

    def _generate_all_templates(self) -> Dict[str, pd.DataFrame]:
        """Return templates for each product category."""
        return {
            cat: self._create_template(params)
            for cat, params in self.config_productos.items()
        }

    def _create_template(self, params: Dict[str, Any]) -> pd.DataFrame:
        raise NotImplementedError

    def run_consolidation(self, sales_plan: pd.DataFrame) -> pd.DataFrame:
        """Consolidate flows of all sales in the plan."""
        months = range(1, self.horizonte_meses + 1)
        # Use the columns from any template
        first_template = next(iter(self.templates.values()))
        consolidated = pd.DataFrame(0.0, index=months, columns=first_template.columns)
        for _, sale in sales_plan.iterrows():
            start = sale["Mes de Inicio"]
            cat = sale["Categoría Producto"]
            template = self.templates[cat]
            end = start + len(template) - 1
            valid_range = consolidated.index[start - 1 : end]
            consolidated.loc[valid_range, :] += template.iloc[: len(valid_range)].values
        return consolidated


class CashFlowModel(FinancialModel):
    """Compute monthly cash flow."""

    def _create_template(self, params: Dict[str, Any]) -> pd.DataFrame:
        df = pd.DataFrame(
            0.0, index=range(self.horizonte_meses), columns=["Total Ingresos", "Total Gastos"]
        )
        # Ingresos puntuales
        for pago in params.get("esquema_pagos_venta", []):
            df.loc[pago["mes_relativo"], "Total Ingresos"] += params["valor_venta"] * pago["porcentaje"]
        # Gastos puntuales
        for pago in params.get("esquema_pago_coste", []):
            df.loc[pago["mes_relativo"], "Total Gastos"] += -params["coste_maquina"] * pago["porcentaje"]

        cond = (
            (df.index >= params["mes_inicio_recurrentes"])
            & (
                df.index
                < params["mes_inicio_recurrentes"] + params["duracion_pagos_recurrentes"]
            )
        )

        pct_pagado = sum(p["porcentaje"] for p in params.get("esquema_pagos_venta", []))
        valor_restante = params["valor_venta"] * (1 - pct_pagado)
        if params["duracion_pagos_recurrentes"]:
            cuota_renting = valor_restante / params["duracion_pagos_recurrentes"]
            df.loc[cond, "Total Ingresos"] += cuota_renting

        if params.get("porcentaje_mantenimiento_anual", 0) > 0:
            venta = (
                2 * params["porcentaje_mantenimiento_anual"] * params["coste_maquina"] / 12
            )
            coste = params["porcentaje_mantenimiento_anual"] * params["coste_maquina"] / 12
            df.loc[cond, "Total Ingresos"] += venta
            df.loc[cond, "Total Gastos"] += -coste

        return df


class ProfitAndLossModel(FinancialModel):
    """Compute P&L."""

    def _create_template(self, params: Dict[str, Any]) -> pd.DataFrame:
        df = pd.DataFrame(
            0.0,
            index=range(self.horizonte_meses),
            columns=["Total Ventas", "Coste Mantenimiento", "Amortizacion"],
        )
        cond_rec = (
            (df.index >= params["mes_inicio_recurrentes"])
            & (
                df.index
                < params["mes_inicio_recurrentes"] + params["duracion_pagos_recurrentes"]
            )
        )
        for pago in params.get("esquema_pagos_venta", []):
            df.loc[pago["mes_relativo"], "Total Ventas"] += params["valor_venta"] * pago["porcentaje"]

        pct_pagado = sum(p["porcentaje"] for p in params.get("esquema_pagos_venta", []))
        valor_restante = params["valor_venta"] * (1 - pct_pagado)
        if params["duracion_pagos_recurrentes"]:
            ingreso = valor_restante / params["duracion_pagos_recurrentes"]
            df.loc[cond_rec, "Total Ventas"] += ingreso

        if params.get("porcentaje_mantenimiento_anual", 0) > 0:
            venta = (
                2 * params["porcentaje_mantenimiento_anual"] * params["coste_maquina"] / 12
            )
            coste = params["porcentaje_mantenimiento_anual"] * params["coste_maquina"] / 12
            df.loc[cond_rec, "Total Ventas"] += venta
            df.loc[cond_rec, "Coste Mantenimiento"] = coste

        if params.get("meses_amortizacion", 0) > 0:
            amort = params["coste_maquina"] / params["meses_amortizacion"]
            inicio_amort = params["mes_inicio_recurrentes"]
            cond_amort = (
                (df.index >= inicio_amort)
                & (df.index < inicio_amort + params["meses_amortizacion"])
            )
            df.loc[cond_amort, "Amortizacion"] = amort
        return df
