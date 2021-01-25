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


pieces_size = 10000


#---------------------------------------------------------------------------------------
#Función como servidor de archivos en comunicación peer to peer (seeder)
class FileSharing(peer2peer_pb2_grpc.FileSharingServicer):
    def Request(self, request, context):
        first_byte = request.firstByte
        last_byte = request.lastByte
        file_name = request.fileName
        file_path = request.filePath

        pieces=''
        with open(file_path+file_name, 'rb') as file:
            pieces=file.read()

        return peer2peer_pb2.Response(response=pieces[first_byte:last_byte])

def serve(seeder_port):
    host_name = socket.gethostname()
    host_ip = socket.gethostbyname(host_name)
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    peer2peer_pb2_grpc.add_FileSharingServicer_to_server(FileSharing(), server)
    server.add_insecure_port(host_ip+':'+str(seeder_port))
    server.start()
    server.wait_for_termination()

#------------------------------------------------------------------------------------
#Función como cliente de archivos en comunicación peer to peer (lecher)
def conexion_peer_peer(seeder_port, seeders, torrent):

    file_name = torrent['name']
    file_path = torrent['filepath']
    amount_of_pieces = int(torrent['pieces'])
    last_piece_size = int(torrent['lastPiece'])
    tracker_port=int(torrent['puertoTracker'])
    tracker_ip=torrent['tracker']

    max_connections=5
    amount_of_bytes_received=0
    bytes_received=b''
    
    if amount_of_pieces==0 :
        #Pedir la última pieza truncada al último seeder
        print('Conectando con el peer: '+seeders[0]['seederIP']+':'+str(seeders[0]['seederPort']))
        with grpc.insecure_channel(seeders[0]['seederIP']+':'+str(seeders[0]['seederPort'])) as channel:
            stub = peer2peer_pb2_grpc.FileSharingStub(channel)
            data = stub.Request(
                peer2peer_pb2.RequestBytes(
                    firstByte = 0,
                    lastByte= last_piece_size-1,
                    fileName=file_name,
                    filePath=file_path
                )
            )
            bytes_received=data.response

        with open('Share/'+'rcv_'+file_name, 'wb') as file: #+filename
            file.write(bytes_received)

        print('Me estoy notificando como parte del enjambre para este archivo')
        host_name = socket.gethostname()
        host_ip = socket.gethostbyname(host_name)
        with grpc.insecure_channel(tracker_ip+':'+str(tracker_port)) as channel:
            stub = tracker_pb2_grpc.SwarmStub(channel)
            data = stub.AddToSwarm(
                tracker_pb2.SwarmNode(
                    fileName = file_name,
                    seederIP = host_ip,
                    seederPort = int(seeder_port)
                )
            )
            print(data)

    else:
        scheduled_connections=min(int(max_connections), len(seeders))
        pieces_to_receive_each_seeder=math.ceil(amount_of_pieces/scheduled_connections)
       
        #amount_pieces=57039
        #scheduled_connections=5
        #Pedir todas las piezas que están completas a diferentes seeders
        it=0
        last_seeder={}
        for i in range(0, scheduled_connections):
            
            desde=pieces_to_receive_each_seeder*it #0
            hasta=pieces_to_receive_each_seeder*(it+1)-1 #4

            #Conexiones con los peers,,,
            print('Conectando con el peer '+seeders[i]['seederIP']+':'+str(seeders[i]['seederPort']))
            with grpc.insecure_channel(seeders[i]['seederIP']+':'+str(seeders[i]['seederPort'])) as channel:
                stub = peer2peer_pb2_grpc.FileSharingStub(channel)
                data = stub.Request(
                    peer2peer_pb2.RequestBytes(
                        firstByte = desde*pieces_size, #0
                        lastByte= (min(hasta, amount_of_pieces-1)+1)*pieces_size-1,#49999    #Aquí es donde podría estar la falla que distorsiona el archivo
                        fileName=file_name,
                        filePath=file_path
                    )
                )
                
                amount_of_bytes_received+=len(data.response)
                
                bytes_received+=data.response
               

            
            it+=1
            last_seeder=i
        
        if last_piece_size!=0: #TRUE 7039
            #Pedir la última pieza truncada al último seeder
            print('Conectando con el peer '+seeders[last_seeder]['seederIP']+':'+str(seeders[last_seeder]['seederPort']))
            with grpc.insecure_channel(seeders[last_seeder]['seederIP']+':'+str(seeders[last_seeder]['seederPort'])) as channel:
                stub = peer2peer_pb2_grpc.FileSharingStub(channel)
                data = stub.Request(
                    peer2peer_pb2.RequestBytes(
                        firstByte = amount_of_pieces*pieces_size, #5*10000 = 50000
                        lastByte= amount_of_pieces*pieces_size+last_piece_size, #57039
                        fileName=file_name,
                        filePath=file_path
                    )
                )
                
                #print(data.response)
                amount_of_bytes_received+=len(data.response)
                
                bytes_received+=data.response
        print('Tamaño del archivo recibido: '+str(amount_of_bytes_received))
        


        with open('Share/'+'rcv_'+file_name, 'wb') as file: #+filename
            file.write(bytes_received)

        print('Me estoy notificando con el tracker como parte del enjambre para este archivo')
        host_name = socket.gethostname()
        host_ip = socket.gethostbyname(host_name)
        with grpc.insecure_channel(tracker_ip+':'+str(tracker_port)) as channel:
            stub = tracker_pb2_grpc.SwarmStub(channel)
            data = stub.AddToSwarm(
                tracker_pb2.SwarmNode(
                    fileName = file_name,
                    seederIP = host_ip,
                    seederPort = int(seeder_port)
                )
            )
            print(data)




