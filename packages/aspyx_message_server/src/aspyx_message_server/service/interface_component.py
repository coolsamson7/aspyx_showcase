from aspyx_service import component, Component

from .interface_service import InterfaceService

@component(services =[
    InterfaceService,
])
class InterfaceComponent(Component):
    pass