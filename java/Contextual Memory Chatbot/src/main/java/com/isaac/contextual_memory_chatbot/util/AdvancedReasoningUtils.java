package com.isaac.contextual_memory_chatbot.util;

import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.chat.prompt.ChatOptions;

/**
 * Utility class for advanced reasoning prompting techniques:
 * - Step-back prompting
 * - Chain of Thought (CoT)
 * - Self-consistency
 * - Tree of Thoughts (ToT)
 */
public class AdvancedReasoningUtils {


    private AdvancedReasoningUtils() {
        // Utility class, no instantiation needed
    }

    /**
     * Demonstrates step-back prompting technique
     *
     * @param chatClientBuilder The chat client builder to use
     * @return The generated response
     */
    public static String stepBackPrompting(ChatClient.Builder chatClientBuilder) {
        ChatClient chatClient = chatClientBuilder.build();

        String output = chatClient.prompt("""
                <s>
                When answering complex questions, first take a step back and identify the core principles or concepts 
                relevant to the question. Then use these principles to guide your detailed answer.
                </s>
                
                What are the implications of quantum computing on modern cryptography?
                """)
                .options(ChatOptions.builder()
                        .model("gemini-1.5-flash")
                        .temperature(0.2)
                        .maxTokens(500)
                        .build())
                .call()
                .content();

        System.out.println("Step-back Prompting Output: " + output);
        return output;
    }

    /**
     * Demonstrates zero-shot chain of thought prompting
     *
     * @param chatClient The chat client to use
     * @return The generated response
     */
    public static String chainOfThoughtZeroShot(ChatClient chatClient) {
        String output = chatClient.prompt("""
                Solve this step-by-step:
                
                A shop owner bought a lamp at $24 and sold it at $30. 
                The next day, she bought the same lamp again from the customer at $27 and sold it to another customer at $33.
                What is the total profit from these transactions?
                
                Let's think through this step by step.
                """)
                .options(ChatOptions.builder()
                        .model("gemini-1.5-flash")
                        .temperature(0.1)
                        .maxTokens(400)
                        .build())
                .call()
                .content();

        System.out.println("Chain of Thought Zero-shot Output: " + output);
        return output;
    }

    /**
     * Demonstrates few-shot chain of thought prompting with examples
     *
     * @param chatClient The chat client to use
     * @return The generated response
     */
    public static String chainOfThoughtFewShot(ChatClient chatClient) {
        String output = chatClient.prompt("""
                I'll solve some word math problems by breaking them down step-by-step.
                
                Problem: Roger has 5 tennis balls. He buys 2 more cans of tennis balls. Each can has 3 tennis balls. How many tennis balls does he have now?
                Step 1: Roger starts with 5 tennis balls.
                Step 2: He buys 2 cans, with 3 tennis balls each. That's 2 * 3 = 6 additional tennis balls.
                Step 3: Now he has 5 + 6 = 11 tennis balls.
                Answer: 11 tennis balls
                
                Problem: A store has 10 shirts. If they put 3 shirts on display and sell 4 shirts, how many shirts are left in the store?
                Step 1: The store starts with 10 shirts.
                Step 2: They put 3 shirts on display, which are still in the store. So they still have 10 shirts.
                Step 3: They sell 4 shirts, reducing the total. 10 - 4 = 6 shirts remain.
                Answer: 6 shirts
                
                Problem: Julia has $12. She buys a book for $7 and 3 pens. Each pen costs $1.50. How much money does she have left?
                """)
                .options(ChatOptions.builder()
                        .model("gemini-1.5-flash")
                        .temperature(0.1)
                        .maxTokens(400)
                        .build())
                .call()
                .content();

        System.out.println("Chain of Thought Few-shot Output: " + output);
        return output;
    }

    /**
     * Demonstrates self-consistency prompting with multiple reasoning paths
     *
     * @param chatClient The chat client to use
     * @return The generated response
     */
    public static String selfConsistency(ChatClient chatClient) {
        String output = chatClient.prompt("""
                <s>
                You are a reasoning assistant that solves problems by exploring multiple different reasoning paths
                and then comparing the results for consistency. When given a problem:
                1. Solve the problem using at least 2 different approaches
                2. Compare your results
                3. If there's a discrepancy, find where the error occurred
                4. Provide the final correct answer
                </s>
                
                Problem: If John has twice as many marbles as Peter, and together they have 36 marbles, 
                how many marbles does John have?
                """)
                .options(ChatOptions.builder()
                        .model("gemini-1.5-flash")
                        .temperature(0.2)
                        .maxTokens(600)
                        .build())
                .call()
                .content();

        System.out.println("Self-consistency Output: " + output);
        return output;
    }

    /**
     * Demonstrates Tree of Thoughts prompting applied to a game scenario
     *
     * @param chatClient The chat client to use
     * @return The generated response
     */
    public static String treeOfThoughtsGame(ChatClient chatClient) {
        String output = chatClient.prompt("""
                <s>
                You are a strategic game-playing assistant that uses Tree of Thoughts reasoning.
                For game scenarios:
                1. Identify all possible initial moves
                2. Explore 2-3 promising branches for each move, considering future states
                3. Evaluate each path's potential outcome
                4. Choose the optimal move based on this analysis
                </s>
                
                Game: Tic-tac-toe
                Current board state (X: player, O: opponent):
                
                |   |   |   |
                | O |   |   |
                |   |   | X |
                
                It's the player's (X's) turn. What's the best move?
                """)
                .options(ChatOptions.builder()
                        .model("gemini-1.5-flash")
                        .temperature(0.2)
                        .maxTokens(800)
                        .build())
                .call()
                .content();

        System.out.println("Tree of Thoughts Game Output: " + output);
        return output;
    }

    /**
     * Demonstrates Tree of Thoughts prompting applied to a complex problem
     *
     * @param chatClient The chat client to use
     * @return The generated response
     */
    public static String treeOfThoughtsProblem(ChatClient chatClient) {
        String output = chatClient.prompt("""
                <s>
                You are a problem-solving assistant that uses Tree of Thoughts reasoning.
                For complex problems:
                1. Break the problem into smaller sub-problems
                2. Explore multiple approaches for each sub-problem
                3. Evaluate the merit of each approach
                4. Choose the most promising path and develop a complete solution
                </s>
                
                Problem: A company wants to schedule 5 different presentations in a single day conference.
                There are 3 available rooms and the presentations vary in length: 30 min, 45 min, 60 min, 60 min, and 90 min.
                Each room can only host one presentation at a time.
                The conference starts at 9 AM and must end by 5 PM, with a mandatory 1-hour lunch break at noon.
                Create an optimal schedule that minimizes the total time required.
                """)
                .options(ChatOptions.builder()
                        .model("gemini-1.5-flash")
                        .temperature(0.3)
                        .maxTokens(1000)
                        .build())
                .call()
                .content();

        System.out.println("Tree of Thoughts Problem Output: " + output);
        return output;
    }
}
