import socket
import ssl
import base64

def send_email(sender_email, sender_password, recipient_email, subject, body):
    # SMTP server configuration
    smtp_server = 'smtp.gmail.com'
    smtp_port = 465

    # Establish a TCP connection to the SMTP server
    print("Connecting to SMTP server...")
    server_socket = socket.create_connection((smtp_server, smtp_port))
    print("Connected to SMTP server.")

    # Wrap the socket with SSL/TLS
    print("Initiating SSL/TLS handshake...")
    context = ssl.create_default_context()
    server_socket = context.wrap_socket(server_socket, server_hostname=smtp_server)
    print("SSL/TLS handshake completed.")

    # Send EHLO command
    print("Sending EHLO...")
    server_socket.send(b'EHLO example.com\r\n')
    print(server_socket.recv(1024))

    # Send authentication credentials
    print("Sending authentication credentials...")
    server_socket.send(b'AUTH LOGIN\r\n')
    print(server_socket.recv(1024))
    server_socket.send(base64.b64encode(sender_email.encode()) + b'\r\n')
    print(server_socket.recv(1024))
    server_socket.send(base64.b64encode(sender_password.encode()) + b'\r\n')
    print(server_socket.recv(1024))

    # Send MAIL FROM command
    print("Sending MAIL FROM...")
    server_socket.send(f'MAIL FROM: <{sender_email}>\r\n'.encode())
    print(server_socket.recv(1024))

    # Send RCPT TO command
    print("Sending RCPT TO...")
    server_socket.send(f'RCPT TO: <{recipient_email}>\r\n'.encode())
    print(server_socket.recv(1024))

    # Send DATA command
    print("Sending DATA...")
    server_socket.send(b'DATA\r\n')
    print(server_socket.recv(1024))

    # Send email content
    print("Sending email content...")
    server_socket.send(f'Subject: {subject}\r\n\r\n{body}\r\n.\r\n'.encode())
    print(server_socket.recv(1024))

    # Send QUIT command
    print("Sending QUIT...")
    server_socket.send(b'QUIT\r\n')
    print(server_socket.recv(1024))

    # Close the connection
    server_socket.close()

def test_smtp_connection():
    smtp_server = 'smtp.gmail.com'
    smtp_port = 465

    try:
        print("Connecting to SMTP server...")
        server_socket = socket.create_connection((smtp_server, smtp_port))
        print("Connected to SMTP server.")
        server_socket.close()
    except Exception as e:
        print("An error occurred:", e)

if __name__ == "__main__":
    test_smtp_connection()
    send_email("youremail@gmail", "YourPassword", "ReceiverEmail", "Test Subject", "Test Body")
