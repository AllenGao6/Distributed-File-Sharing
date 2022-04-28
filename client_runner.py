import argparse
from functools import total_ordering
import os.path
from os import path
import os
from file import File
from client import *
from progress_bar import printProgressBar
import concurrent.futures
import config

parser = argparse.ArgumentParser(description='Choose an action to perform in this P2P network')

# select action
parser.add_argument('--reg', default=False, action='store_true')
parser.add_argument('--file_list_request', default=False, action='store_true')
parser.add_argument('--file_location_request', default=False, action='store_true')
parser.add_argument('--download', default=False, action='store_true')

args = parser.parse_args()
#

# select action
reg= args.reg
file_list_request = args.file_list_request
download = args.download
file_location_request = args.file_location_request

total_ordering = reg + file_list_request + download + file_location_request

if total_ordering == 0:
    print("Please Select an Action")
    exit()
elif total_ordering > 1:
    print("Please Select One Action At a Time")
    exit()

# supporting function call

# ask for a peer a chunk of file
def peer_file_request(data):
    host, port, index, file_name = data
    result = send_peer_request(host, port, index, file_name)
    # this part is not needed, should only need return result, but shown here as ez of understanding 
    if result == None:
        return None

    return result # byte_data, hash_data = result


if reg: 
    # Register Request: Tells the server what files the peer
    # wants to share with the network. Takes in the IP address
    # and port for the endpoint to accept peer connections for
    # download; the number of files to register; and for every
    # file, a file name and its length.
    # check for error
    file_entry = []
    
    # let user enter all file they wish to upload
    file_input = input("Please enter all file path you wish to register: (Seperate by a single space)")
    if len(file_input) != 0:
        file_list = file_input.split(" ")
        for file in file_list:
            if not path.exists(file):
                print(file + " NOT FOUND")
                exit()
        file_entry += file_list

    # let user to enter a dir to upload
    dir_input = input("Please enter the dirctory you want to upload: (Seperate by a single space)")
    if not path.isdir(dir_input) and len(dir_input) != 0:
        print(dir_input + " NOT FOUND")
        exit()
    if len(dir_input) != 0:
        for file in os.listdir(dir_input):
            file_entry.append(os.path.join(dir_input, file))

    # register the file in client side 
    added_file = register_local_file(file_entry)

    send_package = []
    for file in added_file:
        send_package.append((file.getName(), file.get_file_size()))
    machine_info = [config.peer_addr , config.peer_port]
    # sending the package
    result = send_server_request(100, data=send_package, port=machine_info)
    if not result:
        remove_files(added_file, "obj")
        print("registered failed, please try again")
    else:
        remove_file = []
        for filename, status in result.items():
            if status == "Failed":
                remove_file.append(filename)
        # remove_files(remove_file, "name")

        if len(remove_file) == 0:
            print("All file registered successfully")
        else:
            file_str = ", ".join(remove_file)
            print("File failed to register: " + file_str)
    print(get_all_filename())
elif file_list_request:
    # File List Request: Asks the server for the list of files. 
    result = send_server_request(200)
    if not result:
        print("Failed to get file list")
    else:
        for filename, size in result.items():
            print(filename + " : " + str(size))

elif file_location_request:
    filename = input("input the filename to search for locations: ")
    result = send_server_request(300, data=filename)
    if result:
        for key, value in result.items():
            port, index_list= value
            print("IP Addr: "+ str(key) + "   Port: " + str(port)+ " Available Chunks: " + str(index_list))
    else:
        print("File not found :(")

elif download:
    filename = input("Enter the file you wish to download: (Select extractly like file list): ")

    result = send_server_request(200)
    # check for network error or file existence problem
    if get_file(filename) != None:
        print("File already exsited locally!")
        exit()
    if not result:
        print("System Failed, can't not get files list")
        exit()
    if filename not in result.keys():
        print("File Request Does Not Exit, Please Try Again")
        exit()

    # ----------- True procedure for file downloading ------------
    
    # precheck if all required file are present
    if not path.exists(config.Client_Peer_data_storage):
        save_object([])

    # register the empty file object localy
    local_file = File(filename, result[filename])
    # print(result[filename])
    l = local_file.get_chunk_list_size()
    # print(l)
    printProgressBar(0, l, prefix = 'Progress:', suffix = 'Download Complete', length = 100)
    #printProgressBar(i + 1, l, prefix = 'Progress:', suffix = 'Download Complete', length = 100)
    # print(local_file.get_chunk_list_size(), local_file.get_aval_chunk_size())
    while local_file.get_chunk_list_size() != local_file.get_aval_chunk_size():

        # find the rarest block first
        requests = find_rarest_block(local_file, 10)
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            
            future_to_data = {executor.submit(peer_file_request, data): data for data in requests}

            for future in concurrent.futures.as_completed(future_to_data):
                data = future_to_data[future]

                try:
                    info_data = future.result()
                    if info_data:
                        #update json with new data
                        byte_block, hash_byte, chunk_index = info_data
                        # add to local file storage
                        local_file.add_chunk(byte_block, chunk_index)
                        local_file.add_hash_chunk(hash_byte, chunk_index)
                        # register this chunk in central server
                        data = {'chunk_index': chunk_index, 'filename': local_file.getName(), 'file_size': local_file.get_file_size()}
                        res = send_server_request(400, data)
                        if not res:
                            print("Failed to register node from client side, check log for detail")
                        else:
                            # this will show file chunk info, will uncomment if needed
                            # print("chunk ", chunk_index, " in ", local_file.getName(), " registered!" )
                            pass
                        
                        # print the progress bar
                        printProgressBar(local_file.get_aval_chunk_size(), l, prefix = 'Progress:', suffix = 'Download Complete', length = 100)

                    else:
                        pass
                except Exception as exc:
                    print('The process generated an exception: %s' % (exc))

    # create the file in local folder
    local_file.create_file()
    

else:
    # File Chunk Request: Asks the peer to return the file
    # chunk. Reads in a file name, chunk indicator.
    print("Wrong Command Detected")


