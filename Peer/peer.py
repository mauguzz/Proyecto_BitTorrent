import http.client
import json
from typing import Text
import requests
import uuid
import math

#En esta funcion se reciviran los campos del torrent para poder crearlo
def crear_torrent(filename, filepath, tracker_ip):
    Pieces_Size = 10;
    Max_Request = 10;

    with open(filepath+'\\'+filename,"rb") as f:
        file = f.read()
        name = filename[0:filename.rindex('.')];
        fileSize = len(file)
        print(fileSize)
        Pieces_Qty = int(math.ceil(fileSize/Pieces_Size))
        lastpiece = 0;
        indice = 0;
        if Pieces_Qty * Pieces_Size > fileSize:
            lastpiece = fileSize - (Pieces_Qty-1)*Pieces_Size
        checksum = []
        print(Pieces_Qty)
        for i in range(0,Pieces_Qty-1):
            print(i)
            data = file[Pieces_Size*i:Pieces_Size*(i+1)-1]
            checksum.append(hash(data)) 
            print(data)
            indice = i;

        data = file[Pieces_Size*indice:Pieces_Size*indice+lastpiece]
        checksum.append(hash(data))
        print(data)
        
        for i in checksum:
            print(i)

    ids=str(uuid.uuid1())   #Para asignarle un id al torrent
    jsonfile=json.dumps({
        'pieces': 10, 
        'lastPiece': 10, 
        'filepath':filepath, 
        'tracker': tracker_ip, 
        'name':filename, 
        'checksum': ['edfefsdf', 'rtheget343tdf'], 
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
    print(params)
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





