import pandas as pd
from financial_planner.models import CashFlowModel, ProfitAndLossModel


def test_simple_product_flow():
    productos = {
        "Test": {
            "valor_venta": 120,
            "coste_maquina": 60,
            "meses_amortizacion": 12,
            "porcentaje_mantenimiento_anual": 0.0,
            "esquema_pagos_venta": [{"mes_relativo": 1, "porcentaje": 1.0}],
            "esquema_pago_coste": [{"mes_relativo": 1, "porcentaje": 1.0}],
            "mes_inicio_recurrentes": 1,
            "duracion_pagos_recurrentes": 0,
        }
    }
    plan = pd.DataFrame(
        [{"ID Venta": "V1", "Mes de Inicio": 1, "Categoría Producto": "Test"}]
    )
    cash = CashFlowModel(productos, 12).run_consolidation(plan)
    assert cash.loc[1, "Total Ingresos"] == 120
    assert cash.loc[1, "Total Gastos"] == -60

    pyg = ProfitAndLossModel(productos, 12).run_consolidation(plan)
    assert pyg.loc[1, "Total Ventas"] == 120
    assert pyg.loc[1, "Amortizacion"] == 5
    assert pyg.loc[12, "Amortizacion"] == 5
