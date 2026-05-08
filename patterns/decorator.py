"""
DECORATOR PATTERN
Agrega funcionalidades dinámicamente a un servicio sin modificar su clase
"""


class ServiceExtra:
    """Clase base para extras (Decorator)"""
    def __init__(self, name, price):
        self.name = name
        self.price = price

    def get_name(self):
        return self.name

    def get_extra_price(self):
        return self.price


class WaxingExtra(ServiceExtra):
    """Extra: Encerado"""
    def __init__(self):
        super().__init__("Encerado", 15000)


class VacuumExtra(ServiceExtra):
    """Extra: Vacío Interior"""
    def __init__(self):
        super().__init__("Vacío Interior", 12000)


class TirePolishExtra(ServiceExtra):
    """Extra: Pulimiento de Llantas"""
    def __init__(self):
        super().__init__("Pulimiento de Llantas", 10000)
