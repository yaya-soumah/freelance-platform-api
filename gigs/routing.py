from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/gig/(?P<gig_id>\d+)/$', consumers.BidConsumer.as_asgi()),
]