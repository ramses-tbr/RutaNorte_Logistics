"""Query ConsultarEstadoDeOrden y su Handler (N-02, US-002)."""
from __future__ import annotations

from dataclasses import dataclass

from aplicacion.dtos import EstadoDeOrdenVistaDTO
from aplicacion.modelo_de_lectura import ModeloDeLecturaDeEstado


@dataclass(frozen=True)
class ConsultarEstadoDeOrden:
    folio: str


class ConsultarEstadoDeOrdenHandler:
    def __init__(self, modelo_de_lectura: ModeloDeLecturaDeEstado) -> None:
        self._modelo = modelo_de_lectura

    def manejar(self, consulta: ConsultarEstadoDeOrden) -> EstadoDeOrdenVistaDTO:
        # No cambia estado ni carga el Aggregate: solo lee el modelo de lectura.
        return self._modelo.obtener_estado(consulta.folio)
