import threading
import time
import psycopg2
import sys
import os
import numpy
import datetime
import plot
import telepot
from telepot.loop import MessageLoop
from datetime import datetime,timedelta

TOKEN = 'TOKEN_CODE'
bot = telepot.Bot(TOKEN)
INTERVALLS = [120,600]
running_threads = []
check = [True,True] #handle the scritpts that are running or to be stops
SOGLIA = 0.0
FILE_PATH = r"/tmp/plots.pdf" #PLOT FILE PATH
modifica_soglia=False
#controlla dbname che non sia invece il nome della table/relation e anche la password
con = psycopg2.connect("dbname=xxx user=xxx password=xxx")
relation_table="table name"
if not con:
    print("error accured trying connecting to the db")
    sys.exit(1)
cur = con.cursor()


def remove_running_thread(name):
    for x in running_threads:
        if x == name:
            running_threads.remove(x)


def startScript(chat_id, c):
    ultima_ora=""
    c[0] = True
    remove_running_thread("/stop_aggiornamenti_live")
    while c[0]:
        cur.execute(f"SELECT * FROM {relation_table}   WHERE orario=(SELECT MAX(orario) FROM {relation_table} WHERE data=(SELECT MAX(data) FROM {relation_table})) AND data=(SELECT MAX(data) FROM {relation_table});")
        if cur.rowcount != 0:
            data_matrix = from_query_to_matrix(cur)
            if ultima_ora != data_matrix[0][2]:
                bot.sendMessage(chat_id, from_matrix_to_string(data_matrix))
                ultima_ora = data_matrix[0][2]
            else:
                print("temperatura non aggiornata ancora")
            print("dormo 120sec")
            time.sleep(INTERVALLS[0])
            print("mi sveglio")
        else:
            bot.sendMessage(chat_id, "non ci sono temperature nel database (command for: aggiornamenti live) ")
            c[0] = False
            remove_running_thread("/aggiornamenti_live")
    pass


def stopScript(chat_id, c):
    c[0] = False
    bot.sendMessage(chat_id, "script FERMATO per riavviare usare comando: /aggiornamenti_live")
    remove_running_thread("/aggiornamenti_live")
    pass

def print_all_temp(chat_id, c):

    cur.execute(f"SELECT * FROM {relation_table};")
    if cur.rowcount != 0:
        data_matrix = from_query_to_matrix(cur)
        bot.sendMessage(chat_id, from_matrix_to_string(data_matrix))
    else:
        bot.sendMessage(chat_id, "non ci sono temperature nel database (command for: stampa tutte le temperature) ")
    remove_running_thread('/dammi_le_temperature')
    pass


def last_temp(chat_id, c):
    cur.execute(f"SELECT * FROM {relation_table}  WHERE orario=(SELECT MAX(orario) FROM {relation_table} WHERE data=(SELECT MAX(data) FROM {relation_table})) AND data=(SELECT MAX(data) FROM {relation_table});")
    if cur.rowcount != 0:
        data_matrix = from_query_to_matrix(cur)
        bot.sendMessage(chat_id, from_matrix_to_string(data_matrix))
    else:
        bot.sendMessage(chat_id, "non ci sono temperature nel database (command for: utlima temperatura) ")
    remove_running_thread('/vedi_ultima_temperatura_registrata')
    pass

def active_alert(chat_id,c):
    c[1]=True
    remove_running_thread("/ALERT_OFF")
    while c[1]:
        cur.execute(f"SELECT * FROM {relation_table}  WHERE orario=(SELECT MAX(orario) FROM {relation_table} WHERE data=(SELECT MAX(data) FROM {relation_table})) AND data=(SELECT MAX(data) FROM {relation_table});")
        if cur.rowcount != 0:
            matrix=from_query_to_matrix(cur)
            actual_time = datetime.strptime(f"{datetime.today().strftime('%Y-%m-%d')} {datetime.now().strftime('%H:%M:%S')}", '%Y-%m-%d %H:%M:%S')
            time_from_matrix = datetime.strptime(f'{matrix[0][1]} {matrix[0][2]}', '%Y-%m-%d %H:%M:%S')
            deltat=actual_time-time_from_matrix
            if deltat.seconds < 1800:
                if float(matrix[0][0]) < SOGLIA:
                    bot.sendMessage(chat_id,f'ALLERT: temperatura al di sotto della soglia: {matrix[0][0]} °C')
            else:
                print("ultima temperatura registrata presa troppo tempo fa")
            time.sleep(INTERVALLS[1])

        else:
            bot.sendMessage(chat_id, "non ci sono temperature nel database (command for: attiva allerta) ")
            c[1]=False
            remove_running_thread("/ALERT_con_soglia")

    pass


