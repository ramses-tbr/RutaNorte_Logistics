"""Escenarios de CU-02, CU-03 y CU-04, más la Query de estado.

Ejecutar desde la raíz del repositorio:  PYTHONPATH=src python -m unittest discover -s tests -v
"""
import unittest

from aplicacion.cancelar_orden_o_devolver import CancelarOrdenODevolverHandler
from aplicacion.consultar_estado_de_orden import ConsultarEstadoDeOrden, ConsultarEstadoDeOrdenHandler
from aplicacion.orden_de_servicio_service import AppSer_OrdenDeServicio
from dominio.cotizacion import Cotizacion
from dominio.errores import (
    AutorizacionDeOperacionesRequerida, EvidenciaIncompleta, NoEncontrado, OperadorNoDisponible,
    TransicionDeFaseInvalida, CotizacionNoConfirmadaOVencida,
)
from dominio.operador import Operador
from dominio.servicios_dominio import DisponibilidadOperador, DobleVerificacion, Penalizacion
from dominio.unidad import Unidad
from dominio.valores import Evidencia, Fase, TipoEvidencia
from infraestructura.almacen_en_memoria import AlmacenEnMemoria
from infraestructura.eventos_y_lectura_en_memoria import (
    ModeloDeLecturaDeEstadoEnMemoria, ProyectorDeEstadoDeOrden, PublicadorEnMemoria,
)
from infraestructura.unit_of_work_en_memoria import UnitOfWorkEnMemoria

FOTO = Evidencia(TipoEvidencia.FOTO, "foto.jpg")
FIRMA = Evidencia(TipoEvidencia.FIRMA, "firma.png")
ID_OFICIAL = Evidencia(TipoEvidencia.IDENTIFICACION, "ine.png")


class BaseDePruebas(unittest.TestCase):
    def setUp(self):
        self.almacen = AlmacenEnMemoria()
        self.almacen.cotizaciones["COT-1"] = Cotizacion("COT-1", confirmada=True)
        self.almacen.cotizaciones["COT-VIP"] = Cotizacion("COT-VIP", confirmada=True, es_alto_valor=True)
        self.almacen.cotizaciones["COT-SIN-ACEPTAR"] = Cotizacion("COT-SIN-ACEPTAR")
        for i in (1, 2, 3):
            self.almacen.unidades[f"U-{i}"] = Unidad(f"U-{i}")
        self.almacen.operadores["OP-1"] = Operador("OP-1")

        uow = UnitOfWorkEnMemoria(self.almacen)
        self.publicador = PublicadorEnMemoria()
        self.vista = ModeloDeLecturaDeEstadoEnMemoria()
        self.publicador.suscribir(ProyectorDeEstadoDeOrden(self.vista))
        handler = CancelarOrdenODevolverHandler(uow, Penalizacion(), self.publicador)
        self.servicio = AppSer_OrdenDeServicio(
            uow, DisponibilidadOperador(), DobleVerificacion(), handler, self.publicador)
        self.consulta = ConsultarEstadoDeOrdenHandler(self.vista)

    def generar(self, cotizacion="COT-1", unidad="U-1"):
        return self.servicio.generar_orden_y_asignar_unidad(
            cotizacion, unidad, "OP-1", "MTY-SLP", "08:00", "Operaciones")

    def orden(self, folio):
        return self.almacen.ordenes[folio]


class TestCU02GenerarOrdenYAsignarUnidad(BaseDePruebas):
    def test_flujo_normal(self):
        folio = self.generar()
        self.assertEqual(self.orden(folio).fase, Fase.UNIDAD_ASIGNADA)
        self.assertFalse(self.almacen.unidades["U-1"].disponible)
        self.assertEqual(len(self.publicador.publicados), 1)
        estado = self.consulta.manejar(ConsultarEstadoDeOrden(folio))
        self.assertEqual(estado.fase_actual, Fase.UNIDAD_ASIGNADA.value)
        self.assertEqual(estado.responsable_del_cambio, "Operaciones")

    def test_operador_con_orden_en_transito_hace_rollback(self):
        folio = self.generar()
        self.orden(folio).fase = Fase.EN_TRANSITO
        with self.assertRaises(OperadorNoDisponible):
            self.generar(unidad="U-2")
        self.assertEqual(len(self.almacen.ordenes), 1)           # no se creó otra orden
        self.assertTrue(self.almacen.unidades["U-2"].disponible)  # nada quedó asignado

    def test_operador_con_servicio_futuro_si_puede_tomar_otra_orden(self):
        self.generar()  # la primera queda 'Unidad asignada' (futura), no en tránsito
        self.generar(unidad="U-2")
        self.assertEqual(len(self.almacen.ordenes), 2)

    def test_cotizacion_sin_aceptar_se_rechaza(self):
        with self.assertRaises(CotizacionNoConfirmadaOVencida):
            self.generar(cotizacion="COT-SIN-ACEPTAR")
        self.assertEqual(self.almacen.ordenes, {})
        self.assertEqual(self.publicador.publicados, [])


