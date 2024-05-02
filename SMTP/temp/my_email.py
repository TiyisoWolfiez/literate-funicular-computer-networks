import socket
import ssl
import base64
import datetime
import vonage
import email.parser
from twilio.rest import Client

# Replace with your SMTP server hostname and port number
host = 'smtp.gmail.com'
port = 587
username = 'p@gmail.com' #created email address
password = 'hexslwgjyjenpar' # account gmail


client = vonage.Client(key="", secret="")
sms = vonage.Sms(client)

name_or_event = []
eventlist = []
eventslist = ''
eventsToday = []
eventToday = ''

with open('events.txt', 'r') as f:
    # Get today's date
    today = datetime.datetime.now().date()

    # Loop over each line in the file
    for line in f:

        # Split the line into its components
        parts = line.strip().split(' ')

        # Get the date from the first two parts
        day, month = int(parts[0].split('/')[0]), int(parts[0].split('/')[1])

        # Get the name or event from the remaining parts
        name_or_event=' '.join(parts[1:])

        # Calculate the date for the event
        event_date = datetime.date(today.year, month, day)

        diffdays = event_date.day - today.day

        if diffdays == 0:
            print(f"Event '{name_or_event}' occurs exactly today ({today}).")
            eventsToday.append(name_or_event)

        if diffdays == 6:
            print(f"Event '{name_or_event}' occurs exactly 6 days from today ({today}).")
            eventlist.append(name_or_event)

if(len(eventsToday)>0):
    for t in eventsToday:
        if eventToday == '':
            eventToday = eventToday+t
        else:
            eventToday = eventToday+"," + t

if (len(eventlist)>0):
    for event in eventlist:
        if eventslist == "":
            eventslist = eventslist+event
        else:
            eventslist = eventslist+","+event


#Vonage Create Api Account
if len(eventsToday)>0:
    responseData = sms.send_message(
    {
        "from": "Vonage APIs",
        "to": "" , #number
        "text": "Events {} occurs exactly today ({})".format(eventToday,today),
    }
    )
    if responseData["messages"][0]["status"] == "0":
      print("Message sent successfully.")
    else:
        print(f"Message failed with error: {responseData['messages'][0]['error-text']}")


if len(eventlist)>0:
    
# Establish a plain socket connection to the SMTP server
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket:
        socket.connect((host, port))
        response = socket.recv(1024)
        print(response.decode())

        # Send the EHLO command to initiate the SMTP conversation
        ehlo_command = 'EHLO {}\r\n'.format(host)
        socket.sendall(ehlo_command.encode())
        response = socket.recv(1024)
        print(response.decode())

        # Check if the server supports STARTTLS
        if b'STARTTLS' in response:
            # Send the STARTTLS command to initiate the TLS handshake
            starttls_command = 'STARTTLS\r\n'
            socket.sendall(starttls_command.encode())
            response = socket.recv(1024)
            print(response.decode())

            # Upgrade the plain socket to an SSL socket using TLS
            ssl_socket = ssl.wrap_socket(socket, ssl_version=ssl.PROTOCOL_TLSv1_2)

            # Send the EHLO command again to initiate the SMTP conversation over TLS
            ehlo_command = 'EHLO {}\r\n'.format(host)
            ssl_socket.sendall(ehlo_command.encode())
            response = ssl_socket.recv(1024)
            print(response.decode())

            # Send the authentication commands over the SSL socket
            auth_command = 'AUTH LOGIN\r\n'
            ssl_socket.sendall(auth_command.encode())
            response = ssl_socket.recv(1024)
            print(response.decode())

            # Encode the username and password as base64 and send them to the server
            username_b64 = base64.b64encode(username.encode()).decode()
            password_b64 = base64.b64encode(password.encode()).decode()
            ssl_socket.sendall((username_b64 + '\r\n').encode())
            response = ssl_socket.recv(1024)
            print(response.decode())
            ssl_socket.sendall((password_b64 + '\r\n').encode())
            response = ssl_socket.recv(1024)
            print(response.decode())

            # Send the rest of the SMTP commands over the SSL socket
            mail_from_command = 'MAIL FROM:<paccos06@gmail.com>\r\n'
            ssl_socket.sendall(mail_from_command.encode())
            response = ssl_socket.recv(1024)
            print(response.decode())

            rcpt_to_command = 'RCPT TO:<siyabongambuyisa7@gmail.com>\r\n'
            ssl_socket.sendall(rcpt_to_command.encode())
            response = ssl_socket.recv(1024)
            print(response.decode())

            data_command = 'DATA\r\n'
            ssl_socket.sendall(data_command.encode())
            response = ssl_socket.recv(1024)
            print(response.decode())

            
            header = 'Subject: REMIND OF UPCOMING EVENTS\r\n'
            message = 'There is upcoming events {} occurs exactly 6 days from today.\r\n'.format(eventslist)
            end_of_message = '\r\n.\r\n'
            ssl_socket.sendall((header + message + end_of_message).encode())
            response = ssl_socket.recv(1024)
            print(response.decode())

            quit_command = 'QUIT\r\n'
            ssl_socket.sendall(quit_command.encode())
            response = ssl_socket.recv(1024)
            print(response.decode())

            # Close the SSL socket
            ssl_socket.close()

    # Close the plain socket
    socket.close()
else:
    print('No events happen exactly 6 days from today')


