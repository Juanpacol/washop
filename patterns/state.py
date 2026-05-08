"""
STATE PATTERN
Maneja comportamientos diferentes según el estado actual del servicio
"""


class ServiceState:
    """Clase base para estados"""

    def __init__(self, name):
        self.name = name

    def start_service(self):
        raise NotImplementedError

    def complete_service(self):
        raise NotImplementedError

    def cancel_service(self):
        raise NotImplementedError

    def get_state_name(self):
        return self.name


class PendingState(ServiceState):
    """Estado: Pendiente"""
    def __init__(self):
        super().__init__("PENDING")

    def start_service(self):
        return InProgressState()

    def cancel_service(self):
        return CancelledState()


class InProgressState(ServiceState):
    """Estado: En Progreso"""
    def __init__(self):
        super().__init__("IN_PROGRESS")

    def complete_service(self):
        return CompletedState()

    def cancel_service(self):
        return CancelledState()


class CompletedState(ServiceState):
    """Estado: Completado"""
    def __init__(self):
        super().__init__("COMPLETED")


class CancelledState(ServiceState):
    """Estado: Cancelado"""
    def __init__(self):
        super().__init__("CANCELLED")


class ServiceWithState:
    """Servicio que maneja estados (Context del State Pattern)"""

    def __init__(self, service):
        self.service = service
        self.state = PendingState()

    def start(self):
        self.state = self.state.start_service()
        return f"Servicio iniciado. Estado: {self.state.get_state_name()}"

    def complete(self):
        self.state = self.state.complete_service()
        return f"Servicio completado. Estado: {self.state.get_state_name()}"

    def cancel(self):
        self.state = self.state.cancel_service()
        return f"Servicio cancelado. Estado: {self.state.get_state_name()}"

    def get_full_details(self):
        details = self.service.get_details()
        details["state"] = self.state.get_state_name()
        return details
