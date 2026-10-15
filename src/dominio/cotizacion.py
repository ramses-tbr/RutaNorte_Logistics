"""Versión mínima de Cotización: solo lo que CU-02 necesita consultar."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Cotizacion:
    id: str
    confirmada: bool = False
    vigente: bool = True
    es_alto_valor: bool = False

    def esta_confirmada_y_vigente(self) -> bool:
        # La vigencia (5 días hábiles) es regla de la entidad, no del repositorio.
        return self.confirmada and self.vigente
