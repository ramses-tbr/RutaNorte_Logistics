from abc import ABC, abstractmethod
from typing import Optional

from ..entidades.Cotizacion import Cotizacion

class CotizacionRepository(ABC):

    @abstractmethod
    def obtenerPorFolio(self, folio: str) -> Optional[Cotizacion]:
        pass

    @abstractmethod
    def guardar(self, cotizacion: Cotizacion):
        pass