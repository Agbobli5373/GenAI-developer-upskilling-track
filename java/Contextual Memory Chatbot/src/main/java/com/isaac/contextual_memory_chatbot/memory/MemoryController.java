package com.isaac.contextual_memory_chatbot.memory;

import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.chat.client.advisor.MessageChatMemoryAdvisor;
import org.springframework.ai.chat.memory.ChatMemory;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import reactor.core.publisher.Mono;
import reactor.core.scheduler.Schedulers;

@RestController
public class MemoryController {
    private final ChatClient chatClient;

    public MemoryController(ChatClient.Builder builder, ChatMemory chatMemory) {
        this.chatClient = builder
                .defaultAdvisors(MessageChatMemoryAdvisor.builder(chatMemory).build())
                .build();
    }



    @GetMapping("/memory")
    public Mono<String> home(@RequestParam String message) {
        // Use Schedulers.boundedElastic() to handle the blocking call properly in a reactive context
        return Mono.fromCallable(() -> {
            try {
                return chatClient.prompt()
                    .user(message)
                    .call()
                    .content();
            } catch (Exception e) {
                // Add proper error handling
                System.err.println("Error calling AI service: " + e.getMessage());
                throw e;
            }
        }).subscribeOn(Schedulers.boundedElastic()); // This is key - moves blocking code to appropriate thread pool
    }
}
