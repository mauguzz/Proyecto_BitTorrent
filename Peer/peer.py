import http.client 
import json
from typing import Text
import requests #Para hacer peticiones al servidor
import uuid #Para generar un id para cada torrent
import math
import hashlib #Para la verificacion de los pedazos
import socket #Para obtenet la ip del host

import grpc #Para hacer la comunicion entre nodos
import tracker_pb2_grpc
import tracker_pb2

#Obtenemos los datos del servidor y tracker para poder compartir nuestro
def compartir_archivo():
    filepath=input('Ingrese ruta del archivo: ')
    filename=input('Ingrese nombre del archivo: ')
    webserver_ip=input('Ingrese IP del servidor web: ')
    tracker_ip=input('Ingrese IP del tracker: ')
    file=crear_torrent(filename, filepath, tracker_ip) #Al parecer no hacemos uso de este file por el momento
    post_torrent_webserver(filename,webserver_ip)
    anunciarse_tracker(tracker_ip,5000,filename)

#En esta funcion se reciviran los campos del torrent para poder crearlo
def crear_torrent(filename, filepath, tracker_ip):
    Pieces_Size = 10000;
    Max_Request = 10;
    #Para la verificacion de la integridad de los datos
    hasher = hashlib.md5();

    with open(filepath+'\\'+filename,"rb") as f:
        file = f.read()
        name = filename[0:filename.rindex('.')];
        fileSize = len(file)
        print(f"Tamaño del archivo: {fileSize}")
        Pieces_Qty = int(math.ceil(fileSize/Pieces_Size))

        lastpiece = 0;
        indice = 0;

        #Para saber cuanto mide la ultima pieza de la division del archivo
        if Pieces_Qty * Pieces_Size > fileSize:
            lastpiece = fileSize - (Pieces_Qty-1)*Pieces_Size
 
        checksum = []

        for i in range(0,Pieces_Qty-2):
            data = file[Pieces_Size*i:Pieces_Size*(i+1)-1]
            
            #El pedazo de datos pasa por nuestro objeto hasher
            hasher.update(data)
            checksum.append(hasher.hexdigest()) 
            indice = i;
            
        data = file[Pieces_Size*indice:Pieces_Size*indice+lastpiece]
        hasher.update(data)
        checksum.append(hasher.hexdigest())

    ids=str(uuid.uuid1())   #Para asignarle un id al torrent
    jsonfile=json.dumps({
        'pieces': Pieces_Qty-1, 
        'lastPiece': lastpiece, 
        'filepath':filepath, 
        'tracker': tracker_ip, 
        'name':filename, 
        'checksum': checksum, 
        'puertoTracker': 5000, 
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
    r = requests.post('http://localhost:4000/torrent', data = params) #mandando los datos del torrent en formato JSON
    msg=r.json()
    print(msg['Recibi']['checksum']) #Imprimimos el subobjeto checksum de la respues del servidor
    r.status_code

#Para anunciarnos al tracker   
def anunciarse_tracker(trackerIP,pTracker,fileName):

    hostIP = socket.gethostname()

    with grpc.insecure_channel(trackerIP+':'+str(pTracker)) as channel:
        stub = tracker_pb2_grpc.SwarmStub(channel)
        details = stub.CreateSwarm(tracker_pb2.SwarmNode(fileName = fileName,seederIP = hostIP,seederPort = 5500))
        print(details)

#Mandamos a buscar los archivos disponibles en el servidor y en el enjambre
def buscar_archivos():
    r = requests.get('http://localhost:4000/archivos', data={1: 'p'})
    msg=r.json()
    print(msg[0])
    print('Elija un archivo para descargar: ')

    for i,val in enumerate(msg):
        print(f"{i+1}:{val}")
    opc = int(input('Opcion: '))
    nombre = msg[opc-1]
    print(nombre)
    r = requests.get('http://localhost:4000/torrent', params={'name':nombre})
    hostIP = socket.gethostname()
    
    torrent = json.loads(r.text)
    trackerIP = torrent['tracker']
    puertoTrakcer = torrent['puertoTracker']
    fileName = torrent['name']
    id = torrent['id']

    print(trackerIP,puertoTrakcer)

    with grpc.insecure_channel(trackerIP+':'+str(puertoTrakcer)) as channel:
        stub = tracker_pb2_grpc.SwarmStub(channel)
        request = stub.RequestSwarm(tracker_pb2.SwarmData(fileName = fileName,leecherIP = hostIP,leecherPort = str(5000),id = id))
        print(request)

#Programa principal
def main():
    print('¿Qué quieres hacer?')
    opciones={1:'Compartir archivo.', 2:'Buscar archivos para descargar'}
    funciones=[compartir_archivo,buscar_archivos]

    for key, op in opciones.items(): #para mostrar el menu de el diccionario de
        print(f"[{key}] {op}" )
    opt=int(input('Opción: '))
    
    funciones[opt-1]()

main()





