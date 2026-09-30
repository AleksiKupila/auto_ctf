# Project name

Starter template for the **Development of AI Applications** course final group project.

## Team members

- Member 1 Name: Aleksi Kupila 

## Problem

### Intended users
Students, people interested in learning cybersecurity and the usage of local LLM:s in cyber.

### Problem statement
With LLM:s reshaping the field of cybersecurity, automating tasks such as analyzing tool output or performing routine scans is becoming increasingly more relevant. However, as directly running LLM-suggested commands on your own machine is unsafe, a proper sandbox environment, as well as security controls are needed for learning and testing environments. This project offers a basic structure to test LLM:s in a sandbox environment in various cybersecurity related tasks, such as CTF:s.

### Why AI is appropriate
The tasks are often open-ended, and the next command depends on the output of the previous one. Therefore, a simple script or a lookup table would not be able to cover all possible outcomes. The system has to be able to respond in unexpected conditions and outcomes, and to be able to adapt its strategy.

## Solution

1. **User Input:** The user explains a goal such as "find the flag" via the Gradio/Flask user interface.
2. **Query processing:** The application service layer validates and formats the request.
3. **Model Response:** The model client calls Ollama/llama.cpp locally. The model returns a command suggestion, and possibly a short analysis on the situation.
4. **Policy layer/guardrails:** The suggested command gets checked by heuristic checks. The policy layer then allows it, blocks it or asks for user approval. Unsafe or destructive commands will not be allowed.
5. **Command execution:** The command is executed in a docker container, isolated in a sandbox environment. The command output is captured by the system.
6. **Output analysis:** The command output is analyzed by the LLM, and next step is decided based on it.
7. **Final analysis:** When the agent declares it has reached the goal or the step budget runs out, the task is marked as completed. The model then outputs a final analysis, that gets displayed to the user.

## Architecture

Below is the initial starter architecture. As your project evolves with additional capabilities, replace or extend this diagram in [`docs/architecture.md`](docs/architecture.md).

```text
User
  ↓
Gradio/Flask UI (app/ui.py) - Shows the transcript, commands, output, reasoning and analysis
  ↓
Application / AI Service (src/services/ai_service.py) - The core agentic loop
  ↓
Model Client (src/models/model_client.py) - Queries an LLM API, such as llama.cpp
  ↓
Ollama/llama.cpp (Local LLM Server) - Serves the local model
  ↓
Sandbox executor container - A container running in an isolated environment
```

> **Core Architectural Rule:** The user interface must NEVER communicate directly with the model client or Ollama. All interactions must pass through the service layer (`ai_service.py`).

## Model

- **Model(s) used:** Qwen3.6-35B-A3B/Qwen3.8-27B
- **Selection rationale:** Strong agentic and reasoning capabilities for a fairly small open source model, decent performance and context on a wide variety of consumer hardware.

## Additional AI capability

Select at least one additional capability to implement for your final project:

- [ ] RAG (Retrieval-Augmented Generation)
- [*] Tools / External API integration
- [ ] Model Context Protocol (MCP)
- [*] Agentic workflow (Model-selected actions based on observations)
- [*] Memory / Persistent state
- [ ] Multimodal interaction (Text + Images)
- [ ] Other: ______________________

### Capability justification
The main capability is agentic behavior via tool calling. The agent executes a command based on the goal, analyzes the output, and plans its next move based on it. Memory is needed in order to consider the previous outputs and actions when planning. Implementing a persistent sessions could be implemented, which could allow the user to resume sessions later.

## Setup
### TO BE CHANGED

### 1. Create the Conda environment

```bash
conda env create -f environment.yml
```

### 2. Activate the environment

```bash
conda activate dev-ai-project
```

### 3. Configure environment variables

Copy `.env.example` to create your local `.env` configuration file:

On Linux / macOS:
```bash
cp .env.example .env
```

On Windows (Command Prompt / PowerShell):
```powershell
copy .env.example .env
```

Ensure `.env` contains valid values for `OLLAMA_BASE_URL` and `MODEL_NAME`:
```env
OLLAMA_BASE_URL=http://localhost:11434
MODEL_NAME=llama3.2
```

### 4. Start Ollama

Make sure Ollama is installed and running locally, then pull your configured model:

```bash
ollama run llama3.2
```

### 5. Run the application

Run the application from the root directory of the project:

```bash
python -m app.main
```

Then open your browser at `http://localhost:7860`.

### 6. Run automated tests

```bash
pytest
```

## Evaluation

Describe your evaluation methodology and summarize key results. Starter test cases can be found in [`evaluation/test_cases.json`](evaluation/test_cases.json).

Refer to [`evaluation/README.md`](evaluation/README.md) for guidelines on defining success, edge cases, and failure scenarios.

## Known limitations

- Highlight known system limitations, unhandled edge cases, or boundaries of current capabilities.

## Future improvements

- List planned feature enhancements, architectural refactorings, or future capabilities.