#--------------------------------------------------------------------------------
#Funciones de usuario

#Obtenemos los datos del servidor y tracker para poder compartir nuestro
def compartir_archivo(seeder_port):
    file_path=input('Ingrese ruta del archivo: ')
    file_name=input('Ingrese nombre del archivo: ')
    webserver_ip=input('Ingrese IP del servidor web: ')
    tracker_ip=input('Ingrese IP del tracker: ')
    file=crear_torrent(file_name, file_path, tracker_ip) #Al parecer no hacemos uso de este file por el momento
    post_torrent_webserver(file_name,webserver_ip)
    anunciarse_tracker(tracker_ip,5000,file_name, seeder_port)

#En esta funcion se reciviran los campos del torrent para poder crearlo
def crear_torrent(file_name, file_path, tracker_ip):
    hasher = hashlib.md5(); #Para la verificacion de la integridad de los datos
    
    os.system('cls')
    with open(file_path+'\\'+file_name,"rb") as file:
        data = file.read()
        #name = file_name[0:file_name.rindex('.')];
        file_size = len(data)
        
        print(f"Tamaño del archivo: {file_size}")


        amount_of_pieces = int(math.ceil(file_size/pieces_size))
        last_piece_size = 0
        last_piece_index = 0

        #Para saber cuanto mide la ultima pieza de la division del archivo
        if amount_of_pieces * pieces_size > file_size:
            last_piece_size = file_size - (amount_of_pieces-1)*pieces_size
 
        checksum = []

        for i in range(0, amount_of_pieces-2):
            bytes_read = data[pieces_size*i : pieces_size*(i+1)-1]
            
            #El pedazo de datos pasa por nuestro objeto hasher
            hasher.update(bytes_read)
            checksum.append(hasher.hexdigest()) 
            last_piece_index = i
            
        bytes_read = data[pieces_size*last_piece_index : pieces_size*last_piece_index+last_piece_size]
        hasher.update(bytes_read)
        checksum.append(hasher.hexdigest())

    ids=str(uuid.uuid1())   #Para asignarle un id al torrent
    json_file=json.dumps({
        'pieces': amount_of_pieces-1, 
        'lastPiece': last_piece_size, 
        'filepath':file_path, 
        'tracker': tracker_ip, 
        'name':file_name, 
        'checksum': checksum, 
        'puertoTracker': 5000, 
        'id': ids
    })

    with open('TorrentsPeer//'+file_name+'.torrent', 'w') as file: #Creando el archivo .torrent 
        file.write(json_file)

    return file

