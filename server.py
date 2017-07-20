import socket
from threading import *
from SocketServer import ThreadingMixIn
from struct import unpack
from os import _exit

BUFFER_SIZE = 1024
CTRL_SIZE = 9

KEY_LIST = []
SOCKET_LIST = []
TRANSFER_LIST = []
KST_LOCK = Lock()

DONE = Event() 
DONE.set()

class ClientThread(Thread):

    def __init__(self,host,port,sock):
        Thread.__init__(self)
        self.host = host
        self.port = port
        self.sock = sock
        print " New thread started for "+ host + ":" + str(port)

    def run(self):
        ctrlinfo = self.sock.recv(CTRL_SIZE)
        if not ctrlinfo: 
            print 'data error\n'
            exit()

        #process control info
        #ctrlinfo = in_data[0:9]
        ctrlinfo = unpack('c8s', ctrlinfo)
        req_type = ctrlinfo[0]
        key = ctrlinfo[1]
        print 'req: ' + ctrlinfo[0] + ' key: ' + ctrlinfo[1] + '\n'

        if req_type == 'F':
            print 'closing sockets'

            # close all waiting connection
            # ongoing connections will not be in list
            KST_LOCK.acquire()
            try:
                for list_socket in SOCKET_LIST:
                    list_socket.shutdown(socket.SHUT_RDWR)
                    list_socket.close()
                    SOCKET_LIST.remove(list_socket)
                    # just in case a new thread spawns
                    if list_socket in TRANSFER_LIST:
                        TRANSFER_LIST.remove(list_socket)
            finally:
                KST_LOCK.release()

            #while len(TRANSFER_LIST) > 0:
            #    print str(TRANSFER_LIST)
            DONE.wait()
            # close entire process
            _exit(0)
            
        #set opposite type to check KEY_LIST with
        if req_type == 'G':
            opp_type = 'P'
        else:
            opp_type = 'G'

        # check key list for match with the opposite type
        # do within lock in case index changes after
        KST_LOCK.acquire()
        try:
            if opp_type+key in KEY_LIST:
                location = KEY_LIST.index(opp_type+key)
                list_socket = SOCKET_LIST[location]
                # remove from list set so they are not closed upon F signal
                SOCKET_LIST.pop(location)
                KEY_LIST.pop(location)
                #add to transfer list so that program does not close during transfer
                TRANSFER_LIST.append(list_socket)
                #set flag
                in_list = 1
                #clear event 
                DONE.clear()
            else:
                #set flag
                in_list= 0;
        finally:
            KST_LOCK.release()

        if in_list:
            if req_type == 'G': #download, need to send it data from list socket
                transfer_data = list_socket.recv(BUFFER_SIZE) #recieve data from list socket
                while transfer_data:
                    self.sock.send(transfer_data)
                    transfer_data = list_socket.recv(BUFFER_SIZE) #recieve data from list socket
                #close uploader socket
                self.sock.close()
            else: #upload
                #transfer its data to list socket
                transfer_data = self.sock.recv(BUFFER_SIZE)
                while transfer_data:
                    list_socket.send(transfer_data)
                    transfer_data = self.sock.recv(BUFFER_SIZE)
                #close list download socket
                list_socket.close()

            KST_LOCK.acquire()
            try:
                # remove from transfer list once done
                TRANSFER_LIST.remove(list_socket)
            finally:
                KST_LOCK.release()

            # set event if all threads are done transferring
            if len(TRANSFER_LIST) + len(SOCKET_LIST) == 0:
                DONE.set()

        else: #not in list
            # add new key/socket pair to lists
            KST_LOCK.acquire()
            try:
                SOCKET_LIST.append(self.sock)
                KEY_LIST.append(req_type + key)
            finally:
                KST_LOCK.release()

        exit() #exit thread

#end ClientThread

# create connection
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # tell the kernel to reuse a local socket in TIME_WAIT state, without waiting for its natural timeout to expire
s.bind(("",0))
port = s.getsockname()[1]

# write port number to file for client
with open('port', 'wb') as p: 
    p.write(str(port))

# listen for incoming connections
while True:
    s.listen(5)
    print "Waiting for incoming connections on port " + str(port) + " and host " + socket.gethostname()
    (conn, (host,port)) = s.accept() # blocks until a new client connects
    print 'Got connection from ', (host,port)

    newthread = ClientThread(host,port,conn)
    newthread.start()

print 'closing main server'
s.shutdown(socket.SHUT_RDWR)
s.close()