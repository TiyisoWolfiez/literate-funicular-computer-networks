import socket
from clean_data import clean_data
import time
import ssl
import os
import base64
from dotenv import load_dotenv

load_dotenv()

server = os.getenv("HOST")
port = os.getenv("PORT")
email_sender = os.getenv("SENDER_EMAIL")
password = os.getenv("EMAIL_PASSWORD")
smtp_host = os.getenv("SMTP_PORT")
smtp_server = os.getenv("SMTP_HOST")
smtp_receiver_email = os.getenv("SMTP_RECEIVER_EMAIL")

def pop3_client():
    # set up the TCP connection
    sock = socket.create_connection((server, port))

    # wrap the socket in an SSL context
    context = ssl.create_default_context()
    ssl_sock = context.wrap_socket(sock, server_hostname=server)

    # receive the server greeting
    response = ssl_sock.recv(1024).decode('utf-8')
    print(response)

    # send the email_sender and password
    ssl_sock.send(f'USER {email_sender}\r\n'.encode('utf-8'))
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
        print('Message content:')
        print(response.decode('utf-8'))
        print()

    # log out of the server
    ssl_sock.send(b'QUIT\r\n')
    response = ssl_sock.recv(1024).decode('utf-8')
    print(response)

    # close the socket
    ssl_sock.close()

def sendmail(sender_email, receiver_email, host, port, password, email):
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
            subject = 'Practical 9: Email'
            message = email
            ssl_socket.sendall((f'Subject: {subject}\r\n\r\n{message}\r\n.\r\n'.encode()))
            response = ssl_socket.recv(1024)
            print(response.decode())

            # Send QUIT command
            quit_command = 'QUIT\r\n'
            ssl_socket.sendall(quit_command.encode())
            response = ssl_socket.recv(1024)
            print(response.decode())
        
def send_message(message, recipient):
    print("Sending message to recipient")
    sendmail(email_sender, recipient, smtp_server, smtp_host, password, message)
    
    # Call the function
    pop3_client()

def get_mime_type(message):
    content_type = None

    # Split the message into lines
    lines = message.split('\n')

    # Search for the Content-Type header
    for line in lines:
        if line.startswith('Content-Type:'):
            # Extract the content type value
            content_type = line.split(':', 1)[1].strip()
            break

    print("Content Type:", content_type)
    print("Content Type Type:", type(content_type))
    return content_type.strip()

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 55555))
    server_socket.listen(1)
    print('SMTP Proxy Server listening on port 55555')

    client_socket = None
    while client_socket is None:
        client_socket, client_address = server_socket.accept()
    print('Received connection from:', client_address)

    while True:
        data = client_socket.recv(1024).decode('utf-8')
        if not data:
            continue
        print("Received data:", data)
        mimetype = get_mime_type(data)
        print("Got mimetype: ", mimetype)
        print('Received message from client:', data)
        print('Handled by ', email_sender)
        print('Server Username: Handled by ', email_sender)
        print('Client Username: Handled by ', 'johndoe@gmail.com')
        recipient, data = clean_data(data, mimetype)

        ## TEST Remove
        print("Data: ", data)
        if not data:
            resp = 'Your message was rejected by MailServer!'
            client_socket.sendall(resp.encode())
            continue
        send_message(data, recipient)
        print("Email sent to recipient")
        resp = 'MailServer proxy sent: ' + data
        client_socket.sendall(resp.encode())
    
    client_socket.close()

if __name__ == '__main__':
    main()


