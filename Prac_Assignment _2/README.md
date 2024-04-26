# Practical Assignment 2



## Background
A Telnet client is a tool available on all major operating systems for communication with servers. Typically,
one connects to a server by entering commands like `telnet <computer name>` or `telnet <computer name> <port number>`.
Telnet clients are primarily used for communication with Telnet servers, allowing users to work on remote Unix computers
or interact with various servers worldwide.

By default, Telnet clients echo characters locally, meaning they display each character as it's typed.
However, this behavior can be modified using the `localecho` setting. Some servers may not echo input, requiring localecho to be enabled on the client side.

For this assignment, the task is to create a specialized Telnet server. This server should work seamlessly with Telnet clients regardless of the `localecho` setting.
It should echo characters that the user is supposed to see, ensuring a smooth user experience.

# The Assignment

Your task is to develop a program that reads a file containing questions and answers in a specific format. These questions are formatted with `?`, wrong answers with `-`, and correct answers with `+`. The program should listen on port 55555 for Telnet connections.

Upon connection, the program should randomly select a question from the file and display it on the virtual terminal. The program should then prompt the user to enter the correct answer. If the answer is correct, the user should be congratulated; otherwise, the correct answer should be displayed.

After each question, the program should ask the user if they want to continue. Depending on the response, either the next question should be asked, or the user's score should be displayed.

If a question lacks a correct answer (`+`), the server should automatically add "None of the above" as an option and assume it to be correct. If a question has multiple correct answers, the server should automatically add "More than one of the above" as an option and assume it to be correct.

To enhance visual appeal, you may use ANSI escape sequences for screen manipulation.

# Usage
  1. Compile and run the program.
  2. Connect to the server via Telnet using the specified port.
  3. Answer questions presented by the server.
  4. Interact solely via Telnet for all interactions with the server.
