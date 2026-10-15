"""Versión mínima de CotizacionRepository: solo lo que CU-02 necesita."""
from __future__ import annotations

from abc import ABC, abstractmethod

from dominio.cotizacion import Cotizacion


class CotizacionRepository(ABC):
    @abstractmethod
    def obtener_por_id(self, cotizacion_id: str) -> Cotizacion:
        """Lanza NoEncontrado si no existe."""
