from dataclasses import dataclass

@dataclass
class Cliente:
    clienteID: str
    nombre: str
    recurrente: bool = False

    def esRecurrente(self):
        return self.recurrente