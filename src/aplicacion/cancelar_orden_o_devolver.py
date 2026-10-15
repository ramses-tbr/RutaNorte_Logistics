"""Command CancelarOrdenODevolver y su Handler (CU-04)."""
from __future__ import annotations

from dataclasses import dataclass

from aplicacion.dtos import CancelacionDevolucionDTO
from aplicacion.publicador import PublicadorDeEventos
from aplicacion.unit_of_work import UnitOfWork
from dominio.servicios_dominio import Penalizacion


@dataclass(frozen=True)
class CancelarOrdenODevolver:
    folio: str
    motivo: str
    responsable: str
    autorizado_por_operaciones: bool = False


class CancelarOrdenODevolverHandler:
    def __init__(self, uow: UnitOfWork, penalizacion: Penalizacion,
                 publicador: PublicadorDeEventos) -> None:
        self._uow = uow
        self._penalizacion = penalizacion
        self._publicador = publicador

    def manejar(self, comando: CancelarOrdenODevolver) -> CancelacionDevolucionDTO:
        with self._uow as uow:  # inicio de la transacción
            orden = uow.ordenes.obtener_por_folio(comando.folio)
            # La regla de penalización por fase vive en el dominio, no aquí.
            resultado = orden.cancelar_o_devolver(
                self._penalizacion, comando.motivo, comando.responsable,
                comando.autorizado_por_operaciones)
            uow.ordenes.guardar(orden)
            uow.commit()
            eventos = orden.extraer_eventos()
            dto = CancelacionDevolucionDTO(
                orden.folio, orden.fase.value,
                resultado.aplica_penalizacion, resultado.cargo_de_regreso)
        for evento in eventos:  # solo tras el commit (aquí se notifica al cliente)
            self._publicador.publicar(evento)
        return dto
