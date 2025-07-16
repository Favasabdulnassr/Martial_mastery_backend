"""
ASGI config for Martial_mastery_backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter,URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from channels.routing import ProtocolTypeRouter,URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from channels.auth import AuthMiddlewareStack
from chat.middleware import TokenAuthMiddleware



os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Martial_mastery_backend.settings')
django_asgi_app = get_asgi_application()

from chat.routing import websocket_urlpatterns as chat_websocket_urlpatternss
from notifications.routing import websocket_urlpatterns as notification_websocket_url_patterns

combined_websocket_urlpatterns = chat_websocket_urlpatternss + notification_websocket_url_patterns
from channels.security.websocket import OriginValidator

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": OriginValidator(
        AuthMiddlewareStack(
            TokenAuthMiddleware(
                URLRouter(combined_websocket_urlpatterns)
            )
        ),
        [
            "http://localhost:3000",
            'http://localhost:5173'
            
        ]
    ),
})





# from django.core.asgi import get_asgi_application

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Martial_mastery_backend.settings')

# application = get_asgi_application()
