from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator

from openwisp_controller.routing import get_routes
from device_manager.routing import websocket_urlpatterns

application = ProtocolTypeRouter(
    {
        'websocket': AllowedHostsOriginValidator(
            AuthMiddlewareStack(URLRouter(get_routes() + websocket_urlpatterns))
        )
    }
)
