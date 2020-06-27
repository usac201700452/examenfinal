ALIVE_PERIOD = 2 #CFLN Período entre envío de tramas ALIVE del cliente
ALIVE_CONTINUOUS = 0.1 #CFLN Período entre envío de tramas ALIVE si no hay respuesta

#CFLN Comandos utilizados 
FRR = b'\x02'
FTR = b'\x03'
ALIVE = b'\x04'
ACK = b'\x05'
OK = b'\x06'
NO = b'\x07'

COMANDOS = 'comandos/06'
AUDIO_FILE = 'audio_server.wav'

#CLFN Archivos de sistema
USERS = 'usuarios'
ROOMS = 'salas'
