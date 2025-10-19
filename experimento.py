from datetime import datetime


data_agora = datetime.now()
data_formatada = data_agora.strftime("%d-%m-%Y %H:%M:%S")
data_convertida = datetime.strptime(data_formatada, "%d-%m-%Y %H:%M:%S")
print("Convertida para datetime:", data_convertida)
print(data_formatada, type(data_formatada))