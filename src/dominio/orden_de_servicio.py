"""Aggregate Orden de Servicio (raíz).

Versión mínima de la capa de dominio (se puede completar o reemplazar). Protege los
invariantes de fase: toda transición inválida se rechaza aquí, no en el servicio.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from dominio.cotizacion import Cotizacion
from dominio.errores import AutorizacionDeOperacionesRequerida, TransicionDeFaseInvalida
from dominio.eventos import (
    EventoDeDominio,
    MercanciaEntregada,
    OrdenDeDevolucionGenerada,
    OrdenDeServicioCancelada,
    OrdenDeServicioConfirmada,
)
from dominio.valores import Evidencia, Fase

if TYPE_CHECKING:
    from dominio.servicios_dominio import DobleVerificacion, Penalizacion, ResultadoDePenalizacion


@dataclass
class OrdenDeDevolucion:
    motivo: str
    cargo_de_regreso: bool


@dataclass
class OrdenDeServicio:
    folio: str
    cotizacion_id: str
    es_alto_valor: bool
    fase: Fase = Fase.CONFIRMADO
    unidad_id: str | None = None
    operador_id: str | None = None
    ruta: str | None = None
    horario: str | None = None
    fecha_hora_ultimo_cambio: datetime = field(default_factory=datetime.now)
    responsable_ultimo_cambio: str = ""
    evidencias: list[Evidencia] = field(default_factory=list)
    ordenes_de_devolucion: list[OrdenDeDevolucion] = field(default_factory=list)
    _eventos: list[EventoDeDominio] = field(default_factory=list, repr=False)

    @classmethod
    def generar_desde(cls, cotizacion: Cotizacion, responsable: str) -> "OrdenDeServicio":
        return cls(
            folio=f"OS-{uuid4().hex[:8].upper()}",
            cotizacion_id=cotizacion.id,
            es_alto_valor=cotizacion.es_alto_valor,
            responsable_ultimo_cambio=responsable,
        )

    # -- comportamiento del Aggregate ------------------------------------------------
    def asignar_recursos(self, unidad_id: str, operador_id: str, ruta: str,
                         horario: str, responsable: str) -> None:
        if self.fase != Fase.CONFIRMADO:
            raise TransicionDeFaseInvalida(
                f"No se puede asignar unidad a una orden en fase '{self.fase.value}'"
            )
        self.unidad_id, self.operador_id = unidad_id, operador_id
        self.ruta, self.horario = ruta, horario
        self._cambiar_fase(Fase.UNIDAD_ASIGNADA, responsable)
        self._eventos.append(self._evento(OrdenDeServicioConfirmada, responsable))

    def registrar_entrega(self, evidencias: list[Evidencia],
                          verificacion: "DobleVerificacion", responsable: str) -> None:
        if self.fase != Fase.LLEGADA_A_DESTINO:
            raise TransicionDeFaseInvalida(
                f"No se puede entregar una orden en fase '{self.fase.value}'"
            )
        verificacion.validar(evidencias, self.es_alto_valor)
        self.evidencias.extend(evidencias)
        self._cambiar_fase(Fase.ENTREGADO, responsable)
        self._eventos.append(self._evento(MercanciaEntregada, responsable))

    def cancelar_o_devolver(self, politica: "Penalizacion", motivo: str, responsable: str,
                            autorizado_por_operaciones: bool = False) -> "ResultadoDePenalizacion":
        resultado = politica.calcular(self.fase)  # rechaza fases no cancelables
        if resultado.requiere_autorizacion and not autorizado_por_operaciones:
            raise AutorizacionDeOperacionesRequerida(
                "Con unidad asignada, la cancelación requiere la autorización de Operaciones")
        if resultado.requiere_devolucion:
            self.ordenes_de_devolucion.append(OrdenDeDevolucion(motivo, resultado.cargo_de_regreso))
            self._cambiar_fase(Fase.EN_DEVOLUCION, responsable)
            self._eventos.append(self._evento(OrdenDeDevolucionGenerada, responsable))
        else:
            self._cambiar_fase(Fase.CANCELADA, responsable)
            self._eventos.append(self._evento(OrdenDeServicioCancelada, responsable))
        return resultado

    def extraer_eventos(self) -> list[EventoDeDominio]:
        eventos, self._eventos = self._eventos, []
        return eventos

    # -- internos --------------------------------------------------------------------
    def _cambiar_fase(self, nueva: Fase, responsable: str) -> None:
        self.fase = nueva
        self.fecha_hora_ultimo_cambio = datetime.now()
        self.responsable_ultimo_cambio = responsable

    def _evento(self, tipo: type[EventoDeDominio], responsable: str) -> EventoDeDominio:
        return tipo(self.folio, self.fase.value, self.fecha_hora_ultimo_cambio, responsable)
