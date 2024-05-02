import socket
import random
import re
from threading import Thread

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
                    "user_answer": None
                }
            elif line.startswith("-") or line.startswith("+"):
                if line.startswith("+"):
                    question["correct"] = chr(ord('A') + len(question["choices"]))
                question["choices"].append(line[1:].strip())
    random.shuffle(quiz)  # Shuffle the quiz questions
    return quiz

def generate_html_content(question, choices, score, total_questions, num_answered):
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
            .score {{ font-weight: bold; margin-top: 20px; }}
            .correct {{ color: green; }}
            .incorrect {{ color: red; }}
        </style>
    </head>
    <body>
        <div class="content">
            <h1>Quiz</h1>
            <div class="question">{wrapped_question}</div>
            <form id="quiz-form" action="/" method="post" onsubmit="return validateForm()">
    """
    for i, choice in enumerate(choices):
        html_content += f"""
                <input type="radio" id="choice{i}" name="answer" value="{chr(ord('A') + i)}">
                <label class="choice" for="choice{i}">{chr(ord('A') + i)}) {choice}</label><br>
        """
    html_content += """
                <br><input type="submit" name="action" value="Submit">
            </form>
    """
    if num_answered == total_questions:
        html_content += f"""
            <div class="score">Score: {score}/{total_questions}</div>
        """
    html_content += """
        </div>
        <script>
            function validateForm() {
                var form = document.getElementById("quiz-form");
                var selectedAnswer = false;
                var inputs = form.elements["answer"];
                for (var i = 0; i < inputs.length; i++) {
                    if (inputs[i].checked) {
                        selectedAnswer = true;
                        break;
                    }
                }
                // Check if action is "Submit" before displaying the alert
                if (!selectedAnswer && document.activeElement.value === "Submit") {
                    alert("Please select an answer.");
                    return false;
                }
                return true;
            }
        </script>
    </body>
    </html>
    """
    return html_content

def handle_client(client_socket, question_data, quiz, user_scores):
    try:
        request = client_socket.recv(1024).decode()
        request_lines = request.split("\r\n")
        request_method = request_lines[0].split(" ")[0]

        if request_method == "GET":
            question = question_data["question"]
            choices = question_data["choices"]
            current_score = sum(user_scores)
            total_questions = len(quiz)
            html_content = generate_html_content(question, choices, current_score, total_questions, len(user_scores))
            response = "HTTP/1.1 200 OK\r\n"
            response += "Content-Type: text/html\r\n\r\n"
            response += html_content
            client_socket.sendall(response.encode())

        elif request_method == "POST":
            post_data = request_lines[-1]  # Get the POST data from the request
            answer_match = re.search(r"answer=([A-Z])", post_data)
            if answer_match:
                user_answer = answer_match.group(1)
                question_index = quiz.index(question_data)
                correct_answer = question_data["correct"]
                if user_answer == correct_answer:
                    result = "Congratulations! Your answer is correct."
                    user_scores[question_index] += 1  # Increase score
                    feedback_class = "correct"
                else:
                    result = f"Incorrect. The correct answer was {correct_answer}."
                    feedback_class = "incorrect"

                next_question_index = question_index + 1
                if next_question_index < len(quiz):
                    question_data = quiz[next_question_index]
                question = question_data["question"]
                choices = question_data["choices"]
                current_score = sum(user_scores)
                total_questions = len(quiz)
                html_content = generate_html_content(question, choices, current_score, total_questions, len(user_scores))
                response = "HTTP/1.1 200 OK\r\n"
                response += "Content-Type: text/html\r\n\r\n"
                response += html_content.replace('<div class="question">', f'<div class="question {feedback_class}">').replace('<input type="submit" name="action" value="Submit">', '')
                client_socket.sendall(response.encode())

            else:
                total_score = sum(user_scores)
                response = "HTTP/1.1 200 OK\r\n"
                response += "Content-Type: text/html\r\n\r\n"
                response += f"""
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
                        <p>Total Score: {total_score}/{len(quiz)}</p>
                    </div>
                </body>
                </html>
                """
                client_socket.sendall(response.encode())

    except Exception as e:
        print("Error:", e)
    finally:
        client_socket.close()

def start_server(port, quiz):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', port))
    server_socket.listen()

    print(f"Server started on port {port}. Open http://localhost:{port} to take the quiz.")

    question_data = None
    user_scores = [0] * len(quiz)

    while True:
        client_socket, addr = server_socket.accept()
        print("Connection from", addr)

        if question_data is None:  # Start with the first question
            question_data = quiz[0]

        client_thread = Thread(target=handle_client, args=(client_socket, question_data, quiz, user_scores))
        client_thread.start()

if __name__ == "__main__":
    quiz = load_quiz("quiz.txt")
    start_server(55555, quiz)