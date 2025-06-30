package org.acme;

import jakarta.inject.Inject;
import jakarta.ws.rs.GET;
import jakarta.ws.rs.POST;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.core.MediaType;
import jakarta.ws.rs.core.Response;
import java.util.Map;

@Path("/tasks")
public class TaskResource {

    final AgentSpawner agentSpawner;

    @Inject
    public TaskResource(AgentSpawner agentSpawner) {
        this.agentSpawner = agentSpawner;
    }

    @POST
    @Produces(MediaType.TEXT_PLAIN)
    public String createTask(String goal) {
        if (goal == null || goal.isBlank()) {
            return "Please provide a goal in the request body.";
        }
        return agentSpawner.spawnAndExecute(goal);
    }

    @POST
    @Path("/detailed")
    @Produces(MediaType.APPLICATION_JSON)
    public Response createTaskDetailed(String goal) {
        if (goal == null || goal.isBlank()) {
            return Response.status(Response.Status.BAD_REQUEST)
                    .entity(Map.of("error", "Please provide a goal in the request body."))
                    .build();
        }

        try {
            // Get the decomposed instructions first
            DecomposedInstructions instructions = agentSpawner.getInstructionGenerator().generateInstructions(goal);

            // Execute the full process
            String result = agentSpawner.spawnAndExecute(goal);

            // Return detailed response
            var response = Map.of(
                "success", true,
                "goal", goal,
                "plannerInstructions", instructions.plannerInstructions(),
                "writerInstructions", instructions.writerInstructions(),
                "finalResult", result
            );

            return Response.ok(response).build();

        } catch (Exception e) {
            return Response.status(Response.Status.INTERNAL_SERVER_ERROR)
                    .entity(Map.of("error", e.getMessage(), "success", false))
                    .build();
        }
    }

    @GET
    @Path("/health")
    @Produces(MediaType.APPLICATION_JSON)
    public Map<String, Object> health() {
        return Map.of(
            "status", "healthy",
            "service", "Dynamic Agent Spawner",
            "timestamp", System.currentTimeMillis()
        );
    }
}