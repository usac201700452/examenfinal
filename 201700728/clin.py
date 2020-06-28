import paho.mqtt.client as mqtt
import logging
import time
import threading
import os
import socket
from brokerData import *
from manejo_topics import *
from Encrypt import *

CRYPTO_ON = True

SERVER_ADD = '167.71.243.238'
SERVER_PORT = 9806
BUFFER_SIZE = 64 * 1024
FILE_SIZE_E = 0

inicio_proceso=False
oki=False
conti=True
espera=True
FRR=b'\x02'
FTR='\\x03'
ACK=b'\x05'
OK=b'\x06'
NO=b'\x07' 
comand=''
comando='comandos/06'
AUDIO="subprocess1.wav"
usuarioss='usuarios/06'     #CFLN Esta variable se utiliza pasa señalar el topic usuarios
salasss='salas/06'  #CFLN Esta variable se utiliza pasa señalar el topic de salas
wavy='/subprocess1.wav'     #CFLN Esta variable se utiliza para señalar el archivo de audio
#EDVC b es utilizado para enviar un comando arecord por medio de la libreria os
b = ['arecord', '-d','-f','U8','-r','8000', 'subprocess1.wav']
insert_at = 2   #EDVC esta variable sirve para insertar en la posicion 4 de la lista b la duracion que tomara arecord
proc_args = b[:]    #EDVC una copia de b para poder insertar el valor
emp=''  #CFLN una variable que no tienen texto para eliminar lineas de los archivos de texto
veces=0
reciv = topic()    #JMOC Objeto que maneja la recepcion de mensajes

direccion=os.path.abspath(os.getcwd()) #EDVC Aqui obtenemos la direccion de donde se encuentra este archivo py corriendo

with open("usuario") as f:  #CFLN Abrimos el archivo usuario
    content = f.readlines()     #CFLN obtenemos su contenido
content = [x.strip() for x in content]      #CFLN eliminamos los espacios vacios

usu=str(content[0]) #CFLN como content es una lista, declaramos una variable usu que sera usada a lo largo del programa


logging.basicConfig(
    level = logging.INFO, 
    format = '[%(levelname)s] (%(threadName)-10s) %(message)s'
    )
def mostrar_menu():
    logging.info("Desea enviar un audio? 1=SI") 
    logging.info("Desea enviar un mensaje? 2=SI")
    logging.info("Desea enviar salir? 3=SI")

def on_connect(client, userdata, rc):   #CFLN De esta linea a la 45 declaramos las definiciones basicas para mqtt
    logging.info("Conectado al broker")


def on_publish(client, userdata, mid): 
    publishText = "Publicacion satisfactoria"
    logging.debug(publishText)


def on_message(client, userdata, msg):
    global comand
    global oki
    #comand=msg.payload.decode()
    operacion=str(msg.payload).split('$')
    operacion[0]+="'"
    operacion[-1]=operacion[-1].replace("'",'')
    logging.info("Valor de operacion: ")
    logging.info(operacion)
    info = msg.topic.split('/')   #JMOC obtiene la informacion del topic
    #JMOC info[0] = indica si es un audio o un text
    #JMOC info[1] =  indica el subtopic del numero de grupo
    #JMOC info[2] =  indica el nombre del sub topic (sala/usuario)
       
    if info[0] == "comandos" and info[1]=="06" and info[2]==usu:
        logging.info("**************")
        print(operacion)
        print(str(OK))
        logging.info("**************")
        if(operacion[0]==str(OK) and usu in operacion):
            logging.info("Entro al if de linea 73")
            oki=True
        elif(operacion[0]==str(FRR)):
          
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((SERVER_ADD, SERVER_PORT))
            try:
                with open('recibido.wav','wb') as f:
                    peso_actual=b'' 
                    peso=int(operacion[2])
                    while len(peso_actual)<peso:
                        l = sock.recv(64*1024)
                        peso_actual+=l
                    f.write(peso_actual)
                    #f.close()
                
                logging.info("Salio del ciclo")
                        
            finally:
                logging.info("Archivo recibido")
                logging.info(operacion[1])
                sock.close() #Se cierra el socket
                reciv.rep_audio(remit=operacion[1])
                if not inicio_proceso:
                    mostrar_menu()
                #os.system('aplay recibido.wav') #JMOC Reproducir mensaje
                
        elif (operacion[0]==str(NO) and usu in operacion):
            oki=False
        elif (operacion[0]==str(ACK) and usu in operacion):
            reconocido=True     

    elif info[0] == "usuarios" or info[0] == "salas":
        logging.info(reciv.chat(info[0], info[2] ,msg.payload))              #Llama el metodo para mostrar mensaje
        if not inicio_proceso:
            mostrar_menu()
    
