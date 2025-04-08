# freelance_platform/asgi.py
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
# import gigs.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'freelance_platform.settings')

application = ProtocolTypeRouter(
    {
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            gigs.routing.websocket_urlpatterns
        )
    ),
}
)