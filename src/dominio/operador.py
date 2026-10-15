"""Versión mínima de la entidad Operador; puede sustituirse por la del dominio completo."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Operador:
    id: str
    disponible: bool = True
