'''
    objective of node.py:

    define the object class for node,   

    information to include:

    name
    ip address
    port to connect
    a list of file objective

'''

from file import File

class Node:

    ip_addr = ""
    port_num = 0
    file_list = []

    def __init__(self, ip_addr, port_num):
        self.ip_addr = ip_addr
        self.port_num = port_num

    # check if the given ip address is the same as this node's ip address
    def check_ip(self, input_ip):
        return self.ip_addr == input_ip

    
    # get the ip address of this peer node
    def get_ip_addr(self):
        return self.ip_addr

    # get the port number of this peer node
    def get_port(self):
        return self.port_num

    # get the file list of this peer node
    def get_file_list(self):
        return self.file_list

    # get the name of file_list
    def get_file_list_name(self):
        list_item = ""
        for file in self.file_list:
            list_item += " "
            file += file.getName()
        return list_item

    # register a new file on this node
    def register_file(self, file_name, file_size):
        if self.check_file_complete(file_name, file_size):
            return False
        try:
            new_file = File(file_name, file_size, full_info=True)
            self.file_list.append(new_file)
            return True
        except:
            return False

    # check if a particular file exist in this node
    def check_file_exit(self, name):
        for file in self.file_list:
            if file.getName() == name:
                return True
        return False

    # check if a file exit by both filename and size
    def check_file_complete(self, name, size):
        for file in self.file_list:
            if file.getName() == name and file.get_file_size() == size:
                return True
        return False

    # get a particular file object given name
    def get_file(self, name):
        for file in self.file_list:
            if file.getName() == name:
                return file
        return None

    # register a file chunk as recieved given index
    def register_chunk(self, index, filename, file_size):
        if self.check_file_exit(filename):
            return self.get_file(filename).register_chunk(index)
        else:
            new_file = File(filename, file_size)
            self.file_list.append(new_file)
            return new_file.register_chunk(index)

             

        
    
