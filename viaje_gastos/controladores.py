# Enumeraciones, clases de dominio y controladores del sistema de gestión de viajes

from enum import Enum
from datetime import date
from typing import List, Dict
import requests


# Enumeración para el tipo de viaje
class TipoViaje(Enum):
    NACIONAL = 'NACIONAL'
    INTERNACIONAL = 'INTERNACIONAL'


# Enumeración para el método de pago
class MetodoPago(Enum):
    EFECTIVO = 'EFECTIVO'
    TARJETA = 'TARJETA'


# Enumeración para los distintos tipos de gasto
class TipoGasto(Enum):
    TRANSPORTE = 'TRANSPORTE'
    ALOJAMIENTO = 'ALOJAMIENTO'
    ALIMENTACION = 'ALIMENTACION'
    ENTRETENIMIENTO = 'ENTRETENIMIENTO'
    COMPRAS = 'COMPRAS'


# Clase que representa un gasto individual en el viaje
class Gasto:
    def __init__(self, fecha: date, valor_original: float, tipo: TipoGasto, metodo: MetodoPago):
        self.fecha = fecha  # Fecha en la que se realizó el gasto
        self.valor_original = valor_original  # Valor en la moneda de origen
        self.tipo = tipo  # Categoría del gasto
        self.metodo = metodo  # Forma de pago utilizada
        self.valor_pesos = None  # Valor convertido a pesos colombianos


# Clase que representa un viaje y sus gastos asociados
class Viaje:
    def __init__(self, tipo_viaje: TipoViaje, fecha_inicio: date, fecha_fin: date, presupuesto_diario: float,
                 moneda_destino: str = 'COP'):
        self.tipo_viaje = tipo_viaje  # Nacional o Internacional
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.presupuesto_diario = presupuesto_diario  # Presupuesto asignado por día
        self.moneda_destino = moneda_destino  # Moneda del país de destino
        self.gastos: List[Gasto] = []  # Lista de gastos registrados en el viaje

    def esta_activo(self):
        """
        Verifica si el viaje está activo en la fecha actual.
        """
        hoy = date.today()
        return self.fecha_inicio <= hoy <= self.fecha_fin

    def agregar_gasto(self, gasto: Gasto):
        """
        Agrega un nuevo gasto a la lista del viaje.
        """
        self.gastos.append(gasto)

    def total_por_dia(self) -> Dict[date, Dict[str, float]]:
        """
        Agrupa y resume los gastos por día y por método de pago.
        """
        resumen = {}
        for gasto in self.gastos:
            d = gasto.fecha
            if d not in resumen:
                resumen[d] = {"EFECTIVO": 0, "TARJETA": 0, "TOTAL": 0}
            resumen[d][gasto.metodo.name] += gasto.valor_pesos
            resumen[d]["TOTAL"] += gasto.valor_pesos
        return resumen

    def total_por_tipo(self) -> Dict[TipoGasto, Dict[str, float]]:
        """
        Agrupa y resume los gastos por tipo de gasto y por método de pago.
        """
        resumen = {}
        for gasto in self.gastos:
            t = gasto.tipo
            if t not in resumen:
                resumen[t] = {"EFECTIVO": 0, "TARJETA": 0, "TOTAL": 0}
            resumen[t][gasto.metodo.name] += gasto.valor_pesos
            resumen[t]["TOTAL"] += gasto.valor_pesos
        return resumen

    def presupuesto_actual_vs_real(self, fecha_actual: date) -> float:
        """
        Calcula la diferencia entre el presupuesto esperado y los gastos reales
        hasta una fecha dada.
        """
        if fecha_actual < self.fecha_inicio:
            return 0
        dias = (min(fecha_actual, self.fecha_fin) - self.fecha_inicio).days + 1
        esperado = dias * self.presupuesto_diario
        real = sum([g.valor_pesos for g in self.gastos])
        return real - esperado


# Controlador responsable de la conversión de monedas
class ControladorConversorMoneda:
    def __init__(self):
        self.api_base = "https://api.exchangerate-api.com/v4/latest/"

    def convertir(self, valor: float, moneda_origen: str, moneda_destino: str = "COP") -> float:
        """
        Convierte un valor de una moneda origen a una moneda destino utilizando una API externa.
        """
        if moneda_origen == moneda_destino:
            return valor  # No se requiere conversión si ambas monedas son iguales
        try:
            response = requests.get(f"{self.api_base}{moneda_origen}")
            response.raise_for_status()
            data = response.json()
            tasa = data.get("rates", {}).get(moneda_destino)
            if tasa is None:
                raise ValueError(f"No se encontró tasa para {moneda_destino}")
            return valor * tasa
        except Exception as e:
            print(f"Error en la conversión: {e}")
            return valor  # Retorna el valor original en caso de error


# Controlador principal para gestionar el viaje y sus operaciones
class ControladorViaje:
    def __init__(self):
        self.viaje: Viaje = None  # Referencia al viaje actual
        self.conversor = ControladorConversorMoneda()  # Instancia del conversor

    def iniciar_viaje(self, tipo: TipoViaje, fecha_inicio: date, fecha_fin: date, presupuesto: float,
                      moneda: str = 'COP'):
        """
        Inicializa un nuevo viaje con los parámetros dados.
        """
        self.viaje = Viaje(tipo, fecha_inicio, fecha_fin, presupuesto, moneda)

    def registrar_gasto(self, fecha: date, valor: float, tipo: TipoGasto, metodo: MetodoPago):
        """
        Registra un nuevo gasto en el viaje activo, convirtiendo el valor a pesos si es necesario.
        """
        if not self.viaje or not self.viaje.esta_activo():
            raise Exception("No hay viaje activo o la fecha está fuera del rango")

        gasto = Gasto(fecha, valor, tipo, metodo)
        gasto.valor_pesos = self.conversor.convertir(valor, self.viaje.moneda_destino)
        self.viaje.agregar_gasto(gasto)

    def obtener_reporte_dia(self):
        """
        Obtiene un resumen de gastos agrupados por día.
        """
        return self.viaje.total_por_dia()

    def obtener_reporte_tipo(self):
        """
        Obtiene un resumen de gastos agrupados por tipo.
        """
        return self.viaje.total_por_tipo()

    def presupuesto_diferencia(self, fecha_actual: date):
        """
        Retorna la diferencia negativa entre el presupuesto esperado y los gastos reales.
        (Si el gasto real es mayor, el valor será negativo).
        """
        return self.viaje.presupuesto_actual_vs_real(fecha_actual) * -1