from dataclasses import dataclass

@dataclass(frozen=True)
class CotizacionDTO:
    folio: str
    estado: str

@dataclass(frozen=True)
class CotizacionVistaDTO:
    folio: str
    estado: str
    diasRestantesVigencia: int