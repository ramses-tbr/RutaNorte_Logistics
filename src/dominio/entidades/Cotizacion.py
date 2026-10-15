from dataclasses import dataclass
from datetime import date
from enum import Enum

class EstadoDeCotizacion(str, Enum):
    cot = "Cotizada"
    con = "Confirmada"

@dataclass
class Cotizacion:
    folio: str
    clienteID: str
    fechaEmision: date
    estado: EstadoDeCotizacion = EstadoDeCotizacion.cot
    VIGENCIA_DIAS = 5

    def esVigente(self):
        dias = (date.today() - self.fechaEmision).days
        return dias <= self.VIGENCIA_DIAS

    def diasRestantesVigencia(self):
        dias = (date.today() - self.fechaEmision).days
        return max(self.VIGENCIA_DIAS - dias, 0)

    def ConfirmarEstado(self):
        if not self.esVigente():
            raise ValueError(f"La cotización {self.folio} ya no esta vigente")
        self.estado = EstadoDeCotizacion.con
