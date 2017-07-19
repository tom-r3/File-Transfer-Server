import socket
from threading import Thread, Lock
from SocketServer import ThreadingMixIn
from struct import unpack

BUFFER_SIZE = 1024

KEY_LIST = []
SOCKET_LIST = []
KS_LOCK = Lock()

class ClientThread(Thread):

    def __init__(self,host,port,sock):
        Thread.__init__(self)
        self.host = host
        self.port = port
        self.sock = sock
        print " New thread started for "+ host + ":" + str(port)

    def run(self):
        in_data = self.sock.recv(BUFFER_SIZE)
        if not in_data: 
            print 'data error\n'
            exit()

        #process control info
        ctrlinfo = in_data[0:9]
        ctrlinfo = unpack('c8s', ctrlinfo)
        req_type = ctrlinfo[0]
        key = ctrlinfo[1]
        print 'req: ' + ctrlinfo[0] + ' key: ' + ctrlinfo[1] + '\n'
        if req_type == 'F':
            print 'closing socket ' + str(self.sock.getsockname()) + '\n'
            self.sock.close()
            exit()

        # add new key/socket pair to lists
        KS_LOCK.acquire()
        try:
            SOCKET_LIST.append(self.sock)
            KEY_LIST.append(req_type + key)
        finally:
            KS_LOCK.release()

        # process data
        data = in_data[9:]
        print 'in_data: ' + data + '\n'

        # print the list for testing
        for s, k in zip(SOCKET_LIST, KEY_LIST):
            print 'socket: ' + str(s.getsockname()) + ', key: ' + k + '\n'

        #filename='mytext.txt'
        #f = open(filename,'rb')
        #while True:
        #    l = f.read(BUFFER_SIZE)
        #    while (l):
        #        self.sock.send(l)
        #        #print('Sent ',repr(l))
        #        l = f.read(BUFFER_SIZE)
        #    if not l:
        ##        f.close()
         #       self.sock.close()
         #       break

# create connection
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # tell the kernel to reuse a local socket in TIME_WAIT state, without waiting for its natural timeout to expire
s.bind(("",0))
port = s.getsockname()[1]

threads = []

# write port number to file for client
with open('port', 'wb') as p: 
    p.write(str(port))

# listen for incoming connections
while True:
    s.listen(5)
    print "Waiting for incoming connections on port " + str(port) + " and host " + socket.gethostname()
    (conn, (host,port)) = s.accept() # blocks until a new client connects, need to implement select here 
    print 'Got connection from ', (host,port)

    newthread = ClientThread(host,port,conn)
    newthread.start()
    threads.append(newthread)

for t in threads:
    t.join()