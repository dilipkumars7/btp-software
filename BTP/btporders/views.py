from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse
import json
from datetime import datetime
from btporders.models import MasterData, CacheData
from btporders.serializers import MasterDataDbSerializer, CacheDataSerializer

@csrf_exempt
def saveOrders(request):
    if request.method == 'POST':    
        apiData = json.loads(request.body)
        MasterData(  date = datetime.now().date(),
                            orderid     =apiData['orderId'], 
                            binid       =apiData['binId'], 
                            bintransfer =apiData['binTransfer'], 
                            srcRCSlocation  =apiData['srcRCSLocation'], 
                            destRCSlocation = apiData['destRCSLocation'],
                            srcActlocation  =apiData['srcActualLocation'], 
                            destActlocation = apiData['destActualLocation'],
                            binmapping = apiData['binMapping']).save()
        if(CacheData.objects.all()):
            CacheData.objects.update( orderid           = apiData['orderId'], 
                                        binid           = apiData['binId'], 
                                        bintransfer     = apiData['binTransfer'], 
                                        srcRCSlocation  = apiData['srcRCSLocation'], 
                                        destRCSlocation = apiData['destRCSLocation'],
                                        srcActlocation  = apiData['srcActualLocation'], 
                                        destActlocation = apiData['destActualLocation'],
                                        orderstatus     = 0,
                                        srcrackid       = 0,
                                        destrackid      = 0,
                                        binid_status    = 0,
                                        ord_ack_agv     = 0,
                                        recived_status  = 1,
                                        agvstatus       = 0,
                                        agverror        = 0,
                                        binmapping = apiData['binMapping'],
                                        frontbinpresent = apiData['frontBinPresent'])
        else:
            CacheData( orderid=apiData['orderId'], 
                                        binid           = apiData['binId'], 
                                        bintransfer     = apiData['binTransfer'], 
                                        srcRCSlocation  = apiData['srcRCSLocation'], 
                                        destRCSlocation = apiData['destRCSLocation'],
                                        srcActlocation  = apiData['srcActualLocation'], 
                                        destActlocation = apiData['destActualLocation'],
                                        orderstatus     = 0,
                                        srcrackid       = 0,
                                        destrackid      = 0,
                                        binid_status    = 0,
                                        ord_ack_agv     = 0,
                                        recived_status  = 1,
                                        agvstatus       = 0,
                                        agverror        = 0,
                                        binmapping = apiData['binMapping'],
                                        frontbinpresent = apiData['frontBinPresent']).save() 
        return JsonResponse({"statusCode":200,"statusMessage":'Order detail Saved Successfully'}, safe=False)

@csrf_exempt
def getDatas(request):
    if request.method == 'GET':    
        inputdate = request.GET['date']
        Totaldata = MasterData.objects.filter(date=inputdate)
        completed = MasterData.objects.filter(date=inputdate, orderstatus=2)
        InvalidData = MasterData.objects.filter(date=inputdate, orderstatus=1)
        Data = CacheData.objects.all()
        ins = (CacheDataSerializer(Data[0])).data
        overview = {
            "total": Totaldata.count(),
            "invalid": InvalidData.count(),
            "completed": completed.count()
        }
        return JsonResponse({"overview": overview, "status": ins}, safe=False)
    if request.method == 'POST':
        inputdate = request.GET['date']
        tbdata = MasterData.objects.filter(date=inputdate).all()
        serialdata = MasterDataDbSerializer(tbdata, many=True)
        # print(serialdata.data)
        return JsonResponse(serialdata.data, safe=False)
