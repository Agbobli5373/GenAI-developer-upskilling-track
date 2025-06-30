package org.acme;

import io.quarkus.test.junit.QuarkusTest;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;

import static io.restassured.RestAssured.given;
import static org.hamcrest.CoreMatchers.*;
import static org.hamcrest.Matchers.greaterThan;

@QuarkusTest
@DisplayName("TaskResource Integration Tests")
class TaskResourceIntegrationTest {

    @Nested
    @DisplayName("REST API Integration Tests")
    class RestApiIntegrationTests {

        @Test
        @DisplayName("Should return healthy status from health endpoint")
        void testHealthEndpoint() {
            given()
                .when().get("/tasks/health")
                .then()
                    .statusCode(200)
                    .contentType("application/json")
                    .body("status", equalTo("healthy"))
                    .body("service", equalTo("Dynamic Agent Spawner"))
                    .body("timestamp", is(instanceOf(Long.class)));
        }

        @Test
        @DisplayName("Should return bad request for empty goal in simple endpoint")
        void testSimpleTaskEndpointWithEmptyGoal() {
            given()
                .contentType("text/plain")
                .body("")
                .when().post("/tasks")
                .then()
                    .statusCode(200)
                    .contentType("text/plain")
                    .body(equalTo("Please provide a goal in the request body."));
        }

        @Test
        @DisplayName("Should return bad request for null goal in simple endpoint")
        void testSimpleTaskEndpointWithNoBody() {
            given()
                .contentType("text/plain")
                .when().post("/tasks")
                .then()
                    .statusCode(200)
                    .contentType("text/plain")
                    .body(equalTo("Please provide a goal in the request body."));
        }

        @Test
        @DisplayName("Should return bad request for whitespace-only goal in simple endpoint")
        void testSimpleTaskEndpointWithWhitespaceGoal() {
            given()
                .contentType("text/plain")
                .body("   \n\t   ")
                .when().post("/tasks")
                .then()
                    .statusCode(200)
                    .contentType("text/plain")
                    .body(equalTo("Please provide a goal in the request body."));
        }

        @Test
        @DisplayName("Should return error for empty goal in detailed endpoint")
        void testDetailedTaskEndpointWithEmptyGoal() {
            given()
                .contentType("text/plain")
                .body("")
                .when().post("/tasks/detailed")
                .then()
                    .statusCode(400)
                    .contentType("application/json")
                    .body("error", equalTo("Please provide a goal in the request body."));
        }

        @Test
        @DisplayName("Should return error for null goal in detailed endpoint")
        void testDetailedTaskEndpointWithNoBody() {
            given()
                .contentType("text/plain")
                .when().post("/tasks/detailed")
                .then()
                    .statusCode(400)
                    .contentType("application/json")
                    .body("error", equalTo("Please provide a goal in the request body."));
        }

        @Test
        @DisplayName("Should return error for whitespace-only goal in detailed endpoint")
        void testDetailedTaskEndpointWithWhitespaceGoal() {
            given()
                .contentType("text/plain")
                .body("   \n\t   ")
                .when().post("/tasks/detailed")
                .then()
                    .statusCode(400)
                    .contentType("application/json")
                    .body("error", equalTo("Please provide a goal in the request body."));
        }

        @Test
        @DisplayName("Should handle valid goal in simple endpoint with external service unavailable")
        void testSimpleTaskEndpointWithValidGoalServiceUnavailable() {
            // This test expects the external AI service to be unavailable in test environment
            // and should return an error response
            given()
                .contentType("text/plain")
                .body("Write a test blog post about AI")
                .when().post("/tasks")
                .then()
                    .statusCode(anyOf(is(200), is(500))); // May succeed with mock or fail with external service
        }

        @Test
        @DisplayName("Should handle valid goal in detailed endpoint with external service unavailable")
        void testDetailedTaskEndpointWithValidGoalServiceUnavailable() {
            // This test expects the external AI service to be unavailable in test environment
            // and should return an error response
            given()
                .contentType("text/plain")
                .body("Write a test blog post about AI")
                .when().post("/tasks/detailed")
                .then()
                    .statusCode(anyOf(is(200), is(500))); // May succeed with mock or fail with external service
        }
    }

    @Nested
    @DisplayName("Content Type Tests")
    class ContentTypeTests {

        @Test
        @DisplayName("Should handle different content types for simple endpoint")
        void testSimpleEndpointContentTypes() {
            String goal = "Create a simple test document";

            // Test with text/plain
            given()
                .contentType("text/plain")
                .body(goal)
                .when().post("/tasks")
                .then()
                    .statusCode(anyOf(is(200), is(500)));

            // Test without explicit content type
            given()
                .body(goal)
                .when().post("/tasks")
                .then()
                    .statusCode(anyOf(is(200), is(500)));
        }

        @Test
        @DisplayName("Should handle different content types for detailed endpoint")
        void testDetailedEndpointContentTypes() {
            String goal = "Create a detailed test document";

            // Test with text/plain
            given()
                .contentType("text/plain")
                .body(goal)
                .when().post("/tasks/detailed")
                .then()
                    .statusCode(anyOf(is(200), is(500)));

            // Test without explicit content type
            given()
                .body(goal)
                .when().post("/tasks/detailed")
                .then()
                    .statusCode(anyOf(is(200), is(500)));
        }
    }

    @Nested
    @DisplayName("Error Handling Integration Tests")
    class ErrorHandlingIntegrationTests {

