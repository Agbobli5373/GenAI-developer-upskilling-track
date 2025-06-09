package com.isaac.contextual_memory_chatbot.util;

import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.chat.prompt.ChatOptions;

/**
 * Utility class for code-related prompting techniques:
 * - Code writing prompts
 * - Code explanation prompts
 * - Code translation prompts
 * - Automatic prompt engineering
 */
public class CodePromptingUtils {

    private CodePromptingUtils() {}

    /**
     * Demonstrates prompts for writing code
     *
     * @param chatClient The chat client to use
     * @return The generated code
     */
    public static String writeCode(ChatClient chatClient) {
        String output = chatClient.prompt("""
                <s>
                You are an expert Java developer specializing in Spring Boot applications.
                When asked to write code, provide clean, production-ready implementations with:
                - Clear documentation comments
                - Proper error handling
                - Best practices for the requested functionality
                </s>
                
                Write a Spring Boot REST controller that handles CRUD operations for a Product entity.
                The Product has id, name, description, price, and categoryId fields.
                Include appropriate exception handling and validation.
                """)
                .options(ChatOptions.builder()
                        .model("gemini-1.5-flash")
                        .temperature(0.1)
                        .maxTokens(800)
                        .build())
                .call()
                .content();

        System.out.println("Code Writing Output: " + output);
        return output;
    }

    /**
     * Demonstrates prompts for explaining code
     *
     * @param chatClient The chat client to use
     * @return The code explanation
     */
    public static String explainCode(ChatClient chatClient) {
        String output = chatClient.prompt("""
                <s>
                You are an expert programmer who specializes in explaining code in a clear,
                concise manner, highlighting important concepts and patterns.
                </s>
                
                Explain the following Java code, focusing on what it does and any design patterns used:
                
                ```java
                @Service
                public class OrderProcessor {
                    private final OrderRepository orderRepository;
                    private final PaymentService paymentService;
                    private final NotificationService notificationService;
                    
                    public OrderProcessor(OrderRepository orderRepository, 
                                          PaymentService paymentService,
                                          NotificationService notificationService) {
                        this.orderRepository = orderRepository;
                        this.paymentService = paymentService;
                        this.notificationService = notificationService;
                    }
                    
                    @Transactional
                    public Order processOrder(Order order) {
                        Order savedOrder = orderRepository.save(order);
                        PaymentResult result = paymentService.processPayment(order.getPaymentDetails());
                        
                        if (result.isSuccessful()) {
                            savedOrder.setStatus(OrderStatus.PAID);
                            orderRepository.save(savedOrder);
                            notificationService.sendConfirmation(savedOrder);
                        } else {
                            savedOrder.setStatus(OrderStatus.PAYMENT_FAILED);
                            orderRepository.save(savedOrder);
                            throw new PaymentFailedException("Payment failed: " + result.getMessage());
                        }
                        
                        return savedOrder;
                    }
                }
                ```
                """)
                .options(ChatOptions.builder()
                        .model("gemini-1.5-flash")
                        .temperature(0.1)
                        .maxTokens(600)
                        .build())
                .call()
                .content();

        System.out.println("Code Explanation Output: " + output);
        return output;
    }

    /**
     * Demonstrates prompts for translating code between languages
     *
     * @param chatClient The chat client to use
     * @return The translated code
     */
    public static String translateCode(ChatClient chatClient) {
        String output = chatClient.prompt("""
                <s>
                You are an expert polyglot programmer who specializes in translating code
                between different programming languages while maintaining the same functionality
                and following each language's best practices.
                </s>
                
                Translate this Python code to TypeScript:
                
                ```python
                def filter_and_sort_products(products, min_price=0, category=None):
                    filtered_products = [p for p in products if p['price'] >= min_price]
                    
                    if category:
                        filtered_products = [p for p in filtered_products if p['category'] == category]
                        
                    return sorted(filtered_products, key=lambda x: x['price'])
                    
                # Example usage
                products = [
                    {'id': 1, 'name': 'Laptop', 'price': 999, 'category': 'Electronics'},
                    {'id': 2, 'name': 'Headphones', 'price': 99, 'category': 'Electronics'},
                    {'id': 3, 'name': 'Chair', 'price': 199, 'category': 'Furniture'},
                ]
                
                result = filter_and_sort_products(products, min_price=100, category='Electronics')
                print(result)
                ```
                """)
                .options(ChatOptions.builder()
                        .model("gemini-1.5-flash")
                        .temperature(0.1)
                        .maxTokens(600)
                        .build())
                .call()
                .content();

        System.out.println("Code Translation Output: " + output);
        return output;
    }

    /**
     * Demonstrates automatic prompt engineering technique
     *
     * @param chatClient The chat client to use
     * @return The improved prompt and its result
     */
    public static String automaticPromptEngineering(ChatClient chatClient) {
        String output = chatClient.prompt("""
                <s>
                You are an expert prompt engineer that helps improve prompts to get better results from AI models.
                For any given prompt:
                1. Analyze its structure and potential weaknesses
                2. Create an improved version that will produce better, more reliable outputs
                3. Explain your improvements and why they help
                </s>
                
                Original prompt:
                "Write code for a website contact form"
                
                Improve this prompt to get higher quality, more specific and useful results.
                """)
                .options(ChatOptions.builder()
                        .model("gemini-1.5-flash")
                        .temperature(0.3)
                        .maxTokens(800)
                        .build())
                .call()
                .content();

        System.out.println("Automatic Prompt Engineering Output: " + output);
        return output;
    }
}
