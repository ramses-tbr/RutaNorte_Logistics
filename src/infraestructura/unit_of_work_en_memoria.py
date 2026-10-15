"""Unit of Work en memoria: toma una copia al entrar y la restaura si hay rollback."""
from __future__ import annotations

from aplicacion.unit_of_work import UnitOfWork
from infraestructura.almacen_en_memoria import AlmacenEnMemoria
from infraestructura.repositorios_en_memoria import (
    CotizacionRepositoryEnMemoria,
    OperadorRepositoryEnMemoria,
    OrdenDeServicioRepositoryEnMemoria,
    UnidadRepositoryEnMemoria,
)


class UnitOfWorkEnMemoria(UnitOfWork):
    def __init__(self, almacen: AlmacenEnMemoria) -> None:
        self._almacen = almacen
        self._copia = None
        self.ordenes = OrdenDeServicioRepositoryEnMemoria(almacen)
        self.unidades = UnidadRepositoryEnMemoria(almacen)
        self.operadores = OperadorRepositoryEnMemoria(almacen)
        self.cotizaciones = CotizacionRepositoryEnMemoria(almacen)

    def __enter__(self) -> "UnitOfWorkEnMemoria":
        self._copia = self._almacen.copiar()
        return self

    def commit(self) -> None:
        self._copia = None  # los cambios ya quedaron aplicados

    def rollback(self) -> None:
        if self._copia is not None:
            self._almacen.restaurar(self._copia)
            self._copia = None
