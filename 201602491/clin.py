import paho.mqtt.client as mqtt
import logging
import time
import threading
import os
import socket
from brokerData import *
from manejo_topics import *
from Encrypt import *

CRYPTO_ON = True #EDVC Esta variable indica si utilizaremos la encriptacion para enviar un mensaje

SERVER_ADD = '167.71.243.238' #EDVC Datos para la conexion TCP 
SERVER_PORT = 9806
BUFFER_SIZE = 64 * 1024
FILE_SIZE_E = 0

reconocido_alive=False  #EDVC Aqui tenemos todas nuestras variables globales a utilizar
reconocido_audio=False
wavy_encrip='/encripe'
inicio_proceso=False
oki=False
conti=True
espera=True
FRR=b'\x02'
ACK=b'\x05'
OK=b'\x06'
NO=b'\x07' 
comand=''
comando='comandos/06'
AUDIO="subprocess1.wav"
usuarioss='usuarios/06'     
salasss='salas/06'  
wavy='/subprocess1.wav'      
emp=''  
veces=0

reciv = topic()    #EDVC Aqui declaramos los objetos de nuestras clases propias a utilizar
encri = EncriptarMensaje()

direccion=os.path.abspath(os.getcwd()) #EDVC Aqui obtenemos la direccion de donde se encuentra este archivo py corriendo

with open("usuario") as f:  #EDVC Abrimos el archivo usuario para encontrar el usuario que activo el programa
    content = f.readlines()     
content = [x.strip() for x in content]     

usu=str(content[0]) #EDVC como content es una lista, declaramos una variable usu la cual es el usuario que activo el programa 


logging.basicConfig(
    level = logging.INFO, 
    format = '[%(levelname)s] (%(threadName)-10s) %(message)s'
    )
def mostrar_menu():     #EDVC Esta funcion reimprime el menu al usuario, solo se activa cuando el no este en proceso de enviar algun audio o texto
    logging.info("Desea enviar un audio? 1=SI") 
    logging.info("Desea enviar un mensaje? 2=SI")
    logging.info("Desea enviar salir? 3=SI")

def on_connect(client, userdata, rc):   #EDVC Declaramos las funciones basicas para mqtt
    logging.info("Conectado al broker")

def on_publish(client, userdata, mid): 
    publishText = "Publicacion satisfactoria"
    logging.debug(publishText)


