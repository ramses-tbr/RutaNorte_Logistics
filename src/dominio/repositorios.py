"""Interfaces de Repository de Orden de Servicio, Unidad y Operador.

Hablan en términos del dominio y solo recuperan o guardan. Ninguna contiene SQL ni
reglas de negocio. Las implementaciones viven en infraestructura.
Equivalencia con el informe: guardar = guardar, obtener_por_folio = obtenerPorFolio, etc.
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from dominio.operador import Operador
from dominio.orden_de_servicio import OrdenDeServicio
from dominio.unidad import Unidad


class OrdenDeServicioRepository(ABC):
    @abstractmethod
    def guardar(self, orden: OrdenDeServicio) -> None:
        """Guarda el Aggregate completo (orden, cambios, devolución y evidencias)."""

    @abstractmethod
    def obtener_por_folio(self, folio: str) -> OrdenDeServicio:
        """Lanza NoEncontrado si el folio no existe."""

    @abstractmethod
    def obtener_en_transito_del_operador(self, operador_id: str) -> list[OrdenDeServicio]:
        """Devuelve los datos; la regla de disponibilidad la decide el dominio."""


class UnidadRepository(ABC):
    @abstractmethod
    def obtener_por_id(self, unidad_id: str) -> Unidad: ...

    @abstractmethod
    def obtener_disponibles(self) -> list[Unidad]: ...

    @abstractmethod
    def guardar(self, unidad: Unidad) -> None: ...


class OperadorRepository(ABC):
    @abstractmethod
    def obtener_por_id(self, operador_id: str) -> Operador: ...

    @abstractmethod
    def obtener_disponibles(self) -> list[Operador]: ...

    @abstractmethod
    def guardar(self, operador: Operador) -> None: ...
