"""Versión mínima de la entidad Unidad; puede sustituirse por la del dominio completo."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Unidad:
    id: str
    disponible: bool = True

    def marcar_asignada(self) -> None:
        # Supuesto: la U2 no define el criterio de 'unidad disponible'; pendiente de validar.
        self.disponible = False
