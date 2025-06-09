package com.isaac.contextual_memory_chatbot.util;

import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.chat.prompt.ChatOptions;



/**
 * Utility class for contextual prompting techniques:
 * - System prompting
 * - Role prompting
 * - Contextual prompting
 */
public class ContextualPromptingUtils {

    private ContextualPromptingUtils() {}

    /**
     * Demonstrates system prompting with direct instructions
     *
     * @param chatClient The chat client to use
     * @return The generated response
     */
    public static String systemPrompting1(ChatClient chatClient) {
        String output = chatClient.prompt("""
                <system>
                Answer the following questions with short, concise answers.
                </system>

                What is the capital of France?
                """)
                .options(ChatOptions.builder()
                        .model("gemini-1.5-flash")
                        .temperature(0.1)
                        .maxTokens(50)
                        .build())
                .call()
                .content();

        System.out.println("System Prompting 1 Output: " + output);
        return output;
    }

    /**
     * Demonstrates system prompting with specific constraints
     *
     * @param chatClient The chat client to use
     * @return The generated response
     */
    public static String systemPrompting2(ChatClient chatClient) {
        String output = chatClient.prompt("""
                <system>
                Answer questions in a childish and playful tone suitable for a 5-year-old.
                Use simple language and include fun analogies.
                </system>

                What are black holes?
                """)
                .options(ChatOptions.builder()
                        .model("gemini-1.5-flash")
                        .temperature(0.7)
                        .maxTokens(200)
                        .build())
                .call()
                .content();

        System.out.println("System Prompting 2 Output: " + output);
        return output;
    }

    /**
     * Demonstrates system prompting using Spring AI style with separate messages
     *
     * @param chatClient The chat client to use
     * @return The generated response
     */
//    public static String systemPromptingSpringAIStyle(ChatClient chatClient) {
//        // Example of sending a system message separately using Spring AI's API
//        Message systemMessage = new SystemMessage("Answer questions in a childish and playful tone suitable for a 5-year-old. Use simple language and include fun analogies.");
//        Message userMessage = new UserMessage("What are black holes?");
//
//        String output = chatClient.call(new Prompt(List.of(systemMessage, userMessage),
//                ChatOptions.builder()
//                        .model("gemini-1.5-flash")
//                        .temperature(0.7)
//                        .maxTokens(200)
//                        .build()))
//                .content();
//
//        System.out.println("System Prompting Spring AI Style Output: " + output);
//        return output;
//    }

    /**
     * Demonstrates role prompting with a specific professional role
     *
     * @param chatClient The chat client to use
     * @return The generated response
     */
    public static String rolePrompting1(ChatClient chatClient) {
        String output = chatClient.prompt("""
                <system>
                You are an experienced network security engineer.
                Answer security-related questions with technical precision and best practices.
                </system>

                What are the key considerations when setting up a home network?
                """)
                .options(ChatOptions.builder()
                        .model("gemini-1.5-flash")
                        .temperature(0.2)
                        .maxTokens(300)
                        .build())
                .call()
                .content();

        System.out.println("Role Prompting 1 Output: " + output);
        return output;
    }

    /**
     * Demonstrates role prompting with a specific character style
     *
     * @param chatClient The chat client to use
     * @return The generated response
     */
    public static String rolePrompting2(ChatClient chatClient) {
        String output = chatClient.prompt("""
                <system>
                You are a stand-up comedian specialized in computer science jokes.
                Answer questions with humor and witty explanations.
                </system>

                Explain what happens when a computer program crashes.
                """)
                .options(ChatOptions.builder()
                        .model("gemini-1.5-flash")
                        .temperature(0.8)
                        .maxTokens(300)
                        .build())
                .call()
                .content();

        System.out.println("Role Prompting 2 Output: " + output);
        return output;
    }

    /**
     * Demonstrates contextual prompting with additional information
     *
     * @param chatClient The chat client to use
     * @return The generated response
     */
    public static String contextualPrompting(ChatClient chatClient) {
        String output = chatClient.prompt("""
                <system>
                You are an AI assistant helping a software developer understand a specific piece of code.
                </system>

                Here's the context: I'm working with a Spring Boot application that uses Spring Data JPA.
                I'm trying to implement pagination for my REST API that returns a list of products.

                This is my repository interface:
                ```java
                public interface ProductRepository extends JpaRepository<Product, Long> {
                    Page<Product> findByCategoryId(Long categoryId, Pageable pageable);
                }
                ```

                How can I implement a controller method that uses this repository to return paginated results?
                """)
                .options(ChatOptions.builder()
                        .model("gemini-1.5-flash")
                        .temperature(0.1)
                        .maxTokens(500)
                        .build())
                .call()
                .content();

        System.out.println("Contextual Prompting Output: " + output);
        return output;
    }
}
