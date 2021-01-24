#El tracker se encargara agregar nodos a una lista enjmabre
import json
import tracker_pb2_grpc
import tracker_pb2
import grpc
from concurrent import futures
import os.path

#En esta parte definimos el manejador de las funciones del 
class Swarm(tracker_pb2_grpc.SwarmServicer):
    
    file = 'Swarms.upiita'
    def CreateSwarm(self, request, context):
        fileName = request.fileName
        seederIP = request.seederIP
        seederPort = request.seederPort
        
        Swarm = {
            'fileName':fileName,
            'swarm':[{'seederIP': seederIP, 'seederPort': seederPort}]
        }
        if (os.path.isfile(self.file)):
            with open(self.file,'a') as SwarmFile:
                SwarmFile.write('/|->'+json.dumps(Swarm))
        else:
            with open(self.file,'w') as SwarmFile:
                SwarmFile.write(json.dumps(Swarm))
            
        return tracker_pb2.Status(details = json.dumps(Swarm))
    
    def RequestSwarm(self,request,context):
        fileName = request.fileName
        leecherIP = request.leecherIP
        id = request.id
        swarms = []
        

        with open(self.file,'r') as file:
            fileContent = file.read()
            splits = fileContent.split('/|->')
            for i in splits:
                swarms.append(json.loads(i))
        swarm = ""
        for i in swarms:
            if i['fileName'] == fileName:
                swarm = json.dumps(i)

        return tracker_pb2.Status(details = swarm)
       
    def AddToSwarm(self,request,context):
        fileName = request.fileName
        seederIP = request.seederIP
        seederPort = request.seederPort

        return tracker_pb2.Status(details = "hola")

def serve():
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=20))
        tracker_pb2_grpc.add_SwarmServicer_to_server(Swarm(),server)
        server.add_insecure_port('localhost:5000')
        server.start()
        server.wait_for_termination()

if __name__ == "__main__":
    print(f"Running tracker on port: 5000")
    serve()
