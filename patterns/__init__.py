"""
WASHOPS - Patrones de Diseño
Factory Method | Decorator | State Pattern
"""

from .factory import (
    Service,
    BasicService,
    FullService,
    PremiumService,
    ExpressService,
    ServiceFactory,
)

from .decorator import (
    ServiceExtra,
    WaxingExtra,
    VacuumExtra,
    TirePolishExtra,
)

from .state import (
    ServiceState,
    PendingState,
    InProgressState,
    CompletedState,
    CancelledState,
    ServiceWithState,
)

__all__ = [
    # Factory
    "Service",
    "BasicService",
    "FullService",
    "PremiumService",
    "ExpressService",
    "ServiceFactory",
    # Decorator
    "ServiceExtra",
    "WaxingExtra",
    "VacuumExtra",
    "TirePolishExtra",
    # State
    "ServiceState",
    "PendingState",
    "InProgressState",
    "CompletedState",
    "CancelledState",
    "ServiceWithState",
]
