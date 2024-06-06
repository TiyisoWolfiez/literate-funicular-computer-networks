import socket
import base64
import os
from dotenv import load_dotenv

load_dotenv()

def userOptions():
    print('1. Send a message')
    print('2. Quit')
    choice = input('Enter your choice: ')
    message = ''
    if choice == '1':
        print('\t1. Confidentical Email')
        print('\t2. Normal Email')
        print('\t3. Friendly Email')
        choice = input('Enter Email Type Choice: ')
        if choice == '1':
            message = './data/confidential.txt'
        elif choice == '2':
            message = './data/normal.txt'
        elif choice == '3':
            message = './data/friendly.txt'
        else:
            print('Invalid choice. Please try again')
            userOptions()
    elif choice == '2':
        message = 'Quit'
    else:
        print('Invalid choice. Please try again')
        message = userOptions()
    return message

def main():
    # Array of users and passwords
    users = [
        {"username": "johndoe@gmail.com", "password": "password123"},
        {"username": "janedoe@gmail.com", "password": "password456"},
        {"username": "user@gmail.com", "password": "password789"},
    ]

    while True:
        # Get username and password from the user
        input_username = input('Enter your username: ')
        input_password = input('Enter your password: ')

        # Check if the user exists
        user_exists = False
        for user in users:
            if user['username'] == input_username and user['password'] == input_password:
                user_exists = True
                break

        if user_exists:
            print('User authenticated successfully.')
            break
        else:
            print('Invalid username or password. Please try again.')

    # Connect to PROXY server
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('localhost', 55555)
    s.connect(server_address)
    print('Connected to the server:', server_address)

    while True:

        # Get the message from the user
        message = userOptions()

        # Quit if the user wants to quit
        if message == 'Quit':
            s.close()
            return

        # Get the recipient from the user
        recipient = input('Enter the recipient mail: ')

        print("Please Choose a Mimetype:")
        print("\t1. application/octet-stream (base64)")
        print("\t2. text/plain")
        print("\t3. multipart/alternative")
        mimetype = input("Enter your choice: ")
        if mimetype == '1':
            mimetype = 'application/octet-stream'
        elif mimetype == '2':
            mimetype = 'text/plain'
        elif mimetype == '3':
            mimetype = 'multipart/alternative'
        else:
            print("Invalid choice. Defaulting to 'text/plain'")
            mimetype = 'text/plain'

        # Read the message from the file
        with open(message, 'r') as f:
            message = f.read()

        if mimetype == 'application/octet-stream':
            message = base64.b64encode(message.encode('utf-8')).decode('utf-8')

        print("Encoded Message:", message)
        print("Encoded Message Type:", type(message))

        # Add the recipient to the message
        message = "To: " + recipient + '\n' + message
        message = "MIME-Version: 1.0\nContent-Type: " + mimetype + "\n" + message

        print("Final Message", message)

        # Send the message to the proxy server
        print("About to send message to proxy")
        s.sendall(message.encode())
        print("Message sent to proxy")
        while True:
            resp = s.recv(1024).decode()
            if resp:
                break
        print('Proxy response:', resp)

if __name__ == '__main__':
    main()
