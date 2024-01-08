import json
import asyncio
from urllib.parse import parse_qs
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.consumer import AsyncConsumer
from btporders.models import MasterData, CacheData
from channels.db import database_sync_to_async
from .serializers import CacheDataSerializer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils import timezone

class DatabaseUpdater:
    @database_sync_to_async
    def update_database(self, data):
        print("recived:", data)
        # print(data['data']['orderstatus'])
        if data['condition'] == 'IF':
            try:
                CacheData.objects.filter(orderid=data['data']['orderid']).update(ord_ack_agv=data['data']['ord_ack_agv'])
                print('cache Updated')
            except Exception as Er:
                print('IF Error ====> ', Er)
        if data['condition'] == 'ELIF':
            try:
                current_date = timezone.now().date()
                CacheData.objects.filter(orderid=data['data']['orderid']).update(
                                                                        orderstatus     =data['data']['orderstatus'],
                                                                        srcrackid       =data['data']['srcrackid'],
                                                                        destrackid      =data['data']['destrackid'],
                                                                        binid_status    =data['data']['binid_status'],
                                                                        bintransfer     =data['data']['bintransfer'],
                                                                        recived_status  =data['data']['recived_status'],
                                                                        agvstatus       =data['data']['agvstatus'],
                                                                        agverror        =data['data']['agverror']
                                                                        )
                MasterData.objects.filter(orderid=data['data']['orderid']).update(
                                                                        orderstatus     =data['data']['orderstatus'],
                                                                        srcrackid       =data['data']['srcrackid'],
                                                                        destrackid      =data['data']['destrackid'],
                                                                        binid_status    =data['data']['binid_status'],
                                                                        bintransfer     =data['data']['bintransfer']
                                                                        )
                Totaldata = MasterData.objects.filter(date=current_date)
                completed = MasterData.objects.filter(date=current_date, orderstatus=2)
                InvalidData = MasterData.objects.filter(date=current_date, orderstatus=1)
                overview = {"total": Totaldata.count(), "invalid": InvalidData.count(), "completed": completed.count()}
                print('Order ID ----> ',data['data']['orderid'])
                updatedData = CacheData.objects.get(orderid=data['data']['orderid'])
                ins = (CacheDataSerializer(updatedData)).data
                realtimeData = {
                    "Overview" : overview,
                    "status": ins
                }
                print('saved')
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    "currentorder_broadcast",
                    {
                        'type': 'send_currentData',
                        'message': realtimeData
                    })
            except Exception as Err:
                print('Err ---->', Err)
                # pass

        if data['condition'] == 'ELSE':
            print(data['data'])
            # pass
            

class CurrentOrder(AsyncWebsocketConsumer):
        
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'currentorder_%s' % self.room_name
        # print(self.room_group_name)
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
    
    async def disconnect(self, close_code):
        await self.close()
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        print('WebSocket Disconnected')

    async def receive(self, text_data=None, bytes_data=None):
        print(f'WebSocket Data Received : {text_data}')

    async def send_currentData(self, event):
        # print("Sent Data", event)
        currentData = event.get('message', {})
        await self.send(text_data=json.dumps(currentData))


class PlcDataLive(AsyncWebsocketConsumer, DatabaseUpdater):

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'plcdata_%s' % self.room_name
        # print(self.room_group_name)
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        print('PLC ws connected') 

    async def disconnect(self, close_code):
        # await self.close()
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        print('PLC WebSocket Disconnected') 

    async def receive(self, text_data=None, json_data=None):
        try:
            data = json.loads(text_data)
            await self.update_database(data)
        except json.decoder.JSONDecodeError as e:
            print("JSON Decode Error:", e)