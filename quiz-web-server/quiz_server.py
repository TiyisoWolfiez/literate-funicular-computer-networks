import socket
import random
import re
from threading import Thread

QUIZ_LEN = 3

def wrap_text(text, width):
    return "<br>".join([text[i:i + width] for i in range(0, len(text), width)])


def load_quiz(filename):
    quiz = []
    with open(filename, "r") as file:
        lines = file.readlines()
        question = {}
        for line in lines:
            if line.startswith("?"):
                if question:
                    quiz.append(question)
                question = {
                    "question": line[1:].strip(),
                    "choices": [],
                    "correct": None,
                    "user_answer": None  # Add a field to store user's answer
                }
            elif line.startswith("-") or line.startswith("+"):
                if line.startswith("+"):
                    question["correct"] = chr(ord('A') + len(question["choices"]))
                question["choices"].append(line[1:].strip())
        if question:
            quiz.append(question)
    
    return quiz


def generate_html_content(question, choices):
    wrapped_question = wrap_text(question, 80)
    html_content = f"""
    <html>
    <head>
        <title>Quiz</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; display: flex; justify-content: center; align-items: center; height: 100vh; }}
            .content {{ text-align: left; padding: 20px; }}
            .question {{ font-weight: bold; }}
            .choice {{ margin-left: 20px; }}
        </style>
    </head>
    <body>
        <div class="content">
            <h1>Quiz</h1>
            <div class="question">{wrapped_question}</div>
            <form action="/" method="post">
    """
    for i, choice in enumerate(choices):
        html_content += f"""
                <input type="radio" id="choice{i}" name="answer" value="{chr(ord('A') + i)}">
                <label class="choice" for="choice{i}">{chr(ord('A') + i)}) {choice}</label><br>
        """
    html_content += """
                <br><input type="submit" value="Submit">
            </form>
        </div>
    </body>
    </html>
    """
    return html_content


def display_results(total_questions, total_correct):
    html_content = f"""
        <html>
        <head>
            <title>Quiz Result</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; display: flex; justify-content: center; align-items: center; height: 100vh; }}
                .result {{ text-align: center; }}
            </style>
        </head>
        <body>
            <div class="result">
                <h1>Quiz Result</h1>
                <p>Total questions: {total_questions}</p>
                <p>Total correct answers: {total_correct}</p>
                <p>Total score: {total_correct}/{total_questions}</p>
            </div>
        </body>
        </html>
    """
    return html_content


def display_solution(result):
    html_content = f"""
        <html>
        <head>
            <title>Quiz Result</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; display: flex; justify-content: center; align-items: center; height: 100vh; }}
                .result {{ text-align: center; }}
            </style>
        </head>
        <body>
            <div class="result">
                <h1>Quiz Result</h1>
                <p>{result}</p>
                <br><a href="/">Return to Quiz</a>
            </div>
        </body>
        </html>
        """
    return html_content


def display_result_solution(total_questions, total_correct, result):
    html_content = f"""
        <html>
        <head>
            <title>Quiz Result</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; display: flex; justify-content: center; align-items: center; height: 100vh; }}
             display_solution   .result {{ text-align: center; }}
            </style>
        </head>
        <body>
            <div class="result">
                <h1>Quiz Result</h1>
                <p>{result}</p>
                <br>
                <h1>Overall Results</h1>
                <p>Total questions: {total_questions}</p>
                <p>Total correct answers: {total_correct}</p>
                <p>Total score: {total_correct}/{total_questions}</p>
            </div>
        </body>
        </html>
        """
    return html_content


def handle_client(client_socket, question_data, user_answers, scores):
    try:
        request = client_socket.recv(1024).decode()
        request_lines = request.split("\r\n")
        request_method = request_lines[0].split(" ")[0]

        if request_method == "GET":
            question = question_data["question"]
            choices = question_data["choices"]
            html_content = generate_html_content(question, choices)
            response = "HTTP/1.1 200 OK\r\n"
            response += "Content-Type: text/html\r\n\r\n"
            response += html_content
            client_socket.sendall(response.encode())
        elif request_method == "POST":
            post_data = request_lines[-1]
            answer_match = re.search(r"answer=([A-Z])", post_data)
            if answer_match:
                user_answer = answer_match.group(1)
                user_answers.append(user_answer)
                correct_answer = question_data["correct"]
                
                if user_answer == correct_answer:
                    result = "Congratulations! Your answer is correct."
                    scores[0] += 1 
                else:
                    result = f"Incorrect. The correct answer was {correct_answer}."

                if len(user_answers) == QUIZ_LEN:
                    # Send the result back to the client
                    response = "HTTP/1.1 200 OK\r\n"
                    response += "Content-Type: text/html\r\n\r\n"
                    response += display_result_solution(scores[0], QUIZ_LEN, result)
                    try:
                        client_socket.sendall(response.encode())
                    except OSError as e:
                        print("Error sending response:", e)
                else:
                    # Send the result back to the client
                    response = "HTTP/1.1 200 OK\r\n"
                    response += "Content-Type: text/html\r\n\r\n"
                    response += display_solution(result)
                    try:
                        client_socket.sendall(response.encode())
                    except OSError as e:
                        print("Error sending response:", e)
    finally:
        client_socket.close()
        

def start_server(port, quiz):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', port))
    server_socket.listen()

    print(f"Server started on port {port}.\nOpen http://localhost:{port} to take the quiz.")

    user_answers = [] 
    scores = [0]
    while True:
        if len(user_answers) == len(quiz): 
            break
        else:
            client_socket, addr = server_socket.accept()
            random_question = random.choice(quiz)
            client_thread = Thread(target=handle_client, args=(client_socket, random_question, user_answers, scores))
            client_thread.start()

    total_questions = len(quiz)
    total_correct = scores[0]
    client_socket.close()

    print(f"Total questions: {total_questions}")
    print(f"Total correct answers: {total_correct}")
    print(f"Total score: {total_correct}/{total_questions}")


def main():
    host = 'localhost'
    port = 55555
    quiz = load_quiz("quiz.txt")
    start_server(port, quiz)


if __name__ == "__main__":
    main()