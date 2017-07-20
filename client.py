import socket, sys
from struct import pack
from time import sleep
from tempfile import TemporaryFile

host = sys.argv[1]
port = int(sys.argv[2])
print 'host: ' + host + ', port: ' + str(port)

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
if command == 'F':
	print 'closing client'
	s.close()
	exit()

# set up the file
if sys.argv[4].isdigit() and command == 'P':
	f = TemporaryFile()
	f.write("T" * int(sys.argv[4]))
else:
	if command == 'G':
		f = open(sys.argv[4], 'wb')
	elif command == 'P':
		f = open(sys.argv[4], 'rb')

if command == 'G': #download
	in_data = s.recv(int(sys.argv[5]))
	while in_data:
		print in_data
		f.write(in_data)
		in_data = s.recv(int(sys.argv[5]))
			
elif command == 'P': #upload
	#get sleep time in milliseconds
	sleep_time = int(sys.argv[6]) * 0.001

	# send test data
	out_data = f.read(int(sys.argv[5]))
	while out_data:
		print out_data
		s.send(out_data)
		sleep(sleep_time)
		out_data = f.read(int(sys.argv[5]))

#close file and socket
s.close()
f.close()
print('connection closed')

