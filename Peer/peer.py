import http.client 
import json
import os
from typing import Text
import requests #Para hacer peticiones al servidor
import uuid #Para generar un id para cada torrent
import math
import hashlib #Para la verificacion de los pedazos
import socket #Para obtenet la ip del host

import grpc #Para hacer la comunicion entre nodos
from concurrent import futures
import threading
import tracker_pb2_grpc
import tracker_pb2
import peer2peer_pb2_grpc
import peer2peer_pb2


Pieces_Size = 10000


#---------------------------------------------------------------------------------------
#Función como servidor de archivos en comunicación peer to peer (seeder)
class FileSharing(peer2peer_pb2_grpc.FileSharingServicer):
    def Request(self, request, context):
        firstByte = request.firstByte
        lastByte = request.lastByte
        fileName = request.fileName
        filePath = request.filePath

        pieces=''
        with open(filePath+fileName, 'rb') as file:
            pieces=file.read()

        return peer2peer_pb2.Response(response=pieces[firstByte:lastByte])

def serve(seederPort):
    hostName = socket.gethostname()
    hostIP = socket.gethostbyname(hostName)
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    peer2peer_pb2_grpc.add_FileSharingServicer_to_server(FileSharing(), server)
    server.add_insecure_port(hostIP+':'+str(seederPort)) #Se va a tener que cambiar el puerto, debido a que lo vamos a trabajar en puto localhost
    server.start()
    server.wait_for_termination()

#------------------------------------------------------------------------------------
#Función como cliente de archivos en comunicación peer to peer (lecher)
def conexion_peer_peer(lista, torrent):
    numero_conexiones=5
    
    fileName = torrent['name']
    pieces = int(torrent['pieces'])
    lastPieceSize = int(torrent['lastPiece'])
    filePath = torrent['filepath']
    receivedSize=0
    receivedData=''
    receivedDataBytes=b''
    
    if pieces==0 :
        #Pedir la última pieza truncada al último seeder
        with grpc.insecure_channel(lista[0]['seederIP']+':'+str(lista[0]['seederPort'])) as channel:
            stub = peer2peer_pb2_grpc.FileSharingStub(channel)
            details = stub.Request(
                peer2peer_pb2.RequestBytes(
                    firstByte = 0,
                    lastByte= lastPieceSize-1,
                    fileName=fileName,
                    filePath=filePath
                )
            )
            print(details)
        #Hacer una sola conexión
    else:
        minimo=min(int(numero_conexiones), len(lista))
        long=math.ceil(pieces/minimo)
       
        
        #Pedir todas las piezas que están completas a diferentes seeders
        it=0
        last_seeder={}
        for i in range(0, minimo):
            print('Itera')
            desde=long*it
            hasta=long*(it+1)-1

            #Conexiones con los peers,,,
            print(lista[i]['seederIP']+':'+str(lista[i]['seederPort']))
            with grpc.insecure_channel(lista[i]['seederIP']+':'+str(lista[i]['seederPort'])) as channel:
                stub = peer2peer_pb2_grpc.FileSharingStub(channel)
                details = stub.Request(
                    peer2peer_pb2.RequestBytes(
                        firstByte = desde*Pieces_Size,
                        lastByte= (min(hasta, pieces-1)+1)*Pieces_Size-1,
                        fileName=fileName,
                        filePath=filePath
                    )
                )
                print(details.response)
                receivedSize+=len(details.response)
                receivedData+=str(details.response)
                receivedDataBytes+=details.response
                print('Pasamos por 92')

            #print(i)
            print('Pasamos por 95')
            it+=1
            last_seeder=i
        
        if lastPieceSize!=0:
            #Pedir la última pieza truncada al último seeder
            print('Pasamos por 101')
            with grpc.insecure_channel(lista[last_seeder]['seederIP']+':'+str(lista[last_seeder]['seederPort'])) as channel:
                stub = peer2peer_pb2_grpc.FileSharingStub(channel)
                details = stub.Request(
                    peer2peer_pb2.RequestBytes(
                        firstByte = pieces*Pieces_Size,
                        lastByte= pieces*Pieces_Size+lastPieceSize,
                        fileName=fileName,
                        filePath=filePath
                    )
                )
                print('Pasamos por 112')
                print(details.response)
                receivedSize+=len(details.response)
                receivedData+=str(details.response)
                receivedDataBytes+=details.response
            print('Afuera del ultimo request')
        print('Tamaño del archivo recibido: '+str(receivedSize))
        print(receivedData)
        with open('Share/MeshReceived.jpg', 'wb') as file: #+filename
            file.write(receivedDataBytes)



