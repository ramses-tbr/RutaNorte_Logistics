"""DTOs. El de lectura NO reutiliza el modelo de escritura (CQRS)."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class CancelacionDevolucionDTO:  # resultado del Command
    folio: str
    fase_resultante: str
    penalizacion_aplicada: bool
    cargo_de_regreso: bool


@dataclass(frozen=True)
class EstadoDeOrdenVistaDTO:  # resultado de la Query
    folio: str
    fase_actual: str
    fecha_hora_ultimo_cambio: datetime
    responsable_del_cambio: str
