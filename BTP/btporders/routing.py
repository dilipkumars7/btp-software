from django.urls import re_path

from . import websocket

websocket_urlpatterns = [
    re_path(r'ws/currentorder/(?P<room_name>\w+)/$', websocket.CurrentOrder.as_asgi()),
    re_path(r'ws/plcdata/(?P<room_name>\w+)/$', websocket.PlcDataLive.as_asgi())
]
