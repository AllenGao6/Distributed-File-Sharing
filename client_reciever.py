import socket
import json
from client import *
from struct import pack
import config

# socket related constant
ServerSocket = socket.socket()
ThreadCount = 0


try:
   ServerSocket.bind((config.peer_addr, config.peer_port))
except socket.error as e:
   print(str(e))

print('Waitiing for a Connection..')
ServerSocket.listen(20)

def threaded_client(connection, addr):
   address, port = addr
   print("incoming connection: ", address)
   # giving success response code
   connection.send(str.encode('200'))
   # recieving main content of data
   data = connection.recv(2048)
   data = json.loads(data.decode("utf-8"))
   file_name, chunk_index = data['filename'], data['chunk_index']
   
   # retrive desired byte block
   byte_block, hash_block = get_file_chunk(file_name, chunk_index)
   if not byte_block:
      m = str.encode('')
   else:
      m = byte_block
   # use struct to make sure we have a consistent endianness on the length
   length = pack('>Q', len(m))

   # sendall to make sure it blocks if there's back-pressure on the socket
   # print("sending data to peer")
   connection.sendall(length)
   connection.sendall(m)
   # print("data sent")

   # recieve confirmation
   data = connection.recv(2048)
   data = json.loads(data.decode("utf-8"))
   if data['status'] != "Success":
      connection.close()
      return
   # hash_response = json.dumps({"data": hash_block})
   # response = bytes(hash_response,encoding="utf-8")
   connection.send(str.encode(hash_block))
   print("data transfer complete, ending...")
   connection.close()
    
    

while True:
   Client, address = ServerSocket.accept()
   print('Connected to: ' + address[0] + ':' + str(address[1]))
   start_new_thread(threaded_client, (Client, address ))
   ThreadCount += 1
   print('Client Thread Number: ' + str(ThreadCount))
      


   # Response = ClientSocket.recv(2048)
    # print(Response.decode('utf-8'))

    # m = {"id": 2, "name": "abc"} # a real dict.


    # data = json.dumps(m)

    # index = 0
    # print(len( bytelist))
    # while index != len(bytelist):
    #     # client_input = str(input("Say Something: "))
    #     # ClientSocket.send(str.encode(client_input))
    #     # time.sleep(0.2)
    #     ClientSocket.send(bytelist[index])
    #     Response = ClientSocket.recv(1024)
    #     if Response.decode('utf-8') != "200":
    #         print("process error!")
    #         break
    #     print("going througg iteration", str(index))
    #     index += 1

    # ClientSocket.close()