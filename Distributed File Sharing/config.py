# all configuration are listed here
import socket

def find_local_ip_addr():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    local_addr = s.getsockname()[0]
    s.close()
    return local_addr
server_addr = find_local_ip_addr()
print(server_addr)
server_port = 65430
peer_addr = find_local_ip_addr()
peer_port = 61013

Server_data_storage = "server_data.pkl"
Client_Peer_data_storage = "peer_local_store.pkl"