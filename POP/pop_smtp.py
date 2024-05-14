import socket
import ssl
import os
from dotenv import load_dotenv
import base64

load_dotenv()

server = os.getenv("HOST")
port = os.getenv("PORT")
username = os.getenv("SENDER_EMAIL")
password = os.getenv("EMAIL_PASSWORD")

# Function to check if the BCC header contains your email address
def is_bcc_to_you(headers):
    for header in headers:
        if header.startswith("BCC:"):
            bcc_addresses = header.split("BCC:")[1].strip().split(",")
            for addr in bcc_addresses:
                if addr.strip().lower() == username.lower():
                    return True
    return False

# Function to send a warning email
def send_warning(subject, original_message):
    sender_email = os.getenv("SENDER_EMAIL")
    receiver_email = os.getenv("SENDER_EMAIL") 
    host = "smtp.gmail.com"
    port = 465
    password = os.getenv("EMAIL_PASSWORD")
    score = "BCC Warning" 

    # Establish a TCP connection to the SMTP server
    with socket.create_connection((host, port)) as server_socket:
        # Wrap the socket with SSL/TLS
        with ssl.create_default_context().wrap_socket(server_socket, server_hostname=host) as ssl_socket:
            # Send EHLO command
            ehlo_command = 'EHLO {}\r\n'.format(host)
            ssl_socket.sendall(ehlo_command.encode())
            response = ssl_socket.recv(1024)
            print(response.decode())

            # Send authentication credentials
            auth_command = 'AUTH LOGIN\r\n'
            ssl_socket.sendall(auth_command.encode())
            response = ssl_socket.recv(1024)
            print(response.decode())
            username_b64 = base64.b64encode(sender_email.encode()).decode()
            password_b64 = base64.b64encode(password.encode()).decode()
            ssl_socket.sendall((username_b64 + '\r\n').encode())
            response = ssl_socket.recv(1024)
            ssl_socket.sendall((password_b64 + '\r\n').encode())
            response = ssl_socket.recv(1024)

            # Send MAIL FROM command
            mail_from_command = f"MAIL FROM: <{sender_email}>\r\n"
            ssl_socket.sendall(mail_from_command.encode())
            response = ssl_socket.recv(1024)
            print(response.decode())

            # Send RCPT TO command
            rcpt_to_command = f"RCPT TO: <{receiver_email}>\r\n"
            ssl_socket.sendall(rcpt_to_command.encode())
            response = ssl_socket.recv(1024)
            print(response.decode())

            # Send DATA command
            data_command = 'DATA\r\n'
            ssl_socket.sendall(data_command.encode())
            response = ssl_socket.recv(1024)
            print(response.decode())
            
            # Send email content
            ssl_socket.sendall((f'Subject: {subject}\r\n\r\n{score}\r\n.\r\n'.encode()))
            response = ssl_socket.recv(1024)
            print(response.decode())

            # Send QUIT command
            quit_command = 'QUIT\r\n'
            ssl_socket.sendall(quit_command.encode())
            response = ssl_socket.recv(1024)
            print(response.decode())

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
