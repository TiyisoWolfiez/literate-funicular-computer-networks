import java.io.*;
import java.net.*;
import java.util.*;

public class QuizServer {
    public static String wrapText(String text, int width) {
        return String.join("\n", Arrays.asList(text.split("(?<=\\G.{" + width + "})")));
    }

    public static final String CLEAR_SCREEN = "\033[2J";
    public static final String MOVE_CURSOR = "\033[%d;%dH";
    public static List<Map<String, Object>> loadQuiz(String filename) throws IOException {
        List<Map<String, Object>> quiz = new ArrayList<>();
        try (BufferedReader br = new BufferedReader(new FileReader(filename))) {
            String line;
            Map<String, Object> question = null;
            while ((line = br.readLine()) != null) {
                if (line.startsWith("?")) {
                    if (question != null) {
                        quiz.add(question);
                    }
                    question = new HashMap<>();
                    question.put("question", line.substring(1).trim());
                    question.put("choices", new ArrayList<String>());
                    question.put("correct", null);
                } else if (line.startsWith("-") || line.startsWith("+")) {
                    if (line.startsWith("+")) {
                        question.put("correct", Character.toString((char) ('A' + ((List<String>) question.get("choices")).size())));
                    }
                    ((List<String>) question.get("choices")).add(line.substring(1).trim());
                }
            }
            if (question != null) {
                quiz.add(question);
            }
        }
        return quiz;
    }
    public static void handleClient(Socket clientSocket, List<Map<String, Object>> quiz) {
        try {
            PrintWriter out = new PrintWriter(clientSocket.getOutputStream(), true);
            BufferedReader in = new BufferedReader(new InputStreamReader(clientSocket.getInputStream()));

            out.print(CLEAR_SCREEN);
            out.flush();

            int score = 0;
            int questionCount = 0;
            List<Map<String, Object>> remainingQuestions = new ArrayList<>(quiz);

            Random random = new Random();

            while (!remainingQuestions.isEmpty()) {
                out.print(CLEAR_SCREEN);
                out.flush();

                Map<String, Object> question = remainingQuestions.get(random.nextInt(remainingQuestions.size()));
                String wrappedQuestion = wrapText((String) question.get("question"), 80);
                out.print(String.format(MOVE_CURSOR, 1, 1) + wrappedQuestion + "\n");

                List<String> choices = (List<String>) question.get("choices");
                for (int i = 0; i < choices.size(); i++) {
                    String wrappedChoice = wrapText(String.format("%c) %s", 'A' + i, choices.get(i)), 80);
                    out.print(wrappedChoice + "\n");
                }

                out.print(String.format(MOVE_CURSOR, wrappedQuestion.split("\n").length + choices.size() + 3, 1));
                out.print("Your answer: ");
                out.flush();

                String answer = in.readLine();
                answer = (answer != null) ? answer.trim().toUpperCase() : null;
                if (answer != null && !answer.isEmpty() && answer.length() == 1 &&
                    answer.charAt(0) == ((String) question.get("correct")).charAt(0)) {
                    out.print("Congratulations! Your answer is correct.\n");
                    score++;
                } else {
                    out.print("Incorrect. The correct answer was " + question.get("correct") + ".\n");
                }
                out.flush();


                questionCount++;
                remainingQuestions.remove(question);

                if (!remainingQuestions.isEmpty()) {
                    out.print("Do you want to continue? (yes/no): ");
                    out.flush();
                    String continueResponse = in.readLine();
                    if (continueResponse != null && continueResponse.trim().toLowerCase().startsWith("n")) {
                        break;
                    } else if (continueResponse == null || !continueResponse.trim().toLowerCase().startsWith("y")) {
                        out.print(CLEAR_SCREEN);
                        out.print("Please type \"yes\" or \"no\": ");
                        out.flush();
                    }
                } else {
                    out.print("No more questions left. Thank you for participating!\n");
                    out.flush();
                    break;
                }
            }

            out.print("Your final score: " + score + "/" + questionCount + ".\n");
            out.flush();

        } catch (IOException e) {
            e.printStackTrace();
        } finally {
            try {
                clientSocket.close();
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }
    public static void main(String[] args) throws IOException {
        int port = 55555;
        String quizFile = "questions.txt";

        if (args.length > 0) {
            try {
                port = Integer.parseInt(args[0]);
            } catch (NumberFormatException e) {
                System.err.println("Invalid port number, using default port 55555.");
            }
        }
        if (args.length > 1) {
            quizFile = args[1];
        }

        List<Map<String, Object>> quiz = loadQuiz(quizFile);

        try (ServerSocket serverSocket = new ServerSocket(port)) {
            System.out.println("Server listening on port " + port + "...");
            while (true) {
                Socket clientSocket = serverSocket.accept();
                System.out.println("Connection from " + clientSocket.getRemoteSocketAddress());
                
                new Thread(() -> handleClient(clientSocket, quiz)).start();
            }
        }
    }
}
