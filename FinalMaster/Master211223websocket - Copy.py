import snap7
import time
import psycopg2
from pgconfig import config 
import websocket
# import websockets
import json
import asyncio
from websocket import create_connection
import rel
#-------------------------------------------------------------------------------------------------------
#Configure PLC Connection 
ipAddress = '192.66.1.8'
rackaddress = 0
slotaddres = 1
try:
    plc = snap7.client.Client()
    plc.connect(ipAddress, rackaddress, slotaddres)  # IP address, rack, slot (from HW settings)
except:
    pass


#------------------------------------------------------------------------------------------------------
#Define Variables
global db_number
global start_offset
global write_data

# recevied_status = 1
# def formal():
    # reading = plc.db_read(6, 1048, 2)  # 4 bytes for a integer
    # snap7.util.set_int(reading, 0, recevied_status)  
    # plc.db_write(6, 1048, reading)
    # print('Int 3 written success with:', recevied_status)

#----------------------------------PLC Read Function ---------------------------------------------
def readOrderStatus():
    db_number = 6; value_length = 20 ;bit_offset =0 # Adjust the length based on your actual string length
    orderstatus    = snap7.util.get_int(plc.db_read(db_number, 1036, 2), 0)
    return orderstatus


#Funtion to read data from PLC
def readfromPLC():
    plc.disconnect()
    plc.connect(ipAddress, rackaddress, slotaddres)
    if plc.get_connected():
        print('Reading data from Central PLC')
        db_number = 6; value_length = 20 ;bit_offset =0 # Adjust the length based on your actual string length
        # orderstatus    = snap7.util.get_int(plc.db_read(db_number, 1034, 2), 0)
        srcrackid      = snap7.util.get_int(plc.db_read(db_number, 1038, 2), 0)
        destrackid     = snap7.util.get_int(plc.db_read(db_number, 1040, 2), 0)
        binid_status   = snap7.util.get_int(plc.db_read(db_number, 1042, 2), 0)
        bintransfer    = snap7.util.get_bool(plc.db_read(db_number, 512, 1), 0, bit_offset)
        recived_status = snap7.util.get_int(plc.db_read(db_number, 1052, 2), 0)
        agvstatus      = snap7.util.get_int(plc.db_read(db_number, 1054, 2), 0)
        agverror       = snap7.util.get_int(plc.db_read(db_number, 1056, 2), 0)
        return srcrackid,destrackid,binid_status,bintransfer,recived_status,agvstatus,agverror
    else:
        pass
        
#----------------------------------Plc Write Function ------------------------------------------------------
#Function to wirte data into PLC 

# recevied_status = 1

def writetoPLC(datalist):
    print('Writing data to Central PLC')
    db_number = 6; value_length = 50; bit_offset = 0
    #Define API Data
    s_str = '  '
    binTransfer = 1 if datalist[8] == True else 0
    binmap = datalist[16]
    firstBin = datalist[17]
    # binTransfer = True
    dataArray = [s_str+datalist[1], s_str+datalist[2], s_str+datalist[3], s_str+datalist[4]] #[Order_ID, BinID, srcActLoc, destActLoc]
    start_offset = [256, 0, 522, 778] #Addr -> [Order_ID, BinID, srcActLoc, destActLoc]
    length_Array = [1046, 1044, 1048, 1058] #[orderid_len, BinIDlength , srcActLoc_length, destActLoc_length]
    rcsArr = [datalist[5], datalist[6]] #[srcRCSLocation, destRCSLocation]
    rcsoffset = [514, 518] #[srcRCSLocationAddr, destRCSLocationAddr]

    ind = 0
    try:
    #Send API Data
        for write_data1 in dataArray:
            #string write to PLC
            write_data = write_data1.ljust(value_length, '\x00')  # Pad the string with null bytes
            plc.db_write(db_number, start_offset[ind], bytearray(write_data, 'utf-8'))
            # integer write to PLC
            reading = plc.db_read(db_number, length_Array[ind], 2)  # 4 bytes for a double integer
            snap7.util.set_int(reading, 0, len(write_data1)-2) 
            plc.db_write(db_number, length_Array[ind], reading)  
            print("==================================================")
            print("String        Offset   Length   Length Address")
            print(write_data[2:len(write_data1)-2], '   ', start_offset[ind], '   ', len(write_data1)-2, '   ', length_Array[ind])
            print("==================================================")
            ind += 1
        # dword to PLC 
        reading = plc.db_read(db_number, rcsoffset[0], 4)  # 4 bytes for a double integer
        snap7.util.set_dword(reading, 0, rcsArr[0])  
        plc.db_write(db_number, rcsoffset[0], reading)

        reading = plc.db_read(db_number, rcsoffset[1], 4)  # 4 bytes for a double integer
        snap7.util.set_dword(reading, 0, rcsArr[1])  
        plc.db_write(db_number, rcsoffset[1], reading)
        #########################################################################################
        #Int to start AGV Movement
        reading = plc.db_read(6, 1052, 2)  # 4 bytes for a integer
        snap7.util.set_int(reading, 0, datalist[13])  
        plc.db_write(6, 1052, reading)
        ##############################################
        # boolean to PLC 
        reading = plc.db_read(db_number, 512, 1)    # (db number, start offset, read 1 byte)
        snap7.util.set_bool(reading, 0, bit_offset, binTransfer)   # (value 1= true;0=false) (bytearray_: bytearray, byte_index: int, bool_index: int, value: bool)
        plc.db_write(db_number, 512, reading)
        reading = plc.db_read(db_number, 1034, 1)    # (db number, start offset, read 1 byte)
        snap7.util.set_bool(reading, 0, 0, binmap)   # (value 1= true;0=false) (bytearray_: bytearray, byte_index: int, bool_index: int, value: bool)
        plc.db_write(db_number, 1034, reading)
        reading = plc.db_read(db_number, 1034, 1)    # (db number, start offset, read 1 byte)
        snap7.util.set_bool(reading, 0, 1, firstBin)   # (value 1= true;0=false) (bytearray_: bytearray, byte_index: int, bool_index: int, value: bool)
        plc.db_write(db_number, 1034, reading)
        time.sleep(3)
        return 1    
    except Exception as Error:
        print('PLC Write Error: ', Error)
        return 0

