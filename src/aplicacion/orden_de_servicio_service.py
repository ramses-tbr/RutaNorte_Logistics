"""Application Service de la Orden de Servicio (CU-02, CU-03, CU-04).

Solo COORDINA: obtiene objetos, invoca el dominio, pide la persistencia y devuelve un
resultado. Las reglas viven en el Aggregate y en los Domain Services.
Nombre igual al del informe y de los diagramas: AppSer_OrdenDeServicio.
"""
from __future__ import annotations

from aplicacion.cancelar_orden_o_devolver import (
    CancelarOrdenODevolver,
    CancelarOrdenODevolverHandler,
)
from aplicacion.dtos import CancelacionDevolucionDTO
from aplicacion.publicador import PublicadorDeEventos
from aplicacion.unit_of_work import UnitOfWork
from dominio.errores import CotizacionNoConfirmadaOVencida, UnidadNoDisponible
from dominio.orden_de_servicio import OrdenDeServicio
from dominio.servicios_dominio import DisponibilidadOperador, DobleVerificacion
from dominio.valores import Evidencia


class AppSer_OrdenDeServicio:  # noqa: N801 (se respeta el nombre del informe)
    def __init__(self, uow: UnitOfWork, disponibilidad: DisponibilidadOperador,
                 verificacion: DobleVerificacion,
                 cancelar_handler: CancelarOrdenODevolverHandler,
                 publicador: PublicadorDeEventos) -> None:
        self._uow = uow
        self._disponibilidad = disponibilidad
        self._verificacion = verificacion
        self._cancelar_handler = cancelar_handler
        self._publicador = publicador

    # CU-02 ---------------------------------------------------------------------------
    def generar_orden_y_asignar_unidad(self, cotizacion_id: str, unidad_id: str,
                                       operador_id: str, ruta: str, horario: str,
                                       responsable: str) -> str:
        with self._uow as uow:  # inicio de la transacción
            cotizacion = uow.cotizaciones.obtener_por_id(cotizacion_id)
            if not cotizacion.esta_confirmada_y_vigente():
                raise CotizacionNoConfirmadaOVencida(
                    f"La cotización {cotizacion_id} no fue aceptada o ya venció")
            unidad = uow.unidades.obtener_por_id(unidad_id)
            if not unidad.disponible:
                raise UnidadNoDisponible(f"La unidad {unidad_id} no está disponible")
            operador = uow.operadores.obtener_por_id(operador_id)
            self._disponibilidad.verificar(
                operador, uow.ordenes.obtener_en_transito_del_operador(operador_id))

            orden = OrdenDeServicio.generar_desde(cotizacion, responsable)
            orden.asignar_recursos(unidad.id, operador.id, ruta, horario, responsable)
            unidad.marcar_asignada()

            uow.ordenes.guardar(orden)
            uow.unidades.guardar(unidad)
            uow.commit()
            eventos = orden.extraer_eventos()
            folio = orden.folio
        for evento in eventos:
            self._publicador.publicar(evento)
        return folio

    # CU-03 ---------------------------------------------------------------------------
    def registrar_entrega(self, folio: str, evidencias: list[Evidencia],
                          responsable: str) -> None:
        with self._uow as uow:
            orden = uow.ordenes.obtener_por_folio(folio)
            orden.registrar_entrega(evidencias, self._verificacion, responsable)
            uow.ordenes.guardar(orden)
            uow.commit()
            eventos = orden.extraer_eventos()
        for evento in eventos:
            self._publicador.publicar(evento)

    # CU-04 ---------------------------------------------------------------------------
    def cancelar_o_devolver(self, folio: str, motivo: str, responsable: str,
                            autorizado_por_operaciones: bool = False) -> CancelacionDevolucionDTO:
        return self._cancelar_handler.manejar(
            CancelarOrdenODevolver(folio, motivo, responsable, autorizado_por_operaciones))
