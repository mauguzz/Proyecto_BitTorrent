import http.client
import json
from typing import Text
import requests
import uuid
import math
import hashlib #Para la verificacion de los pedazos 

#En esta funcion se reciviran los campos del torrent para poder crearlo
def crear_torrent(filename, filepath, tracker_ip):
    Pieces_Size = 1024;
    Max_Request = 10;
    #Para la verificacion de la integridad de los datos
    hasher = hashlib.md5();

    with open(filepath+'\\'+filename,"rb") as f:
        file = f.read()
        name = filename[0:filename.rindex('.')];
        fileSize = len(file)
        print(f"Tamaño del archivo: {fileSize}")

        #Hay un pequeño error, muestra una piezaz mas de las que deberian ser
        #Por ejemplo, se fragmento un archivo de 382 bytes y con un tamaño por pieza de 10 
        #pero salio 39 piezas con un tamaño de ultima pieza de 2 bytes
        Pieces_Qty = int(math.ceil(fileSize/Pieces_Size))

        lastpiece = 0;
        indice = 0;

        #Para saber cuanto mide la ultima pieza de la division del archivo
        if Pieces_Qty * Pieces_Size > fileSize:
            lastpiece = fileSize - (Pieces_Qty-1)*Pieces_Size

        checksum = []

        for i in range(0,Pieces_Qty-1):
            data = file[Pieces_Size*i:Pieces_Size*(i+1)-1]
            #El pedazo de datos pasa por nuestro objeto hasher
            hasher.update(data)
            checksum.append(hasher.hexdigest()) 
            indice = i;
            
        data = file[Pieces_Size*indice:Pieces_Size*indice+lastpiece]
        hasher.update(data)
        checksum.append(hasher.hexdigest())
        
        for i in checksum:
            print(f"[{i}]")

    ids=str(uuid.uuid1())   #Para asignarle un id al torrent
    jsonfile=json.dumps({
        'pieces': Pieces_Qty, 
        'lastPiece': lastpiece, 
        'filepath':filepath, 
        'tracker': tracker_ip, 
        'name':filename, 
        'checksum': checksum, 
        'puertoTracker': 6000, 
        'id': ids
    })

    with open(filename+'.torrent', 'w') as file: #Creando el archivo .torrent 
        file.write(jsonfile)

    return file

#Compartiendo el arhivo .torrent con el servidor
def post_torrent_webserver(filename, webserver_ip):

    with open(filename+'.torrent', 'r') as file:
        filecontent=file.read()

    params=json.loads(filecontent)
    r = requests.post('http://localhost:5000/torrent', data = params) #mandando los datos del torrent en formato JSON
    msg=r.json()
    print(msg['Recibi']['checksum']) #Imprimimos el subobjeto checksum de la respues del servidor
    r.status_code

#Obtenemos los datos del servidor y tracker para poder compartir nuestro
def compartir_archivo():
    filepath=input('Ingrese ruta del archivo: ')
    filename=input('Ingrese nombre del archivo: ')
    webserver_ip=input('Ingrese IP del servidor web: ')
    tracker_ip=input('Ingrese IP del tracker: ')
    file=crear_torrent(filename, filepath, tracker_ip) #Al parecer no hacemos uso de este file por el momento
    post_torrent_webserver(filename,webserver_ip)

#Mandamos a buscar los archivos disponibles en el servidor y en el enjambre
def buscar_archivos():
    r = requests.get('http://localhost:5000/archivos', data={1: 'p'})
    msg=r.json()
    print(msg)
    r.status_code

def main():
    print('¿Qué quieres hacer?')
    opciones={1:'Compartir archivo.', 2:'Buscar archivos para descargar'}
    
    for key, op in opciones.items(): #para mostrar el menu de el diccionario de
        print(f"[{key}] {op}" )
    opt=int(input('Opción: '))
    
    compartir_archivo()
    buscar_archivos()

main()





