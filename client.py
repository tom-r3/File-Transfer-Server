import socket, sys

#download: client <host> <port> G<key> <file name> <recv size>
#upload: client <host> <port> P<key> <file name> <send size> <wait time>

s = socket.socket()
host = sys.argv[1] #socket.gethostname()
port = int(sys.argv[2])

BUFFER_SIZE = 1024

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

print 'host: ' + host + ', port: ' + str(port)

s.connect((host, port))
with open(sys.argv[3], 'wb') as f:
    print 'file opened'
    while True:
        #print('receiving data...')
        data = s.recv(BUFFER_SIZE)
        print('data=%s', (data))
        if not data:
            f.close()
            print 'file close()'
            break
        # write data to a file
        f.write(data)

print('Successfully get the file')
s.close()
print('connection closed')