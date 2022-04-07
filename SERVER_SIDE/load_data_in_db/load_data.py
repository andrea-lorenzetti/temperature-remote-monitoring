import socket
import psycopg2
from datetime import datetime
import sys

host = ""
port = 000 #CHANGE

con = psycopg2.connect("dbname=XXX user=XXX password=XXX") #INSERT YOUR DATA
relation_table = "temperature_table"
if not con:
    print("error accured trying connecting to the db")
    sys.exit(1)

cur = con.cursor()


def insert_tuple(temp):
    try:
        cur.execute(f"INSERT INTO {relation_table}(temperatura, data, orario) "
                    f"VALUES({temp},"
                    f"\'{datetime.today().strftime('%Y-%m-%d')}\',"
                    f"\'{datetime.now().strftime('%H:%M:%S')}\');"
                    )
        print("tuple inserted")
        con.commit()
    except Exception as arg:
        print(f"tuple insertion error in fun:{arg}")

    pass




while True:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    print("socket binded to %s" % (port))
    s.listen(1)
    print("socket is listening")
    # Establish connection with client.
    c, addr = s.accept()
    print('Got connection from', addr)

    c.settimeout(360) #set timeout in case the receive doesnt get anything in 6 minutes
    s.close()#destry socket s to avoid new connection of the esp in case it disconnect itself
    print("socket s closed")
    while True:
        try:
            print("waiting for msg for next 6 min")
            msg = c.recv(1024)
            print("received:" + msg.decode())
            try:
                temp_str = msg.decode()
                temp_float = float(temp_str)
                insert_tuple(temp_float)
            except:
                print("casting error,system closing")
                continue

        except:
            print("timeout occured in receive..")
            break

    # try Close the connection with the client
    try:
        c.close()
    except:
        print("c.close failed failed")
