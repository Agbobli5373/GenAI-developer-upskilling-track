package com.isaac.contextual_memory_chatbot;

import com.isaac.contextual_memory_chatbot.util.ContextualPromptingUtils;
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.boot.CommandLineRunner;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;

import com.isaac.contextual_memory_chatbot.util.AdvancedReasoningUtils;
import com.isaac.contextual_memory_chatbot.util.BasicPromptingUtils;
import com.isaac.contextual_memory_chatbot.util.CodePromptingUtils;


/**
 * Main application class demonstrating various prompt engineering techniques
 * using the Spring AI library.
 */
@SpringBootApplication
public class PromptEngineeringApplication {

    public static void main(String[] args) {
        SpringApplication.run(PromptEngineeringApplication.class, args);
    }

    @Bean
    public CommandLineRunner commandLineRunner(ChatClient.Builder chatClientBuilder) {
        return args -> {
            System.out.println("=== Prompt Engineering Techniques Demonstration ===");

            // Create a shared chat client instance for most examples
            ChatClient chatClient = chatClientBuilder.build();

//            // 1. Basic Prompting Techniques
//            System.out.println("\n=== Basic Prompting Techniques ===");
//
//            // 1.1 Zero-shot prompting
//            System.out.println("\n--- Zero-shot Prompting ---");
//            BasicPromptingUtils.zeroShotPrompting(chatClient);
//
//            // 1.2 One-shot & few-shot prompting
//            System.out.println("\n--- One-shot & Few-shot Prompting ---");
//            BasicPromptingUtils.oneAndFewShotPrompting(chatClient);
//
//            // 2. Contextual Prompting Techniques
//            System.out.println("\n=== Contextual Prompting Techniques ===");
//
//            // 2.1 System prompting
//            System.out.println("\n--- System Prompting ---");
//            ContextualPromptingUtils.systemPrompting1(chatClient);
//            ContextualPromptingUtils.systemPrompting2(chatClient);
//            ContextualPromptingUtils.systemPromptingSpringAIStyle(chatClient);
//
//            // 2.2 Role prompting
//            System.out.println("\n--- Role Prompting ---");
//            ContextualPromptingUtils.rolePrompting1(chatClient);
//            ContextualPromptingUtils.rolePrompting2(chatClient);
//
//            // 2.3 Contextual prompting
//            System.out.println("\n--- Contextual Prompting ---");
//            ContextualPromptingUtils.contextualPrompting(chatClient);
//
//            // 3. Advanced Reasoning Techniques
//            System.out.println("\n=== Advanced Reasoning Techniques ===");
//
//            // 3.1 Step-back prompting
//            System.out.println("\n--- Step-back Prompting ---");
//            AdvancedReasoningUtils.stepBackPrompting(chatClientBuilder);
//
//            // 3.2 Chain of Thought (CoT)
//            System.out.println("\n--- Chain of Thought ---");
//            AdvancedReasoningUtils.chainOfThoughtZeroShot(chatClient);
//            AdvancedReasoningUtils.chainOfThoughtFewShot(chatClient);
//
//            // 3.3 Self-consistency
//            System.out.println("\n--- Self-consistency ---");
//            AdvancedReasoningUtils.selfConsistency(chatClient);
//
//            // 3.4 Tree of Thoughts (ToT)
//            System.out.println("\n--- Tree of Thoughts ---");
//            AdvancedReasoningUtils.treeOfThoughtsGame(chatClient);
//            AdvancedReasoningUtils.treeOfThoughtsProblem(chatClient);
//
//            // 4. Code-related Prompting Techniques
//            System.out.println("\n=== Code-related Prompting Techniques ===");
//
//            // 4.1 Prompts for writing code
//            System.out.println("\n--- Writing Code ---");
//            CodePromptingUtils.writeCode(chatClient);
//
//            // 4.2 Prompts for explaining code
//            System.out.println("\n--- Explaining Code ---");
//            CodePromptingUtils.explainCode(chatClient);
//
//            // 4.3 Prompts for translating code
//            System.out.println("\n--- Translating Code ---");
//            CodePromptingUtils.translateCode(chatClient);
//
//            // 4.4 Automatic prompt engineering
//            System.out.println("\n--- Automatic Prompt Engineering ---");
//            CodePromptingUtils.automaticPromptEngineering(chatClient);

            System.out.println("\n=== Demonstration Completed ===");
        };
    }
}