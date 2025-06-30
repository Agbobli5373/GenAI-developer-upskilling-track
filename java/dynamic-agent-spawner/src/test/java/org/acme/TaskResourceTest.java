package org.acme;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.mockito.Mockito;

import jakarta.ws.rs.core.Response;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

@DisplayName("TaskResource Tests")
class TaskResourceTest {

    private AgentSpawner mockAgentSpawner;
    private InstructionGeneratorAgent mockInstructionGenerator;
    private TaskResource taskResource;
    private DecomposedInstructions testInstructions;

    @BeforeEach
    void setUp() {
        mockAgentSpawner = Mockito.mock(AgentSpawner.class);
        mockInstructionGenerator = Mockito.mock(InstructionGeneratorAgent.class);
        taskResource = new TaskResource(mockAgentSpawner);
        testInstructions = new DecomposedInstructions(
            "Create a structured plan for the content",
            "Write engaging content based on the plan"
        );
    }

    @Nested
    @DisplayName("POST /tasks endpoint tests")
    class CreateTaskTests {

        @Test
        @DisplayName("Should process valid goal successfully")
        void testCreateTaskWithValidGoal() {
            // Given
            String goal = "Write a technical blog post";
            String expectedResult = "Generated content about technical blog post";
            when(mockAgentSpawner.spawnAndExecute(goal)).thenReturn(expectedResult);

            // When
            String result = taskResource.createTask(goal);

            // Then
            assertEquals(expectedResult, result);
            verify(mockAgentSpawner).spawnAndExecute(goal);
        }

        @Test
        @DisplayName("Should handle null goal")
        void testCreateTaskWithNullGoal() {
            // When
            String result = taskResource.createTask(null);

            // Then
            assertEquals("Please provide a goal in the request body.", result);
            verify(mockAgentSpawner, never()).spawnAndExecute(any());
        }

        @Test
        @DisplayName("Should handle empty goal")
        void testCreateTaskWithEmptyGoal() {
            // When
            String result = taskResource.createTask("");

            // Then
            assertEquals("Please provide a goal in the request body.", result);
            verify(mockAgentSpawner, never()).spawnAndExecute(any());
        }

        @Test
        @DisplayName("Should handle blank goal")
        void testCreateTaskWithBlankGoal() {
            // When
            String result = taskResource.createTask("   \n\t   ");

            // Then
            assertEquals("Please provide a goal in the request body.", result);
            verify(mockAgentSpawner, never()).spawnAndExecute(any());
        }

        @Test
        @DisplayName("Should handle goal with only whitespace")
        void testCreateTaskWithWhitespaceGoal() {
            // Given
            String whitespaceGoal = "     ";

            // When
            String result = taskResource.createTask(whitespaceGoal);

            // Then
            assertEquals("Please provide a goal in the request body.", result);
            verify(mockAgentSpawner, never()).spawnAndExecute(any());
        }

        @Test
        @DisplayName("Should handle agent spawner exception")
        void testCreateTaskWithException() {
            // Given
            String goal = "Test goal";
            RuntimeException expectedException = new RuntimeException("Agent execution failed");
            when(mockAgentSpawner.spawnAndExecute(goal)).thenThrow(expectedException);

            // When & Then
            assertThrows(RuntimeException.class, () -> taskResource.createTask(goal));
            verify(mockAgentSpawner).spawnAndExecute(goal);
        }
    }

    @Nested
    @DisplayName("POST /tasks/detailed endpoint tests")
    class CreateTaskDetailedTests {

        @Test
        @DisplayName("Should return detailed response for valid goal")
        void testCreateTaskDetailedWithValidGoal() {
            // Given
            String goal = "Create a marketing strategy";
            String expectedResult = "Detailed marketing strategy content";
            
            when(mockAgentSpawner.getInstructionGenerator()).thenReturn(mockInstructionGenerator);
            when(mockInstructionGenerator.generateInstructions(goal)).thenReturn(testInstructions);
            when(mockAgentSpawner.spawnAndExecute(goal)).thenReturn(expectedResult);

            // When
            Response response = taskResource.createTaskDetailed(goal);

            // Then
            assertEquals(Response.Status.OK.getStatusCode(), response.getStatus());
            
            @SuppressWarnings("unchecked")
            Map<String, Object> responseBody = (Map<String, Object>) response.getEntity();
            
            assertTrue((Boolean) responseBody.get("success"));
            assertEquals(goal, responseBody.get("goal"));
            assertEquals(testInstructions.plannerInstructions(), responseBody.get("plannerInstructions"));
            assertEquals(testInstructions.writerInstructions(), responseBody.get("writerInstructions"));
            assertEquals(expectedResult, responseBody.get("finalResult"));

            verify(mockAgentSpawner).getInstructionGenerator();
            verify(mockInstructionGenerator).generateInstructions(goal);
            verify(mockAgentSpawner).spawnAndExecute(goal);
        }

