"""Plotting utilities using plotly."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class Visualizer:
    """Create plots for financial outputs."""

    @staticmethod
    def plot_pnl_annual(pyg_anual_df: pd.DataFrame, show: bool = True):
        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=pyg_anual_df["Año"],
                y=pyg_anual_df["Total Ventas"],
                name="Ventas Anuales",
                marker_color="green",
            )
        )
        fig.add_trace(
            go.Bar(
                x=pyg_anual_df["Año"],
                y=-pyg_anual_df["Coste Mantenimiento"],
                name="Coste Mantenimiento Anual",
                marker_color="orange",
            )
        )
        fig.add_trace(
            go.Bar(
                x=pyg_anual_df["Año"],
                y=-pyg_anual_df["Amortizacion"],
                name="Amortización Anual",
                marker_color="yellow",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=pyg_anual_df["Año"],
                y=pyg_anual_df["EBIT"],
                name="Beneficio (EBIT) Anual",
                mode="lines+markers",
                line=dict(color="black", width=3),
            )
        )
        fig.update_layout(
            title_text="<b>Cuenta de Pérdidas y Ganancias (PyG) Anual</b>",
            xaxis_title="Año del Plan",
            yaxis_title="Importe (€)",
            barmode="relative",
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            template="plotly_white",
            xaxis=dict(tickmode="linear", tick0=1, dtick=1),
        )
        if show:
            fig.show()
        return fig

    @staticmethod
    def plot_cash_flow_monthly(
        caja_mensual_df: pd.DataFrame,
        capital_necesario: float,
        min_flujo_acumulado: float,
        mes_capital_minimo: int,
        show: bool = True,
    ):
        datos = caja_mensual_df.reset_index().rename(columns={"index": "Mes"})
        datos["Mes"] += 1
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(
            go.Bar(
                x=datos["Mes"],
                y=datos["Total Ingresos"],
                name="Ingresos Mensuales",
                marker_color="#4CAF50",
            ),
            secondary_y=False,
        )
        fig.add_trace(
            go.Bar(
                x=datos["Mes"],
                y=datos["Total Gastos"].abs(),
                customdata=datos["Total Gastos"],
                name="Gastos Mensuales",
                marker_color="#F44336",
            ),
            secondary_y=False,
        )
        fig.add_trace(
            go.Scatter(
                x=datos["Mes"],
                y=datos["Flujo Neto Acumulado"],
                name="Flujo Neto Acumulado",
                mode="lines+markers",
                line=dict(color="blue", width=3),
            ),
            secondary_y=True,
        )
        if capital_necesario > 0:
            fig.add_trace(
                go.Scatter(
                    x=[mes_capital_minimo],
                    y=[min_flujo_acumulado],
                    mode="markers",
                    marker=dict(color="red", size=15, symbol="star"),
                    name="Necesidad Máxima de Tesorería",
                ),
                secondary_y=True,
            )
        fig.update_layout(
            title_text="<b>Análisis de Tesorería (Flujo de Caja Mensual)</b>",
            xaxis_title="Mes del Plan",
            barmode="group",
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            template="plotly_white",
        )
        fig.update_yaxes(title_text="Importe Mensual (€)", secondary_y=False)
        fig.update_yaxes(title_text="Flujo Neto Acumulado (€)", secondary_y=True, color="blue")
        if show:
            fig.show()
        return fig
