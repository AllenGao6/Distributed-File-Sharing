from ipaddress import ip_address
import socket
import os
from _thread import *
#import other class object/function
import json
import base64
from node import Node
try:
    import cPickle as pickle
except ModuleNotFoundError:
    import pickle
from os import path
import config
from struct import pack


# local data storage
local_store_file = config.Server_data_storage
# read data into pickle file
def save_object(obj):
    with open(local_store_file, 'wb') as outp:  # Overwrites any existing file.
        pickle.dump(obj, outp, pickle.HIGHEST_PROTOCOL)

# get all object stored in file
def getData():
    if not path.exists(local_store_file):
        save_object([])
    with open(local_store_file, 'rb') as inp:
        data_list = pickle.load(inp)
    return data_list

# save all object stored in file
def saveData(data):
    save_object(data)
    
#-----------------supporting function call-------------------
# see if port match with address
def match_port(addr, port):
    for node in getData():
        if node.get_ip_addr() == addr and node.get_port() == port:
            return node
    return None
# get all address
def get_all_address():
    return [node.get_ip_addr() for node in getData()]

#check if the port number match the record
def check_node_valid(address, port):
    node_list = getData()
    address_book = get_all_address()
    if address in address_book:
        result = match_port(address, port)
        if result:
            return result
        else:
            return None
    else:
        new_node = Node(address, port) 
        node_list.append(new_node)
        saveData(node_list)
        return new_node

# package response and send to client
def package_response(data, status_code, Error_code=None):
    res = {}
    res["data"] = data
    res["status"] =  status_code
    if status_code == "Failed":
        res["error"] = Error_code

    response  = json.dumps(res)
    return bytes(response,encoding="utf-8")

# get all files avaiable to download in the network
def get_file_list():
    result = {}
    for node in getData():
        for file in node.get_file_list():
            file_name = file.getName()
            file_size = file.get_file_size()
            if file_name in result:
                if file_size != result[file_name]:
                    result[file_name] = file_size
            else:
                result[file_name] = file_size
    result["total_file"] = len(result)
    return result

# get all location for a particular file
def get_file_location(filename):
    locations = {}
    for node in getData():
        if node.check_file_exit(filename):
            # print([node.get_port(), node.get_file(filename).get_chunk_info()])
            locations[node.get_ip_addr()] = [node.get_port(), node.get_file(filename).get_chunk_info()]
    return locations

# register a file chunk for a particular peer node
def register_file_chunk(chunk_index, peer_addr, peer_port, filename, file_size):
    
    data_list = getData()
    check_node_valid(peer_addr, peer_port)
    index = -999
    for i in range(len(data_list)):
        if data_list[i].get_ip_addr() == peer_addr and data_list[i].get_port() == peer_port:
            index = i

    if index == -999:
        print("Critical Error Detected! ")
        return False
    status = data_list[index].register_chunk(chunk_index, filename, file_size)
    
    saveData(data_list)

    return status



# --------------------------------Socket Content Below------------------------------#
# kill port command if port is ocuppied
#sudo lsof -i :3000
#kill -9 <PID>
# socket related constant
ServerSocket = socket.socket()
ThreadCount = 0

try:
    ServerSocket.bind((config.server_addr, config.server_port))
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
    if data['code'] == 100:
        print("recieved code 100")
        node = check_node_valid(data['addr'], data['port'])
        if not node:
            print("incorrect port number")
            connection.send(package_response({}, "Failed", Error_code="ERROR: Incorrect Port Number!"))
            connection.close()
            return

        # register all file into node and save locally
        files = data["data"]
        status_json = {}
        for file in files:
            if node.register_file(file[0], file[1]):
                status_json[file[0]] = "Success"
            else:
                status_json[file[0]] = "Failed"
        print(status_json)
        print("sending back response...")
        response  = package_response(status_json, "Success")
        connection.send(response)
        connection.close()

    elif data['code'] == 200: # request file list
        result = get_file_list()
        response = package_response(result, "Success")
        connection.send(response)
        connection.close()

    elif data['code'] == 300: # file location request
        result = get_file_location(data['data'])
        response = package_response(result, "Success")
        length = pack('>Q', len(response))

        # sendall to make sure it blocks if there's back-pressure on the socket
        # print("sending data to peer")
        connection.sendall(length)
        connection.sendall(response)
        connection.close()

    elif data['code'] == 400: # Chunk Register Request:
        info = data['data']
        chunk_index, peer_addr, peer_port, filename, file_size = info['chunk_index'], info['peer_addr'], info['peer_port'], info['filename'], info['file_size']

        result = register_file_chunk(chunk_index, peer_addr, peer_port, filename, file_size)
        
        if result:
            response = package_response({}, "Success")
        else:
            response = package_response({}, "Failed", Error_code="Failed to register chunk for this file")
        connection.send(response)
        connection.close()

    elif data['code'] == 500: # File Chunk Request:
        pass
    else:
        print("INVALID CODE RECIEVED!")
        response = package_response({}, "Failed", Error_code="INVALID CODE RECIEVED!")
        connection.send(response)
        connection.close()
    

while True:
    Client, address = ServerSocket.accept()
    print('Connected to: ' + address[0] + ':' + str(address[1]))
    start_new_thread(threaded_client, (Client, address ))
    ThreadCount += 1
    print('Thread Number: ' + str(ThreadCount))





     # index = 0
    # while index != 4318:
    #     data = connection.recv(1024)
    #     if len(data) <= 1024:
    #         local_byte_list.append(data)
    #         print("iteration ", str(index), "recieved")
    #     # do something else here
    #     if not data:
    #         print("no data recieved!")
    #         break
    #     reply = "200"
    #     connection.sendall(str.encode(reply))
    #     index += 1
    
    # construct_file()


    # def threaded_client(connection, address):
#     print("incoming connection: ", address)
#     connection.send(str.encode('Welcome to the Servern'))
#     while True:
#         data = connection.recv(2048)
#         decrypted_data = data.decode('utf-8')
#         # do something else here
#         if not data:
#             break
#         name, ip_addr, port = decrypted_data.split(' ')
#         node = register_node(client_list, name, ip_addr, port)
#         reply = "welcome, "+ node.getName()+ "! Your existing file list : "+ node.get_file_list_name()
#         print("recieved", reply)
#         if not data:
#             break
#         connection.sendall(str.encode(reply))
#     connection.close()

# while True:
#     Client, address = ServerSocket.accept()
#     print('Connected to: ' + address[0] + ':' + str(address[1]))
#     start_new_thread(threaded_client, (Client, address ))
#     ThreadCount += 1
#     print('Thread Number: ' + str(ThreadCount))

# ServerSocket.close()


# local_byte_list = []

# def construct_file():

#     converted_string = b"".join(local_byte_list)
#     print(len(converted_string))
#     decodeit = open('out.pdf', 'wb')
#     decodeit.write(base64.b64decode((converted_string)))
#     decodeit.close()