import snap7
import struct
 
plc = snap7.client.Client()
plc.connect('192.168.0.2', 0, 1)  # IP address, rack, slot (from HW settings)
 
db_number = 2
start_offset = 40
bit_offset = 0
value = 1  # 1 = true | 0 = false
 
def writeBool(db_number, start_offset, bit_offset, value):
    reading = plc.db_read(db_number, start_offset, 1)    # (db number, start offset, read 1 byte)
    snap7.util.set_bool(reading, 0, bit_offset, value)   # (value 1= true;0=false) (bytearray_: bytearray, byte_index: int, bool_index: int, value: bool)
    plc.db_write(db_number, start_offset, reading)       #  write back the bytearray and now the boolean value is changed in the PLC.
    return None
 
def readBool(db_number, start_offset, bit_offset):
    reading = plc.db_read(db_number, start_offset, 1)  
    a = snap7.util.get_bool(reading, 0, bit_offset)
    print('DB Number: ' + str(db_number) + ' Bit: ' + str(start_offset) + '.' + str(bit_offset) + ' Value: ' + str(a))
    return None
 
writeBool(db_number, start_offset, bit_offset, value)
 
readBool(db_number, start_offset, bit_offset)