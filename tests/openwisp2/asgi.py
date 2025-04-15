from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

from device_manager.routing import websocket_urlpatterns
from openwisp_controller.routing import get_routes

application = ProtocolTypeRouter(
    {
        'websocket': AllowedHostsOriginValidator(
            AuthMiddlewareStack(URLRouter(get_routes() + websocket_urlpatterns))
        ),
        'http': get_asgi_application(),
    }
)