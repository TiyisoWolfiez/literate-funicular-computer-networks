from http.server import BaseHTTPRequestHandler, HTTPServer
import random
import urllib.parse
import smtplib
import ssl
import os
from dotenv import load_dotenv, dotenv_values

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
                self.send_email(session, email_address)
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

    def send_email(self, session, email_address):
        load_dotenv()
        email_sender = os.getenv("SENDER_EMAIL")
        email_password = os.getenv("EMAIL_PASSWORD")
        message = f"From: {email_sender}\nTo: {email_address}\nSubject: Quiz Results\n\nQuiz completed! Your final score: {self.sessions[session]['score']}"
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as server:
            server.login(email_sender, email_password)
            server.sendmail(email_sender, email_address, message)

def run(server_class=HTTPServer, handler_class=QuizHandler, port=8080):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print('Starting httpd on port', port)
    httpd.serve_forever()

if __name__ == '__main__':
    run()