def on_message(client, userdata, msg): #EDVC esta funcion se activara siempre que se reciba un audio o texto 
    global comand
    global oki
    global reconocido_alive
    global reconocido_audio
    
    operacion=str(msg.payload).split('$') #EDVC Aqui separamos el mensaje si es que tiene $
    operacion[0]+="'"
    operacion[-1]=operacion[-1].replace("'",'') #EDVC operacion nos servirar para indentificar la orden que de el servidor
    
    info = msg.topic.split('/')   #EDVC obtiene la informacion del topic
    
    
    
    if info[0] == "comandos" and info[1]=="06" and len(info)==2: #EDVC Si se envio al topic comandos/06 se activa el if
        
        if (operacion[0]==str(ACK) and usu in operacion): #EDVC Con operacion sabemos si el servidor envion un ACK y para saber si va dirijido a este usuario se hace usu in operacion
            reconocido_alive=True                         #EDVC si nuestro alive fue reconocido decimos reconocido_alive

    elif info[0] == "comandos" and info[1]=="06" and info[2]==usu: #EDVC Si se envio al topic comandos/06/usu se activa el if
        
        if(operacion[0]==str(OK) and usu in operacion):
            oki=True                        #EDVC Si se recibio un OK y el usuario esta en la trama oki se vuelve true

        elif(operacion[0]==str(FRR)):
            #EDVC Si se recibe un FRR activamos el socket para empezar a recibir el archivo
            #EDVC NO hay necesidad de verificar si es nuestro ya que estamos dentro del if de la linea 86
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((SERVER_ADD, SERVER_PORT))
            try:
                nombre_audio=str(time.time())   #EDVC el nombre del archivo de audio sera el timestamp del momento que se reciba
                with open(nombre_audio+'.wav','wb') as f:
                    peso_actual=b'' 
                    peso=int(operacion[2])
                    while len(peso_actual)<peso:
                        l = sock.recv(64*1024)
                        peso_actual+=l
                    if CRYPTO_ON:   #EDVC si la encriptacion esta activva debemos desencriptar antes de crear el archivo
                        f.write(encri.desencriptar(peso_actual))
                    else:
                        f.write(peso_actual)
                f.close()         
                         
            finally:
                logging.info("Archivo recibido")
                sock.close()                            #EDVC Se cierra el socket y luego reproducimos el audio
                reciv.rep_audio(remit=operacion[1],nomr=nombre_audio)
                if not inicio_proceso: #EDVC si el usuario no ha iniciado algun proceso le volvemos a mostrar el menu
                    mostrar_menu()   
               
                
        elif (operacion[0]==str(NO) and usu in operacion):
            oki=False       #EDVC Si se recibio un NO volvemos ok=false

        elif (operacion[0]==str(ACK) and usu in operacion):
            reconocido_audio=True   #EDVC SI se recibio un ACK dirijido al topic del usuario decimos que el audio fue enviado correctamente
            logging.info("El audio se envio")
        
    elif info[0] == "usuarios" or info[0] == "salas": #EDVC Si se recibe algo a un topic que inicia con usuario o salas significa que se recibira un texto
        #EDVC NO es necesario verificar que haya sido escrito en el topic de textos del usuario ya que el solo estara suscrito a sus topics y no al de los demas
        #EDVC Si la encriptacion esta activa desencriptamos el mensaje
        if CRYPTO_ON:
            logging.info(reciv.chat(info[0], info[2] ,encri.desencriptar(msg.payload)))  
        else:
            logging.info(reciv.chat(info[0], info[2] ,msg.payload)) 
        if not inicio_proceso:
            mostrar_menu()
    
def publishData(topic, value, qos = 0, retain = False): #EDVC definimos la funcion basica publishData
    client.publish(topic, value, qos, retain)

def comunicacionCS(usuario='',sala='',size=''): #EDVC Esta funcion se encarga de hacer la comunicacion del cliente al servidor
    #EDVC comunicacionCS solo se activa si se enviara un audio
    if(sala!=''): #EDVC Si se recibio una sala significa que el audio es para una sala
        while True: 
            publishData(comando+'/'+usu,'\x03$'+sala+'$'+size)  #EDVC le enviamos un FTR al servidor con la sala a enviar y el tamaño
            time.sleep(1)   #EDVC Esperamos en caso haya mala conexion de internet
            if oki:
                #EDVC   SI oki se volvio True podemos empezar a enviar el audio
                logging.info("El servidor envio un OK enviando audio (sala)")
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((SERVER_ADD, SERVER_PORT))
               
                if CRYPTO_ON: #EDVC Si la encriptacion esta activa abrimos el audio ya encriptado (linea 277)
                    with open('encripe', 'rb') as f: 
                        sock.sendfile(f, 0)
                    f.close()
                    sock.close()
                else:
                    with open('subprocess1.wav', 'rb') as f: 
                        sock.sendfile(f, 0)
                    f.close()
                    sock.close()
                break
            else:
                logging.error("El servidor envio un NO, no se enviara el archivo")
                break
    if(usuario!=''):
        while True:
            publishData(comando+'/'+usu,'\x03$'+usuario+'$'+size) #EDVC le enviamos un FTR al servidor con el usuario a enviar y el tamaño
            time.sleep(1)
            if oki:
                logging.info("El servidor envio un OK enviando audio(usuario)")
                
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((SERVER_ADD, SERVER_PORT))
                if CRYPTO_ON: #EDVC Si la encriptacion esta activa abrimos el audio ya encriptado (linea 277)
                    with open('encripe', 'rb') as f: 
                        sock.sendfile(f, 0)
                    f.close()
                    sock.close()
                else:
                    with open('subprocess1.wav', 'rb') as f: 
                        sock.sendfile(f, 0)
                    f.close()
                    sock.close()
                break
            else:
                #EDVC En caso el servidor envio un NO le decimos al usuario
                logging.info("El servidor envio un NO, no se enviara el archivo")
                break



