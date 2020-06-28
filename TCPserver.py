import socket
import os
import logging
from TCPserverData import *
from globals import *

logging.basicConfig(
    level = logging.DEBUG, 
    format = '[%(levelname)s] (%(threadName)-10s) %(message)s'
    )
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((SERVER_ADDR, SERVER_PORT))
server_socket.listen(10) #1 conexion activa y 9 en cola
class tcp_server(object):

    def __init__(self):
        pass        
    
    def receive(self, peso):    #Recibir un archivo
        logging.debug("Esperando Conexion remota para iniciar la recepcion")
        conn, addr = server_socket.accept()
        try:
            self.peso = int(peso)
            peso_actual=b''
            f = open(AUDIO_FILE,'wb')
            while len(peso_actual) < self.peso:   #lee el bufer hasta que el tamaño del archivo sea el especificado
                l = conn.recv(BUFFER_SIZE)
                peso_actual+=l                    #Guarda en una variable los datos del buffer   
            f.write(peso_actual)                  #Escribe en el buffer los datos recividos
            f.close()
            logging.info("Archivo recibido con exito")
        except:
            logging.info("No se pudo recibir archivo")
        finally:
            conn.close() #Se cierra el socket    

    def transf(self, dest):     #transferencia de archivo
        self.dest = dest
        try:
            logging.debug("Esperando Conexion remota para iniciar la transmision")
            conn, addr = server_socket.accept()
            with open(AUDIO_FILE, 'rb') as f: #Se abre el archivo a enviar en BINARIO
                conn.sendfile(f, 0)
                f.close()
            logging.info("Archivo enviado a " + self.dest)
        except:
            logging.info("No se puedo enviar el archivo a " + self.dest)
        finally:
            #logging.debug("cerrando coneccion")
            conn.close() #Se cierra el socket