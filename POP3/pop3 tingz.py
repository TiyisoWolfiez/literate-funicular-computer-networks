import socket
import ssl
import os
from dotenv import load_dotenv

load_dotenv()

server = os.getenv("HOST")
port = os.getenv("PORT")
username = os.getenv("SENDER_EMAIL")
password = os.getenv("EMAIL_PASSWORD")

# set up the TCP connection
sock = socket.create_connection((server, port))

# wrap the socket in an SSL context
context = ssl.create_default_context()
ssl_sock = context.wrap_socket(sock, server_hostname=server)

# receive the server greeting
response = ssl_sock.recv(1024).decode('utf-8')
print(response)

# send the username and password
ssl_sock.send(f'USER {username}\r\n'.encode('utf-8'))
response = ssl_sock.recv(1024).decode('utf-8')
print(response)
ssl_sock.send(f'PASS {password}\r\n'.encode('utf-8'))
response = ssl_sock.recv(1024).decode('utf-8')
print(response)

# get the mailbox statistics
ssl_sock.send(b'STAT\r\n')
response = ssl_sock.recv(1024).decode('utf-8')
print(response)

# list the messages on the server
ssl_sock.send(b'LIST\r\n')
response = ssl_sock.recv(1024).decode('utf-8')
print(response)

# retrieve the headers of each message
num_messages = int(response.split()[1])
for i in range(1, num_messages+1):
    ssl_sock.send(f'RETR {i}\r\n'.encode('utf-8'))
    response = b''
    while b'\r\n.\r\n' not in response:
        response += ssl_sock.recv(1024)
    print(f'Message {i} headers:')
    for line in response.split(b'\r\n'):
        if line.startswith(b'From:'):
            print(line.decode('utf-8'))
        elif line.startswith(b'Subject:'):
            print(line.decode('utf-8'))
        elif line.startswith(b'Content-Length:'):
            print(line.decode('utf-8'))
    print()

# log out of the server
ssl_sock.send(b'QUIT\r\n')
response = ssl_sock.recv(1024).decode('utf-8')
print(response)

# close the socket
ssl_sock.close()
