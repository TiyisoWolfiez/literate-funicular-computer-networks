import socket
import ssl
import base64
import os
from dotenv import load_dotenv

load_dotenv()

def send_email(sender_email, receiver_email, host, port, password, score):
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
            header = 'Subject: Your Score\r\n'
            message = 'Your Score is: {}/3.\r\n'.format(score)
            end_of_message = '\r\n.\r\n'
            ssl_socket.sendall((header + message + end_of_message).encode())
            response = ssl_socket.recv(1024)
            print(response.decode())

            # Send QUIT command
            quit_command = 'QUIT\r\n'
            ssl_socket.sendall(quit_command.encode())
            response = ssl_socket.recv(1024)
            print(response.decode())

if __name__ == "__main__":
    host = os.getenv("HOST")
    port = os.getenv("PORT")
    username = os.getenv("SENDER_EMAIL")
    password = os.getenv("EMAIL_PASSWORD")
    receiver_email = os.getenv("RECEIVER_EMAIL")

    send_mail = True
    score = 4

    if send_mail:
        send_email(username, receiver_email, host, port, password, score)
    else:
        print('Results will be released after the IMY310 ones (^_^)')