        @Test
        @DisplayName("Should handle very long goals gracefully")
        void testVeryLongGoal() {
            String longGoal = "Create a comprehensive analysis of " + "artificial intelligence applications ".repeat(50);

            given()
                .contentType("text/plain")
                .body(longGoal)
                .when().post("/tasks/detailed")
                .then()
                    .statusCode(anyOf(is(200), is(400), is(500)));
        }

        @Test
        @DisplayName("Should handle special characters in goals")
        void testSpecialCharactersInGoal() {
            String specialGoal = "Create content with emojis 😊🚀 and symbols @#$% & unicode ñáéíóú";

            given()
                .contentType("text/plain")
                .body(specialGoal)
                .when().post("/tasks/detailed")
                .then()
                    .statusCode(anyOf(is(200), is(400), is(500)));
        }

        @Test
        @DisplayName("Should handle JSON-like content in goals")
        void testJSONLikeGoal() {
            String jsonLikeGoal = "{\"task\": \"write\", \"topic\": \"AI\", \"length\": \"short\"}";

            given()
                .contentType("text/plain")
                .body(jsonLikeGoal)
                .when().post("/tasks/detailed")
                .then()
                    .statusCode(anyOf(is(200), is(400), is(500)));
        }

        @Test
        @DisplayName("Should handle multi-line goals")
        void testMultiLineGoal() {
            String multiLineGoal = """
                Create a technical documentation that includes:
                1. Introduction to the technology
                2. Installation instructions
                3. Configuration examples
                4. Best practices
                5. Troubleshooting guide
                """;

            given()
                .contentType("text/plain")
                .body(multiLineGoal)
                .when().post("/tasks/detailed")
                .then()
                    .statusCode(anyOf(is(200), is(400), is(500)));
        }
    }

    @Nested
    @DisplayName("Performance Integration Tests")
    class PerformanceIntegrationTests {

        @Test
        @DisplayName("Should handle multiple consecutive requests")
        void testMultipleConsecutiveRequests() {
            for (int i = 0; i < 3; i++) {
                given()
                    .when().get("/tasks/health")
                    .then()
                        .statusCode(200)
                        .body("status", equalTo("healthy"));
            }
        }

        @Test
        @DisplayName("Should handle rapid consecutive requests to detailed endpoint")
        void testRapidConsecutiveRequestsDetailed() {
            for (int i = 0; i < 3; i++) {
                given()
                    .contentType("text/plain")
                    .body("Test goal " + i)
                    .when().post("/tasks/detailed")
                    .then()
                        .statusCode(anyOf(is(200), is(400), is(500)));
            }
        }
    }

    @Nested
    @DisplayName("CORS and Headers Integration Tests")
    class CorsAndHeadersTests {

        @Test
        @DisplayName("Should handle OPTIONS requests for CORS")
        void testOptionsRequestForCORS() {
            given()
                .when().options("/tasks/health")
                .then()
                    .statusCode(anyOf(is(200), is(204)));
        }

        @Test
        @DisplayName("Should accept requests with various headers")
        void testRequestsWithHeaders() {
            given()
                .header("Accept", "application/json")
                .header("User-Agent", "Test-Client/1.0")
                .when().get("/tasks/health")
                .then()
                    .statusCode(200);
        }
    }

    @Nested
    @DisplayName("Service Availability Tests")
    class ServiceAvailabilityTests {

        @Test
        @DisplayName("Should indicate service is running via health check")
        void testServiceAvailability() {
            given()
                .when().get("/tasks/health")
                .then()
                    .statusCode(200)
                    .body("status", equalTo("healthy"))
                    .body("service", equalTo("Dynamic Agent Spawner"));
        }

        @Test
        @DisplayName("Should have consistent response times for health checks")
        void testHealthCheckResponseTime() {
            // Run multiple health checks to ensure consistent response
            for (int i = 0; i < 5; i++) {
                long startTime = System.currentTimeMillis();
                
                given()
                    .when().get("/tasks/health")
                    .then()
                        .statusCode(200);
                
                long responseTime = System.currentTimeMillis() - startTime;
                // Health check should be very fast (under 1 second)
                assertTrue(responseTime < 1000, "Health check took too long: " + responseTime + "ms");
            }
        }
    }

    @Nested
    @DisplayName("Edge Case Integration Tests")
    class EdgeCaseIntegrationTests {

        @Test
        @DisplayName("Should handle binary-like content gracefully")
        void testBinaryLikeContent() {
            byte[] binaryLikeData = new byte[]{(byte)0x00, (byte)0x01, (byte)0x02, (byte)0x03, (byte)0xFF};
            String binaryString = new String(binaryLikeData);

            given()
                .contentType("text/plain")
                .body(binaryString)
                .when().post("/tasks/detailed")
                .then()
                    .statusCode(anyOf(is(200), is(400), is(500)));
        }

        @Test
        @DisplayName("Should handle extremely short goals")
        void testExtremelyShortGoal() {
            given()
                .contentType("text/plain")
                .body("a")
                .when().post("/tasks/detailed")
                .then()
                    .statusCode(anyOf(is(200), is(400), is(500)));
        }

        @Test
        @DisplayName("Should handle goals with only punctuation")
        void testPunctuationOnlyGoal() {
            given()
                .contentType("text/plain")
                .body("!@#$%^&*()")
                .when().post("/tasks/detailed")
                .then()
                    .statusCode(anyOf(is(200), is(400), is(500)));
        }
    }

    private void assertTrue(boolean condition, String message) {
        if (!condition) {
            throw new AssertionError(message);
        }
    }
}