import threading 
import logging
import os

AUDIO_RECIBIDO = 'recibido.wav'

logging.basicConfig(
    level = logging.INFO, 
    format = '%(message)s'
    )

#JMOC Esta función será lanzada en un hilo para repodrucir el audio

class topic(object):
    def __init__(self):
        pass

    

 
    def rep_audio(self, remit):        #JMOC Metodo para reproducir mensajes
        logging.info("Entro a rep_audio")
        self.remit = remit
        logging.info(self.remit+" envio un audio")
        os.system('aplay ' + AUDIO_RECIBIDO) #JMOC Reproducir mensaje

    def chat(self, inf_tipo, inf_remit, mensg):   #JMOC Se encarga de la lectura de mensajes
        self.inf_tipo = inf_tipo
        self.inf_remit = inf_remit
        self.mensg = mensg
        
        m=''                        #JMOC Guarda el mensaje a retornar
        if self.inf_tipo == "usuarios":    #JMOC El remitente es un usuario
            m = "Mensaje para " + self.inf_remit + ": " + self.mensg.decode()
        
        if self.inf_tipo == "salas":    #JMOC El remitente es una sala
            m = "Mensaje de " + self.inf_remit + ": " + self.mensg.decode()
        return m

    def __str__(self):     #JOMOC Sobrecarga str
        return 'Manejo de mensajes'

    def __repr__(self):   #JOMOC Sobrecarga repr
        return self.__str__()