def publishData(topic, value, qos = 0, retain = False):
    client.publish(topic, value, qos, retain)

def comunicacionCS(usuario='',sala='',size=''):
    logging.info("Si entro")
    logging.info(sala)
    logging.info(usuario)
    if(sala!=''):
        while True: 
            publishData(comando+'/'+usu,'\x03$'+sala+'$'+size)
            time.sleep(1)
            if oki:
                logging.info("El servidor envio un OK enviando audio (sala)")
                
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((SERVER_ADD, SERVER_PORT))
                #print("\nEsperando conexion remota...\n")
                #conn, addr = sock.accept()
                with open('subprocess1.wav', 'rb') as f: #Se abre el archivo a enviar en BINARIO
                    sock.sendfile(f, 0)
                    f.close()
                sock.close()
                break
            else:
                logging.info("El servidor envio un NO, no se enviara el archivo")
                break
    if(usuario!=''):
        while True:
            publishData(comando+'/'+usu,'\x03$'+usuario+'$'+size)
            time.sleep(1)
            if oki:
                logging.info("El servidor envio un OK enviando audio(usuario)")
                
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((SERVER_ADD, SERVER_PORT))
               
                
                with open('subprocess1.wav', 'rb') as f: #Se abre el archivo a enviar en BINARIO
                    sock.sendfile(f, 0)
                    f.close()
                sock.close()
                break
            else:
                logging.info("El servidor envio un NO, no se enviara el archivo")
                break


'''
def alive():
    while(True):
        publishData(comando,'\x04$'+usu)
        if reconocido:
           time.sleep(2)
        else
            time.sleep(0.2)
publishData(comando,'\x04$'+usu)

alive_threadd = threading.Thread(target=alive, daemon=True)
alive_threadd.start()
'''
print("Bienvenido! " + str(content[0]))     #CFLN Damos la bienvenida al usuario

accep=True #CFLN dejamos que accep sea verdadero si content encontro al usuario y asi poder correr la aplicación

with open("salas") as ff: #EDVC Abrimos el archivo que contiene las salas del usuario
    salas_usuario = ff.readlines() #EDVC leemos las lineas y lo guardamos en una lista
    salas_usuario = [xx.strip() for xx in salas_usuario] #EDVC eliminamos espacios vacios en cada elemento
while emp in salas_usuario: salas_usuario.remove(emp)  #EDVC eliminamos las lineas vacias gracias a la variable emp(linea 16)



client = mqtt.Client(clean_session=True) #CFLN iniciamos la sesion
client.on_connect = on_connect 
client.on_publish = on_publish
client.on_message = on_message
client.username_pw_set(MQTT_USER, MQTT_PASS) #CFLN MQTT_USER, MQTT_PASS sale del archivo BrokerData
client.connect(host=MQTT_HOST, port = MQTT_PORT) #CFLN Al igual que MQTT_HOST, MQTT_PORT


qos = 2

usuario_topics=[(usuarioss+'/'+content[0], qos),(comando,qos),(comando+'/'+usu,qos)]  #EDVC Se inicia con los topics que todos los usuarios tienen en comun

for i in salas_usuario:#EDVC Dependiendo de las salas que tenga el usuario 
    usuario_topics.append((salasss+'/'+str(i), qos)) #EDVC agregamos estas a su lista de topics
    
