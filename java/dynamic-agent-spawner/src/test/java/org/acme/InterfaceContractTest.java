package org.acme;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;

import static org.junit.jupiter.api.Assertions.*;

@DisplayName("Interface Contract Tests")
class InterfaceContractTest {

    @Nested
    @DisplayName("InstructionGeneratorAgent Interface Tests")
    class InstructionGeneratorAgentTests {

        @Test
        @DisplayName("Should define correct method signature for generateInstructions")
        void testGenerateInstructionsMethodSignature() throws NoSuchMethodException {
            // Verify the interface has the expected method
            var method = InstructionGeneratorAgent.class.getMethod("generateInstructions", String.class);
            
            assertNotNull(method);
            assertEquals(DecomposedInstructions.class, method.getReturnType());
            assertEquals(1, method.getParameterCount());
            assertEquals(String.class, method.getParameterTypes()[0]);
        }

        @Test
        @DisplayName("Should be a public interface")
        void testInterfaceVisibility() {
            assertTrue(InstructionGeneratorAgent.class.isInterface());
            assertTrue(java.lang.reflect.Modifier.isPublic(InstructionGeneratorAgent.class.getModifiers()));
        }

        @Test
        @DisplayName("Should have expected annotations")
        void testInterfaceAnnotations() {
            // Verify the interface has RegisterAiService annotation
            boolean hasRegisterAiService = false;
            for (var annotation : InstructionGeneratorAgent.class.getAnnotations()) {
                if (annotation.annotationType().getSimpleName().equals("RegisterAiService")) {
                    hasRegisterAiService = true;
                    break;
                }
            }
            assertTrue(hasRegisterAiService, "Interface should have @RegisterAiService annotation");
        }
    }

    @Nested
    @DisplayName("TaskExecutionAgent Interface Tests")
    class TaskExecutionAgentTests {

        @Test
        @DisplayName("Should define correct method signature for executeTask")
        void testExecuteTaskMethodSignature() throws NoSuchMethodException {
            // Verify the interface has the expected method
            var method = TaskExecutionAgent.class.getMethod("executeTask", String.class, String.class);
            
            assertNotNull(method);
            assertEquals(String.class, method.getReturnType());
            assertEquals(2, method.getParameterCount());
            assertEquals(String.class, method.getParameterTypes()[0]);
            assertEquals(String.class, method.getParameterTypes()[1]);
        }

        @Test
        @DisplayName("Should be a public interface")
        void testInterfaceVisibility() {
            assertTrue(TaskExecutionAgent.class.isInterface());
            assertTrue(java.lang.reflect.Modifier.isPublic(TaskExecutionAgent.class.getModifiers()));
        }

        @Test
        @DisplayName("Should have expected method annotations")
        void testMethodAnnotations() throws NoSuchMethodException {
            var method = TaskExecutionAgent.class.getMethod("executeTask", String.class, String.class);
            
            // Check for SystemMessage annotation
            boolean hasSystemMessage = false;
            for (var annotation : method.getAnnotations()) {
                if (annotation.annotationType().getSimpleName().equals("SystemMessage")) {
                    hasSystemMessage = true;
                    break;
                }
            }
            assertTrue(hasSystemMessage, "executeTask method should have @SystemMessage annotation");

            // Check for UserMessage annotation on first parameter
            var parameterAnnotations = method.getParameterAnnotations();
            boolean hasUserMessage = false;
            if (parameterAnnotations.length > 0) {
                for (var annotation : parameterAnnotations[0]) {
                    if (annotation.annotationType().getSimpleName().equals("UserMessage")) {
                        hasUserMessage = true;
                        break;
                    }
                }
            }
            assertTrue(hasUserMessage, "First parameter should have @UserMessage annotation");
        }
    }

    @Nested
    @DisplayName("DecomposedInstructions Record Tests")
    class DecomposedInstructionsRecordTests {

        @Test
        @DisplayName("Should be a record class")
        void testIsRecord() {
            assertTrue(DecomposedInstructions.class.isRecord());
        }

        @Test
        @DisplayName("Should have correct record components")
        void testRecordComponents() {
            var components = DecomposedInstructions.class.getRecordComponents();
            
            assertEquals(2, components.length);
            
            // Check plannerInstructions component
            assertEquals("plannerInstructions", components[0].getName());
            assertEquals(String.class, components[0].getType());
            
            // Check writerInstructions component
            assertEquals("writerInstructions", components[1].getName());
            assertEquals(String.class, components[1].getType());
        }

        @Test
        @DisplayName("Should have accessor methods for record components")
        void testAccessorMethods() throws NoSuchMethodException {
            // Test plannerInstructions accessor
            var plannerMethod = DecomposedInstructions.class.getMethod("plannerInstructions");
            assertEquals(String.class, plannerMethod.getReturnType());
            assertEquals(0, plannerMethod.getParameterCount());
            
            // Test writerInstructions accessor
            var writerMethod = DecomposedInstructions.class.getMethod("writerInstructions");
            assertEquals(String.class, writerMethod.getReturnType());
            assertEquals(0, writerMethod.getParameterCount());
        }

        @Test
        @DisplayName("Should have proper constructor")
        void testConstructor() throws NoSuchMethodException {
            var constructor = DecomposedInstructions.class.getConstructor(String.class, String.class);
            assertNotNull(constructor);
            assertEquals(2, constructor.getParameterCount());
        }

        @Test
        @DisplayName("Should extend Record class")
        void testExtendsRecord() {
            assertEquals(Record.class, DecomposedInstructions.class.getSuperclass());
        }
    }

    @Nested
    @DisplayName("AgentSpawner Class Tests")
    class AgentSpawnerClassTests {

