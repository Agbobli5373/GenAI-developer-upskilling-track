package org.acme;

import dev.langchain4j.service.SystemMessage;
import dev.langchain4j.service.UserMessage;
import io.quarkiverse.langchain4j.RegisterAiService;

@RegisterAiService
public interface InstructionGeneratorAgent {

    @SystemMessage("""
        You are a project management AI that generates simple, clear instructions.
        Your responses must ALWAYS be in valid JSON format with STRING values only.
        Do not use nested objects or arrays in your JSON response.
        """)
    @UserMessage("""
        Generate two sets of instructions as simple text strings for two different AI agents: a PLANNER and a WRITER.
        
        - The PLANNER agent creates structured outlines or key points
        - The WRITER agent writes final, polished content based on the planner's output
        
        Return ONLY a valid JSON object with this EXACT structure (both values must be simple strings):
        {
          "plannerInstructions": "Your complete instructions for the planner agent as a single text string...",
          "writerInstructions": "Your complete instructions for the writer agent as a single text string..."
        }
        
        Goal: {{goal}}
        
        Important: Each instruction field must contain ALL guidance as one continuous text string, not as nested objects or arrays.
        """)
    DecomposedInstructions generateInstructions(String goal);
}
