"""Puerto del lado de lectura (CQRS): la Query NO lee del repositorio de escritura."""
from __future__ import annotations

from abc import ABC, abstractmethod

from aplicacion.dtos import EstadoDeOrdenVistaDTO


class ModeloDeLecturaDeEstado(ABC):
    @abstractmethod
    def obtener_estado(self, folio: str) -> EstadoDeOrdenVistaDTO:
        """Lanza NoEncontrado si el folio no existe."""
