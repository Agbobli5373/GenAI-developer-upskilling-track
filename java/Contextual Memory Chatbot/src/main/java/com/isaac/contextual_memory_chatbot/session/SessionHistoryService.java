package com.isaac.contextual_memory_chatbot.session;

import org.springframework.stereotype.Service;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Collectors;

/**
 * Service for managing session history and conversation tracking.
 * Provides functionality to store, retrieve, and analyze conversation sessions.
 */
@Service
public class SessionHistoryService {

    private final Map<String, SessionHistory> sessions = new ConcurrentHashMap<>();
    private final Map<String, List<ConversationEntry>> conversationHistory = new ConcurrentHashMap<>();

    /**
     * Creates a new session and returns the session ID.
     * 
     * @return unique session identifier
     */
    public String createSession() {
        String sessionId = generateSessionId();
        SessionHistory session = new SessionHistory(sessionId, LocalDateTime.now());
        sessions.put(sessionId, session);
        conversationHistory.put(sessionId, new ArrayList<>());
        return sessionId;
    }

    /**
     * Adds a conversation entry to the specified session.
     * 
     * @param sessionId   the session identifier
     * @param userMessage the user's message
     * @param botResponse the bot's response
     */
    public void addConversationEntry(String sessionId, String userMessage, String botResponse) {
        ensureSessionExists(sessionId);

        ConversationEntry entry = new ConversationEntry(
                userMessage,
                botResponse,
                LocalDateTime.now());

        conversationHistory.get(sessionId).add(entry);

        // Update session statistics
        SessionHistory session = sessions.get(sessionId);
        session.incrementMessageCount();
        session.updateLastActivity();
    }

    /**
     * Retrieves the conversation history for a session.
     * 
     * @param sessionId the session identifier
     * @return list of conversation entries
     */
    public List<ConversationEntry> getConversationHistory(String sessionId) {
        return conversationHistory.getOrDefault(sessionId, new ArrayList<>());
    }

    /**
     * Gets session information including statistics.
     * 
     * @param sessionId the session identifier
     * @return session history object
     */
    public SessionHistory getSessionInfo(String sessionId) {
        return sessions.get(sessionId);
    }

    /**
     * Gets all active sessions sorted by last activity.
     * 
     * @return list of session histories
     */
    public List<SessionHistory> getAllSessions() {
        return sessions.values().stream()
                .sorted((s1, s2) -> s2.getLastActivity().compareTo(s1.getLastActivity()))
                .collect(Collectors.toList());
    }

    /**
     * Clears conversation history for a specific session.
     * 
     * @param sessionId the session identifier
     */
    public void clearSession(String sessionId) {
        conversationHistory.remove(sessionId);
        sessions.remove(sessionId);
    }

    /**
     * Gets statistics across all sessions.
     * 
     * @return session statistics object
     */
    public SessionStatistics getGlobalStatistics() {
        int totalSessions = sessions.size();
        int totalMessages = sessions.values().stream()
                .mapToInt(SessionHistory::getMessageCount)
                .sum();

        OptionalDouble avgMessagesPerSession = sessions.values().stream()
                .mapToInt(SessionHistory::getMessageCount)
                .average();

        return new SessionStatistics(
                totalSessions,
                totalMessages,
                avgMessagesPerSession.orElse(0.0));
    }

    /**
     * Exports conversation history as formatted text.
     * 
     * @param sessionId the session identifier
     * @return formatted conversation history
     */
    public String exportConversationHistory(String sessionId) {
        List<ConversationEntry> history = getConversationHistory(sessionId);
        SessionHistory session = getSessionInfo(sessionId);

        StringBuilder export = new StringBuilder();
        export.append("=== Conversation History ===\n");
        export.append("Session ID: ").append(sessionId).append("\n");
        export.append("Started: ")
                .append(session.getStartTime().format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss"))).append("\n");
        export.append("Messages: ").append(history.size()).append("\n");
        export.append("===========================================\n\n");

        for (int i = 0; i < history.size(); i++) {
            ConversationEntry entry = history.get(i);
            export.append("[").append(i + 1).append("] ");
            export.append(entry.getTimestamp().format(DateTimeFormatter.ofPattern("HH:mm:ss")));
            export.append("\nUser: ").append(entry.getUserMessage()).append("\n");
            export.append("Bot: ").append(entry.getBotResponse()).append("\n\n");
        }

        return export.toString();
    }

    /**
     * Searches conversations for a specific term.
     * 
     * @param sessionId  the session identifier
     * @param searchTerm the term to search for
     * @return list of matching conversation entries
     */
    public List<ConversationEntry> searchConversations(String sessionId, String searchTerm) {
        List<ConversationEntry> history = getConversationHistory(sessionId);
        String lowerSearchTerm = searchTerm.toLowerCase();

        return history.stream()
                .filter(entry -> entry.getUserMessage().toLowerCase().contains(lowerSearchTerm) ||
                        entry.getBotResponse().toLowerCase().contains(lowerSearchTerm))
                .collect(Collectors.toList());
    }

    private void ensureSessionExists(String sessionId) {
        if (!sessions.containsKey(sessionId)) {
            createSessionWithId(sessionId);
        }
    }

    private void createSessionWithId(String sessionId) {
        SessionHistory session = new SessionHistory(sessionId, LocalDateTime.now());
        sessions.put(sessionId, session);
        conversationHistory.put(sessionId, new ArrayList<>());
    }

    private String generateSessionId() {
        return "session_" + System.currentTimeMillis() + "_" +
                Integer.toHexString(new Random().nextInt());
    }

    /**
     * Inner class representing a single conversation entry.
     */
    public static class ConversationEntry {
        private final String userMessage;
        private final String botResponse;
        private final LocalDateTime timestamp;

        public ConversationEntry(String userMessage, String botResponse, LocalDateTime timestamp) {
            this.userMessage = userMessage;
            this.botResponse = botResponse;
            this.timestamp = timestamp;
        }

        public String getUserMessage() {
            return userMessage;
        }

        public String getBotResponse() {
            return botResponse;
        }

        public LocalDateTime getTimestamp() {
            return timestamp;
        }
    }

    /**
     * Inner class representing session history and metadata.
     */
    public static class SessionHistory {
        private final String sessionId;
        private final LocalDateTime startTime;
        private LocalDateTime lastActivity;
        private int messageCount;

        public SessionHistory(String sessionId, LocalDateTime startTime) {
            this.sessionId = sessionId;
            this.startTime = startTime;
            this.lastActivity = startTime;
            this.messageCount = 0;
        }

        public void incrementMessageCount() {
            this.messageCount++;
        }

        public void updateLastActivity() {
            this.lastActivity = LocalDateTime.now();
        }

        public String getSessionId() {
            return sessionId;
        }

        public LocalDateTime getStartTime() {
            return startTime;
        }

        public LocalDateTime getLastActivity() {
            return lastActivity;
        }

        public int getMessageCount() {
            return messageCount;
        }
    }

    /**
     * Inner class for global session statistics.
     */
    public static class SessionStatistics {
        private final int totalSessions;
        private final int totalMessages;
        private final double averageMessagesPerSession;

        public SessionStatistics(int totalSessions, int totalMessages, double averageMessagesPerSession) {
            this.totalSessions = totalSessions;
            this.totalMessages = totalMessages;
            this.averageMessagesPerSession = averageMessagesPerSession;
        }

        public int getTotalSessions() {
            return totalSessions;
        }

        public int getTotalMessages() {
            return totalMessages;
        }

        public double getAverageMessagesPerSession() {
            return averageMessagesPerSession;
        }
    }
}
