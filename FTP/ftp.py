import socket
import hashlib
import time
import os

# Localhost if running on the same machine
FTP_SERVER = '127.0.0.1'

FTP_USER = 'ftpuser'
FTP_PASS = 'ShizukeCruzer@7'
LOCAL_FILE = 'protected_file.txt'
REMOTE_FILE = 'good_file.txt'
POLL_INTERVAL = 30

def get_file_hash(filename):
    """Compute MD5 hash of a file."""
    hasher = hashlib.md5()
    with open(filename, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

def ftp_download_file():
    """Download the known-good file from the FTP server."""
    ftp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ftp_socket.connect((FTP_SERVER, 21))
    ftp_socket.recv(1024)  # Read welcome message

    ftp_socket.send(b'USER ' + FTP_USER.encode() + b'\r\n')
    ftp_socket.recv(1024)  # Read user response

    ftp_socket.send(b'PASS ' + FTP_PASS.encode() + b'\r\n')
    ftp_socket.recv(1024)  # Read pass response

    ftp_socket.send(b'TYPE I\r\n')  # Set binary mode
    ftp_socket.recv(1024)  # Read type response

    ftp_socket.send(b'PASV\r\n')  # Enter passive mode
    response = ftp_socket.recv(1024).decode()  # Read pasv response

    # Extract host and port for passive data connection
    start = response.find('(') + 1
    end = response.find(')')
    parts = response[start:end].split(',')
    data_host = '.'.join(parts[:4])
    data_port = (int(parts[4]) << 8) + int(parts[5])

    # Open passive data connection
    data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    data_socket.connect((data_host, data_port))

    ftp_socket.send(b'RETR ' + REMOTE_FILE.encode() + b'\r\n')
    ftp_socket.recv(1024)  # Read retr response

    with open(LOCAL_FILE, 'wb') as f:
        while True:
            data = data_socket.recv(1024)
            if not data:
                break
            f.write(data)

    data_socket.close()
    ftp_socket.send(b'QUIT\r\n')
    ftp_socket.close()

def monitor_file():
    """Monitor the protected file and restore if modified or deleted."""
    last_hash = get_file_hash(LOCAL_FILE) if os.path.exists(LOCAL_FILE) else None

    while True:
        try:
            current_hash = get_file_hash(LOCAL_FILE) if os.path.exists(LOCAL_FILE) else None
            if current_hash != last_hash:
                print(f"File changed or deleted. Restoring from FTP server...")
                ftp_download_file()
                last_hash = get_file_hash(LOCAL_FILE)
                print(f"Restored file with hash: {last_hash}")
            else:
                print(f"No changes detected. File hash: {current_hash}")
        except Exception as e:
            print(f"Error: {e}")

        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    monitor_file()
