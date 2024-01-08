import snap7
import time
import psycopg2
from pgconfig import config 
import websocket
# import websockets
import json
import asyncio
from websocket import create_connection
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
#Funtion to read data from PLC
def readfromPLC():
    print('Reading data from PLC ')
    db_number = 6; value_length = 20 ;bit_offset =0 # Adjust the length based on your actual string length
    orderstatus    = snap7.util.get_int(plc.db_read(db_number, 1034, 2), 0)
    srcrackid      = snap7.util.get_int(plc.db_read(db_number, 1036, 2), 0)
    destrackid     = snap7.util.get_int(plc.db_read(db_number, 1036, 2), 0)
    binid_status   = snap7.util.get_int(plc.db_read(db_number, 1040, 2), 0)
    bintransfer    = snap7.util.get_bool(plc.db_read(db_number, 512, 1), 0, bit_offset)
    recived_status = snap7.util.get_int(plc.db_read(db_number, 1050, 2), 0)
    agvstatus      = snap7.util.get_int(plc.db_read(db_number, 1052, 2), 0)
    agverror       = snap7.util.get_int(plc.db_read(db_number, 1054, 2), 0)
    return orderstatus,srcrackid,destrackid,binid_status,bintransfer,recived_status,agvstatus,agverror

#----------------------------------Plc Write Function ------------------------------------------------------
#Function to wirte data into PLC 

# recevied_status = 1

def writetoPLC(datalist):
    print('Writing data to PLC: ', datalist)
    db_number = 6; value_length = 50; bit_offset = 0
    #Define API Data
    s_str = '  '
    binTransfer = 1 if datalist[8] == True else 0
    # binTransfer = True
    dataArray = [s_str+datalist[1], s_str+datalist[2], s_str+datalist[3], s_str+datalist[4]] #[Order_ID, BinID, srcActLoc, destActLoc]
    start_offset = [256, 0, 522, 778] #Addr -> [Order_ID, BinID, srcActLoc, destActLoc]
    length_Array = [1044, 1042, 1046, 1048] #[orderid_len, BinIDlength , srcActLoc_length, destActLoc_length]
    rcsArr = [datalist[5], datalist[6]] #[srcRCSLocation, destRCSLocation]
    rcsoffset = [514, 518] #[srcRCSLocationAddr, destRCSLocationAddr]

    ind = 0
    try:
    #Send API Data
        for write_data1 in dataArray:
            #string write to PLC
            write_data = write_data1.ljust(value_length, '\x00')  # Pad the string with null bytes
            plc.db_write(db_number, start_offset[ind], bytearray(write_data, 'utf-8'))
            print(write_data, start_offset[ind])
            # integer write to PLC
            reading = plc.db_read(db_number, length_Array[ind], 2)  # 4 bytes for a double integer
            snap7.util.set_int(reading, 0, len(write_data1)-2)  
            plc.db_write(db_number, length_Array[ind], reading)  
            ind += 1
        print('String written success')
        # dword to PLC 
        reading = plc.db_read(db_number, rcsoffset[0], 4)  # 4 bytes for a double integer
        snap7.util.set_dword(reading, 0, rcsArr[0])  
        plc.db_write(db_number, rcsoffset[0], reading)

        reading = plc.db_read(db_number, rcsoffset[1], 4)  # 4 bytes for a double integer
        snap7.util.set_dword(reading, 0, rcsArr[1])  
        plc.db_write(db_number, rcsoffset[1], reading)
        #########################################################################################
        #Int to start AGV Movement
        reading = plc.db_read(6, 1050, 2)  # 4 bytes for a integer
        snap7.util.set_int(reading, 0, datalist[13])  
        plc.db_write(6, 1050, reading)
        ##############################################
        # boolean to PLC 
        reading = plc.db_read(db_number, 512, 1)    # (db number, start offset, read 1 byte)
        snap7.util.set_bool(reading, 0, bit_offset, binTransfer)   # (value 1= true;0=false) (bytearray_: bytearray, byte_index: int, bool_index: int, value: bool)
        plc.db_write(db_number, 512, reading)
        print('Boolean written success')
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
    rows = cur.fetchone()
    datalist = list(rows)
    ordAcktoPLC = datalist[12]  # Getting agv acknowledgement data from DB
    orderstatus = datalist[7]  # Getting agv acknowledgement data from DB
    agvstatusid = datalist[14]
    print(ordAcktoPLC, agvstatusid)
    if ordAcktoPLC == 0 and agvstatusid == 0:
        print('If')
        try:
            sendApitoAGV = writetoPLC(datalist)
        except:
            sendApitoAGV = 1
        # Update via WebSocket for cache_update
        cache_update_payload = {
            "ord_ack_agv": sendApitoAGV,
            "orderid": rows[1]
        }
        print(cache_update_payload)
        ws.send(json.dumps({"condition":"IF","data": cache_update_payload}))
    elif ordAcktoPLC == 1 and orderstatus == 0:
        print('Else IF')
        while True:
            print('Reading PLC data')
            orderstatus,srcrackid,destrackid,binid_status,bintransfer,recived_status,agvstatus,agverror = readfromPLC()
            # Update via WebSocket for orderstatus_upd_Cache & Master
            cache_update_payload = {
                "orderstatus": orderstatus,
                "srcrackid": srcrackid,
                "destrackid": destrackid,
                "binid_status": binid_status,
                "bintransfer": bintransfer,
                "recived_status":recived_status, 
                "agvstatus":agvstatus, 
                "agverror":agverror,
                "orderid": rows[1]
            }
            ws.send(json.dumps({"condition":"ELIF", "data":cache_update_payload}))
            con.commit()
            if orderstatus > 0:
                break
            time.sleep(1)
    else:
        ws.send(json.dumps({"condition":"ELSE", "data":"Invalid Data"}))
        print('Else')
        # ws.run_forever()
        return
    # Close the connection
    cur.close()
    con.close()
#--------------------------------Main Function----------------------------------------------------
# Start the loop
async def main():
    while True:
        if plc.get_connected():
            print("on connect")
            await onConnect()
            # break  # Uncomment if needed
            await asyncio.sleep(1)
        else:
            print('Trying to establish connection with ' + ipAddress)
            try:
                plc.connect(ipAddress, rackaddress, slotaddres)
                connection = '''
                Established Connection with the PLC.
                Connection Details:
                -------------------
                IP Address:''' + ipAddress + '''
                Rack      :''' + str(rackaddress) + '''
                Slot      :''' + str(slotaddres) + '''
                --------------------'''
                print(connection)
            except:
                print('*')
        await asyncio.sleep(1)
        # ws.run_forever(dispached=rel, reconnect=100)
        # rel.signal(2, rel.abort)
        # rel.dispached

# Run the asyncio event loop
def on_message(ws, messsge):
    print("sending messsge")
def on_error(ws, error):
    print(error)
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