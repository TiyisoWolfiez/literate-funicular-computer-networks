import socket
import random
import textwrap


# Authors: Tshegofatso Mapheto and Sello Selepe
# Function to wrap text to a specified width
def wrap_text(text, width=80):
    return '\n'.join(textwrap.wrap(text, width))

# ANSI escape sequences for screen control
CLEAR_SCREEN = '\x1b[2J'
MOVE_CURSOR = '\x1b[{};{}H'

# Function to read and parse the quiz file
def load_quiz(filename):
    quiz = []
    with open(filename, 'r') as file:
        question = None
        for line in file:
            if line.startswith('?'):
                if question:
                    if not question['correct']:
                        question['choices'].append('None of the above')
                        question['correct'] = chr(ord('A') + len(question['choices']) - 1)
                    elif len(question['correct']) > 1:
                        question['choices'].append('More than one of the above')
                        question['correct'] = chr(ord('A') + len(question['choices']) - 1)
                    quiz.append(question)
                question = {'question': line[1:].strip(), 'choices': [], 'correct': []}
            elif line.startswith('-') or line.startswith('+'):
                if line.startswith('+'):
                    question['correct'].append(chr(ord('A') + len(question['choices'])))
                question['choices'].append(line[1:].strip())
        if question:
            if not question['correct']:
                question['choices'].append('None of the above')
                question['correct'] = chr(ord('A') + len(question['choices']) - 1)
            elif len(question['correct']) > 1:
                question['choices'].append('More than one of the above')
                question['correct'] = chr(ord('A') + len(question['choices']) - 1)
            quiz.append(question)
    return quiz

# Function to handle a client connection
def handle_client(client_socket, quiz):
    try:
        client_socket.sendall(CLEAR_SCREEN.encode())

        score = 0
        question_count = 0
        remaining_questions = quiz[:]  # Make a copy of the quiz list

        while remaining_questions:
            # Clear the screen before showing a new question
            client_socket.sendall(CLEAR_SCREEN.encode())

            question = random.choice(remaining_questions)
            # Wrap the question text
            wrapped_question = wrap_text(question['question'])
            client_socket.sendall((MOVE_CURSOR.format(1, 1) + wrapped_question + '\n').encode())
            
            for i, choice in enumerate(question['choices']):
                # Wrap each choice text
                wrapped_choice = wrap_text('{}) {}'.format(chr(ord('A') + i), choice))
                client_socket.sendall((wrapped_choice + '\n').encode())

            client_socket.sendall(MOVE_CURSOR.format(len(wrapped_question.split('\n')) + len(question['choices']) + 3, 1).encode())
            client_socket.sendall('Your answer (A/B/C/D): '.encode())
            
            answer = client_socket.recv(1).decode().strip().upper()  # Accept lowercase
            answer = answer[0] if answer else None  # Consider only the first character

            if answer == question['correct']:
                response = ' Congratulations! Correct answer.\n'
                score += 1
            else:
                response = ' Incorrect. The correct answer was {}.\n'.format(question['correct'])
            client_socket.sendall(response.encode())

            question_count += 1
            remaining_questions.remove(question)  # Remove the asked question

            if remaining_questions:  # Only prompt to continue if there are questions left
                client_socket.sendall('Do you want to continue? (yes/no): '.encode())
                continue_response = client_socket.recv(1024).decode().strip().lower()
                if continue_response.startswith('n'):
                    break
                elif not continue_response.startswith('y'):
                    client_socket.sendall(CLEAR_SCREEN.encode())  # Clear screen for potential message to type "yes" or "no"
                    client_socket.sendall('Please type "yes" or "no": '.encode())
            else:
                client_socket.sendall('No more questions left. Thank you for participating!\n'.encode())
                break

        # Final score display
        client_socket.sendall(f'Your final score: {score}/{question_count}.\n'.encode())

    except Exception as e:
        print("An exception occurred: ", e)
    finally:
        client_socket.close()

# Main function to start the Telnet server
def start_quiz_server(port, quiz_file):
    quiz = load_quiz(quiz_file)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('', port))
    server_socket.listen(5)

    print(f'Server listening on port {port}...')

    while True:
        client_socket, addr = server_socket.accept()
        print(f'Connection from {addr}')
        handle_client(client_socket, quiz)

# Replace 'quiz.txt' with the path to your quiz file
if __name__ == '__main__':
    start_quiz_server(55555, 'quiz.txt')