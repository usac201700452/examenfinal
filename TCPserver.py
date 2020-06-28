import socket
import os
import logging
from TCPserverData import *
from globals import AUDIO_FILE

logging.basicConfig(
    level = logging.DEBUG, 
    format = '[%(levelname)s] (%(threadName)-10s) %(message)s'
    )
#CFLN Configuracion inicial del socker tcp  
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((SERVER_ADDR, SERVER_PORT))
server_socket.listen(10) #CFLN 1 conexion activa y 9 en cola

#CFLN Clase para manejo de servidor TCP
class tcp_server(object):

    def __init__(self):
        pass        
    
    #CFLN Metodo para recibir archivos utilizando su peso
    def receive(self, peso):    
        logging.debug("Esperando Conexion remota para iniciar la recepcion")
        conn, addr = server_socket.accept()
        try:
            self.peso = int(peso)                   #CFLN Se convierte el peso a entero
            peso_actual=b''                         #CFLN Variable de control para saber si ya se han recibido todos los datos
            f = open(AUDIO_FILE,'wb')
            while len(peso_actual) < self.peso:     #CFLN Lee el buffer hasta que el tamaño del archivo sea el especificado por el peso
                l = conn.recv(BUFFER_SIZE)          #CFLN Se estan almacenando los datos del buffer en una variable
                peso_actual+=l                      #CFLN Cada dato que se recibe se añade a la variable de control para ser comparada nuevamente
            f.write(peso_actual)                    #CFLN Una vez se reciben todos los datos del buffer se escribe en el archivo los datos recibidos
            f.close()
            logging.info("Archivo recibido con exito")
        except:                                     #CFLN Si no se logra hacer la transferencia, se notifica el fallo
            logging.info("No se pudo recibir archivo")
        finally:
            conn.close()    #CFLN Una vez se realizaron todas las operaciones, se cierra el socket

    #CFLN Metodo para tranferencia de archivos
    def transf(self, dest):     
        self.dest = dest                #CFLN Destinatario del archivo
        try:
            logging.debug("Esperando Conexion remota para iniciar la transmision")
            conn, addr = server_socket.accept()
            with open(AUDIO_FILE, 'rb') as f:       #CFLN Se abre el archivo a enviar en BINARIO
                conn.sendfile(f, 0)                 #CFLN Se envia por el socket el archivo completo
                f.close()                           #CFLN No es necesario controlar el tamaño del archivo enviado ya que esto se realiza en la recepcion
            logging.info("Archivo enviado a " + self.dest)      #CFLN Se notifica del envio exitoso al destino
        except:
            logging.info("No se puedo enviar el archivo a " + self.dest)        #CFLN Se notifica del fallo y el detinatario
        finally:
            conn.close()    #CFLN Una vez se realizaron todas las operaciones, se cierra el socket