#-------------------------------------Connect Function-----------------------------------------------------
async def onConnect():
    # connect to the database
    params = config()
    con = psycopg2.connect(**params)
    cur = con.cursor()

    # Get data from DB
    cachedata = cur.execute('''SELECT * FROM public.btporders_cachedata ORDER BY id ASC''')
    datalist = list(cur.fetchone())
    ordAcktoPLC = datalist[12]  # Getting agv acknowledgement data from DB
    orderstatus = datalist[7]  # Getting agv acknowledgement data from DB
    agvstatusid = datalist[14]
    if ordAcktoPLC == 0 and agvstatusid == 0:
        try:
            sendApitoAGV = writetoPLC(datalist)
        except:
            sendApitoAGV = 1
        # Update via WebSocket for cache_update
        cache_update_payload = {
            "ord_ack_agv": sendApitoAGV,
            "orderid": datalist[1]
        }
        ws.send(json.dumps({"condition":"IF","data": cache_update_payload}))
    elif ordAcktoPLC == 1 and orderstatus == 0:
        while True:
            print('Reading PLC data')
            try:
                orderstatus = readOrderStatus()
                # ws.send(json.dumps({"condition":"ELSE", "data":""})) #to make web socket conn enabled
                print('Order Status ------->>', orderstatus)
                srcrackid,destrackid,binid_status,bintransfer,recived_status,agvstatus,agverror = readfromPLC() 
                cache_update_payload = {
                    "orderstatus": orderstatus,
                    "srcrackid": srcrackid,
                    "destrackid": destrackid,
                    "binid_status": binid_status,
                    "bintransfer": bintransfer,
                    "recived_status":recived_status, 
                    "agvstatus":agvstatus, 
                    "agverror":agverror,
                    "orderid": datalist[1]
                }
                # print(cache_update_payload)
                ws.send(json.dumps({"condition":"ELIF", "data":cache_update_payload}))
                con.commit()
                if(orderstatus > 0):
                    break
                time.sleep(3)
            except Exception as Error:
                print('Error: ', Error)
                # break# Update via WebSocket for orderstatus_upd_Cache & Master
    else:
        ws.send(json.dumps({"condition":"ELSE", "data":"Invalid Data"}))
        return
    # Close the connection
    cur.close()
    con.close()
#--------------------------------Main Function----------------------------------------------------
# Start the loop
async def main():
    while True:
        if plc.get_connected():
            await onConnect()
        else:
            try:
                plc.connect(ipAddress, rackaddress, slotaddres)
                print('----------PLC Connected------------')
            except:
                print('Connecting to Central System ....')
        await asyncio.sleep(2)

# Run the asyncio event loop
def on_message(ws, messsge):
    print("sending messsge")
def on_error(ws, error):
    print('Error:',error)
def on_close(ws, close_status_code):
    print("## close ##")
def on_open(ws):
    print("open Connection")
    
ws_url = "ws://192.66.1.97:8080/ws/plcdata/boardcast/"
websocket.enableTrace(True)
ws = websocket.WebSocketApp(ws_url, on_message=on_message, on_error=on_error, on_close=on_close, on_open=on_open)
ws = create_connection(ws_url)
asyncio.run(main())
ws.run_forever(dispached=rel, reconnect=100)
rel.signal(2, rel.abort)
rel.dispached