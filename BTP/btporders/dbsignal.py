from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CacheData
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from btporders.serializers import CacheDataSerializer
from btporders.models import MasterData
from django.utils import timezone
from django.db import models
from django.db.backends.signals import connection_created


@receiver(post_save, sender=CacheData)
def Loging(sender, instance, **kwargs):
    if instance.pk:
        inst = (CacheDataSerializer(instance)).data
        SendData(inst)

def SendData(Data):
    current_date = timezone.now().date()
    Totaldata = MasterData.objects.filter(date=current_date)
    completed = MasterData.objects.filter(date=current_date, orderstatus=2)
    InvalidData = MasterData.objects.filter(date=current_date, orderstatus=1)
    overview = {"total": Totaldata.count(), "invalid": InvalidData.count(), "completed": completed.count()}
    realtimeData = {
       "Overview" : overview,
       "status": Data
    }
    # Use Django's transaction.on_commit to perform actions after the transaction is committed
    transaction.on_commit(lambda: broadcast_realtime_data(realtimeData))

def broadcast_realtime_data(realtimeData):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "currentorder_broadcast",
        {
            'type': 'send_currentData',
            'message': realtimeData
        }
    )

# Connect the signal
post_save.connect(Loging, sender=CacheData)
