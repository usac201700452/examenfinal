import paho.mqtt.client as mqtt
import logging
import time
import os 
import socket
from brokerData import * #JMOC Informacion de la conexion
from ClasesAndFun import * #JMOC Importa las clases y funciones escritas 
from globals import * #CFLN Variables globales del programa
from TCPserver import * #CFLN Importa la configuracion y la clase del servidor TCP 
import threading #CFLN Para uso de hilos

#JMOC Configuracion inicial de logging
logging.basicConfig(
    level = logging.DEBUG, 
    format = '[%(levelname)s] (%(threadName)-10s) %(message)s'
    )

TCP = tcp_server()           #JMOC Crea un objeto para el manejo de la recepcion y transmision de archivos de audio

ClientesOnline = []            #CFLN Lista de todos los clientes que envian msg

#JMOC Callback que se ejecuta cuando nos conectamos al broker
def on_connect(client, userdata, rc):
    logging.info("Conectado al broker")


#JMOC Callback que se ejecuta cuando llega un mensaje al topic suscrito
def on_message(client, userdata, msg):
    global ClientesOnline
    #logging.debug(str(msg.topic) + "     " + str(msg.payload)) 

    trama = str(msg.payload).split('$')       #JMOC Guarda la informacion de la trama
    info_remit = str(msg.topic).split('/')       #JMOC Guarda la información del remitente
    #info_remit[0] = 'comandos'
    #info_remit[1] = numero de grupo '06'
    #info_remit[2] = usuario que hace la solicitud  
     
    trama[0] += "'"
    trama[-1] = trama[-1].replace("'",'')       #JMOC elimina el caracter ' que sobra al final 
    
    mult_usua = []                                                      
    if len(trama) > 3:
        for i in range(1,len(trama)-1):
            mult_usua.append(trama[i])         #JMOC si una trama contiene varios usuarios, estos se guardan el la lista mult_usua

    if trama[0] == str(FTR):                 #JMOC Se necesita una transferencia de archivos)
        #JMOC El destinatario es una sala y el remitente es valido
        if len(trama[1]) == 5 and remite_valido(info_remit[2],usuarios):
            logging.info(info_remit[2] + " solicita transferencia a una sala " + trama[1])         
            #JMOC pregunta si la sala es valida (si se encuentra en el archivo salas) y si esta vacia    
            if sala_valida(trama[1]) and sala_vacia(trama[1],info_remit[2],usuarios, ClientesOnline):        
                publishData(msg.topic, OK + b'$' + info_remit[2].encode())    #JMOC Se le notifica al cliente que los destinatarios son validos
                logging.debug("Sala valida")            #INICIA LA RECEPCION
                #JMOC Distribucion de mensaje utilizando un hilo
                h_dist_salas = None
                #JMOC Hilo que se encargara de distribuir los mensajes a todos los usuarios de las salas             
                h_dist_salas = threading.Thread(name = 'Distribucion de mensajes en salas',   
                        target = dist_salas,
                        args = (trama, info_remit, msg.topic),
                        daemon = True
                        )
                h_dist_salas.start()    #JMOC Inicia el hilo que se encargara de distribuir los mensajes a cada usuario de la sala                         
            else:
                publishData(msg.topic, NO + b'$' + info_remit[2].encode())    #JMOC Sala no valida
                logging.debug("Sala no valida")              
        #JMOC Pregunta si el destinatario es un usuario y es un usuario valido
        if (len(trama[1]) == 9) and (remite_valido(info_remit[2],usuarios)) and (mult_usua == []) :  
            logging.info(info_remit[2] + " solicita transferencia a " + trama[1])  
            #JMOC Verifica si el usuario es valido y esta conectado 
            if (usuario_valido(trama[1], usuarios)) and (online(trama[1],ClientesOnline)):          
                publishData(msg.topic, OK + b'$' + info_remit[2].encode())    #JMOC Se le notifica al cliente que los destinatarios son validos
                logging.debug("Usuario valido")
                #JMOC Enviar el mensjae al usuario
                h_dist_usu = None
                #JMOC Hilo que se encargara de enviar el mensaje a un usuario especifico            
                h_dist_usu = threading.Thread(name = 'Distribucion de mensajes a usuario',   
                        target = dist_usu,
                        args = (trama, info_remit, msg.topic),
                        daemon = True
                        )
                h_dist_usu.start()    #JMOC Inicia el hilo que se encargara de distribuir los mensajes a cada usuario

            else:
                publishData(msg.topic, NO + b'$' + info_remit[2].encode())   #JMOC Usuario no valido
                logging.debug("Usuario no valido")

        if (mult_usua != []) and (remite_valido(info_remit[2],usuarios)):         #Si se decea enviar un archivo a varios usuarios
            logging.info(info_remit[2] + " solicita transferencia a multiples usuarios")
            if usuarios_validos(info_remit[2],mult_usua,usuarios):    #Pregunta si los usuarios son validos y si alguno esta conectado
                logging.debug("Usuarios validos")
                publishData(msg.topic, OK + b'$' + info_remit[2].encode())    #JMOC Se le notifica al cliente que los destinatarios son validos
                #JMOC Distribucion de mensajes utilizando un hilo
                h_dist_usus = None
                #JMOC Hilo que se encargara de distribuir los mensajes a todos los usuarios             
                h_dist_usus = threading.Thread(name = 'Distribucion de mensajes a multiples usuarios',   
                        target = dist_usus,
                        args = (mult_usua, trama, info_remit, msg.topic),
                        daemon = True
                        )
                h_dist_usus.start()    #JMOC Inicia el hilo que se encargara de distribuir los mensajes a cada usuario
            else:
                publishData(msg.topic, NO + b'$' + info_remit[2].encode())
                logging.debug("Usuarios no validos o no hay ninguno conectado")

    elif trama[0]==str(ALIVE):           #CFLN Si se recibe el ALIVE
        publishData(msg.topic, ACK + b'$' + trama[1].encode())   #CFLN Se manda la respuesta ACK
        NuevoUsu = True
        for i in range(len(ClientesOnline)):          #CFLN Se verifica si el usuario es un usuario nuevo, de lo contraio
            if trama[1] in ClientesOnline[i]:         #se modifica el valor de su contador  ClientesOnline[i][1] para indicar que esta conectado
                ClientesOnline[i]=[trama[1],0]
                NuevoUsu = False
        if NuevoUsu:                                  #CFLN Si el usuario es nuevo se agrega a la lista de usuarios conectados  
            ClientesOnline.append([trama[1],0])
            logging.info(trama[1]+" se ha conectado")                              
    
