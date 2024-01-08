import snap7
import time
import psycopg2
from pgconfig import config 

#-------------------------------------------------------------------------------------------------------
#Define Variables
global db_number
global start_offset
global write_data
global plc

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
#-------------------------------------------------------------------------------------------------------
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
def onConnect():
    #connect to the database
    params = config()
    con = psycopg2.connect(**params)
    cur = con.cursor()
    #-------------------------------------------------------------------------------------------------------
    # Update Queries
    orderstatus_upd_Cache = '''UPDATE public.btporders_cachedata SET orderstatus=%s,srcrackid=%s, destrackid=%s, binid_status=%s,bintransfer=%s,recived_status=%s, agvstatus=%s, agverror=%s WHERE orderid=%s;'''
    orderstatus_upd_Master = '''UPDATE public.btporders_masterdata SET orderstatus=%s,srcrackid=%s, destrackid=%s, binid_status=%s,bintransfer=%s WHERE orderid=%s;'''
    agv_ack = '''UPDATE public.btporders_cachedata SET ord_ack_agv=%s WHERE orderid=%s;'''
    #-------------------------------------------------------------------------------------------------------
    #Get data from DB
    cachedata = cur.execute('''SELECT * FROM public.btporders_cachedata ORDER BY id ASC''')
    try:
        datalist = list(cur.fetchone())
        ordAcktoPLC = datalist[12] # Getting agv acknowledgement data from DB
        orderstatus = datalist[7] # Getting agv acknowledgement data from DB
        agvstatus = datalist[14]
        #sendApitoAGV = writetoPLC(datalist)
        if(ordAcktoPLC == 0 and agvstatus == 0):
            try:
                sendApitoAGV = writetoPLC(datalist)
            except:
                sendApitoAGV = 1
            cur.execute(agv_ack, (sendApitoAGV, datalist[1]))
            con.commit()

        elif((ordAcktoPLC == 1) and (orderstatus == 0)):
            while(True):
                orderstatus,srcrackid,destrackid,binid_status,bintransfer,recived_status,agvstatus,agverror = readfromPLC()
                cur.execute(orderstatus_upd_Cache, (orderstatus,srcrackid,destrackid,binid_status,bintransfer,recived_status,agvstatus,agverror, datalist[1]))
                cur.execute(orderstatus_upd_Master, (orderstatus,srcrackid,destrackid,binid_status,bintransfer, datalist[1]))
                con.commit()
                if(orderstatus > 0):
                    break
                time.sleep(0.5)
        else:
            pass
        #Close the connection
        cur.close()
        con.close()
    except:
        print('No Orders received from ASRS System')
#--------------------------------Main Function----------------------------------------------------
# Start the loop
while True:
    if plc.get_connected():
        onConnect()
        # break                     ############### if need comment it
        time.sleep(0.5)
        # recevied_status = 0
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
    time.sleep(0.1)