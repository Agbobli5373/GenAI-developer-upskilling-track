package com.isaac.contextual_memory_chatbot.session;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.List;
import java.util.Map;

/**
 * REST Controller for managing session history and conversation tracking.
 * Provides endpoints for session management, history retrieval, and analytics.
 */
@RestController
@RequestMapping("/api/sessions")
public class SessionHistoryController {

    private final SessionHistoryService sessionHistoryService;

    public SessionHistoryController (SessionHistoryService sessionHistoryService) {
        this.sessionHistoryService = sessionHistoryService;
    }

    /**
     * Creates a new conversation session.
     * 
     * @return session ID and creation timestamp
     */
    @PostMapping("/create")
    public ResponseEntity<Map<String, String>> createSession() {
        String sessionId = sessionHistoryService.createSession();
        return ResponseEntity.ok(Map.of(
                "sessionId", sessionId,
                "status", "created",
                "timestamp", java.time.LocalDateTime.now().toString()));
    }

    /**
     * Adds a conversation entry to a session.
     * 
     * @param sessionId the session identifier
     * @param request   conversation entry data
     * @return confirmation response
     */
    @PostMapping("/{sessionId}/messages")
    public ResponseEntity<Map<String, String>> addMessage(
            @PathVariable String sessionId,
            @RequestBody ConversationRequest request) {

        sessionHistoryService.addConversationEntry(
                sessionId,
                request.getUserMessage(),
                request.getBotResponse());

        return ResponseEntity.ok(Map.of(
                "status", "added",
                "sessionId", sessionId,
                "timestamp", java.time.LocalDateTime.now().toString()));
    }

    /**
     * Retrieves conversation history for a session.
     * 
     * @param sessionId the session identifier
     * @return list of conversation entries
     */
    @GetMapping("/{sessionId}/history")
    public ResponseEntity<List<SessionHistoryService.ConversationEntry>> getHistory(
            @PathVariable String sessionId) {

        List<SessionHistoryService.ConversationEntry> history = sessionHistoryService.getConversationHistory(sessionId);

        return ResponseEntity.ok(history);
    }

    /**
     * Gets detailed session information including statistics.
     * 
     * @param sessionId the session identifier
     * @return session information
     */
    @GetMapping("/{sessionId}/info")
    public ResponseEntity<SessionHistoryService.SessionHistory> getSessionInfo(
            @PathVariable String sessionId) {

        SessionHistoryService.SessionHistory session = sessionHistoryService.getSessionInfo(sessionId);

        if (session == null) {
            return ResponseEntity.notFound().build();
        }

        return ResponseEntity.ok(session);
    }

    /**
     * Gets all active sessions.
     * 
     * @return list of all sessions
     */
    @GetMapping("/all")
    public ResponseEntity<List<SessionHistoryService.SessionHistory>> getAllSessions() {
        List<SessionHistoryService.SessionHistory> sessions = sessionHistoryService.getAllSessions();

        return ResponseEntity.ok(sessions);
    }

    /**
     * Clears conversation history for a session.
     * 
     * @param sessionId the session identifier
     * @return confirmation response
     */
    @DeleteMapping("/{sessionId}")
    public ResponseEntity<Map<String, String>> clearSession(@PathVariable String sessionId) {
        sessionHistoryService.clearSession(sessionId);

        return ResponseEntity.ok(Map.of(
                "status", "cleared",
                "sessionId", sessionId,
                "timestamp", java.time.LocalDateTime.now().toString()));
    }

    /**
     * Gets global statistics across all sessions.
     * 
     * @return session statistics
     */
    @GetMapping("/statistics")
    public ResponseEntity<SessionHistoryService.SessionStatistics> getStatistics() {
        SessionHistoryService.SessionStatistics stats = sessionHistoryService.getGlobalStatistics();

        return ResponseEntity.ok(stats);
    }

    /**
     * Exports conversation history as formatted text.
     * 
     * @param sessionId the session identifier
     * @return formatted conversation export
     */
    @GetMapping("/{sessionId}/export")
    public ResponseEntity<Map<String, String>> exportHistory(@PathVariable String sessionId) {
        String exportData = sessionHistoryService.exportConversationHistory(sessionId);

        return ResponseEntity.ok(Map.of(
                "sessionId", sessionId,
                "export", exportData,
                "timestamp", java.time.LocalDateTime.now().toString()));
    }

    /**
     * Searches conversations for a specific term.
     * 
     * @param sessionId the session identifier
     * @param query     the search query
     * @return matching conversation entries
     */
    @GetMapping("/{sessionId}/search")
    public ResponseEntity<List<SessionHistoryService.ConversationEntry>> searchConversations(
            @PathVariable String sessionId,
            @RequestParam String query) {

        List<SessionHistoryService.ConversationEntry> results = sessionHistoryService.searchConversations(sessionId,
                query);

        return ResponseEntity.ok(results);
    }

    /**
     * Request object for adding conversation entries.
     */
    public static class ConversationRequest {
        private String userMessage;
        private String botResponse;

        public ConversationRequest() {
        }

        public ConversationRequest(String userMessage, String botResponse) {
            this.userMessage = userMessage;
            this.botResponse = botResponse;
        }

        public String getUserMessage() {
            return userMessage;
        }

        public void setUserMessage(String userMessage) {
            this.userMessage = userMessage;
        }

        public String getBotResponse() {
            return botResponse;
        }

        public void setBotResponse(String botResponse) {
            this.botResponse = botResponse;
        }
    }
}
