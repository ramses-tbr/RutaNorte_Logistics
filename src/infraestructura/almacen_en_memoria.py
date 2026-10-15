"""Almacén en memoria que sustituye a la base de datos en las pruebas.

En producción habría implementaciones SQL de las mismas interfaces
(SqlOrdenDeServicioRepository, etc.) sin cambiar el dominio ni la aplicación.
"""
from __future__ import annotations

import copy


class AlmacenEnMemoria:
    def __init__(self) -> None:
        self.ordenes: dict = {}
        self.unidades: dict = {}
        self.operadores: dict = {}
        self.cotizaciones: dict = {}

    def copiar(self) -> tuple:
        return copy.deepcopy((self.ordenes, self.unidades, self.operadores, self.cotizaciones))

    def restaurar(self, copia: tuple) -> None:
        for actual, guardada in zip(
                (self.ordenes, self.unidades, self.operadores, self.cotizaciones), copia):
            actual.clear()
            actual.update(guardada)
