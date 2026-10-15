"""Domain Services de la Orden de Servicio.

Aquí viven las reglas que no pertenecen a una sola entidad. El Application Service
solo los invoca.
"""
from __future__ import annotations

from dataclasses import dataclass

from dominio.errores import EvidenciaIncompleta, OperadorNoDisponible, TransicionDeFaseInvalida
from dominio.operador import Operador
from dominio.valores import Evidencia, Fase, TipoEvidencia


@dataclass(frozen=True)
class ResultadoDePenalizacion:
    aplica_penalizacion: bool
    requiere_devolucion: bool
    cargo_de_regreso: bool
    requiere_autorizacion: bool = False  # US-008: con unidad asignada autoriza Operaciones


class Penalizacion:
    """Calcula qué ocurre al cancelar según la fase (BPMN: Cancelación Anticipada).

    Reglas en una tabla, no en una cadena de if: agregar una variante es agregar una
    entrada (principio Abierto/Cerrado).
    Supuesto: 'Recolectado' ya cuenta como 'en ruta'; pendiente de validar con la entrevista.
    """

    _REGLAS: dict[Fase, ResultadoDePenalizacion] = {
        Fase.CONFIRMADO: ResultadoDePenalizacion(False, False, False),       # sin unidad: sin costo
        Fase.UNIDAD_ASIGNADA: ResultadoDePenalizacion(True, False, False, True),  # con unidad: penaliza y autoriza Operaciones
        Fase.RECOLECTADO: ResultadoDePenalizacion(True, True, True),         # en ruta: devolución
        Fase.EN_TRANSITO: ResultadoDePenalizacion(True, True, True),
        Fase.LLEGADA_A_DESTINO: ResultadoDePenalizacion(True, True, True),
    }

    def calcular(self, fase: Fase) -> ResultadoDePenalizacion:
        try:
            return self._REGLAS[fase]
        except KeyError:
            raise TransicionDeFaseInvalida(
                f"Una orden en fase '{fase.value}' ya no puede cancelarse ni devolverse"
            ) from None


class DobleVerificacion:
    """Evidencia obligatoria en la entrega; las cargas de alto valor exigen además identificación."""

    def validar(self, evidencias: list[Evidencia], es_alto_valor: bool) -> None:
        requeridas = {TipoEvidencia.FOTO, TipoEvidencia.FIRMA}
        if es_alto_valor:
            requeridas.add(TipoEvidencia.IDENTIFICACION)
        presentes = {e.tipo for e in evidencias}
        faltantes = requeridas - presentes
        if faltantes:
            nombres = ", ".join(sorted(t.value for t in faltantes))
            raise EvidenciaIncompleta(f"Falta evidencia obligatoria: {nombres}")


class DisponibilidadOperador:
    """Regla que cruza Operador y Orden: solo puede tener una orden EN TRÁNSITO a la vez.

    Puede tener servicios futuros ya agendados (entrevista), por eso solo se cuentan
    las órdenes en tránsito.
    """

    def verificar(self, operador: Operador, ordenes_en_transito: list) -> None:
        if not operador.disponible:
            raise OperadorNoDisponible(f"El operador {operador.id} no está disponible")
        if ordenes_en_transito:
            raise OperadorNoDisponible(
                f"El operador {operador.id} ya tiene una orden en tránsito"
            )
