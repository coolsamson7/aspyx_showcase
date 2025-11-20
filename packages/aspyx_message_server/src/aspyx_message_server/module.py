from aspyx.di import module, create
from aspyx_event import EventModule
from aspyx_service import SessionManager, ServiceManager, ComponentRegistry, FastAPIServer
from aspyx_service.service import LocalComponentRegistry
from dotenv import load_dotenv
from fastapi import FastAPI


@module(imports=[EventModule])
class PushInterfaceModule:
    # properties

    app: FastAPI

    def __init__(self):
        load_dotenv(override=True)

    @create()
    def create_server(self, service_manager: ServiceManager, component_registry: ComponentRegistry) -> FastAPIServer:
        return FastAPIServer(self.app, service_manager, component_registry)

    @create()
    def create_session_storage(self) -> SessionManager.Storage:
        return SessionManager.InMemoryStorage(max_size=1000, ttl=3600)

    @create()
    def create_registry(self) -> ComponentRegistry:
        return LocalComponentRegistry()
        #return ConsulComponentRegistry(port=int(os.getenv("FAST_API_PORT", "8000")),
        #                               consul=Consul(host="localhost", port=8500))

