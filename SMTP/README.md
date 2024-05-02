# Documentation

This Python script is used to send an email with a score to a specified receiver. The email is sent using the SMTP protocol over a secure SSL connection. The script uses environment variables to store sensitive information such as the email password.

## Dependencies

The script uses the following Python libraries:

- `socket`: This library provides low-level networking interface. It's used to establish a connection to the SMTP server.
- `ssl`: This library is used to upgrade the plain socket connection to an SSL encrypted connection.
- `base64`: This library is used to encode the email username and password in base64 as required by the SMTP protocol.
- `os`: This library is used to access environment variables.
- `dotenv`: This library is used to load environment variables from a .env file.

## Environment Variables

The script uses the following environment variables:

- `EMAIL_PASSWORD`: The password for the sender's email account.
- `SENDER_EMAIL`: The email address of the sender.
- `PORT`: The port number to connect to the SMTP server. Usually, port 587 is used for SMTP.
- `HOST`: The hostname of the SMTP server. For Gmail, it's `smtp.gmail.com`.
- `RECEIVER_EMAIL`: The email address of the receiver.

These variables are stored in a .env file and loaded using the `dotenv` library.

## .env File

The script requires a .env file in the same directory with the following structure:

```properties
EMAIL_PASSWORD = "YourEmailPassword"
SENDER_EMAIL = "YourEmailAddress"
PORT = 587
HOST = "smtp.gmail.com"
RECEIVER_EMAIL = "ReceiverEmailAddress"
```

Replace `YourEmailPassword`, `YourEmailAddress`, and `ReceiverEmailAddress` with your actual email password, your email address, and the receiver's email address respectively.

## How It Works

The script first loads the environment variables using `load_dotenv()`. Then it defines a function `send_email` which takes the sender email, receiver email, host, port, password, and score as parameters.

The `send_email` function performs the following steps:

- **Establishes a socket connection to the SMTP server**: The function uses the `socket` library to create a socket and connect to the SMTP server. The `socket` library provides a low-level networking interface.

- **Sends the EHLO command**: The function sends the EHLO command to the SMTP server to initiate the SMTP conversation. EHLO is an SMTP command that's sent by an email server to identify itself when connecting to another email server to start the process of sending an email.

- **Checks if the server supports STARTTLS**: The function checks the server's response to the EHLO command to see if it includes 'STARTTLS'. STARTTLS is an SMTP command that tells the server to switch to a secure TLS connection.

- **Sends the STARTTLS command**: If the server supports STARTTLS, the function sends the STARTTLS command to initiate the TLS handshake. This upgrades the connection to a secure connection.

- **Upgrades the socket to an SSL socket**: The function uses the `ssl` library to upgrade the plain socket connection to an SSL encrypted connection. This ensures that the email data is encrypted and secure.

- **Sends the EHLO command again**: The function sends the EHLO command again, but this time over the secure SSL connection. This is done because the SMTP conversation needs to be restarted for the secure connection.

- **Sends the AUTH LOGIN command**: The function sends the AUTH LOGIN command to start the authentication process. AUTH LOGIN is an SMTP command that tells the server that the client wants to authenticate with a username and password.

- **Encodes the username and password in base64**: The function encodes the email username and password in base64 and sends them to the server. SMTP requires the username and password to be base64 encoded.

- **Sends the MAIL FROM command**: The function sends the MAIL FROM command with the sender's email address. This tells the server who's sending the email.

- **Sends the RCPT TO command**: The function sends the RCPT TO command with the receiver's email address. This tells the server who the email is being sent to.

- **Sends the DATA command**: The function sends the DATA command to start the data section of the email. This tells the server that what follows is the body of the email.

- **Sends the email headers, message, and end of message marker**: The function sends the email headers (like the subject), the message body (which includes the score), and the end of message marker (a line with just a period). This is the content of the email.

- **Sends the QUIT command**: The function sends the QUIT command to end the SMTP conversation. This tells the server that it has finished sending the email.

- **Closes the SSL and plain socket connections**: Finally, the function closes the SSL and plain socket connections. This is done to free up system resources.

Finally, the script checks if the `send_mail` variable is True. If it is, it calls the `send_email` function with the appropriate parameters. If not, it prints a message saying that the results will be released later.