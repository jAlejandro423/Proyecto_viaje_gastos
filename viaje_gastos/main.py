from datetime import date
from viaje_gastos.controladores import ControladorViaje
from viaje_gastos.modelos import TipoViaje, TipoGasto, MetodoPago

ctrl = ControladorViaje()
ctrl.iniciar_viaje(TipoViaje.INTERNACIONAL, date(2025, 6, 1), date(2025, 6, 5), 200000, "USD")

ctrl.registrar_gasto(date(2025, 6, 1), 20, TipoGasto.ALIMENTACION, MetodoPago.TARJETA)
ctrl.registrar_gasto(date(2025, 6, 1), 10, TipoGasto.TRANSPORTE, MetodoPago.EFECTIVO)
ctrl.registrar_gasto(date(2025, 6, 2), 15, TipoGasto.ENTRETENIMIENTO, MetodoPago.TARJETA)


print("\nReporte por Día:")
for dia, valores in ctrl.obtener_reporte_dia().items():
    print(f"{dia}: {valores}")

print("\nReporte por Tipo:")
for tipo, valores in ctrl.obtener_reporte_tipo().items():
    print(f"{tipo.name}: {valores}")

fecha_actual = date(2025, 6, 2)
print("\nDiferencia con presupuesto:")
print(round(ctrl.presupuesto_diferencia(fecha_actual)))