        @Test
        @DisplayName("Should return bad request for null goal")
        void testCreateTaskDetailedWithNullGoal() {
            // When
            Response response = taskResource.createTaskDetailed(null);

            // Then
            assertEquals(Response.Status.BAD_REQUEST.getStatusCode(), response.getStatus());
            
            @SuppressWarnings("unchecked")
            Map<String, Object> responseBody = (Map<String, Object>) response.getEntity();
            
            assertEquals("Please provide a goal in the request body.", responseBody.get("error"));
            verify(mockAgentSpawner, never()).spawnAndExecute(any());
        }

        @Test
        @DisplayName("Should return bad request for empty goal")
        void testCreateTaskDetailedWithEmptyGoal() {
            // When
            Response response = taskResource.createTaskDetailed("");

            // Then
            assertEquals(Response.Status.BAD_REQUEST.getStatusCode(), response.getStatus());
            
            @SuppressWarnings("unchecked")
            Map<String, Object> responseBody = (Map<String, Object>) response.getEntity();
            
            assertEquals("Please provide a goal in the request body.", responseBody.get("error"));
            verify(mockAgentSpawner, never()).spawnAndExecute(any());
        }

        @Test
        @DisplayName("Should return bad request for blank goal")
        void testCreateTaskDetailedWithBlankGoal() {
            // When
            Response response = taskResource.createTaskDetailed("   \n\t   ");

            // Then
            assertEquals(Response.Status.BAD_REQUEST.getStatusCode(), response.getStatus());
            
            @SuppressWarnings("unchecked")
            Map<String, Object> responseBody = (Map<String, Object>) response.getEntity();
            
            assertEquals("Please provide a goal in the request body.", responseBody.get("error"));
            verify(mockAgentSpawner, never()).spawnAndExecute(any());
        }

        @Test
        @DisplayName("Should handle instruction generation exception")
        void testCreateTaskDetailedWithInstructionException() {
            // Given
            String goal = "Test goal";
            RuntimeException expectedException = new RuntimeException("Instruction generation failed");
            
            when(mockAgentSpawner.getInstructionGenerator()).thenReturn(mockInstructionGenerator);
            when(mockInstructionGenerator.generateInstructions(goal)).thenThrow(expectedException);

            // When
            Response response = taskResource.createTaskDetailed(goal);

            // Then
            assertEquals(Response.Status.INTERNAL_SERVER_ERROR.getStatusCode(), response.getStatus());
            
            @SuppressWarnings("unchecked")
            Map<String, Object> responseBody = (Map<String, Object>) response.getEntity();
            
            assertEquals("Instruction generation failed", responseBody.get("error"));
            assertEquals(false, responseBody.get("success"));

            verify(mockAgentSpawner).getInstructionGenerator();
            verify(mockInstructionGenerator).generateInstructions(goal);
            verify(mockAgentSpawner, never()).spawnAndExecute(any());
        }

        @Test
        @DisplayName("Should handle agent execution exception")
        void testCreateTaskDetailedWithExecutionException() {
            // Given
            String goal = "Test goal";
            RuntimeException expectedException = new RuntimeException("Agent execution failed");
            
            when(mockAgentSpawner.getInstructionGenerator()).thenReturn(mockInstructionGenerator);
            when(mockInstructionGenerator.generateInstructions(goal)).thenReturn(testInstructions);
            when(mockAgentSpawner.spawnAndExecute(goal)).thenThrow(expectedException);

            // When
            Response response = taskResource.createTaskDetailed(goal);

            // Then
            assertEquals(Response.Status.INTERNAL_SERVER_ERROR.getStatusCode(), response.getStatus());
            
            @SuppressWarnings("unchecked")
            Map<String, Object> responseBody = (Map<String, Object>) response.getEntity();
            
            assertEquals("Agent execution failed", responseBody.get("error"));
            assertEquals(false, responseBody.get("success"));

            verify(mockAgentSpawner).getInstructionGenerator();
            verify(mockInstructionGenerator).generateInstructions(goal);
            verify(mockAgentSpawner).spawnAndExecute(goal);
        }

        @Test
        @DisplayName("Should handle null instruction generator")
        void testCreateTaskDetailedWithNullInstructionGenerator() {
            // Given
            String goal = "Test goal";
            when(mockAgentSpawner.getInstructionGenerator()).thenReturn(null);

            // When
            Response response = taskResource.createTaskDetailed(goal);

            // Then
            assertEquals(Response.Status.INTERNAL_SERVER_ERROR.getStatusCode(), response.getStatus());
            
            @SuppressWarnings("unchecked")
            Map<String, Object> responseBody = (Map<String, Object>) response.getEntity();
            
            assertNotNull(responseBody.get("error"));
            assertEquals(false, responseBody.get("success"));
        }

