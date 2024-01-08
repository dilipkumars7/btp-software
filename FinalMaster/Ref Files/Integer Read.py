import snap7
import struct
import time
 
db_number = 6
start_offset = 512
bit_offset = 0
value = 50
 
def writeDoubleInt(db_number, start_offset, bit_offset, value):
    reading = plc.db_read(db_number, start_offset, 4)  # 4 bytes for a double integer
    snap7.util.set_dword(reading, 0, value)  
    plc.db_write(db_number, start_offset, reading)      
    return None
 
def readDoubleInt(db_number, start_offset, bit_offset):
    reading = plc.db_read(db_number, start_offset, 4)  # 4 bytes for a double integer
    a = snap7.util.get_dword(reading, 0)
    print('DB Number: ' + str(db_number) + ' DWord: ' + str(start_offset) + ' Value: ' + str(a))
    return None
 
# writeDoubleInt(db_number, start_offset, bit_offset, value)

while True:
    plc = snap7.client.Client()
    plc.connect('192.66.1.8', 0, 1)  # IP address, rack, slot (from HW settings)
    if plc.get_connected():
        print('Connected')
        readDoubleInt(db_number, start_offset, bit_offset)
        time.sleep(1)
    else:
        print('disconnected')
        
    plc.disconnect()
    
    if plc.get_connected():
        print('Connected')
    else:
        print('disconnected')
 