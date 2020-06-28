import hashlib
import math
import os
from Crypto.Cipher import AES

class EncriptarMensaje(object):
    
    def __init__(self):
        pass

    def __str__(self):
        return 'Encriptar mensajes'

    def __repr__(self):
        return self.__str__()

    def encriptar(self,mensaje):
        
        self.mensaje = mensaje

        IV_SIZE = 16 # 128 bit
        KEY_SIZE = 32 # 256 bit
        SALT_SIZE = 16 # Tamaño arbitrario
        password = b'contrasenia altamente segura'       

        cleartext = mensaje.encode()        
        
        salt = os.urandom(SALT_SIZE)
        derived = hashlib.pbkdf2_hmac('sha256', password, salt, 100000, dklen=IV_SIZE+KEY_SIZE)

        iv = derived[0:IV_SIZE]
        key = derived[IV_SIZE:]

        encriptado = salt + AES.new(key, AES.MODE_CFB, iv).encrypt(cleartext)

        return encriptado

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
