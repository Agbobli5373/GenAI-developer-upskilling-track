package com.isaac.contextual_memory_chatbot;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;

/**
 * Controller for handling page routing and rendering for the Contextual Memory
 * Chatbot application.
 * Provides endpoints for various user interface pages including the main chat
 * interface,
 * help documentation, about information, and error handling.
 */
@Controller
public class PageController {

    /**
     * Serves the main chat interface page.
     * This is the primary user interaction point for the chatbot.
     * 
     * @return the chat template name
     */
    @GetMapping("/")
    public String chatPage() {
        return "chat";
    }

    /**
     * Serves the main chat interface page with explicit '/chat' mapping.
     * Provides an alternative route to access the chat functionality.
     * 
     * @return the chat template name
     */
    @GetMapping("/chat")
    public String explicitChatPage() {
        return "chat";
    }

    /**
     * Serves the help page with usage instructions and FAQs.
     * Provides users with guidance on how to effectively use the chatbot.
     * 
     * @param model the Spring MVC model for passing data to the view
     * @return the help template name
     */
    @GetMapping("/help")
    public String helpPage(Model model) {
        model.addAttribute("pageTitle", "Help & Usage Guide");
        model.addAttribute("appName", "Contextual Memory Chatbot");
        return "help";
    }

    /**
     * Serves the about page with application information and features.
     * Displays information about the chatbot's capabilities and technology stack.
     * 
     * @param model the Spring MVC model for passing data to the view
     * @return the about template name
     */
    @GetMapping("/about")
    public String aboutPage(Model model) {
        model.addAttribute("pageTitle", "About");
        model.addAttribute("appName", "Contextual Memory Chatbot");
        model.addAttribute("version", "1.0.0");
        model.addAttribute("description",
                "An intelligent chatbot with contextual memory powered by Spring AI and Gemini");
        return "about";
    }

    /**
     * Serves the privacy policy page.
     * Provides users with information about data handling and privacy practices.
     * 
     * @param model the Spring MVC model for passing data to the view
     * @return the privacy template name
     */
    @GetMapping("/privacy")
    public String privacyPage(Model model) {
        model.addAttribute("pageTitle", "Privacy Policy");
        model.addAttribute("appName", "Contextual Memory Chatbot");
        return "privacy";
    }

    /**
     * Serves the settings page for user preferences.
     * Allows users to configure chatbot behavior and interface preferences.
     * 
     * @param model the Spring MVC model for passing data to the view
     * @return the settings template name
     */
    @GetMapping("/settings")
    public String settingsPage(Model model) {
        model.addAttribute("pageTitle", "Settings");
        model.addAttribute("appName", "Contextual Memory Chatbot");
        return "settings";
    }

    /**
     * Custom error handler for 404 Not Found errors.
     * Provides a user-friendly error page when requested resources are not found.
     * 
     * @param model the Spring MVC model for passing data to the view
     * @return the 404 error template name
     */
    @GetMapping("/error/404")
    public String error404Page(Model model) {
        model.addAttribute("pageTitle", "Page Not Found");
        model.addAttribute("errorCode", "404");
        model.addAttribute("errorMessage", "The page you're looking for doesn't exist.");
        return "error/404";
    }

    /**
     * Custom error handler for 500 Internal Server Error.
     * Provides a user-friendly error page when server errors occur.
     * 
     * @param model the Spring MVC model for passing data to the view
     * @return the 500 error template name
     */
    @GetMapping("/error/500")
    public String error500Page(Model model) {
        model.addAttribute("pageTitle", "Server Error");
        model.addAttribute("errorCode", "500");
        model.addAttribute("errorMessage", "Something went wrong on our end. Please try again later.");
        return "error/500";
    }
}
