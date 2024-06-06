import socket

# Authors: Tshegofatso Mapheto and Sello Selepe

# Function to read Fibonacci numbers from file
def read_fibonacci_numbers():
    try:
        with open("fib.txt", "r") as file:
            content = file.readline()
        return content
    except FileNotFoundError:
        return "Fibonacci file not found!"
    except IOError:
        return "Error reading Fibonacci file!"

# Function to update Fibonacci numbers in file
def update_fibonacci_numbers(new_numbers):
    try:
        with open("fib.txt", "w") as file:
            file.write(new_numbers)
        return new_numbers
    except IOError:
        return None

# Function to generate HTML content based on Fibonacci sequence
def generate_html_content(fibonacci_content):
    if fibonacci_content is None:
        fibonacci_content = "Fibonacci sequence is not available."
    
    fib_array = list(map(int, fibonacci_content.split(",")))

    # Check if the sequence is at 0, 1, 1 to disable "Previous" button
    disable_previous = False
    if len(fib_array) >= 3 and fib_array[-3:] == [0, 1, 1]:
        disable_previous = True

    html_content = """
    <html>
    <head>
        <title>Fibonacci Sequence</title>
        <style>
            body {{ background-color: lightblue; font-family: Arial, sans-serif; margin: 0; display: flex; justify-content: center; align-items: center; height: 100vh; }}
            .content {{ text-align: center; }}
            .button-container {{ margin-top: 20px; }}
            .button {{ padding: 10px 20px; font-size: 16px; margin-right: 10px; background-color: black; color: white; }}
        </style>
    </head>
    <body>
        <div class="content">
            <h1>Fibonacci Sequence</h1>
            <p>{}</p>
            <div class="button-container">
                <form action="/" method="post">
                    <input type="submit" name="previous" class="button" value="Previous" {}>
                    <input type="submit" name="next" class="button" value="Next">
                </form>
            </div>
        </div>
    </body>
    </html>
    """.format(fibonacci_content, 'disabled' if disable_previous else '')
    return html_content

# Function to handle client requests
def handle_request(client_socket):
    try:
        request = client_socket.recv(1024).decode()
        request_lines = request.split("\r\n")
        request_method = request_lines[0].split(" ")[0]

        if request_method == "GET":
            fibonacci_content = read_fibonacci_numbers()
            response = "HTTP/1.1 200 OK\r\n"
            response += "Content-Type: text/html\r\n\r\n"
            response += generate_html_content(fibonacci_content)
            client_socket.sendall(response.encode())
        elif request_method == "POST":
            post_data = request_lines[-1]
            
            if "previous" in post_data:
                fibonacci_content = read_fibonacci_numbers()
                fib_array = list(map(int, fibonacci_content.split(",")))
                new_first = fib_array[1] - fib_array[0]
                updated_content = update_fibonacci_numbers("{},{},{}".format(new_first, fib_array[0], fib_array[1]))
                
                if updated_content:
                    response = "HTTP/1.1 200 OK\r\n"
                    response += "Content-Type: text/html\r\n\r\n"
                    response += generate_html_content(updated_content)
                else:
                    response = "HTTP/1.1 500 Internal Server Error\r\n"
                    response += "Content-Type: text/html; charset=utf-8\r\n\r\n"
                    response += "Internal Server Error. Please try again later."
            elif "next" in post_data:
                fibonacci_content = read_fibonacci_numbers()
                fib_array = list(map(int, fibonacci_content.split(",")))
                new_first = fib_array[1]
                new_second = fib_array[2]
                new_third = fib_array[1] + fib_array[2] #"fib_array[0] + "
                updated_content = update_fibonacci_numbers("{},{},{}".format(new_first, new_second, new_third))
                
                if updated_content:
                    response = "HTTP/1.1 200 OK\r\n"
                    response += "Content-Type: text/html\r\n\r\n"
                    response += generate_html_content(updated_content)
                else:
                    response = "HTTP/1.1 500 Internal Server Error\r\n"
                    response += "Content-Type: text/html; charset=utf-8\r\n\r\n"
                    response += "Internal Server Error. Please try again later."
            else:
                response = "HTTP/1.1 400 Bad Request\r\n"
                response += "Content-Type: text/html; charset=utf-8\r\n\r\n"
                response += "Bad Request."
            
            client_socket.sendall(response.encode())

        client_socket.close()
    except IOError as e:
        response = "HTTP/1.1 500 Internal Server Error\r\n"
        response += "Content-Type: text/html; charset=utf-8\r\n\r\n"
        response += "Internal Server Error. Please try again later."
        client_socket.sendall(response.encode())
        client_socket.close()

# Main function to run the server
def main():
    host = 'localhost'
    port = 55555

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)
    print("Server is listening on port", port)

    while True:
        client_socket, addr = server_socket.accept()
        print("Connection from", addr)
        handle_request(client_socket)

    server_socket.close()

if __name__ == "__main__":
    main()
