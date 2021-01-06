import http.client
import json
<<<<<<< HEAD
import requests # python -m pip install requests
 
 datos = '''
 {
     "people": [
         {
             "name":"John",
             "phone":"555"
         },
         {
             "name":"Mathias",
             "phone":"566"
         }
     ]
 }
 '''
data = json.load(datos)
r = requests.post('http://localhost:5000/torrent', data)
r.status_code
=======
from typing import Text
import requests
import uuid


def crear_torrent(filename, filepath, tracker_ip):
    ids=str(uuid.uuid1())
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
    with open(filename+'.torrent', 'w') as file:
        file.write(jsonfile)
    return file

def post_torrent_webserver(filename, webserver_ip):

    with open(filename+'.torrent', 'r') as file:
        filecontent=file.read()

    params=json.loads(filecontent)
    print(params)
    r = requests.post('http://localhost:5000/torrent', data = params)
    msg=r.json()
    print(msg['Recibi']['checksum'])
    r.status_code

def compartir_archivo():
    filepath=input('Ingrese ruta del archivo: ')
    filename=input('Ingrese nombre del archivo: ')
    webserver_ip=input('Ingrese IP del servidor web: ')
    tracker_ip=input('Ingrese IP del tracker: ')
    file=crear_torrent(filename, filepath, tracker_ip)
    post_torrent_webserver(filename,webserver_ip)

    
def buscar_archivos():
    r = requests.get('http://localhost:5000/archivos', data={1: 'p'})
    msg=r.json()
    print(msg)
    r.status_code

def main():
    print('¿Qué quieres hacer?')
    opciones={1:'Compartir archivo.', 2:'Buscar archivos para descargar'}
    
    for key, op in opciones.items():
        print(f"[{key}] {op}" )
    opt=int(input('Opción: '))
    compartir_archivo()
    buscar_archivos()

main()

# params=json.loads(json.dumps({'Verdadero? ': 'Si', 'Falso': 'No', 'checksumm': ('fsf234234', 'dfg45f34t')}))

# print(params)

# r = requests.post('http://localhost:5000/torrent', data = params)

# msg=r.json()
# print(msg['Recibi']['checksumm'])




#r.status_code
>>>>>>> 682aec387b9262808a6754c5a01f2a31b2590b9c
