"""Implementaciones en memoria de los Repositories."""
from __future__ import annotations

from dominio.cotizacion import Cotizacion
from dominio.errores import NoEncontrado
from dominio.operador import Operador
from dominio.orden_de_servicio import OrdenDeServicio
from dominio.repositorio_cotizacion import CotizacionRepository
from dominio.repositorios import OperadorRepository, OrdenDeServicioRepository, UnidadRepository
from dominio.unidad import Unidad
from dominio.valores import Fase
from infraestructura.almacen_en_memoria import AlmacenEnMemoria


def _buscar(diccionario: dict, clave: str, descripcion: str):
    try:
        return diccionario[clave]
    except KeyError:
        raise NoEncontrado(f"{descripcion} {clave} no existe") from None


class OrdenDeServicioRepositoryEnMemoria(OrdenDeServicioRepository):
    def __init__(self, almacen: AlmacenEnMemoria) -> None:
        self._a = almacen

    def guardar(self, orden: OrdenDeServicio) -> None:
        self._a.ordenes[orden.folio] = orden

    def obtener_por_folio(self, folio: str) -> OrdenDeServicio:
        return _buscar(self._a.ordenes, folio, "La orden de servicio")

    def obtener_en_transito_del_operador(self, operador_id: str) -> list[OrdenDeServicio]:
        return [o for o in self._a.ordenes.values()
                if o.operador_id == operador_id and o.fase == Fase.EN_TRANSITO]


class UnidadRepositoryEnMemoria(UnidadRepository):
    def __init__(self, almacen: AlmacenEnMemoria) -> None:
        self._a = almacen

    def obtener_por_id(self, unidad_id: str) -> Unidad:
        return _buscar(self._a.unidades, unidad_id, "La unidad")

    def obtener_disponibles(self) -> list[Unidad]:
        return [u for u in self._a.unidades.values() if u.disponible]

    def guardar(self, unidad: Unidad) -> None:
        self._a.unidades[unidad.id] = unidad


class OperadorRepositoryEnMemoria(OperadorRepository):
    def __init__(self, almacen: AlmacenEnMemoria) -> None:
        self._a = almacen

    def obtener_por_id(self, operador_id: str) -> Operador:
        return _buscar(self._a.operadores, operador_id, "El operador")

    def obtener_disponibles(self) -> list[Operador]:
        return [o for o in self._a.operadores.values() if o.disponible]

    def guardar(self, operador: Operador) -> None:
        self._a.operadores[operador.id] = operador


class CotizacionRepositoryEnMemoria(CotizacionRepository):  # versión mínima
    def __init__(self, almacen: AlmacenEnMemoria) -> None:
        self._a = almacen

    def obtener_por_id(self, cotizacion_id: str) -> Cotizacion:
        return _buscar(self._a.cotizaciones, cotizacion_id, "La cotización")