        @Test
        @DisplayName("Should handle complex goal scenarios")
        void testCreateTaskDetailedWithComplexGoal() {
            // Given
            String complexGoal = "Design a comprehensive user experience for a mobile application " +
                               "that includes accessibility features, multi-language support, and " +
                               "integration with social media platforms";
            String expectedResult = "Comprehensive UX design with all requested features";
            
            when(mockAgentSpawner.getInstructionGenerator()).thenReturn(mockInstructionGenerator);
            when(mockInstructionGenerator.generateInstructions(complexGoal)).thenReturn(testInstructions);
            when(mockAgentSpawner.spawnAndExecute(complexGoal)).thenReturn(expectedResult);

            // When
            Response response = taskResource.createTaskDetailed(complexGoal);

            // Then
            assertEquals(Response.Status.OK.getStatusCode(), response.getStatus());
            
            @SuppressWarnings("unchecked")
            Map<String, Object> responseBody = (Map<String, Object>) response.getEntity();
            
            assertTrue((Boolean) responseBody.get("success"));
            assertEquals(complexGoal, responseBody.get("goal"));
            assertEquals(expectedResult, responseBody.get("finalResult"));
        }
    }

    @Nested
    @DisplayName("GET /tasks/health endpoint tests")
    class HealthTests {

        @Test
        @DisplayName("Should return healthy status")
        void testHealthEndpoint() {
            // When
            Map<String, Object> response = taskResource.health();

            // Then
            assertNotNull(response);
            assertEquals("healthy", response.get("status"));
            assertEquals("Dynamic Agent Spawner", response.get("service"));
            assertTrue(response.containsKey("timestamp"));
            assertTrue(response.get("timestamp") instanceof Long);
            
            Long timestamp = (Long) response.get("timestamp");
            assertTrue(timestamp > 0);
            assertTrue(timestamp <= System.currentTimeMillis());
        }

        @Test
        @DisplayName("Should return consistent health status")
        void testHealthEndpointConsistency() {
            // When - Call health endpoint multiple times
            Map<String, Object> response1 = taskResource.health();
            Map<String, Object> response2 = taskResource.health();

            // Then - Status and service should be consistent
            assertEquals(response1.get("status"), response2.get("status"));
            assertEquals(response1.get("service"), response2.get("service"));
            
            // Timestamps should be different (assuming some time passes between calls)
            Long timestamp1 = (Long) response1.get("timestamp");
            Long timestamp2 = (Long) response2.get("timestamp");
            assertTrue(timestamp2 >= timestamp1);
        }
    }

    @Nested
    @DisplayName("Constructor and Dependency Injection Tests")
    class ConstructorTests {

        @Test
        @DisplayName("Should create TaskResource with valid AgentSpawner")
        void testConstructorWithValidAgentSpawner() {
            // Given
            AgentSpawner mockSpawner = mock(AgentSpawner.class);

            // When
            TaskResource resource = new TaskResource(mockSpawner);

            // Then
            assertNotNull(resource);
        }

        @Test
        @DisplayName("Should handle null AgentSpawner in constructor")
        void testConstructorWithNullAgentSpawner() {
            // When & Then
            assertDoesNotThrow(() -> new TaskResource(null));
        }
    }

    @Nested
    @DisplayName("Performance and Edge Case Tests")
    class PerformanceTests {

        @Test
        @DisplayName("Should handle multiple concurrent requests gracefully")
        void testConcurrentRequests() {
            // Given
            String goal = "Test concurrent execution";
            String expectedResult = "Concurrent execution result";
            
            when(mockAgentSpawner.getInstructionGenerator()).thenReturn(mockInstructionGenerator);
            when(mockInstructionGenerator.generateInstructions(goal)).thenReturn(testInstructions);
            when(mockAgentSpawner.spawnAndExecute(goal)).thenReturn(expectedResult);

            // When - Simulate multiple requests
            for (int i = 0; i < 5; i++) {
                Response response = taskResource.createTaskDetailed(goal);
                assertEquals(Response.Status.OK.getStatusCode(), response.getStatus());
            }

            // Then - Verify all interactions occurred
            verify(mockAgentSpawner, times(5)).getInstructionGenerator();
            verify(mockInstructionGenerator, times(5)).generateInstructions(goal);
            verify(mockAgentSpawner, times(5)).spawnAndExecute(goal);
        }

        @Test
        @DisplayName("Should handle very long response content")
        void testLongResponseContent() {
            // Given
            String goal = "Generate long content";
            String longResult = "Very long result content. ".repeat(1000);
            
            when(mockAgentSpawner.getInstructionGenerator()).thenReturn(mockInstructionGenerator);
            when(mockInstructionGenerator.generateInstructions(goal)).thenReturn(testInstructions);
            when(mockAgentSpawner.spawnAndExecute(goal)).thenReturn(longResult);

            // When
            Response response = taskResource.createTaskDetailed(goal);

            // Then
            assertEquals(Response.Status.OK.getStatusCode(), response.getStatus());
            
            @SuppressWarnings("unchecked")
            Map<String, Object> responseBody = (Map<String, Object>) response.getEntity();
            
            assertEquals(longResult, responseBody.get("finalResult"));
        }
    }
}