        @Test
        @DisplayName("Should have ApplicationScoped annotation")
        void testApplicationScopedAnnotation() {
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
        @DisplayName("Should have required public methods")
        void testRequiredMethods() throws NoSuchMethodException {
            // Test spawnAndExecute method
            var spawnMethod = AgentSpawner.class.getMethod("spawnAndExecute", String.class);
            assertEquals(String.class, spawnMethod.getReturnType());
            
            // Test getInstructionGenerator method
            var getterMethod = AgentSpawner.class.getMethod("getInstructionGenerator");
            assertEquals(InstructionGeneratorAgent.class, getterMethod.getReturnType());
        }

        @Test
        @DisplayName("Should be a public class")
        void testClassVisibility() {
            assertTrue(java.lang.reflect.Modifier.isPublic(AgentSpawner.class.getModifiers()));
            assertFalse(AgentSpawner.class.isInterface());
        }
    }

    @Nested
    @DisplayName("TaskResource Class Tests")
    class TaskResourceClassTests {

        @Test
        @DisplayName("Should have Path annotation")
        void testPathAnnotation() {
            boolean hasPath = false;
            for (var annotation : TaskResource.class.getAnnotations()) {
                if (annotation.annotationType().getSimpleName().equals("Path")) {
                    hasPath = true;
                    break;
                }
            }
            assertTrue(hasPath, "TaskResource should have @Path annotation");
        }

        @Test
        @DisplayName("Should have required HTTP method annotations on endpoints")
        void testEndpointAnnotations() throws NoSuchMethodException {
            // Test createTask method has POST annotation
            var createTaskMethod = TaskResource.class.getMethod("createTask", String.class);
            boolean hasPost = false;
            for (var annotation : createTaskMethod.getAnnotations()) {
                if (annotation.annotationType().getSimpleName().equals("POST")) {
                    hasPost = true;
                    break;
                }
            }
            assertTrue(hasPost, "createTask method should have @POST annotation");

            // Test health method has GET annotation
            var healthMethod = TaskResource.class.getMethod("health");
            boolean hasGet = false;
            for (var annotation : healthMethod.getAnnotations()) {
                if (annotation.annotationType().getSimpleName().equals("GET")) {
                    hasGet = true;
                    break;
                }
            }
            assertTrue(hasGet, "health method should have @GET annotation");
        }

        @Test
        @DisplayName("Should have constructor with AgentSpawner parameter")
        void testConstructor() throws NoSuchMethodException {
            var constructor = TaskResource.class.getConstructor(AgentSpawner.class);
            assertNotNull(constructor);
            
            // Check for Inject annotation
            boolean hasInject = false;
            for (var annotation : constructor.getAnnotations()) {
                if (annotation.annotationType().getSimpleName().equals("Inject")) {
                    hasInject = true;
                    break;
                }
            }
            assertTrue(hasInject, "Constructor should have @Inject annotation");
        }

        @Test
        @DisplayName("Should be a public class")
        void testClassVisibility() {
            assertTrue(java.lang.reflect.Modifier.isPublic(TaskResource.class.getModifiers()));
            assertFalse(TaskResource.class.isInterface());
        }
    }

    @Nested
    @DisplayName("Package Structure Tests")
    class PackageStructureTests {

        @Test
        @DisplayName("Should have all classes in correct package")
        void testPackageNames() {
            assertEquals("org.acme", AgentSpawner.class.getPackageName());
            assertEquals("org.acme", TaskResource.class.getPackageName());
            assertEquals("org.acme", DecomposedInstructions.class.getPackageName());
            assertEquals("org.acme", InstructionGeneratorAgent.class.getPackageName());
            assertEquals("org.acme", TaskExecutionAgent.class.getPackageName());
        }

        @Test
        @DisplayName("Should have proper imports available")
        void testImportAvailability() {
            // This test ensures that the classes are properly structured
            // and can reference each other within the same package
            assertDoesNotThrow(() -> {
                // These should all be accessible within the same package
                Class.forName("org.acme.AgentSpawner");
                Class.forName("org.acme.TaskResource");
                Class.forName("org.acme.DecomposedInstructions");
                Class.forName("org.acme.InstructionGeneratorAgent");
                Class.forName("org.acme.TaskExecutionAgent");
            });
        }
    }

    @Nested
    @DisplayName("Dependency Contract Tests")
    class DependencyContractTests {

        @Test
        @DisplayName("Should verify AgentSpawner can accept InstructionGeneratorAgent")
        void testAgentSpawnerDependencies() {
            // This test ensures the dependency contracts are correct
            assertDoesNotThrow(() -> {
                // AgentSpawner should be able to work with InstructionGeneratorAgent
                // and return DecomposedInstructions
                var agentSpawnerClass = AgentSpawner.class;
                var getterMethod = agentSpawnerClass.getMethod("getInstructionGenerator");
                assertEquals(InstructionGeneratorAgent.class, getterMethod.getReturnType());
            });
        }

        @Test
        @DisplayName("Should verify TaskResource can accept AgentSpawner")
        void testTaskResourceDependencies() throws NoSuchMethodException {
            // TaskResource should have a constructor that accepts AgentSpawner
            var constructor = TaskResource.class.getConstructor(AgentSpawner.class);
            assertNotNull(constructor);
            assertEquals(1, constructor.getParameterCount());
            assertEquals(AgentSpawner.class, constructor.getParameterTypes()[0]);
        }

        @Test
        @DisplayName("Should verify InstructionGeneratorAgent returns correct type")
        void testInstructionGeneratorReturn() throws NoSuchMethodException {
            var method = InstructionGeneratorAgent.class.getMethod("generateInstructions", String.class);
            assertEquals(DecomposedInstructions.class, method.getReturnType());
        }
    }
}