#--------------------------------------------------------------------------------
#Funciones de usuario

#Obtenemos los datos del servidor y tracker para poder compartir nuestro
def compartir_archivo(seederPort):
    filepath=input('Ingrese ruta del archivo: ')
    filename=input('Ingrese nombre del archivo: ')
    webserver_ip=input('Ingrese IP del servidor web: ')
    tracker_ip=input('Ingrese IP del tracker: ')
    file=crear_torrent(filename, filepath, tracker_ip) #Al parecer no hacemos uso de este file por el momento
    post_torrent_webserver(filename,webserver_ip)
    anunciarse_tracker(tracker_ip,5000,filename, seederPort)

#En esta funcion se reciviran los campos del torrent para poder crearlo
def crear_torrent(filename, filepath, tracker_ip):
    
    Max_Request = 10;
    #Para la verificacion de la integridad de los datos
    hasher = hashlib.md5();
    
    os.system('cls')
    with open(filepath+'\\'+filename,"rb") as f:
        file = f.read()
        name = filename[0:filename.rindex('.')];
        fileSize = len(file)
        print(file)
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

    with open('TorrentsPeer//'+filename+'.torrent', 'w') as file: #Creando el archivo .torrent 
        file.write(jsonfile)

    return file

#Compartiendo el arhivo .torrent con el servidor
def post_torrent_webserver(filename, webserver_ip):
    with open('TorrentsPeer//'+filename+'.torrent', 'r') as file:
        filecontent=file.read()

    params=json.loads(filecontent)
    r = requests.post('http://localhost:4000/torrent', data = params) #mandando los datos del torrent en formato JSON
    msg=r.json()
    print(msg['Recibi']['checksum']) #Imprimimos el subobjeto checksum de la respues del servidor
    r.status_code

#Para anunciarnos al tracker   
def anunciarse_tracker(trackerIP,pTracker,fileName, seederPort):
    hostName = socket.gethostname()
    hostIP = socket.gethostbyname(hostName)


    with grpc.insecure_channel(trackerIP+':'+str(pTracker)) as channel:
        stub = tracker_pb2_grpc.SwarmStub(channel)
        details = stub.CreateSwarm(tracker_pb2.SwarmNode(fileName = fileName,seederIP = hostIP,seederPort = int(seederPort)))
        print(details)



#Mandamos a buscar los archivos disponibles en el servidor y en el enjambre
def buscar_archivos(seederPort):
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
    
    hostName = socket.gethostname()
    hostIP = socket.gethostbyname(hostName)
    
    torrent = json.loads(r.text)
    trackerIP = torrent['tracker']
    puertoTrakcer = torrent['puertoTracker']
    fileName = torrent['name']
    idTorrent = torrent['id']
    pieces = torrent['pieces']
    lastPiece = torrent['lastPiece']


    print(trackerIP,puertoTrakcer)

    swarm_data=[]
    with grpc.insecure_channel(trackerIP+':'+str(puertoTrakcer)) as channel:
        stub = tracker_pb2_grpc.SwarmStub(channel)
        request = stub.RequestSwarm(tracker_pb2.SwarmData(fileName = fileName,leecherIP = hostIP,leecherPort = 5000,id = idTorrent))
        print(request)
        swarm_data=json.loads(request.details)
    print(swarm_data)
    conexion_peer_peer(swarm_data['swarm'], torrent)
    
def usuario(seederPort):

    while 1:
        print('¿Qué quieres hacer?')
        opciones={1:'Compartir archivo.', 2:'Buscar archivos para descargar'}
        funciones=[compartir_archivo,buscar_archivos]

        for key, op in opciones.items(): #para mostrar el menu de el diccionario de
            print(f"[{key}] {op}" )
        opt=int(input('Opción: '))
        
        funciones[opt-1](seederPort)




#Programa principal
def main():
    seederPort=input('Ingrese número de puerto: ')
    hostName = socket.gethostname()
    hostIP = socket.gethostbyname(hostName)
    print(hostIP+':'+str(seederPort))
    t=threading.Thread(target=usuario,args=[seederPort])
    t.start()
    serve(seederPort)
    

    


main()





