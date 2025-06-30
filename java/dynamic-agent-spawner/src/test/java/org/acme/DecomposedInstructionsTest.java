package org.acme;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;

import static org.junit.jupiter.api.Assertions.*;

@DisplayName("DecomposedInstructions Tests")
class DecomposedInstructionsTest {

    @Nested
    @DisplayName("Record Creation Tests")
    class RecordCreationTests {

        @Test
        @DisplayName("Should create record with valid instructions")
        void testCreateWithValidInstructions() {
            // Given
            String plannerInstructions = "Create a detailed outline with main sections and subsections";
            String writerInstructions = "Write engaging content based on the provided outline";

            // When
            DecomposedInstructions instructions = new DecomposedInstructions(plannerInstructions, writerInstructions);

            // Then
            assertNotNull(instructions);
            assertEquals(plannerInstructions, instructions.plannerInstructions());
            assertEquals(writerInstructions, instructions.writerInstructions());
        }

        @Test
        @DisplayName("Should create record with null instructions")
        void testCreateWithNullInstructions() {
            // When
            DecomposedInstructions instructions = new DecomposedInstructions(null, null);

            // Then
            assertNotNull(instructions);
            assertNull(instructions.plannerInstructions());
            assertNull(instructions.writerInstructions());
        }

        @Test
        @DisplayName("Should create record with empty instructions")
        void testCreateWithEmptyInstructions() {
            // When
            DecomposedInstructions instructions = new DecomposedInstructions("", "");

            // Then
            assertNotNull(instructions);
            assertEquals("", instructions.plannerInstructions());
            assertEquals("", instructions.writerInstructions());
        }

        @Test
        @DisplayName("Should create record with mixed null and valid instructions")
        void testCreateWithMixedInstructions() {
            // Test planner null, writer valid
            DecomposedInstructions instructions1 = new DecomposedInstructions(null, "Write content");
            assertNull(instructions1.plannerInstructions());
            assertEquals("Write content", instructions1.writerInstructions());

            // Test planner valid, writer null
            DecomposedInstructions instructions2 = new DecomposedInstructions("Plan content", null);
            assertEquals("Plan content", instructions2.plannerInstructions());
            assertNull(instructions2.writerInstructions());
        }

        @Test
        @DisplayName("Should create record with whitespace instructions")
        void testCreateWithWhitespaceInstructions() {
            // Given
            String whitespaceInstructions = "   \n\t   ";

            // When
            DecomposedInstructions instructions = new DecomposedInstructions(whitespaceInstructions, whitespaceInstructions);

            // Then
            assertNotNull(instructions);
            assertEquals(whitespaceInstructions, instructions.plannerInstructions());
            assertEquals(whitespaceInstructions, instructions.writerInstructions());
        }

        @Test
        @DisplayName("Should create record with very long instructions")
        void testCreateWithLongInstructions() {
            // Given
            String longInstruction = "This is a very long instruction that contains many details. ".repeat(100);

            // When
            DecomposedInstructions instructions = new DecomposedInstructions(longInstruction, longInstruction);

            // Then
            assertNotNull(instructions);
            assertEquals(longInstruction, instructions.plannerInstructions());
            assertEquals(longInstruction, instructions.writerInstructions());
        }
    }

    @Nested
    @DisplayName("Record Equality Tests")
    class EqualityTests {

        @Test
        @DisplayName("Should be equal when all fields match")
        void testEqualityWithMatchingFields() {
            // Given
            String plannerInst = "Plan the content";
            String writerInst = "Write the content";
            
            DecomposedInstructions instructions1 = new DecomposedInstructions(plannerInst, writerInst);
            DecomposedInstructions instructions2 = new DecomposedInstructions(plannerInst, writerInst);

            // When & Then
            assertEquals(instructions1, instructions2);
            assertEquals(instructions1.hashCode(), instructions2.hashCode());
        }

        @Test
        @DisplayName("Should not be equal when planner instructions differ")
        void testInequalityWithDifferentPlannerInstructions() {
            // Given
            DecomposedInstructions instructions1 = new DecomposedInstructions("Plan A", "Write content");
            DecomposedInstructions instructions2 = new DecomposedInstructions("Plan B", "Write content");

            // When & Then
            assertNotEquals(instructions1, instructions2);
        }

        @Test
        @DisplayName("Should not be equal when writer instructions differ")
        void testInequalityWithDifferentWriterInstructions() {
            // Given
            DecomposedInstructions instructions1 = new DecomposedInstructions("Plan content", "Write A");
            DecomposedInstructions instructions2 = new DecomposedInstructions("Plan content", "Write B");

            // When & Then
            assertNotEquals(instructions1, instructions2);
        }

        @Test
        @DisplayName("Should be equal when both have null fields")
        void testEqualityWithNullFields() {
            // Given
            DecomposedInstructions instructions1 = new DecomposedInstructions(null, null);
            DecomposedInstructions instructions2 = new DecomposedInstructions(null, null);

            // When & Then
            assertEquals(instructions1, instructions2);
            assertEquals(instructions1.hashCode(), instructions2.hashCode());
        }

