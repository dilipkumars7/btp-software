import psycopg2
from pgconfig import config 

#connect to the database
binTrans_upd_Cache = '''UPDATE public.btporders_cachedata SET bintransfer=%s WHERE orderid=%s;'''
orderstatus_upd_Cache = '''UPDATE public.btporders_cachedata SET orderstatus=%s WHERE orderid=%s;'''

binTrans_upd_Master = '''UPDATE public.btporders_masterdata SET bintransfer=%s WHERE orderid=%s;'''
orderstatus_upd_Master = '''UPDATE public.btporders_masterdata SET orderstatus=%s WHERE orderid=%s;'''

params = config()
con = psycopg2.connect(**params)
cur = con.cursor()
cachedata = cur.execute('''SELECT * FROM public.btporders_cachedata ORDER BY id ASC''')
rows = cur.fetchone()
datalist = list(rows)
# print(datalist)
print('OrderID      : ', rows[1])
print('BinID        : ', rows[2])
print('SrcLoc       : ', rows[3])
print('DstLoc       : ', rows[4])
print('Ord_Status   : ', rows[5])
print('Bin_status   : ', rows[6])

# cur.execute(binTrans_upd, (True, rows[1]))
cur.execute(orderstatus_upd_Cache, (2, rows[1]))
print('Order Status set to 2 in Cache Table')
cur.execute(orderstatus_upd_Master, (2, rows[1]))
print('Order Status set to 2 in Master Table')
cur.execute(binTrans_upd_Cache, (True, rows[1]))
print('BinTransfer Status set to True in Cache Table')
cur.execute(binTrans_upd_Master, (True, rows[1]))
print('BinTransfer Status set to True in Master Table')
con.commit()
cur.close()
#Close the connection
con.close()



    