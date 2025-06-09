package com.isaac.contextual_memory_chatbot.memory;

import com.isaac.contextual_memory_chatbot.session.SessionHistoryService;
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.chat.client.advisor.MessageChatMemoryAdvisor;
import org.springframework.ai.chat.memory.ChatMemory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import reactor.core.publisher.Mono;
import reactor.core.scheduler.Schedulers;

/**
 * Controller for handling AI chat interactions with memory and session
 * tracking.
 * Integrates Spring AI's contextual memory with comprehensive session history
 * tracking.
 */
@RestController
public class MemoryController {
    private final ChatClient chatClient;

    private final SessionHistoryService sessionHistoryService;

    public MemoryController(ChatClient.Builder builder, ChatMemory chatMemory,
                            SessionHistoryService sessionHistoryService) {
        this.chatClient = builder
                .defaultAdvisors(MessageChatMemoryAdvisor.builder(chatMemory).build())
                .build();
        this.sessionHistoryService = sessionHistoryService;
    }

    /**
     * Processes a chat message with contextual memory and session tracking.
     * 
     * @param message   the user's message
     * @param sessionId optional session identifier for tracking conversations
     * @return AI response wrapped in Mono for reactive processing
     */
    @GetMapping("/memory")
    public Mono<String> chat(
            @RequestParam String message,
            @RequestParam(required = false) String sessionId) {

        return Mono.fromCallable(() -> {
            try {
                // Generate AI response
                String response = chatClient.prompt()
                        .user(message)
                        .call()
                        .content();

                // Track conversation if session ID is provided
                if (sessionId != null && !sessionId.trim().isEmpty()) {
                    sessionHistoryService.addConversationEntry(sessionId, message, response);
                }

                return response;
            } catch (Exception e) {
                System.err.println("Error calling AI service: " + e.getMessage());
                throw new RuntimeException("Failed to process chat message: " + e.getMessage(), e);
            }
        }).subscribeOn(Schedulers.boundedElastic());
    }

    /**
     * Legacy endpoint for backward compatibility.
     * 
     * @param message the user's message
     * @return AI response
     */
    @GetMapping("/memory/legacy")
    public Mono<String> home(@RequestParam String message) {
        return chat(message, null);
    }
}
