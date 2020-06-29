from globals import * #CFLN Variables globales del programa

#JMOC Clase realizar la subscripcion a los distintos topics
class usuario(object):
    def __init__(self, user, user_name, rooms=[]): #JMOC El constructor se inicializa con los datos del usuario y se subscribe a los topics
        self.user = user
        self.user_name = user_name
        self.rooms = rooms

    def getuser(self):    #JMOC Devuelve el usuario 
        return self.user

    def getusername(self):  #JMOC Devuelve el nombre de usuario
        return self.user_name

    def getrooms(self):        #JMOC Devuelve las salas a las que pertenece el usuario 
        return self.rooms

    def __str__(self):
        return self.user + " " + self.user_name     #JMOC str devuelve el usuario y combre de usuario

    def __repr__(self):
        return self.__str__()       #JMOC devuelve el usuario y el nombre de usuario

#JMOC Verifica si una sala es valida
def sala_valida(salav):
    f = open(ROOMS, "r")        #JMOC abre el archivo de salas en modo lectura
    lineas = f.readlines()         #JMOC guarda las lineas del archivo de usuarios
    f.close()                       #JMOC cierra el archivo
    valid_room = False              #JMOC Variable que indica si la sala es valida
    for i in lineas:
        i=i.replace('\n','')          #JMOC Elimina los caracteres de salto de las lineas
        if salav == i:
            valid_room = True       #JMOC La sala es valida porque se encuentra en el archvio salas
    return valid_room

#JMOC Verifica si un usuario es valido 
def usuario_valido(usu,ava_usuarios):
    valid_user = False                  #JMOC Variable que indica si un usuario es valido
    for i in ava_usuarios:              #JMOC recorre la lista de objetos usuario
        if usu == i.getuser():    
            valid_user = True             #preguntar si el usuario esta en linea
    return valid_user

#JMOC Verifica si un grupo de usuarios es valido 
def usuarios_validos(user_origen,mul_usu,ava_usuarios):
    valid_user = False                  #JMOC Variable que indica si un usuario es valido
    for i in ava_usuarios:              #JMOC recorre la lista de objetos usuario
        valid_user = False
        for j in mul_usu:
            if j == i.getuser():    
                valid_user = True         
        if (valid_user==False) and (i.getuser()!=user_origen):            #JMOC Si un usuario de destinatario no esta en la lista del archivo usuarios no se realizara la operacion
            break
        #preguntar si el usuario esta en linea
    return valid_user

#JMOC Verifica si la sala esta vacia
#CFLN nosala = sala por la cual se desea consultar
#CFLN user_origen = usuario que esta haceindo la peticion a la sala
#CFLN salas_usus = lista que contiene objetos del tipo usuario (contiene informacion de las salas a las que pertenece cada usuario)
#CFLN lista_online = lista de usuarios conectados
def sala_vacia(nosala,user_origen,salas_usus, lista_online):
    sa_state = False
    for i in salas_usus:
        for j in i.getrooms():
            if (i.getuser() != user_origen) and j == nosala:     
                if online(usu_on, lista_online):
                    sa_state = True                                      #preguntar si esta en linea
    return  sa_state

#JMOC Verifica si el remitente de un mensaje es valido
def remite_valido(remit, valid_remit):
    state = False
    for i in valid_remit:
        if remit == i.getuser():
            state = True                
    return state

#CFLN Verifica si un usuario esta en linea
def online(usu_on, lista_online):
    #CFLN usu_on = usuario que se desea saber si esta en linea
    #CFLN lista_online = lista de usuarios que estan en linea
    li=False
    for i in lista_online:
        if usu_on in i[0]:
            li=True
    return li
