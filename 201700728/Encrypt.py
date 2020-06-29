import hashlib
import math
import os
from Crypto.Cipher import AES

#CFLN Manejo de encriptado/desencriptado por medio de una clase
class EncriptarMensaje(object):
    
    def __init__(self):
        pass

    def __str__(self):
        return 'Encriptacion/Desencriptacion de mensajes'

    def __repr__(self):
        return self.__str__()

    #CFLN Metodo para encriptar mensajes mediante generacion
    #del algoritmo hash sha256 y mediante el uso de AES
    #y una contraseña convertida a binario.
    def encriptar(self,mensaje):
        
        self.mensaje = mensaje

        IV_SIZE = 16 # 128 bit
        KEY_SIZE = 32 # 256 bit
        SALT_SIZE = 16 # Tamaño arbitrario
        password = b'contrasenia altamente segura'       

        if type(mensaje)!=bytes:                #CFLN si el mensaje no es binario se convierte
            cleartext = mensaje.encode()
        else:                                   #CFLN si el mensaje ya es binario simplemente se toma su valor
            cleartext = mensaje
        
        salt = os.urandom(SALT_SIZE)
        derived = hashlib.pbkdf2_hmac('sha256', password, salt, 100000, dklen=IV_SIZE+KEY_SIZE)

        iv = derived[0:IV_SIZE]
        key = derived[IV_SIZE:]

        encriptado = salt + AES.new(key, AES.MODE_CFB, iv).encrypt(cleartext)

        return encriptado           
        #CFLN El mensaje encritado se devuelve en hexadecimal binario

    #CFLN Metodo para desencriptar el mensaje que se recibe en binario
    #utilizando el algoritmo de hash sha256 y el uso de AES
    def desencriptar(self, mensaje_enc):
        self. mensaje_enc = mensaje_enc

        IV_SIZE = 16 # 128 bit
        KEY_SIZE = 32 # 256 bit
        SALT_SIZE = 16 # Tamaño arbitrario  
        password = b'contrasenia altamente segura'  

        salt = mensaje_enc[0:SALT_SIZE]
        derived = hashlib.pbkdf2_hmac('sha256', password, salt, 100000, dklen=IV_SIZE + KEY_SIZE)

        iv = derived[0:IV_SIZE]
        key = derived[IV_SIZE:]

        desencriptado = AES.new(key, AES.MODE_CFB, iv).decrypt(mensaje_enc[SALT_SIZE:])

        return desencriptado
        #El mensaje encriptado se devuelve en string binario