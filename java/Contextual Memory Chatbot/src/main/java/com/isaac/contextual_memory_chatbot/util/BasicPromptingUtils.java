package com.isaac.contextual_memory_chatbot.util;

import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.chat.prompt.ChatOptions;
import com.fasterxml.jackson.annotation.JsonProperty;

/**
 * Utility class for basic prompting techniques:
 * - Zero shot prompting
 * - One-shot and few-shot prompting
 */
public class BasicPromptingUtils {

    /**
     * Demonstrates zero-shot prompting technique
     *
     * @param chatClient The chat client to use
     * @return The sentiment result
     */
    public static Sentiment zeroShotPrompting(ChatClient chatClient) {
        // General prompting / zero shot (page 15)
        String rawResponse = chatClient.prompt("""
                Classify movie reviews as POSITIVE, NEUTRAL or NEGATIVE.
                Review: "Her" is a disturbing study revealing the direction
                humanity is headed if AI is allowed to keep evolving,
                unchecked. I wish there were more movies like this masterpiece.
                Your response should be just one word: POSITIVE, NEUTRAL, or NEGATIVE.
                """)
                .options(ChatOptions.builder()
                        .model("gemini-1.5-flash")
                        .temperature(0.1)
                        .maxTokens(5)
                        .build())
                .call()
                .content();

        // Parse the response directly
        Sentiment sentiment;
        try {
            rawResponse = rawResponse.trim().toUpperCase();
            sentiment = Sentiment.valueOf(rawResponse);
        } catch (IllegalArgumentException e) {
            // Default to NEUTRAL if parsing fails
            System.out.println("Failed to parse sentiment from: " + rawResponse);
            sentiment = Sentiment.NEUTRAL;
        }

        System.out.println("Zero-shot Output: " + sentiment);
        return sentiment;
    }

    /**
     * Demonstrates one-shot and few-shot prompting techniques
     *
     * @param chatClient The chat client to use
     * @return The JSON response as a string
     */
    public static String oneAndFewShotPrompting(ChatClient chatClient) {
        // One-shot & few-shot prompting with examples
        String pizzaOrder = chatClient.prompt("""
                Parse a customer's pizza order into valid JSON

                EXAMPLE 1:
                I want a small pizza with cheese, tomato sauce, and pepperoni.
                JSON Response:
                ```
                {
                    "size": "small",
                    "type": "normal",
                    "ingredients": ["cheese", "tomato sauce", "peperoni"]
                }
                ```

                EXAMPLE 2:
                Can I get a large pizza with tomato sauce, basil and mozzarella.
                JSON Response:
                ```
                {
                    "size": "large",
                    "type": "normal",
                    "ingredients": ["tomato sauce", "basil", "mozzarella"]
                }
                ```

                Now, I would like a large pizza, with the first half cheese and mozzarella.
                And the other tomato sauce, ham and pineapple.

                """)
                .options(ChatOptions.builder()
                        .model("gemini-1.5-flash")
                        .temperature(0.1)
                        .maxTokens(250)
                        .build())
                .call()
                .content();

        System.out.println("Few-shot Output: " + pizzaOrder);
        return pizzaOrder;
    }

    /**
     * Sentiment enum for classification results
     */
    public enum Sentiment {
        POSITIVE, NEUTRAL, NEGATIVE
    }

    /**
     * Wrapper class for Sentiment enum to handle JSON deserialization
     */
    public static class SentimentResponse {
        @JsonProperty("Sentiment")
        private Sentiment sentiment;

        public Sentiment getSentiment() {
            return sentiment;
        }

        public void setSentiment(Sentiment sentiment) {
            this.sentiment = sentiment;
        }
    }
}
