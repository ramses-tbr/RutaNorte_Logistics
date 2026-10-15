"""Unit of Work: una transacción por caso de uso.

Inicia al entrar al bloque `with`, se confirma con commit() y ante cualquier error
se hace rollback: no queda ningún cambio parcial.
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from dominio.repositorio_cotizacion import CotizacionRepository
from dominio.repositorios import OperadorRepository, OrdenDeServicioRepository, UnidadRepository


class UnitOfWork(ABC):
    ordenes: OrdenDeServicioRepository
    unidades: UnidadRepository
    operadores: OperadorRepository
    cotizaciones: CotizacionRepository

    def __enter__(self) -> "UnitOfWork":
        return self

    def __exit__(self, tipo, valor, traza) -> bool:
        if tipo is not None:
            self.rollback()
        return False  # el error original se propaga

    @abstractmethod
    def commit(self) -> None: ...

    @abstractmethod
    def rollback(self) -> None: ...
