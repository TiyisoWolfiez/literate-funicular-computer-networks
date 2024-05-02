from http.server import BaseHTTPRequestHandler, HTTPServer
import random
import urllib.parse
import ssl
import os
import socket
import ssl
import base64
import os
from dotenv import load_dotenv

load_dotenv()

host = os.getenv("HOST")
port = os.getenv("PORT")
username = os.getenv("SENDER_EMAIL")
password = os.getenv("EMAIL_PASSWORD")
receiver_email = os.getenv("RECEIVER_EMAIL")

def load_questions(filename):
    questions = []
    question_number = 0
    with open(filename, 'r') as file:
        question = None
        correct_count = 0
        for line in file:
            if line.startswith('?'):
                if question:
                    if correct_count > 1:
                        question['answers'].append('More than one of these is correct')
                        question['correct_multi'] = True
                    questions.append(question)
                question_number += 1
                question = {
                    'question': line[1:].strip(),
                    'answers': [],
                    'correct': None,
                    'correct_multi': False,
                    'number': question_number
                }
                correct_count = 0
            elif line.startswith('-') or line.startswith('+'):
                if line.startswith('+'):
                    correct_count += 1
                    if correct_count == 1:
                        question['correct'] = chr(ord('A') + len(question['answers']))
                question['answers'].append(line[1:].strip())
        if question:
            if correct_count > 1:
                question['answers'].append('More than one of these is correct')
                question['correct_multi'] = True
            questions.append(question)
    return questions

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

class QuizHandler(BaseHTTPRequestHandler):
    questions = load_questions('questions.txt')
    sessions = {}
    

    def _send_response(self, content, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(content.encode('utf-8'))

    def do_GET(self):
        session = self.address_string()
        if self.path == '/reset':
            self.sessions[session] = {
                'remaining_questions': self.questions.copy(),
                'score': 0
            }
            self.send_response(302)
            self.send_header('Location', '/')
            self.end_headers()
            return

        if session not in self.sessions or not self.sessions[session]['remaining_questions']:
            self.sessions[session] = {
                'remaining_questions': self.questions.copy(),
                'score': 0
            }
            content = "<html><head><title>Quiz Game</title></head><body><h1>Welcome to the Quiz Game!</h1><a href='/'>Start Quiz</a></body></html>"
            self._send_response(content)
            return

        question = random.choice(self.sessions[session]['remaining_questions'])
        content = f"<html><head><title>Quiz Game</title></head><body><h1>Question {question['number']}: {question['question']}</h1><form method='POST'>"
        for i, answer in enumerate(question['answers']):
            content += f"<input type='radio' name='answer' value='{chr(ord('A') + i)}'/> {answer}<br>"
        content += "<input type='submit' value='Submit'/></form></body></html>"
        self._send_response(content)

    def do_POST(self):
        session = self.address_string()
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        data = urllib.parse.parse_qs(post_data)

        if self.path == '/submit_email':
            email_address = data.get('email', [None])[0]
            if email_address:
                self.send_email(session)
                content = f"<html><head><title>Email Sent</title></head><body><h2>Email sent to {email_address} with your quiz results.</h2><a href='/'>Home</a></body></html>"
                self._send_response(content)
            return

        answer = data.get('answer', [None])[0]
        question = random.choice(self.sessions[session]['remaining_questions'])
        if answer == question['correct']:
            self.sessions[session]['score'] += 1
            response = "Correct!"
        else:
            response = f"Incorrect! Correct answer was {question['correct']}."

        self.sessions[session]['remaining_questions'].remove(question)
        if not self.sessions[session]['remaining_questions']:
            content = f"<html><head><title>Quiz Completed</title></head><body><h2>{response}</h2><h2>Quiz completed! Your final score: {self.sessions[session]['score']}</h2><form method='POST' action='/submit_email'><input type='text' name='email' placeholder='Enter your email'><input type='submit' value='Send Results'></form></body></html>"
        else:
            content = f"<html><head><title>Quiz Game</title></head><body><h2>{response}</h2><h2>Your score: {self.sessions[session]['score']}</h2><a href='/'>Next question</a></body></html>"
        self._send_response(content)

    def send_email(self, session):
        score = self.sessions[session]['score']
        if score is not None and score >= 0:
            send_email(username, receiver_email, host, port, password, score)
        else:
            print('Results will be released soon!')

def run(server_class=HTTPServer, handler_class=QuizHandler, port=8080):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print('Starting Server on PORT: ', port)
    httpd.serve_forever()

if __name__ == '__main__':
    run()
