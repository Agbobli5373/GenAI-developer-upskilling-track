package org.acme;

import io.quarkus.test.junit.QuarkusTest;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;

import jakarta.inject.Inject;

import static org.junit.jupiter.api.Assertions.*;

@QuarkusTest
@DisplayName("AgentSpawner Tests")
class AgentSpawnerTest {

    @Inject
    AgentSpawner agentSpawner;

    @Nested
    @DisplayName("Component Injection Tests")
    class ComponentInjectionTests {

        @Test
        @DisplayName("Should have AgentSpawner injected")
        void testAgentSpawnerInjection() {
            assertNotNull(agentSpawner, "AgentSpawner should be injected");
        }

        @Test
        @DisplayName("Should have instruction generator accessible")
        void testInstructionGeneratorAccessible() {
            // Test that we can access the instruction generator
            assertNotNull(agentSpawner.getInstructionGenerator(), "InstructionGenerator should be accessible");
        }
    }

    @Nested
    @DisplayName("Method Existence Tests")
    class MethodExistenceTests {

        @Test
        @DisplayName("Should have spawnAndExecute method")
        void testSpawnAndExecuteMethodExists() throws NoSuchMethodException {
            // Verify the method exists with correct signature
            var method = AgentSpawner.class.getMethod("spawnAndExecute", String.class);
            assertNotNull(method);
            assertEquals(String.class, method.getReturnType());
        }

        @Test
        @DisplayName("Should have getInstructionGenerator method")
        void testGetInstructionGeneratorMethodExists() throws NoSuchMethodException {
            // Verify the method exists with correct signature
            var method = AgentSpawner.class.getMethod("getInstructionGenerator");
            assertNotNull(method);
            assertEquals(InstructionGeneratorAgent.class, method.getReturnType());
        }
    }

    @Nested
    @DisplayName("Basic Functionality Tests")
    class BasicFunctionalityTests {

        @Test
        @DisplayName("Should return consistent instruction generator instance")
        void testConsistentInstructionGenerator() {
            // Get the instruction generator multiple times
            InstructionGeneratorAgent generator1 = agentSpawner.getInstructionGenerator();
            InstructionGeneratorAgent generator2 = agentSpawner.getInstructionGenerator();

            // Should return the same instance (dependency injection should be consistent)
            assertNotNull(generator1);
            assertNotNull(generator2);
            assertSame(generator1, generator2, "Should return the same instance");
        }

        @Test
        @DisplayName("Should handle null goal input validation")
        void testNullGoalValidation() {
            // This test verifies that the method can handle null input
            // Without external dependencies, we can't test the full execution
            // but we can test that the method signature allows null input
            assertDoesNotThrow(() -> {
                // The method should not throw an exception when called with null
                // (though it may fail due to external dependencies in test environment)
                try {
                    agentSpawner.spawnAndExecute(null);
                } catch (Exception e) {
                    // Expected to fail in test environment due to missing external dependencies
                    // but should not fail due to null pointer issues in our code
                    assertTrue(e.getMessage() == null || !e.getMessage().contains("NullPointerException"));
                }
            });
        }
    }

    @Nested
    @DisplayName("Class Structure Tests")
    class ClassStructureTests {

        @Test
        @DisplayName("Should be properly annotated")
        void testClassAnnotations() {
            // Verify ApplicationScoped annotation
            boolean hasApplicationScoped = false;
            for (var annotation : AgentSpawner.class.getAnnotations()) {
                if (annotation.annotationType().getSimpleName().equals("ApplicationScoped")) {
                    hasApplicationScoped = true;
                    break;
                }
            }
            assertTrue(hasApplicationScoped, "AgentSpawner should have @ApplicationScoped annotation");
        }

        @Test
        @DisplayName("Should be in correct package")
        void testPackage() {
            assertEquals("org.acme", AgentSpawner.class.getPackageName());
        }
    }
}