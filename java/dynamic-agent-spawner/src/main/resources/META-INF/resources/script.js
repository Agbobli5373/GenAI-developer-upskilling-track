class AgentSpawnerUI {
    constructor() {
        // Wait for DOM to be fully loaded before initializing
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.init());
        } else {
            this.init();
        }
    }

    init() {
        this.executeBtn = document.getElementById('executeBtn');
        this.taskInput = document.getElementById('taskInput');
        this.resultsSection = document.getElementById('resultsSection');
        this.errorSection = document.getElementById('errorSection');
        this.retryBtn = document.getElementById('retryBtn');

        // Verify all essential elements exist
        if (!this.executeBtn || !this.taskInput || !this.resultsSection || !this.errorSection) {
            console.error('Essential DOM elements not found');
            return;
        }

        this.initEventListeners();
        this.checkHealthStatus().then(r => {});
    }

    initEventListeners() {
        if (this.executeBtn) {
            this.executeBtn.addEventListener('click', () => this.executeTask());
        }
        if (this.retryBtn) {
            this.retryBtn.addEventListener('click', () => this.hideError());
        }

        // Allow Enter + Ctrl to submit
        if (this.taskInput) {
            this.taskInput.addEventListener('keydown', (e) => {
                if (e.ctrlKey && e.key === 'Enter') {
                    this.executeTask().then(r => {});
                }
            });
        }
    }

    async checkHealthStatus() {
        try {
            const response = await fetch('/tasks/health');
            const health = await response.json();
            console.log('Service health:', health);
        } catch (error) {
            console.warn('Health check failed:', error);
        }
    }

    async executeTask() {
        if (!this.taskInput) return;

        const task = this.taskInput.value.trim();

        if (!task) {
            this.showError('Please enter a task description.');
            return;
        }

        this.startExecution();

        try {
            // Use the detailed endpoint for better UI feedback
            const response = await fetch('/tasks/detailed', {
                method: 'POST',
                headers: {
                    'Content-Type': 'text/plain',
                },
                body: task
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ error: `HTTP ${response.status}` }));
                throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            this.handleDetailedSuccess(result);

        } catch (error) {
            console.error('Error executing task:', error);
            this.showError(`Failed to execute task: ${error.message}`);
        }
    }

    startExecution() {
        this.hideError();

        if (this.executeBtn) {
            this.executeBtn.disabled = true;
            this.executeBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Executing...';
        }

        if (this.resultsSection) {
            this.resultsSection.style.display = 'block';
        }

        // Reset all steps
        this.resetStep(1);
        this.resetStep(2);
        this.resetStep(3);

        // Start step 1
        this.activateStep(1);

        // Clear previous content
        this.updateElement('plannerInstructions', 'Generating instructions...');
        this.updateElement('writerInstructions', 'Generating instructions...');
        this.updateElement('planOutput', 'Waiting for planner agent...');
        this.updateElement('finalOutput', 'Waiting for writer agent...');
    }

    handleDetailedSuccess(result) {
        // Step 1: Show generated instructions
        setTimeout(() => {
            this.updateElement('plannerInstructions', result.plannerInstructions);
            this.updateElement('writerInstructions', result.writerInstructions);
            this.completeStep(1);
            this.activateStep(2);

            // Step 2: Show planning phase
            setTimeout(() => {
                this.updateElement('planOutput',
                    'Planning completed successfully. The planner agent has created a structured outline and passed it to the writer agent for final content creation.');
                this.completeStep(2);
                this.activateStep(3);

                // Step 3: Show final result
                setTimeout(() => {
                    this.updateElement('finalOutput', result.finalResult);
                    this.completeStep(3);

                    // Re-enable button
                    if (this.executeBtn) {
                        this.executeBtn.disabled = false;
                        this.executeBtn.innerHTML = '<i class="fas fa-play"></i> Execute Task';
                    }
                }, 1000);

            }, 1500);

        }, 1000);
    }

    handleSuccess(result) {
        // Fallback for simple text response
        this.completeStep(1);
        this.completeStep(2);
        this.completeStep(3);

        this.updateElement('finalOutput', result);
        this.updateInstructionPlaceholders();

        if (this.executeBtn) {
            this.executeBtn.disabled = false;
            this.executeBtn.innerHTML = '<i class="fas fa-play"></i> Execute Task';
        }
    }

    updateInstructionPlaceholders() {
        if (!this.taskInput) return;

        const task = this.taskInput.value.trim();

        this.updateElement('plannerInstructions',
            `Create a structured outline for: "${task}". Focus on key points, target audience, and main objectives.`);

        this.updateElement('writerInstructions',
            `Write polished, engaging content based on the planner's outline for: "${task}". Ensure the tone matches the intended purpose and audience.`);

        this.updateElement('planOutput',
            'Plan generated successfully by the planner agent and passed to the writer agent.');
    }

    updateElement(id, content) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = content;
        }
    }

    showError(message) {
        if (this.errorSection) {
            this.errorSection.style.display = 'block';
            this.updateElement('errorMessage', message);
        }
        if (this.resultsSection) {
            this.resultsSection.style.display = 'none';
        }

        if (this.executeBtn) {
            this.executeBtn.disabled = false;
            this.executeBtn.innerHTML = '<i class="fas fa-play"></i> Execute Task';
        }
    }

    hideError() {
        if (this.errorSection) {
            this.errorSection.style.display = 'none';
        }
    }

    activateStep(stepNumber) {
        const stepCard = this.getStepCard(stepNumber);
        const spinner = document.getElementById(`step${stepNumber}Spinner`);

        if (stepCard) {
            stepCard.classList.remove('completed', 'error');
            stepCard.classList.add('active');
        }
        if (spinner) {
            spinner.classList.add('active');
        }
    }

    completeStep(stepNumber) {
        const stepCard = this.getStepCard(stepNumber);
        const spinner = document.getElementById(`step${stepNumber}Spinner`);

        if (stepCard) {
            stepCard.classList.remove('active', 'error');
            stepCard.classList.add('completed');
        }
        if (spinner) {
            spinner.classList.remove('active');
        }
    }

    errorStep(stepNumber) {
        const stepCard = this.getStepCard(stepNumber);
        const spinner = document.getElementById(`step${stepNumber}Spinner`);

        if (stepCard) {
            stepCard.classList.remove('active', 'completed');
            stepCard.classList.add('error');
        }
        if (spinner) {
            spinner.classList.remove('active');
        }
    }

    resetStep(stepNumber) {
        const stepCard = this.getStepCard(stepNumber);
        const spinner = document.getElementById(`step${stepNumber}Spinner`);

        if (stepCard) {
            stepCard.classList.remove('active', 'completed', 'error');
        }
        if (spinner) {
            spinner.classList.remove('active');
        }
    }

    getStepCard(stepNumber) {
        if (!this.resultsSection) {
            return null;
        }

        const stepCards = this.resultsSection.querySelectorAll('.step-card');
        return stepCards[stepNumber - 1] || null;
    }
}

// Initialize the UI when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new AgentSpawnerUI();
});

// Add some utility functions for better UX
function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
            console.log('Copied to clipboard');
        }).catch(err => {
            console.error('Failed to copy text: ', err);
        });
    }
}

// Auto-resize textarea
document.addEventListener('DOMContentLoaded', () => {
    const textarea = document.getElementById('taskInput');
    if (textarea) {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = this.scrollHeight + 'px';
        });
    }
});
