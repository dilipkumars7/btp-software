import snap7
import time

#Configure PLC Connection 
plc = snap7.client.Client()
plc.connect('192.168.0.96', 0, 1)  # IP address, rack, slot (from HW settings)

#Define Variables
global db_number
global start_offset
global write_data

#Funtion to read data from PLC
def readfromPLC():
    db_number = 6; value_length = 20  # Adjust the length based on your actual string length
    orderComplete_op    = snap7.util.get_int(plc.db_read(db_number, 1034, 2), 0)
    rackid_op           = snap7.util.get_int(plc.db_read(db_number, 1036, 2), 0)
    binId_op            = snap7.util.get_int(plc.db_read(db_number, 1038, 2), 0)

#Function to wirte data into PLC
def writetoPLC():
    db_number = 6; value_length = 50
    #Define API Data
    binTransfer = 0
    dataArray = ["  PHB0061","  ZH2B1FE","  ASRS-IN","  AA-R2-01-02-01-A"]
    start_offset = [0, 256, 522, 778 ]
    length_Array = [1040, 1042, 1044, 1046]
    ind = 0

    #Send API Data
    for write_data in dataArray:
        #string write to PLC
        write_data = write_data.ljust(value_length, '\x00')  # Pad the string with null bytes
        plc.db_write(db_number, start_offset[ind], bytearray(write_data, 'utf-8'))
        print(write_data, start_offset[ind])
        #integer write to PLC
        # reading = plc.db_read(db_number, start_offset, 2)  # 2 bytes for an integer
        # snap7.util.set_int(reading, 0, 1)   
        plc.db_write(db_number, length_Array[ind], len(write_data)-2) 
        ind += 1

   #boolean Write to PLC 
    # reading = plc.db_read(db_number, start_offset, 1)    # (db number, start offset, read 1 byte)
    # snap7.util.set_bool(reading, 0, bit_offset, 1)   # (value 1= true;0=false) (bytearray_: bytearray, byte_index: int, bool_index: int, value: bool)
    plc.db_write(db_number, start_offset, binTransfer)       #  write back the bytearray and now the boolean value is changed in the PLC.
    return 1

# Start the loop
while True:
    readfromPLC()
    time.sleep(2)
    writetoPLC()
    time.sleep(2)
