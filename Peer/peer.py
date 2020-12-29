import http.client
import json
from typing import Text
import requests




params=json.loads(json.dumps({'Verdadero? ': 'Si', 'Falso': 'No', 'checksumm': ('fsf234234', 'dfg45f34t')}))

print(params)

r = requests.post('http://localhost:5000/torrent', data = params)
r.status_code