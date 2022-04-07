import numpy as np
import datetime
from datetime import datetime
import matplotlib.pyplot as plt

def set_up_and_plot(M:np.matrix, FILE_PATH:str):
    array_date = M[:, 1]
    date_uniche = np.unique(array_date)
    A, B = sort_matrix(M)
    tempi_ieri, temperature_ieri = convert_matrix_to_temparray_and_tempiarray(A)
    tempi_oggi, temperature_oggi = convert_matrix_to_temparray_and_tempiarray(B)

    tempi = [tempi_ieri, tempi_oggi]
    temperature = [temperature_ieri, temperature_oggi]
    plotting(tempi,temperature,FILE_PATH,date_uniche)
    pass





# FUNZIONE PER RIORDINARE LA MATRICE con 2 colonne 3
def sort_matrix(M:np.matrix):
    array_date = M[:, 1]
    date_uniche = np.unique(array_date)
    date_uniche.sort()
    nr, nc = M.shape
    B = np.empty((nr, nc - 1), dtype="<U15")
    A = np.empty((nr, nc - 1), dtype="<U15")
    # salvo tutti i dati di ieri e li ordino per ora
    i = 0
    for row in M:
        if row[1] == date_uniche[0]:
            A[i][0] = row[0]
            A[i][1] = row[2]
        i += 1
    A = A[~np.all(A == "", axis=1)]  # elimino le righe senza dati
    A = A[A[:, 1].argsort()]  # ordino in base agli orari della giornata

    # SALVO TUTTI I DATI DI OGGI E LI ORDINO PER ORA
    i = 0
    for row in M:
        if row[1] == date_uniche[1]:
            B[i][0] = row[0]
            B[i][1] = row[2]
        i += 1
    B = B[~np.all(B == "", axis=1)]  # elimino le righe senza dati
    B = B[B[:, 1].argsort()]  # ordino in base agli orari della giornata

    return A, B

#converte una matrice in 2 array di float e di orari
def convert_matrix_to_temparray_and_tempiarray(M:np.matrix):
    array_tempe = []
    array_tempi = []

    for t in M:
        array_tempe.append(float(t[0]))
        ora = (datetime.strptime(t[1], '%H:%M:%S'))
        array_tempi.append(ora.strftime('%H:%M'))
    return array_tempi, array_tempe





################################# PARTE DI PLOT ###########################
def plotting(tempi,temperature,FILE_PATH,date_uniche):
    granularita = 0.3 #spostare la variabile nella sezione VARIABILI ????? ATTENZIONE WARNING DI DEFERENZIAMENTO
    fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(16, 9), )
    j = 0
    for id, ax in enumerate(axes):
        ax.plot(tempi[j], temperature[j], color="green", lw=1, marker="o", markersize=3)
        ax.set_xlabel("orario")
        ax.set_ylabel("temperature")
        if abs(min(temperature[j]) - 5 - max(temperature[j]) + 5) > 10:
            granularita = 1.5
            for tick in ax.yaxis.get_major_ticks():
                tick.label.set_fontsize(8)
        ax.yaxis.set_ticks(np.arange(min(temperature[j]) - 5, max(temperature[j]) + 5, granularita))
        ax.set_title(f'temperature della giornata {date_uniche[j]}')
        ax.grid(True)
        for i, txt in enumerate(temperature[j]):
            text = ax.annotate(f"{txt}°", (tempi[j][i], temperature[j][i]))
            text.set_fontsize(9)
            text.set_color("red")
        j +=1

    fig.tight_layout()
    plt.savefig(FILE_PATH)
    #plt.show()

    pass