#JMOC Handler cuando se publique satisfactoriamente en el broker MQTT
def on_publish(client, userdata, mid): 
    publishText = "Publicacion satisfactoria"
    logging.debug(publishText)

#JMOC Funcion para publicar en topics
def publishData(topicName, value, qos = 2, retain = False):
    client.publish(topicName, value, qos, retain)


client = mqtt.Client(clean_session=True) #JMOC Nueva instancia de cliente
client.on_connect = on_connect #JMOC Se configura la funcion "Handler" cuando suceda la conexion
client.on_message = on_message #JMOC Se configura la funcion "Handler" que se activa al llegar un mensaje a un topic subscrito
client.username_pw_set(MQTT_USER, MQTT_PASS) #JMOC Credenciales requeridas por el broker
client.connect(host=MQTT_HOST, port = MQTT_PORT) #JMOC Conectar al servidor remoto

#JMOC *************** En este apartado se lee la lista de usuarios y se obtienen los datos de estos mismos****************
f = open(USERS, "r")        #CFLN abre el archivo instanciado de usuarios en modo lectura
lineas = f.readlines()         #JMOC guarda las lineas del archivo de usuarios
f.close()                       #JMOC cierra el archivo
infousuarios = []              #JMOC guarda la informacion de cada usuario la posicion [n][0]=usuario, [n][1]=nombre de usu, [n][3]....[n] salas a las que esta suscrito
usuarios = []                  #JMOC lista que guarda objetos del tipo usuario

for i in lineas:  #JMOC Recorre las lineas del archivo de usuarios
    infousuarios.append(i.replace('\n','').split(','))   #JMOC elimina los caracteres de salto de linea
salas = []  #JMOC en esta lista se guardara temporalmente las salas a las que pertenece cada usuario
for i in infousuarios:
    for j in range(2,len(i)):
        salas.append(i[j])
    usuarios.append(usuario(i[0],i[1],salas)) #JMOC Guarda un objeto de tipo usuarios en la lista usuarios
    salas = []
#JMOC **********************************************************************************************************************

