import paho.mqtt.client as mqtt
import logging
import time
import random

from brokerData import * #Informacion de la conexion
import socket
import os

TOPIC_USU = "comandos/06/201700728"

#Configuracion inicial de logging
logging.basicConfig(
    level = logging.INFO, 
    format = '[%(levelname)s] (%(processName)-10s) %(message)s'
    )

#JMOC Callback que se ejecuta cuando nos conectamos al broker
def on_connect(client, userdata, rc):
    logging.info("Conectado al broker")

#Callback que se ejecuta cuando llega un mensaje al topic suscrito
def on_message(client, userdata, msg):
    #Se muestra en pantalla informacion que ha llegado
    logging.info(str(msg.topic) + ": " + str(msg.payload))

#JMOC Handler cuando se publique satisfactoriamente en el broker MQTT
def on_publish(client, userdata, mid): 
    publishText = "Publicacion satisfactoria"
    logging.debug(publishText)

#JMOC Funcion para publicar en topics
def publishData(topicName, value, qos = 2, retain = False):
    client.publish(topicName, value, qos, retain)

'''
Config. inicial del cliente MQTT
'''
client = mqtt.Client(clean_session=True) #JMOC Nueva instancia de cliente
client.on_connect = on_connect #JMOC Se configura la funcion "Handler" cuando suceda la conexion
client.on_message = on_message #JMOC Se configura la funcion "Handler" que se activa al llegar un mensaje a un topic subscrito
client.username_pw_set(MQTT_USER, MQTT_PASS) #JMOC Credenciales requeridas por el broker
client.connect(host=MQTT_HOST, port = MQTT_PORT) #JMOC Conectar al servidor remoto
'''        -----------------------    '''

#Nos conectaremos a distintos topics:
qos = 2

#Subscripcion simple con tupla (topic,qos)
client.subscribe((TOPIC_USU, qos))

#Iniciamos el thread (implementado en paho-mqtt) para estar atentos a mensajes en los topics subscritos
client.loop_start()
print("201700728")
while True:
    try:
        print("1. enviar audio por TCP")
        print("2. recebir audio por TCP")
        print("3. 0x03 solicitar transferencia de archivos")
        print("4. salir")
        opcion = input("ingrese opcion: ")
        
        if opcion == "1":
            SERVER_ADD = '167.71.243.238'
            SERVER_PORT = 9806

            BUFFER_SIZE = 64 * 1024
            FILE_SIZE_E = 0
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((SERVER_ADD, SERVER_PORT))

            #print("\nEsperando conexion remota...\n")
            #conn, addr = sock.accept()
            with open('enviarTCP.wav', 'rb') as f: #Se abre el archivo a enviar en BINARIO
                sock.sendfile(f, 0)
                f.close()
            sock.close()


            
        if opcion == "2":
            SERVER_ADD = '167.71.243.238'
            SERVER_PORT = 9806

            BUFFER_SIZE = 64 * 1024
            FILE_SIZE_E = 0
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((SERVER_ADD, SERVER_PORT))

            try:
                #peso = 104182
                #peso_actual=0
                with open('recibidoTCP.wav','wb') as f:
                    while True:
                        l = sock.recv(64*1024)
                        if not l: 
                            break
                        f.write(l)
                        break
                    """while peso_actual < peso:
                        l = sock.recv(BUFFER_SIZE)
                        f.write(l)
                        peso_actual=os.stat('recibidoTCP.wav').st_size"""
                    f.close()
                #conn.close() 
            
            finally:
                logging.debug("Archivo recibido")
                sock.close() #Se cierra el socket
        
        if opcion == "3":
            dest = input("ingrese destinatario: ")
            peso = os.stat('enviarTCP.wav').st_size
            publishData(TOPIC_USU, (b'\x03'+ b'$' + dest.encode() + b'$' + str(peso).encode()))
        
        if opcion == "4":
            exit()

    except KeyboardInterrupt:
        logging.warning("Desconectando del broker MQTT...")
