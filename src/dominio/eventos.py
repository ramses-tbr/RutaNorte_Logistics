"""Domain Events: hechos del negocio que ya ocurrieron (en pasado).

Supuesto: OrdenDeServicioCancelada no está en la lista del mapa de dominio; se propone
agregarla porque CU-04 y CU-05 cancelan órdenes.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class EventoDeDominio:
    folio: str
    fase: str
    fecha_hora: datetime
    responsable: str


@dataclass(frozen=True)
class OrdenDeServicioConfirmada(EventoDeDominio):
    pass


@dataclass(frozen=True)
class MercanciaEntregada(EventoDeDominio):
    pass


@dataclass(frozen=True)
class OrdenDeServicioCancelada(EventoDeDominio):
    pass


@dataclass(frozen=True)
class OrdenDeDevolucionGenerada(EventoDeDominio):
    pass