#JMOC *****************************************suscripcion a los topics*****************************************************
qos = 2 #JMOC define quality of service
client.subscribe((COMANDOS, qos))    #JMOC suscripcion al topic que recivira los comandos alive de los usuarios
for i in usuarios:
    client.subscribe((COMANDOS+"/"+i.getuser(), qos))   #JMOC conecta al topic correspondiente de cada usuario
#JMOC Iniciamos el thread (implementado en paho-mqtt) para estar atentos a mensajes en los topics subscritos
client.loop_start()
#***************************************************************************************************************************

#JMOC definicion para distribucion de mensajes a una sala
def dist_salas(trama, info_remit, topic):    #JMOC funcion que se encarga de distribuir los mensajes a las salas
    TCP.receive(trama[-1])
    publishData(topic, ACK + b'$' + info_remit[2].encode())    #JMOC Se le notifica al cliente que el archivo ha sido recibido en el servidor
    #JMOC Inicia la distribucion de mensajes
    for i in usuarios:
        for j in i.getrooms():
            if j == trama[1]:
                #JMOC Se hace una solicitud FRR al usuario de la sala si esta conectado
                if online(i.getuser(), ClientesOnline):   #CFLN pregunta si el usuairo de la sala esta conectado
                    publishData(COMANDOS+"/"+i.getuser(), FRR+b'$'+info_remit[2].encode()+b'$'+trama[-1].encode())
                    TCP.transf(i.getuser())  #Inicia la transferencia del archivo 

#JMOC definicion para distribucion de mensajes a multiples ususarios
def dist_usus(mult_usua, trama ,info_remit, topic):    #JMOC funcion que se encarga de distribuir los mensajes a las salas
    TCP.receive(trama[-1])
    publishData(topic, ACK + b'$' + info_remit[2].encode())    #JMOC Se le notifica al cliente que el archivo ha sido recibido en el servidor
    #JMOC Inicia la distribucion de mensajes
    for i in mult_usua:
        if online(i):
            #JMOC se le envia una solicitud de tranferencia a los destinatarios
            publishData(COMANDOS+"/"+i, FRR+b'$'+info_remit[2].encode()+b'$'+trama[-1].encode())  
            TCP.transf(i)  #Inicia la transferencia del archivo   

#JMOC definicion para distribucion de mensaje a un ususario
def dist_usu(trama ,info_remit, topic):    #JMOC funcion que se encarga de distribuir los mensajes a las salas
    TCP.receive(trama[-1])
    publishData(topic, ACK + b'$' + info_remit[2].encode())    #JMOC Se le notifica al cliente que el archivo ha sido recibido en el servidor
    
    #JMOC Se hace una solicitud FRR al usuario receptor  
    publishData(COMANDOS+"/"+trama[1], FRR+b'$'+info_remit[2].encode()+b'$'+trama[-1].encode())
    TCP.transf(trama[1])  #Inicia la transferencia del archivo       

#CFLN def que se encarga de limpiar la lista de clientes
# que no estan enviando su comando ALIVE
def is_alive():
    while True:
        global ClientesOnline
        time.sleep(ALIVE_PERIOD)
        for i in range(len(ClientesOnline)):   #CFLN este ciclo suma al contador de usuarios, para determinar si estan desconectados
            ClientesOnline[i][1]+=1
        
        l=len(ClientesOnline)-1
        i=0
        while i<=l and (len(ClientesOnline)!=0):  #CFLN cilco para eliminar a los usuarios que no estan conectados
            if ClientesOnline[i][1]==3: 
                logging.info(ClientesOnline[i][0]+" se ha desconectado")      
                del ClientesOnline[i]    #CFLN Si el contador del usuario es igual a 3, este se elimina de la lista de usuarios conectados
                l=len(ClientesOnline)-1
                i-=1
            i+=1
        

#CFLN Hilo para correr el metodo isAlive sin afectar el hilo principal        
hiloAlive = threading.Thread(target=is_alive, daemon = True)
hiloAlive.start()

try:
    while True:
        #logging.info("olakease")
        #print(online("201700728", ClientesOnline))
        time.sleep(5)
        #logging.debug(ClientesOnline)
        #publishData("comandos06/201700728", "JOSE")


except KeyboardInterrupt:
    logging.warning("Desconectando del broker...")

finally:
    client.loop_stop() #Se mata el hilo que verifica los topics en el fondo
    client.disconnect() #Se desconecta del broker
    logging.info("Desconectado del broker. Saliendo...")