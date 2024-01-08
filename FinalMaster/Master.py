import snap7
import time
import psycopg2
from pgconfig import config 

#-------------------------------------------------------------------------------------------------------
#Configure PLC Connection 
ipAddress = '192.168.0.96'
rackaddress = 0
slotaddres = 1
try:
    plc = snap7.client.Client()
    plc.connect(ipAddress, rackaddress, slotaddres)  # IP address, rack, slot (from HW settings)
except:
    pass
#-------------------------------------------------------------------------------------------------------
#Define Variables
global db_number
global start_offset
global write_data

#----------------------------------PLC Read Function ---------------------------------------------
#Funtion to read data from PLC
def readfromPLC():
    print('Reading data from PLC ')
    db_number = 6; value_length = 20 ;bit_offset =0 # Adjust the length based on your actual string length
    orderComplete_op    = snap7.util.get_int(plc.db_read(db_number, 1034, 2), 0)
    rackid_op           = snap7.util.get_int(plc.db_read(db_number, 1036, 2), 0)
    binId_op            = snap7.util.get_int(plc.db_read(db_number, 1038, 2), 0)
    binTransfer_op      = snap7.util.get_bool(plc.db_read(db_number, 512, 1), 0, bit_offset)
    print('Read Data: ', orderComplete_op,rackid_op,binId_op,binTransfer_op)
    return orderComplete_op,rackid_op,binId_op,binTransfer_op

#----------------------------------Plc Write Function ------------------------------------------------------
#Function to wirte data into PLC 
def writetoPLC(datalist):
    print('Writing data to PLC: ', datalist)
    db_number = 6; value_length = 50; bit_offset =0
    #Define API Data
    s_str = '  '
    binTransfer = 1 if datalist[8] == True else 0
    dataArray = [datalist[1]+s_str, datalist[2]+s_str, datalist[3]+s_str, datalist[4]+s_str]
    start_offset = [256, 0, 522, 778]
    length_Array = [1044, 1040, 1048, 1052]

    rcsArr = [datalist[5], datalist[6]]
    rcsoffset = [514, 518]

    ind = 0
    try:
    #Send API Data
        for write_data in dataArray:
            #string write to PLC
            write_data = write_data.ljust(value_length, '\x00')  # Pad the string with null bytes
            plc.db_write(db_number, start_offset[ind], bytearray(write_data, 'utf-8'))
            print(write_data, start_offset[ind])
            # integer write to PLC
            reading = plc.db_read(db_number, length_Array[ind], 4)  # 4 bytes for a double integer
            snap7.util.set_dword(reading, 0, len(write_data)-2)  
            plc.db_write(db_number, length_Array[ind], reading)  
            ind += 1
            print()
        print('String written success')
        # dword to PLC 
        reading = plc.db_read(db_number, rcsoffset[0], 4)  # 4 bytes for a double integer
        snap7.util.set_dword(reading, 0, rcsArr[0])  
        plc.db_write(db_number, rcsoffset[0], reading)  
        print('Int 1 written success')
        reading = plc.db_read(db_number, rcsoffset[1], 4)  # 4 bytes for a double integer
        snap7.util.set_dword(reading, 0, rcsArr[1])  
        plc.db_write(db_number, rcsoffset[0], reading)  
        print('Int 2 written success')
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
def onConnect():
    #connect to the database
    params = config()
    con = psycopg2.connect(**params)
    cur = con.cursor()
    # print(con)
    #-------------------------------------------------------------------------------------------------------
    # Update Queries
    orderstatus_upd_Cache = '''UPDATE public.btporders_cachedata SET orderstatus=%s,rackid_status=%s,binid_status=%s,bintransfer=%s WHERE orderid=%s;'''
    orderstatus_upd_Master = '''UPDATE public.btporders_masterdata SET orderstatus=%s,rackid_status=%s,binid_status=%s,bintransfer=%s WHERE orderid=%s;'''
    agv_ack = '''UPDATE public.btporders_cachedata SET ord_ack_agv=%s WHERE orderid=%s;'''
    #-------------------------------------------------------------------------------------------------------
    #Get data from DB
    cachedata = cur.execute('''SELECT * FROM public.btporders_cachedata ORDER BY id ASC''')
    rows = cur.fetchone()
    datalist = list(rows)
    ordAcktoPLC = datalist[11] # Getting agv acknowledgement data from DB
    orderstatus = datalist[7] # Getting agv acknowledgement data from DB

    print(ordAcktoPLC,orderstatus)
    sendApitoAGV = writetoPLC(datalist)
    # if(ordAcktoPLC == 0):
    #     print('IF Cond')
    #     try:
    #         sendApitoAGV = writetoPLC(datalist)
    #     except:
    #         sendApitoAGV = 1
    #     print("sendApitoAGV: ", sendApitoAGV)
    #     cur.execute(agv_ack, (sendApitoAGV, rows[1]))
    #     con.commit()

    # elif((ordAcktoPLC == 1) and (orderstatus == 0)):
    #     print('ELIF Cond')
    #     while(True):
    #         print('Reading PLC data')
    #         orderComplete_op,rackid_op,binId_op,binTransfer_op = readfromPLC()
    #         print('Order Status: ', orderComplete_op)
    #         cur.execute(orderstatus_upd_Cache, (orderComplete_op,rackid_op,binId_op,binTransfer_op, rows[1]))
    #         cur.execute(orderstatus_upd_Master, (orderComplete_op,rackid_op,binId_op,binTransfer_op, rows[1]))
    #         con.commit()
    #         if(orderComplete_op > 0):
    #             break
    #         time.sleep(1)
    # else:
    #     print('Else Cond')
    #     pass

    #Close the connection
    cur.close()
    con.close()
    
#--------------------------------Main Function----------------------------------------------------
# Start the loop

while True:
    if plc.get_connected():
        onConnect()
        break
        time.sleep(2)
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
    time.sleep(2)