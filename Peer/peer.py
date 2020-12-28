import http.client
import json
from typing import Text
import requests

mensaje = json.dumps([None, True, False, 'Hola, mundo!'])
'[null, true, false, "Hola, mundo!"]'
r = requests.post('http://localhost:5000/torrent', data = mensaje)
r.status_code