import json
import tracker_pb2_grpc
import tracker_pb2
import grpc
from concurrent import futures


class Swarm(tracker_pb2_grpc.SwarmServicer):
    
    def CreateSwarm(self, request, context):
        fileName = request.fileName
        seederIP = request.seederIP
        seederPort = request.seederPort
        Swarm = {
            'fileName':fileName,
            'swarm':[{'seederIP': seederIP, 'seederPort': seederPort}]
        }
        with open('Swarms.json','a') as SwarmFile:
            SwarmFile.write(json.dumps(Swarm))
            
        return tracker_pb2.Status(details = json.dumps(Swarm))
    
    def RequestSwarm(self,request,context):
        SwarmData = request.SwarmData
        fileName = request.fileName
        leecherIP = request.leecherIP
        id = request.id
        
        return tracker_pb2.Seeders()
       
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
    serve()