def disable_alert(chat_id, c):
    c[1] = False
    bot.sendMessage(chat_id, "ALERT CON SOGLIA FERMATO, per riavviare usare comando: /ALERT_con_soglia")
    remove_running_thread("/ALERT_con_soglia")
    pass

def send_plot(chat_id,c):
    cur.execute(f"SELECT * FROM {relation_table} WHERE data=\'{str(datetime.today().strftime('%d-%m-%Y'))}\' OR data=\'{str((datetime.today()-timedelta(days=1)).strftime('%d-%m-%Y'))}\'")
    if cur.rowcount != 0:
        print(FILE_PATH)
        M=from_query_to_matrix(cur)
        try:
            plot.set_up_and_plot(M,FILE_PATH)
        except:
            bot.sendMessage(chat_id,"cè stato un errrore nella funzione di plot, probabilmente non ci sono temperature registrate per ieri o oggi, riprovare in un secondo momento")
        else:
            bot.sendDocument(chat_id,open(FILE_PATH,'rb')) #rb = read binary
            os.remove(FILE_PATH)
    else:
        bot.sendMessage(chat_id,"non ci sono temperature per ieri e oggi")
    remove_running_thread("/temp_ieri_oggi")
    pass


def info(chat_id, c):
    bot.sendMessage(chat_id, "/aggiornamenti_live -> to start the script")
    bot.sendMessage(chat_id, "/stop_aggiornamenti_live -> to stop the script")
    bot.sendMessage(chat_id, "/vedi_ultima_temperatura_registrata -> ti do l'ultima temperature")
    bot.sendMessage(chat_id, "/dammi_le_temperature -> ti do le temperature nel database ")
    bot.sendMessage(chat_id, f"/ALERT_con_soglia -> ti avverto se la temperatura scende sotto la soglia di {SOGLIA}°C ")
    bot.sendMessage(chat_id, "/ALERT_OFF -> disabilita l'allerta ")
    bot.sendMessage(chat_id, "/modifica_soglia -> permette di modificare la soglia di allerta")
    bot.sendMessage(chat_id, "/temp_ieri_oggi -> ti mando un grafico delle temperature di ieri e oggi ")
    bot.sendMessage(chat_id, "/INFO -> to know what you can do")
    running_threads.pop()


switcher = {
    "/aggiornamenti_live": startScript,
    "/stop_aggiornamenti_live": stopScript,
    "/vedi_ultima_temperatura_registrata": last_temp,
    "/dammi_le_temperature": print_all_temp,
    "/ALERT_con_soglia": active_alert,
    "/ALERT_OFF":disable_alert,
    "/temp_ieri_oggi":send_plot,
    "/INFO": info
}


def mod_soglia(new_soglia_string,chat_id):
     global SOGLIA
     try:
         SOGLIA=float(new_soglia_string)
         bot.sendMessage(chat_id,"soglia modificata correttamente")
     except:
         bot.sendMessage(chat_id,"soglia non modificata ci deve essere stato qualche errore riprovare il comando /modifica_soglia")
     pass

def handle(msg):
    msg_content, chat_type, chat_id = telepot.glance(msg)
    global modifica_soglia
    if msg_content == 'text':
        text_msg = msg['text']
        res = switcher.get(text_msg, "invalid")
        if modifica_soglia:
            mod_soglia(text_msg,chat_id)
            modifica_soglia=False
        else:
            if res != "invalid":
                if text_msg not in running_threads:
                    running_threads.append(text_msg)
                    th = threading.Thread(target=res, args=(chat_id, check))
                    th.start()
                    print(running_threads)
                else:
                    bot.sendMessage(chat_id, "command already running")
            elif text_msg=="/modifica_soglia":
                modifica_soglia=True
                bot.sendMessage(chat_id,
                                "dammi la nuova soglia dell'allerta o inviami qualsiasi parola per uscire da questa funzione")
            else:
                bot.sendMessage(chat_id, "invalid command, try again or type: /INFO")
    else:
        bot.sendMessage(chat_id, 'error, only text message accepted')
    pass


############################working with queries###########################
def from_query_to_matrix(cur):
    matrix = numpy.empty((cur.rowcount, 3), dtype="<U15")
    i = 0
    all_tuples = cur.fetchall()
    for tuple in all_tuples:
        matrix[i][0] = tuple[0]
        matrix[i][1] = tuple[1]
        matrix[i][2] = tuple[2]
        i += 1

    return matrix


# da matrice a stringa stampabile
def from_matrix_to_string(data_matrix):
    mess = ''
    for row in data_matrix:
        mess += f'TEMPERATURA= {row[0]}°C | ORE: {row[2]} | DATA: {row[1]} '
        mess += '\n'
    return mess


MessageLoop(bot, handle).run_as_thread()
while 1:
    time.sleep(1)
