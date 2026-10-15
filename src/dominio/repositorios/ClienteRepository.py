from abc import ABC, abstractmethod
from typing import Optional

from ..entidades.Cliente import Cliente

class ClienteRepository(ABC):

    @abstractmethod
    def obtenerPorID(self, clienteID: str) -> Optional[Cliente]:
        pass

    @abstractmethod
    def clienteEsRecurrente(self, clienteID: str) -> bool:
        pass