client.subscribe(usuario_topics) #EDVC Se suscribe a los topics del usuario

client.loop_start()
while accep: #EDVC Iniciamos el menu
    try:
        while True:
            inicio_proceso=False
            logging.info("Desea enviar un audio? 1=SI") #EDVC   Mostramos el menu al usuario
            logging.info("Desea enviar un mensaje? 2=SI")
            logging.info("Desea enviar salir? 3=SI")
            respu=int(input())
            inicio_proceso=True 
            if(respu==1): 
                if os.path.exists("subprocess1.wav"):
                    os.remove("subprocess1.wav")
                print("Ingrese la duracion del mensaje (no mayor a 30 seg)") #EDVC  Si enviara un audio le pedimos que sea menor a 30 segundos
                dura=int(input())
                if(dura<=30.0): #EDVC si la duracion es menor permitimos que grabe
                    argu='arecord -d ' + str(dura) + ' -f U8 -r 8000 '+ AUDIO
                    os.system(argu)
                    size = str(os.path.getsize(direccion+wavy))            
                    logging.info("\n Este audio es para una sala o alguien? 1=Sala 2=Alguien") #EDVC Una vez grabado el audio le pedimos al usuario que indique a quien es
                    elec=int(input())
                    if(elec==1):
                        logging.info("Estas son sus salas:")
                        logging.info(str(salas_usuario))
                        logging.info("Escriba la sala receptora ej(06S01):") #EDVC Si eligio una sala le pedimos que indique cual es
                        sal=str(input())
                        logging.info("Enviando solicitud al server FTR") 
                        
                        comunicacionCS(sala=sal,size=size)
               
                        
                    elif(elec==2):
                        logging.info("Escriba el carnet receptor:") #EDVC Si eligio un carnet le pedimos que indique cual es
                        cardes=str(input())
                        comunicacionCS(usuario=cardes,size=size)
                        logging.info("Esperando que el servidor autorize que se envie el audio...")


                else:
                    logging.info("No es posible enviar mas de 30seg!") #EDVC si el usuario ingreso una duracion mayor a 30seg le decimos que no es posible hacer el envio
                
            elif(respu==2):
                logging.info("El mensaje es para una sala o alguien? 1=alguien 2=Sala") #EDVC Si el usuario quiere enviar un mensaje le indicamos si es para alguien o un sala
                res=int(input())
                if(res==1):
                    logging.info("Escriba el carnet del receptor:") #EDVC Si eligio un carnet le pedimos que indique cual es
                    carn=int(input())
                    logging.info("Escriba su mensaje: ") #EDVC luego le pedimos que ingrese el mensaje
                    men=str(input())
                    publishData(usuarioss+'/'+str(carn),men) #EDVC Publicamos en el topic usuarioss(linea 9) + el carnet ingresado
                elif(res==2):
                    logging.info("Estas son sus salas:") #EDVC Si eligio una sala le pedimos que indique cual es
                    logging.info(str(salas_usuario))
                    logging.info("Escriba la sala receptora ej(06S01):")
                    salaa=str(input())
                    if salaa in salas_usuario: #EDVC Si el usuario pertenece a la sala que ingrese permitimos que escriba el mensaje
                        logging.info("Escriba su mensaje: ")
                        men=str(input())
                        publishData(salasss+'/'+str(salaa),men) #EDVC Hacemos el publish a la sala indicada
                    else:
                        logging.info("Usted no esta suscrito a esta sala!") #EDVC Si no esta suscrito le indicamos al usuario
            elif(respu==3):
                break #EDVC Si el usuario indico que quiere salir hacemos break del while loop
           

    except KeyboardInterrupt:
        logging.warning("Desconectando del broker...") #EDVC Si ocurre un error desconectamos al usuario del servidor

    finally:
        client.loop_stop()  #EDVC cuando el usuario sale del while loop paramos el thread del cliente
        client.disconnect() #EDVC lo desconetamos
        logging.info("Desconectado del broker. Saliendo...") #EDVC y le indicamos que salio
        break #EDVC finalmente salimos del while accep