import socket, sys
from struct import pack

#download: client <host> <port> G<key> <file name> <recv size>
#upload: client <host> <port> P<key> <file name> <send size> <wait time>

host = sys.argv[1] #socket.gethostname()
port = int(sys.argv[2])
print 'host: ' + host + ', port: ' + str(port)

BUFFER_SIZE = 1024

# connect to server
s = socket.socket()
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))

# send control info
command = sys.argv[3][0]
key = sys.argv[3][1:]
print 'cmd: ' + command + ', key: ' + key

if (len(key) > 8) or (command != 'P' and command != 'G' and command != 'F'):
	print 'Error: key must be 8 characters or less and begin with P or G.'
	exit()

key = key.ljust(9, '\0')
ctrlinfo = pack('!c8s', command, key)
s.send(ctrlinfo)

# listen or send depending on command
if command == 'G': #download
	in_data = s.recv(BUFFER_SIZE)
	print in_data
elif command == 'P': #upload
	# send test data
	data = 'this is test data, I am pretending to be an uploader'
	s.send(data)
elif command == 'F':
	s.close()
	print('connection closed')

#with open(sys.argv[4], 'wb') as f:
  #  print 'file opened'
 #   while True:
 #       #print('receiving data...')
 #       data = s.recv(BUFFER_SIZE)
 #       print('data=%s', (data))
 #       if not data:
 #           f.close()
#            print 'file close()'
#            break
#        # write data to a file
#        f.write(data)

#print('Successfully get the file')