def alive(): #EDVC aqui creamos la funcion que enviara un alive al servidor
    cont=0
    tiempo=0
    while(True):
        global reconocido_alive     #EDVC Cuando iniciemos el usuario reconocido_alive falso
        publishData(comando,'\x04$'+usu)   #EDVC Hacemos un publich ALIVE x04 para cambiar el valor de reconocido_alive
        time.sleep(2)
        if reconocido_alive and cont <=3: #EDVC Luego de esperar 2 seg si el servidor contesto reconocido_alive sera true y cont siempre sera 0
           reconocido_alive=False  
           cont=0
        else:
            cont=cont+1 #EDVC en el caso el servidor no contestara haremos el mosmo procedimiento 3 veces
        while cont>3: #EDVC si ya intentamos 3 veces empezamos a enviar cada 0.1 segundos
            publishData(comando,'\x04$'+usu)
            time.sleep(0.1)
            if reconocido_alive: #Si en algun momento el servidor responde reiniciamos todo
                cont=0
                tiempo=0
                break
            elif tiempo==200: #EDVC Si pasaron 20 segundos y el servidor nunca contesto cerramos el programa
                 logging.critical("El servidor no contesto, saliendo")
                 os._exit(0)
            else:
                tiempo=tiempo+1 #EDVC vamos aumentando nuestro contador de tiempo
            
                
               

with open("salas") as ff: #EDVC Abrimos el archivo que contiene las salas del usuario
    salas_usuario = ff.readlines() #EDVC leemos las lineas y lo guardamos en una lista
    salas_usuario = [xx.strip() for xx in salas_usuario] #EDVC eliminamos espacios vacios en cada elemento
while emp in salas_usuario: salas_usuario.remove(emp)  #EDVC eliminamos las lineas vacias gracias a la variable emp(linea 16)



client = mqtt.Client(clean_session=True) #EDVC iniciamos la sesion
client.on_connect = on_connect 
client.on_publish = on_publish
client.on_message = on_message
client.username_pw_set(MQTT_USER, MQTT_PASS) #EDVC MQTT_USER, MQTT_PASS sale del archivo BrokerData
client.connect(host=MQTT_HOST, port = MQTT_PORT) #EDVC Al igual que MQTT_HOST, MQTT_PORT


qos = 2

usuario_topics=[(usuarioss+'/'+content[0], qos),(comando,qos),(comando+'/'+usu,qos)]  #EDVC Se inicia con los topics que todos los usuarios tienen en comun

for i in salas_usuario:#EDVC Dependiendo de las salas que tenga el usuario 
    usuario_topics.append((salasss+'/'+str(i), qos)) #EDVC agregamos estas a su lista de topics
    
client.subscribe(usuario_topics) #EDVC Se suscribe a los topics del usuario

client.loop_start()



publishData(comando,'\x04$'+usu) #EDVC Siempre que se inicia el programa enviamos un alive al servidor una vez

alive_threadd = threading.Thread(target=alive, daemon=True) #EDVC Activamos nuestro hilo para verificar si estamos en comunicacion con el servidor
alive_threadd.start()

accep=True #EDVC dejamos que accep sea verdadero si content encontro al usuario y asi poder correr la aplicación


