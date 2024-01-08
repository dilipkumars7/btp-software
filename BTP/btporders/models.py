from django.db import models
# Create your models here.
class MasterData(models.Model):
    id              = models.AutoField(primary_key=True)
    orderid         = models.CharField(max_length=255,default=False,null=True)
    date            = models.DateField()
    binid           = models.CharField(max_length=255,default=False,null=True)
    srcActlocation  = models.CharField(max_length=255,default=False,null=True)
    destActlocation = models.CharField(max_length=255,default=False,null=True)
    srcRCSlocation  = models.IntegerField(default=0, null=True)
    destRCSlocation = models.IntegerField(default=0, null=True)
    orderstatus     = models.IntegerField(default=0,null=True)
    bintransfer     = models.BooleanField(default=False,null=True)
    srcrackid       = models.IntegerField(default=0, null=True)
    destrackid      = models.IntegerField(default=0, null=True)
    binid_status    = models.IntegerField(default=0, null=True)
    ord_ack_agv     = models.IntegerField(default=0, null=True)
    binmapping      = models.BooleanField(default=False,null=True)

class CacheData(models.Model):
    orderid         = models.CharField(max_length=255,default=False,null=True)
    binid           = models.CharField(max_length=255,default=False,null=True)
    srcActlocation  = models.CharField(max_length=255,default=False,null=True)
    destActlocation = models.CharField(max_length=255,default=False,null=True)
    srcRCSlocation  = models.IntegerField(default=0, null=True)
    destRCSlocation = models.IntegerField(default=0, null=True)
    orderstatus     = models.IntegerField(default=0,null=True)
    bintransfer     = models.BooleanField(default=False,null=True)
    srcrackid       = models.IntegerField(default=0, null=True)
    destrackid      = models.IntegerField(default=0, null=True)
    binid_status    = models.IntegerField(default=0, null=True)
    ord_ack_agv     = models.IntegerField(default=0, null=True)
    recived_status  = models.IntegerField(default=1, null=True)
    agvstatus       = models.IntegerField(default=0, null=True)
    agverror        = models.IntegerField(default=0, null=True)
    binmapping      = models.BooleanField(default=False,null=True)
    frontbinpresent = models.BooleanField(default=False,null=True)