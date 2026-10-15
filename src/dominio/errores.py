"""Errores del dominio, explicables en términos del negocio."""


class ErrorDeDominio(Exception):
    """Base de todos los errores de negocio."""


class NoEncontrado(ErrorDeDominio):
    """El folio o identificador buscado no existe (BPMN: 'Orden no encontrada')."""


class CotizacionNoConfirmadaOVencida(ErrorDeDominio):
    """No se puede generar la orden: la cotización no fue aceptada o ya venció."""


class OperadorNoDisponible(ErrorDeDominio):
    """El operador no está disponible o ya tiene una orden en tránsito."""


class UnidadNoDisponible(ErrorDeDominio):
    """La unidad no está disponible para asignarse."""


class TransicionDeFaseInvalida(ErrorDeDominio):
    """La orden no puede pasar a esa fase desde su fase actual."""


class EvidenciaIncompleta(ErrorDeDominio):
    """Falta evidencia obligatoria para registrar la entrega."""


class AutorizacionDeOperacionesRequerida(ErrorDeDominio):
    """Con unidad asignada, cancelar requiere la autorización de Operaciones (US-008)."""