print("Bienvenido! " + str(content[0]))     #EDVC Damos la bienvenida al usuario



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
                print("Ingrese la duracion del mensaje (no mayor a 30 seg)") 
                dura=int(input())
                if(dura<=30.0): #EDVC si la duracion es menor permitimos que grabe
                    argu='arecord -d ' + str(dura) + ' -f U8 -r 8000 '+ AUDIO
                    os.system(argu)
                    if CRYPTO_ON: #EDVC si la encriptacion esta activada creamos un archivo llamado encripe que es el archivo de audio encriptado
                        t=open('encripe', 'wb')
                        f=open('subprocess1.wav', 'rb')
                        t.write(encri.encriptar(f.read()))
                        f.close()
                        t.close()
                        size = str(os.path.getsize(direccion+wavy_encrip)) #EDVC obtenemos el tamaño de este archivo nuevo
                    else: 
                        size = str(os.path.getsize(direccion+wavy))            
                    logging.info("\n Este audio es para una sala o alguien? 1=Sala 2=Alguien") #EDVC Una vez grabado el audio le pedimos al usuario que indique a quien es
                    elec=int(input())
                    if(elec==1):
                        logging.info("Estas son sus salas:")
                        logging.info(str(salas_usuario))
                        logging.info("Escriba la sala receptora ej(06S01):") #EDVC Si eligio una sala le pedimos que indique cual es
                        sal=str(input())
                        logging.info("Enviando solicitud al server FTR") 
                        
                        comunicacionCS(sala=sal,size=size)      #EDVC le enviamos a comunicacionCS la sala y el tamaño del archivo a enviar
               
                        
                    elif(elec==2):
                        logging.info("Escriba el carnet receptor:")     #EDVC Si eligio un carnet le pedimos que indique cual es
                        cardes=str(input())
                        comunicacionCS(usuario=cardes,size=size)    #EDVC le enviamos a comunicacionCS el usuario y el tamaño del archivo a enviar
                        
                else:
                    logging.info("No es posible enviar mas de 30seg!")  #EDVC si el usuario ingreso una duracion mayor a 30seg le decimos que no es posible hacer el envio
                
            elif(respu==2):
                logging.info("El mensaje es para una sala o alguien? 1=alguien 2=Sala") #EDVC Si el usuario quiere enviar un mensaje le indicamos si es para alguien o un sala
                res=int(input())
                if(res==1):
                    logging.info("Escriba el carnet del receptor:") #EDVC Si eligio un carnet le pedimos que indique cual es
                    carn=int(input())
                    logging.info("Escriba su mensaje: ") #EDVC luego le pedimos que ingrese el mensaje
                    men=str(input())
                    if CRYPTO_ON:                                   #EDVC si la encriptacion esta activada encriptaremos el mensaje de texto
                        men=encri.encriptar(men)
                    publishData(usuarioss+'/'+str(carn),men)        #EDVC Publicamos en el topic usuarioss + el carnet ingresado
                elif(res==2):
                    logging.info("Estas son sus salas:")            #EDVC Si eligio una sala le pedimos que indique cual es
                    logging.info(str(salas_usuario))
                    logging.info("Escriba la sala receptora ej(06S01):")
                    salaa=str(input())
                    if salaa in salas_usuario:                      #EDVC Si el usuario pertenece a la sala que ingrese permitimos que escriba el mensaje
                        logging.info("Escriba su mensaje: ")
                        men=str(input())
                        if CRYPTO_ON:
                            men=encri.encriptar(men)
                        publishData(salasss+'/'+str(salaa),men)     #EDVC Hacemos el publish a la sala indicada
                    else:
                        logging.info("Usted no esta suscrito a esta sala!") #EDVC Si no esta suscrito le indicamos al usuario
            elif(respu==3):
                break #EDVC Si el usuario indico que quiere salir hacemos break del while loop
           

    except KeyboardInterrupt:
        logging.warning("Desconectando del broker...") #EDVC Si ocurre un error desconectamos al usuario del servidor

    finally:
        client.loop_stop()          #EDVC cuando el usuario sale del while loop paramos el thread del cliente
        client.disconnect()         #EDVC lo desconetamos
        logging.info("Desconectado del broker. Saliendo...") #EDVC y le indicamos que salio
        break #EDVC finalmente salimos del while accep