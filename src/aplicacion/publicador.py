"""Puerto para publicar Domain Events. Solo se usa DESPUÉS del commit."""
from __future__ import annotations

from abc import ABC, abstractmethod

from dominio.eventos import EventoDeDominio


class PublicadorDeEventos(ABC):
    @abstractmethod
    def publicar(self, evento: EventoDeDominio) -> None: ...
