"""Publicador de eventos y modelo de lectura (CQRS) en memoria."""
from __future__ import annotations

from typing import Callable

from aplicacion.dtos import EstadoDeOrdenVistaDTO
from aplicacion.modelo_de_lectura import ModeloDeLecturaDeEstado
from aplicacion.publicador import PublicadorDeEventos
from dominio.errores import NoEncontrado
from dominio.eventos import EventoDeDominio


class PublicadorEnMemoria(PublicadorDeEventos):
    def __init__(self) -> None:
        self.publicados: list[EventoDeDominio] = []
        self._suscriptores: list[Callable[[EventoDeDominio], None]] = []

    def suscribir(self, suscriptor: Callable[[EventoDeDominio], None]) -> None:
        self._suscriptores.append(suscriptor)

    def publicar(self, evento: EventoDeDominio) -> None:
        self.publicados.append(evento)
        for suscriptor in self._suscriptores:
            suscriptor(evento)


class ModeloDeLecturaDeEstadoEnMemoria(ModeloDeLecturaDeEstado):
    def __init__(self) -> None:
        self._vistas: dict[str, EstadoDeOrdenVistaDTO] = {}

    def actualizar(self, vista: EstadoDeOrdenVistaDTO) -> None:
        self._vistas[vista.folio] = vista

    def obtener_estado(self, folio: str) -> EstadoDeOrdenVistaDTO:
        try:
            return self._vistas[folio]
        except KeyError:
            raise NoEncontrado(f"La orden de servicio {folio} no existe") from None


class ProyectorDeEstadoDeOrden:
    """Suscriptor que mantiene el modelo de lectura a partir de los Domain Events."""

    def __init__(self, modelo: ModeloDeLecturaDeEstadoEnMemoria) -> None:
        self._modelo = modelo

    def __call__(self, evento: EventoDeDominio) -> None:
        self._modelo.actualizar(EstadoDeOrdenVistaDTO(
            evento.folio, evento.fase, evento.fecha_hora, evento.responsable))
