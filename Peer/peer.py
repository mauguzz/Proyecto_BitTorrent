import http.client
import json
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
