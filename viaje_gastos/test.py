import unittest
from datetime import date
from viaje_gastos.modelos import Viaje, Gasto, TipoViaje, TipoGasto, MetodoPago

class TestViaje(unittest.TestCase):

    def test_presupuesto_actual_vs_real(self):
        """Verifica que el presupuesto se calcule correctamente hasta una fecha determinada"""
        viaje = Viaje(
            tipo_viaje=TipoViaje.NACIONAL,
            fecha_inicio=date(2025, 6, 1),
            fecha_fin=date(2025, 6, 10),
            presupuesto_diario=100000
        )

        # Gasto dentro del rango evaluado
        gasto1 = Gasto(date(2025, 6, 1), 90000, TipoGasto.ALIMENTACION, MetodoPago.EFECTIVO)
        gasto1.valor_pesos = 90000
        gasto2 = Gasto(date(2025, 6, 2), 110000, TipoGasto.ALIMENTACION, MetodoPago.TARJETA)
        gasto2.valor_pesos = 110000

        # Gasto fuera del rango (no debe contarse)
        gasto3 = Gasto(date(2025, 6, 4), 100000, TipoGasto.ALIMENTACION, MetodoPago.EFECTIVO)
        gasto3.valor_pesos = 100000

        viaje.agregar_gasto(gasto1)
        viaje.agregar_gasto(gasto2)
        viaje.agregar_gasto(gasto3)

        diferencia = viaje.presupuesto_actual_vs_real(date(2025, 6, 3))
        self.assertEqual(diferencia, 100000)

    def test_total_por_tipo(self):
        """Verifica que se agrupen correctamente los gastos por tipo y método"""
        viaje = Viaje(
            tipo_viaje=TipoViaje.NACIONAL,
            fecha_inicio=date(2025, 6, 1),
            fecha_fin=date(2025, 6, 10),
            presupuesto_diario=100000
        )

        gasto1 = Gasto(date(2025, 6, 1), 50000, TipoGasto.ALIMENTACION, MetodoPago.EFECTIVO)
        gasto1.valor_pesos = 50000
        gasto2 = Gasto(date(2025, 6, 1), 70000, TipoGasto.ALIMENTACION, MetodoPago.TARJETA)
        gasto2.valor_pesos = 70000
        gasto3 = Gasto(date(2025, 6, 2), 30000, TipoGasto.TRANSPORTE, MetodoPago.EFECTIVO)
        gasto3.valor_pesos = 30000

        viaje.agregar_gasto(gasto1)
        viaje.agregar_gasto(gasto2)
        viaje.agregar_gasto(gasto3)

        resumen = viaje.total_por_tipo()
        self.assertEqual(resumen[TipoGasto.ALIMENTACION]["EFECTIVO"], 50000)
        self.assertEqual(resumen[TipoGasto.ALIMENTACION]["TARJETA"], 70000)
        self.assertEqual(resumen[TipoGasto.ALIMENTACION]["TOTAL"], 120000)
        self.assertEqual(resumen[TipoGasto.TRANSPORTE]["EFECTIVO"], 30000)
        self.assertEqual(resumen[TipoGasto.TRANSPORTE]["TOTAL"], 30000)

    def test_presupuesto_actual_vs_real_sin_gastos(self):
        """Verifica que si no hay gastos registrados, se devuelve todo el presupuesto esperado como diferencia"""
        viaje = Viaje(
            tipo_viaje=TipoViaje.NACIONAL,
            fecha_inicio=date(2025, 6, 1),
            fecha_fin=date(2025, 6, 5),
            presupuesto_diario=50000
        )

        # No se agregan gastos
        diferencia = viaje.presupuesto_actual_vs_real(date(2025, 6, 3))

        self.assertEqual(diferencia, 150000)  # 3 días * 50000

    def test_total_por_tipo_sin_gastos(self):
        """Verifica que se retorne un diccionario vacío si no hay gastos"""
        viaje = Viaje(
            tipo_viaje=TipoViaje.NACIONAL,
            fecha_inicio=date(2025, 6, 1),
            fecha_fin=date(2025, 6, 5),
            presupuesto_diario=60000
        )

        resumen = viaje.total_por_tipo()
        self.assertEqual(resumen, {})


if __name__ == '__main__':
    unittest.main()