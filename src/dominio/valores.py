"""Fases y Value Objects de la Orden de Servicio.

Versión mínima: se puede completar o reemplazar con el dominio completo del equipo.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Fase(str, Enum):
    # Las 8 fases del BRD, más los estados finales de cancelación y devolución.
    CONFIRMADO = "Confirmado"
    UNIDAD_ASIGNADA = "Unidad asignada"
    RECOLECTADO = "Recolectado"
    EN_TRANSITO = "En tránsito"
    LLEGADA_A_DESTINO = "Llegada a destino"
    ENTREGADO = "Entregado"
    CANCELADA = "Cancelada"
    EN_DEVOLUCION = "En devolución"


class TipoEvidencia(str, Enum):
    FOTO = "Foto de la mercancía"
    FIRMA = "Firma del receptor"
    IDENTIFICACION = "Identificación oficial"


@dataclass(frozen=True)
class Evidencia:
    """Value Object: se define por sus valores, no tiene identidad propia."""

    tipo: TipoEvidencia
    referencia: str
