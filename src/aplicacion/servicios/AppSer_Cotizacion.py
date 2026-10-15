from ..comandos.ConfirmarCotizacionCommand import ConfirmarCotizacion
from ..queries.ConsultarCotizacionQuery import ConsultarCotizacion
from ..dtos.cotizacionDTO import CotizacionDTO, CotizacionVistaDTO
from ...dominio.repositorios.CotizacionRepository import CotizacionRepository


class CotizacionService:
    def __init__(self, cotizacionRepository: CotizacionRepository):
        self._cotizacionRepository = cotizacionRepository

    # Command
    def confirmarCotizacion(self, command: ConfirmarCotizacion) -> CotizacionDTO:
        cotizacion = self._cotizacionRepository.obtenerPorFolio(command.cotizacionID)
        if cotizacion is None:
            raise ValueError(f"No existe una cotizacion con folio {command.cotizacionID}")

        cotizacion.ConfirmarEstado()
        self._cotizacionRepository.guardar(cotizacion)

        return CotizacionDTO(folio=cotizacion.folio, estado=cotizacion.estado.value)

    # Query
    def consultarCotizacion(self, query: ConsultarCotizacion) -> CotizacionVistaDTO:
        cotizacion = self._cotizacionRepository.obtenerPorFolio(query.folio)
        if cotizacion is None:
            raise ValueError(f"No existe una cotizacion con folio {query.folio}")

        return CotizacionVistaDTO(
            folio=cotizacion.folio,
            estado=cotizacion.estado.value,
            diasRestantesVigencia=cotizacion.diasRestantesVigencia(),
        )