class TestCU03RegistrarEntrega(BaseDePruebas):
    def llegada(self, cotizacion):
        folio = self.generar(cotizacion=cotizacion)
        self.orden(folio).fase = Fase.LLEGADA_A_DESTINO
        return folio

    def test_carga_normal_con_foto_y_firma(self):
        folio = self.llegada("COT-1")
        self.servicio.registrar_entrega(folio, [FOTO, FIRMA], "Operador")
        self.assertEqual(self.orden(folio).fase, Fase.ENTREGADO)

    def test_alto_valor_sin_identificacion_hace_rollback(self):
        folio = self.llegada("COT-VIP")
        with self.assertRaises(EvidenciaIncompleta):
            self.servicio.registrar_entrega(folio, [FOTO, FIRMA], "Operador")
        self.assertEqual(self.orden(folio).fase, Fase.LLEGADA_A_DESTINO)
        self.assertEqual(self.orden(folio).evidencias, [])

    def test_alto_valor_con_identificacion(self):
        folio = self.llegada("COT-VIP")
        self.servicio.registrar_entrega(folio, [FOTO, FIRMA, ID_OFICIAL], "Operador")
        self.assertEqual(self.orden(folio).fase, Fase.ENTREGADO)


class TestCU04CancelarOrdenODevolver(BaseDePruebas):
    def test_cancelacion_con_unidad_asignada_requiere_autorizacion(self):
        folio = self.generar()
        with self.assertRaises(AutorizacionDeOperacionesRequerida):
            self.servicio.cancelar_o_devolver(folio, "Cliente cambió de planes", "Cliente")
        self.assertEqual(self.orden(folio).fase, Fase.UNIDAD_ASIGNADA)  # nada cambió

    def test_cancelacion_autorizada_con_unidad_asignada_aplica_penalizacion(self):
        folio = self.generar()
        dto = self.servicio.cancelar_o_devolver(
            folio, "Cliente cambió de planes", "Operaciones", autorizado_por_operaciones=True)
        self.assertEqual(dto.fase_resultante, Fase.CANCELADA.value)
        self.assertTrue(dto.penalizacion_aplicada)
        self.assertFalse(dto.cargo_de_regreso)

    def test_cancelacion_sin_unidad_asignada_es_sin_costo(self):
        folio = self.generar()
        self.orden(folio).fase = Fase.CONFIRMADO  # aún sin unidad asignada
        dto = self.servicio.cancelar_o_devolver(folio, "Ya no lo necesito", "Cliente")
        self.assertEqual(dto.fase_resultante, Fase.CANCELADA.value)
        self.assertFalse(dto.penalizacion_aplicada)

    def test_orden_en_ruta_genera_devolucion_con_cargo(self):
        folio = self.generar()
        self.orden(folio).fase = Fase.EN_TRANSITO
        dto = self.servicio.cancelar_o_devolver(folio, "Cliente cancela en ruta", "Cliente")
        self.assertEqual(dto.fase_resultante, Fase.EN_DEVOLUCION.value)
        self.assertTrue(dto.cargo_de_regreso)
        self.assertEqual(len(self.orden(folio).ordenes_de_devolucion), 1)

    def test_orden_entregada_no_se_cancela_y_no_cambia(self):
        folio = self.generar()
        self.orden(folio).fase = Fase.ENTREGADO
        publicados = len(self.publicador.publicados)
        with self.assertRaises(TransicionDeFaseInvalida):
            self.servicio.cancelar_o_devolver(folio, "Tarde", "Cliente")
        self.assertEqual(self.orden(folio).fase, Fase.ENTREGADO)
        self.assertEqual(len(self.publicador.publicados), publicados)


class TestQueryEstado(BaseDePruebas):
    def test_folio_inexistente(self):
        with self.assertRaises(NoEncontrado):
            self.consulta.manejar(ConsultarEstadoDeOrden("OS-NO-EXISTE"))


if __name__ == "__main__":
    unittest.main()
