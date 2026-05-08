"""
FACTORY METHOD PATTERN
Crea diferentes tipos de servicios sin especificar sus clases exactas
"""


class Service:
    """Clase base para servicios"""
    def __init__(self, name, base_price, description):
        self.name = name
        self.base_price = base_price
        self.description = description
        self.extras = []

    def get_price(self):
        total = self.base_price
        for extra in self.extras:
            total += extra.get_extra_price()
        return total

    def get_details(self):
        return {
            "type": self.name,
            "base_price": self.base_price,
            "description": self.description,
            "extras": [e.get_name() for e in self.extras],
            "total_price": self.get_price(),
        }


class BasicService(Service):
    """Servicio Básico - Lavado simple"""
    def __init__(self):
        super().__init__(
            name="BASIC",
            base_price=45000,
            description="Lavado con agua y jabón"
        )


class FullService(Service):
    """Servicio Full - Lavado completo"""
    def __init__(self):
        super().__init__(
            name="FULL",
            base_price=75000,
            description="Lavado + Secado + Limpieza interior"
        )


class PremiumService(Service):
    """Servicio Premium - Profesional"""
    def __init__(self):
        super().__init__(
            name="PREMIUM",
            base_price=120000,
            description="Lavado profesional completo"
        )


class ExpressService(Service):
    """Servicio Express - Rápido"""
    def __init__(self):
        super().__init__(
            name="EXPRESS",
            base_price=35000,
            description="Lavado rápido (20 min)"
        )


class ServiceFactory:
    """Factory Method - Crea servicios según tipo"""

    @staticmethod
    def create_service(service_type):
        service_type = service_type.lower()
        services = {
            "basic": BasicService,
            "full": FullService,
            "premium": PremiumService,
            "express": ExpressService,
        }
        if service_type not in services:
            raise ValueError(f"Tipo de servicio no válido: {service_type}")
        return services[service_type]()
