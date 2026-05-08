"""
WASHOPS - Sistema de Patrones de Diseño
Demostración de Factory Method, Decorator y State Pattern
"""

from patterns import (
    ServiceFactory,
    Service,
    BasicService,
    FullService,
    PremiumService,
    ExpressService,
    ServiceExtra,
    WaxingExtra,
    VacuumExtra,
    TirePolishExtra,
    ServiceWithState,
)

__version__ = "1.0.0"
__author__ = "Juan Pablo Botero"

__all__ = [
    "ServiceFactory",
    "Service",
    "BasicService",
    "FullService",
    "PremiumService",
    "ExpressService",
    "ServiceExtra",
    "WaxingExtra",
    "VacuumExtra",
    "TirePolishExtra",
    "ServiceWithState",
]