        @Test
        @DisplayName("Should not be equal when one has null fields and other doesn't")
        void testInequalityWithNullAndNonNullFields() {
            // Given
            DecomposedInstructions instructions1 = new DecomposedInstructions(null, null);
            DecomposedInstructions instructions2 = new DecomposedInstructions("Plan", "Write");

            // When & Then
            assertNotEquals(instructions1, instructions2);
        }

        @Test
        @DisplayName("Should not be equal to null")
        void testInequalityWithNull() {
            // Given
            DecomposedInstructions instructions = new DecomposedInstructions("Plan", "Write");

            // When & Then
            assertNotEquals(instructions, null);
        }

        @Test
        @DisplayName("Should not be equal to different type")
        void testInequalityWithDifferentType() {
            // Given
            DecomposedInstructions instructions = new DecomposedInstructions("Plan", "Write");
            String notAnInstruction = "Not an instruction object";

            // When & Then
            assertNotEquals(instructions, notAnInstruction);
        }
    }

    @Nested
    @DisplayName("toString Tests")
    class ToStringTests {

        @Test
        @DisplayName("Should generate meaningful toString with valid values")
        void testToStringWithValidValues() {
            // Given
            DecomposedInstructions instructions = new DecomposedInstructions("Plan content", "Write content");

            // When
            String toString = instructions.toString();

            // Then
            assertNotNull(toString);
            assertTrue(toString.contains("Plan content"));
            assertTrue(toString.contains("Write content"));
            assertTrue(toString.contains("DecomposedInstructions"));
        }

        @Test
        @DisplayName("Should generate toString with null values")
        void testToStringWithNullValues() {
            // Given
            DecomposedInstructions instructions = new DecomposedInstructions(null, null);

            // When
            String toString = instructions.toString();

            // Then
            assertNotNull(toString);
            assertTrue(toString.contains("null"));
            assertTrue(toString.contains("DecomposedInstructions"));
        }

        @Test
        @DisplayName("Should generate toString with empty values")
        void testToStringWithEmptyValues() {
            // Given
            DecomposedInstructions instructions = new DecomposedInstructions("", "");

            // When
            String toString = instructions.toString();

            // Then
            assertNotNull(toString);
            assertTrue(toString.contains("DecomposedInstructions"));
        }
    }

    @Nested
    @DisplayName("Immutability Tests")
    class ImmutabilityTests {

        @Test
        @DisplayName("Should be immutable record")
        void testImmutability() {
            // Given
            String originalPlanner = "Original planner instruction";
            String originalWriter = "Original writer instruction";
            
            DecomposedInstructions instructions = new DecomposedInstructions(originalPlanner, originalWriter);

            // When - Try to access the values
            String plannerAccessed = instructions.plannerInstructions();
            String writerAccessed = instructions.writerInstructions();

            // Then - Values should be the same (records are immutable by nature)
            assertEquals(originalPlanner, plannerAccessed);
            assertEquals(originalWriter, writerAccessed);
            
            // The record cannot be modified after creation - this is guaranteed by the record syntax
            // We verify the accessor methods return the original values
            assertSame(originalPlanner, instructions.plannerInstructions());
            assertSame(originalWriter, instructions.writerInstructions());
        }
    }

    @Nested
    @DisplayName("Special Character Tests")
    class SpecialCharacterTests {

        @Test
        @DisplayName("Should handle special characters in instructions")
        void testSpecialCharacters() {
            // Given
            String plannerWithSpecialChars = "Plan: Use emojis 😊, symbols @#$%, and unicode characters ñáéíóú";
            String writerWithSpecialChars = "Write with quotes \"hello\", apostrophes 'world', and newlines\n\ntab\ttabs";

            // When
            DecomposedInstructions instructions = new DecomposedInstructions(plannerWithSpecialChars, writerWithSpecialChars);

            // Then
            assertEquals(plannerWithSpecialChars, instructions.plannerInstructions());
            assertEquals(writerWithSpecialChars, instructions.writerInstructions());
        }

        @Test
        @DisplayName("Should handle JSON-like strings")
        void testJSONLikeStrings() {
            // Given
            String jsonLikePlanner = "{\"task\": \"plan\", \"priority\": \"high\"}";
            String jsonLikeWriter = "[\"write\", \"edit\", \"review\"]";

            // When
            DecomposedInstructions instructions = new DecomposedInstructions(jsonLikePlanner, jsonLikeWriter);

            // Then
            assertEquals(jsonLikePlanner, instructions.plannerInstructions());
            assertEquals(jsonLikeWriter, instructions.writerInstructions());
        }

        @Test
        @DisplayName("Should handle multi-line instructions")
        void testMultiLineInstructions() {
            // Given
            String multiLinePlanner = """
                Step 1: Analyze the requirements
                Step 2: Create an outline
                Step 3: Define key sections
                Step 4: Plan the flow
                """;
            
            String multiLineWriter = """
                1. Write introduction
                2. Develop main content
                3. Add examples
                4. Write conclusion
                """;

            // When
            DecomposedInstructions instructions = new DecomposedInstructions(multiLinePlanner, multiLineWriter);

            // Then
            assertEquals(multiLinePlanner, instructions.plannerInstructions());
            assertEquals(multiLineWriter, instructions.writerInstructions());
        }
    }
}