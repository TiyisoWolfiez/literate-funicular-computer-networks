import socket
import ssl
import base64
import os
from dotenv import load_dotenv

load_dotenv()

def send_email(sender_email, receiver_email, host, port, password, score):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket:
        socket.connect((host, port))

        ehlo_command = 'EHLO {}\r\n'.format(host)
        socket.sendall(ehlo_command.encode())
        response = socket.recv(1024)
        print(response.decode())

        if b'STARTTLS' in response:
            starttls_command = 'STARTTLS\r\n'
            socket.sendall(starttls_command.encode())
            response = socket.recv(1024)
            print(response.decode())

            ssl_socket = ssl.wrap_socket(socket, ssl_version=ssl.PROTOCOL_TLSv1_2)

            ehlo_command = 'EHLO {}\r\n'.format(host)
            ssl_socket.sendall(ehlo_command.encode())
            response = socket.recv(1024)
            print(response.decode())

            auth_command = 'AUTH LOGIN\r\n'
            ssl_socket.sendall(auth_command.encode())
            response = socket.recv(1024)
            print(response.decode())

            username_b64 = base64.b64encode(sender_email.encode()).decode()
            password_b64 = base64.b64encode(password.encode()).decode()
            ssl_socket.sendall((username_b64 + '\r\n').encode())
            response = socket.recv(1024)
            ssl_socket.sendall((password_b64 + '\r\n').encode())
            response = socket.recv(1024)

            mail_from_command = f"MAIL FROM: <{sender_email}>\r\n"
            ssl_socket.sendall(mail_from_command.encode())
            response = socket.recv(1024)
            print(response.decode())

            rcpt_to_command = f"RCPT TO: <{receiver_email}>\r\n"
            ssl_socket.sendall(rcpt_to_command.encode())
            response = socket.recv(1024)
            print(response.decode())

            data_command = 'DATA\r\n'
            ssl_socket.sendall(data_command.encode())
            response = socket.recv(1024)
            print(response.decode())
            
            header = 'Subject: Your Score\r\n'
            message = 'Your Score is: {}/3.\r\n'.format(score)
            end_of_message = '\r\n.\r\n'
            ssl_socket.sendall((header + message + end_of_message).encode())
            response = socket.recv(1024)
            print(response.decode())

            quit_command = 'QUIT\r\n'
            ssl_socket.sendall(quit_command.encode())
            response = socket.recv(1024)
            print(response.decode())

            ssl_socket.close()

        socket.close()

host = os.getenv("HOST")
port = os.getenv("PORT")
username = os.getenv("SENDER_EMAIL")
password = os.getenv("EMAIL_PASSWORD")
receiver_email = os.getenv("RECEIVER_EMAIL")

send_mail = False
score = 4

if send_mail:
    send_email(username, receiver_email, host, port, password, score)
else:
    print('Results will be released after the IMY310 ones (^_^)')