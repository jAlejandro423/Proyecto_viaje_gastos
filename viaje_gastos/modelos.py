# Módulos y Tipado
from enum import Enum
from datetime import date
from typing import List, Dict

# Enumeración para clasificar el tipo de viaje
class TipoViaje(Enum):
    NACIONAL = 'NACIONAL'
    INTERNACIONAL = 'INTERNACIONAL'

# Enumeración para los métodos de pago posibles
class MetodoPago(Enum):
    EFECTIVO = 'EFECTIVO'
    TARJETA = 'TARJETA'

# Enumeración para categorizar los distintos tipos de gasto
class TipoGasto(Enum):
    TRANSPORTE = 'TRANSPORTE'
    ALOJAMIENTO = 'ALOJAMIENTO'
    ALIMENTACION = 'ALIMENTACION'
    ENTRETENIMIENTO = 'ENTRETENIMIENTO'
    COMPRAS = 'COMPRAS'

# Clase que representa un gasto realizado durante un viaje
class Gasto:
    def __init__(self, fecha: date, valor_original: float, tipo: TipoGasto, metodo: MetodoPago):
        self.fecha = fecha  # Fecha del gasto
        self.valor_original = valor_original  # Monto original en la moneda de origen
        self.tipo = tipo  # Tipo de gasto (ej: alimentación)
        self.metodo = metodo  # Método de pago utilizado
        self.valor_pesos = None  # Valor convertido a pesos (COP), se asigna después

# Clase que representa un viaje con su presupuesto y gastos
class Viaje:
    def __init__(
        self,
        tipo_viaje: TipoViaje,
        fecha_inicio: date,
        fecha_fin: date,
        presupuesto_diario: float,
        moneda_destino: str = 'COP'
    ):
        self.tipo_viaje = tipo_viaje  # Nacional o Internacional
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.presupuesto_diario = presupuesto_diario  # Monto disponible por día
        self.moneda_destino = moneda_destino  # Moneda usada durante el viaje
        self.gastos: List[Gasto] = []  # Lista de objetos Gasto

    def esta_activo(self) -> bool:
        """
        Verifica si el viaje está en curso según la fecha actual.
        """
        hoy = date.today()
        return self.fecha_inicio <= hoy <= self.fecha_fin

    def agregar_gasto(self, gasto: Gasto):
        """
        Añade un nuevo gasto a la lista de gastos del viaje.
        """
        self.gastos.append(gasto)

    def total_por_dia(self) -> Dict[date, Dict[str, float]]:
        """
        Calcula el total de gastos por día, discriminando por método de pago.
        """
        resumen = {}
        for gasto in self.gastos:
            d = gasto.fecha
            if d not in resumen:
                resumen[d] = {"EFECTIVO": 0.0, "TARJETA": 0.0, "TOTAL": 0.0}
            resumen[d][gasto.metodo.name] += gasto.valor_pesos
            resumen[d]["TOTAL"] += gasto.valor_pesos
        return resumen

    def total_por_tipo(self) -> Dict[TipoGasto, Dict[str, float]]:
        """
        Calcula el total de gastos por tipo (alimentación, transporte, etc.), discriminando por método de pago.
        """
        resumen = {}
        for gasto in self.gastos:
            t = gasto.tipo
            if t not in resumen:
                resumen[t] = {"EFECTIVO": 0.0, "TARJETA": 0.0, "TOTAL": 0.0}
            resumen[t][gasto.metodo.name] += gasto.valor_pesos
            resumen[t]["TOTAL"] += gasto.valor_pesos
        return resumen

    def presupuesto_actual_vs_real(self, fecha_actual: date) -> float:
        """
        Compara el presupuesto esperado con el gasto real acumulado hasta una fecha dada.
        Devuelve el saldo restante (positivo si se ha gastado menos de lo presupuestado).
        """
        if fecha_actual < self.fecha_inicio:
            return 0  # No se ha iniciado el viaje

        # Número de días entre el inicio y la fecha actual (o final del viaje)
        dias = (min(fecha_actual, self.fecha_fin) - self.fecha_inicio).days + 1
        esperado = dias * self.presupuesto_diario

        # Suma de los gastos realizados hasta la fecha actual (inclusive)
        real = sum([
            g.valor_pesos for g in self.gastos
            if self.fecha_inicio <= g.fecha <= min(fecha_actual, self.fecha_fin)
        ])

        return esperado - real  # Positivo si hay ahorro, negativo si hay sobrepaso