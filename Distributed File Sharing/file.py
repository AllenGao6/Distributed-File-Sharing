'''
    objective of file.py:

    define the object class for file,   

    information to include:

    name
    size of file
    chunk list (should automaticlly be splitted into chunks, each chunk should have indicator)

'''
import base64
import sys
import hashlib

JPG, PNG, PDF, MP3, MP4, UNKNOWN = 1, 2, 3, 4, 5, 0

class File:

    file_name = ""
    file_type = "" 
    file_size = 0
    chunk_list_size = 0
    # will be decided later how to handle indicator and hashing for each chunk, most likely will define a chunk hash function
    chunk_list = []
    hashed_chunk_list = []
    SINGLE_CHUNK_SIZE = 131072

    def __init__(self, file_name, file_size=None, full_info=False):
        self.file_name = file_name
        self.file_type = self.get_fileType()
        if not file_size:
            self.chunk_list = []
            self.hashed_chunk_list = []
            self.chunkize()
        else:
            self.file_size = file_size
            if full_info:
                self.chunk_list = [True] * (self.file_size // self.SINGLE_CHUNK_SIZE + 1)
                self.chunk_list_size = len(self.chunk_list)
                self.hashed_chunk_list = [True] * (self.file_size // self.SINGLE_CHUNK_SIZE + 1)
            else:
                self.chunk_list = [None] * (self.file_size // self.SINGLE_CHUNK_SIZE + 1)
                self.chunk_list_size = len(self.chunk_list)
                self.hashed_chunk_list = [None] * (self.file_size // self.SINGLE_CHUNK_SIZE + 1)

    # create the file in local folder
    def create_file(self):
        true_file_name = self.file_name.split('/')[-1]
        converted_string = b"".join(self.chunk_list)
        if len(converted_string) != self.file_size:
            print("Error when constructing file, file size does not match")
        f = open('FILE_RECIEVE/'+true_file_name, 'wb')
        f.write(base64.b64decode((converted_string)))
        f.close()
        print("File Created locally!!!!!!!!")

    # pre-define chunk indicator given the size of the file
    def chunkize(self):
        # the encoded binary format of file
        if self.file_type == JPG or self.file_type == PNG or self.file_type == PDF or self.file_type == MP4:
            # base64 encode all these file from local file path
            with open(self.file_name, "rb") as image2string:
                converted_string = base64.b64encode(image2string.read())
            print(len(converted_string))
            # set the total file size in byte
            self.file_size = len(converted_string)

            for i in range(0, (self.file_size // self.SINGLE_CHUNK_SIZE)+1):
        
                if i == len(converted_string) // self.SINGLE_CHUNK_SIZE:
                    chunk_block = converted_string[i*self.SINGLE_CHUNK_SIZE: self.file_size]
                else:
                    chunk_block = converted_string[i*self.SINGLE_CHUNK_SIZE: (i+1)*self.SINGLE_CHUNK_SIZE]

                # append original block and hashed block into local storage
                # hashed block is used to verification for data integrity
                self.chunk_list.append(chunk_block)
                self.hashed_chunk_list.append(self.hash_chunk(chunk_block))

            # set the total chunk list size
            self.chunk_list_size = len(self.chunk_list)

        elif self.file_type == MP3:
            print("not supported yet")
        elif self.file_type == MP4:
            print("not supported yet")
        else:
            print("INVALID FILE TYPE")
              

    def get_fileType(self):
        extention = self.file_name.split('.')[-1]
        if extention == "jpg":
            return JPG
        elif extention == "png":
            return PNG
        elif extention == 'pdf':
            return PDF
        elif extention == 'mp3':
            return MP3
        elif extention == 'mp4':
            return MP4
        else:
            return UNKNOWN

    # get the name of this file
    def getName(self):
        return self.file_name

    # get the size of this file
    def get_file_size(self):
        return self.file_size

    # get the file type
    def get_file_type(self):
        return self.file_type

    # define a hash algorithm for the chunk
    def hash_chunk(self, data):
        # implement sha1 for verification
        obj_sha3_256 = hashlib.sha3_256(data)
    
        # print in hexadecimal
        # print("\nSHA3-256 Hash: ", obj_sha3_256.hexdigest())

        return obj_sha3_256.hexdigest()

    # add a piece to chunk_list
    def add_chunk(self, chunk, index):
        self.chunk_list[index] = chunk

    # add a piece to hash chunk_list
    def add_hash_chunk(self, hash_chunk, index):
        self.hashed_chunk_list[index] = hash_chunk
    
    # get the size of chunk_list
    def get_chunk_list_size(self):
        return self.chunk_list_size
    # check the chunk of a file
    def check_file_chunk(self, index):
        if index >= self.chunk_list_size:
            return False
        # print("actual chunk_size:", len(self.chunk_list))
        # print("chunk_size:", self.chunk_list_size)
        return self.chunk_list[index] != None

    # get a particular chunk in chunk_list
    def get_index_chunk(self, index):
        if self.check_file_chunk(index):
            return self.chunk_list[index]
        return None

     # get a particular chunk hash in chunk_list
    def get_index_chunk_hash(self, index):
        if self.check_file_chunk(index):
            return self.hashed_chunk_list[index]
        return None


    # register a chunk in file given index
    def register_chunk(self, index):
        try:
            self.chunk_list[index] = True
            return True
        except:
            return False

    # get chunk ownership info
    def get_chunk_info(self, find_miss=False):
        # this part of the code is not optimized, but this should do the trick
        index_list = []
        for i in range(len(self.chunk_list)):
            if find_miss:
                if self.chunk_list[i] == None:
                    index_list.append(i)
            else:
                if self.chunk_list[i] != None:
                    index_list.append(i)
        return index_list

    # get the number of available chunk in file
    def get_aval_chunk_size(self):
        result = self.get_chunk_info(find_miss=False)
        return len(result)

    