#Compartiendo el arhivo .torrent con el servidor
def post_torrent_webserver(file_name, webserver_ip):
    with open('TorrentsPeer//'+file_name+'.torrent', 'r') as file:
        data=file.read()

    params=json.loads(data)
    r = requests.post('http://localhost:4000/torrent', data = params) #mandando los datos del torrent en formato JSON
    msg=r.json()
    r.status_code
    print('Publiqué el archivo en el servidor web.')

#Para anunciarnos al tracker   
def anunciarse_tracker(tracker_ip,tracker_port,file_name, seeder_port):
    host_name = socket.gethostname()
    host_ip = socket.gethostbyname(host_name)

    with grpc.insecure_channel(tracker_ip+':'+str(tracker_port)) as channel:
        stub = tracker_pb2_grpc.SwarmStub(channel)
        data = stub.CreateSwarm(
            tracker_pb2.SwarmNode(
                fileName = file_name,
                seederIP = host_ip,
                seederPort = int(seeder_port)
            )
        )
        print('Notifiqué al tracker del archivo compartido solicitando crear un enjambre.')



#Mandamos a buscar los archivos disponibles en el servidor y en el enjambre
def buscar_archivos(seeder_port):
    r = requests.get('http://localhost:4000/archivos', data={1: 'p'})
    msg=r.json()
    os.system('cls')
    print('Elija un archivo para descargar: ')

    for i,val in enumerate(msg):
        print(f"{i+1}:{val}")

    opt = int(input('Opcion: '))
    name_of_file_selected = msg[opt-1]
    print('Seleccionó el archivo: '+name_of_file_selected)
    r = requests.get('http://localhost:4000/torrent', params={'name':name_of_file_selected})
    
    host_name = socket.gethostname()
    host_ip = socket.gethostbyname(host_name)
    
    torrent = json.loads(r.text)
    tracker_ip = torrent['tracker']
    tracker_port = torrent['puertoTracker']
    file_name = torrent['name']
    torrent_id = torrent['id']
    amount_of_pieces = torrent['pieces']
    last_piece_size = torrent['lastPiece']


    print('Conectando con el tracker en '+ tracker_ip+':'+str(tracker_port)+' para solicitar el enjambre')

    swarm_data=[]
    with grpc.insecure_channel(tracker_ip+':'+str(tracker_port)) as channel:
        stub = tracker_pb2_grpc.SwarmStub(channel)
        data = stub.RequestSwarm(tracker_pb2.SwarmData(fileName = file_name,leecherIP = host_ip,leecherPort = 5000,id = torrent_id))
        print(data)
        swarm_data=json.loads(data.details)
    print('La información recibida desde el tracker fue: \n'+str(swarm_data))
    conexion_peer_peer(seeder_port, swarm_data['swarm'], torrent)

#Función de menú del usuario   
def usuario(seeder_port):

    while 1:
        print('¿Qué quieres hacer?')
        options={1:'Compartir archivo.', 2:'Buscar archivos para descargar'}
        functions=[compartir_archivo,buscar_archivos]

        for key, op in options.items(): #para mostrar el menu de el diccionario de
            print(f"[{key}] {op}" )
        opt=int(input('Opción: '))
        
        functions[opt-1](seeder_port)




#Programa principal
def main():
    seeder_port=input('Ingrese número de puerto: ')
    host_name = socket.gethostname()
    host_ip = socket.gethostbyname(host_name)
    print(host_ip+':'+str(seeder_port))
    t=threading.Thread(target=usuario,args=[seeder_port])
    t.start()
    serve(seeder_port)
    


main()





