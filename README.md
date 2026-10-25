# Auto-CTF

An agent harness for solving CTF challenges, built from scratch.

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

1. **User Input:** The user explains a goal such as "find the flag" via the Gradio user interface.
2. **Query processing:** The application service layer validates and formats the request.
3. **Model Response:** The model client calls local llama.cpp or an external server. The model analyzes the context, and proposes a tool call.
4. **User approval:** If the command is state-altering, running it needs user validation. The agent is able to enumerate directories and read files in the container without human approval.
5. **Command execution:** The command is executed in a docker container, isolated in a sandbox environment. The command output is captured by the system.
6. **Output analysis:** The command output is analyzed by the LLM, and next step is decided based on it.
7. **Final analysis:** When the agent declares it has reached the goal or the step budget runs out, the task is marked as finished. The model then outputs a final analysis, that gets displayed to the user.

## Architecture

Below is a block diagram of the system:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                       UI  (Gradio / CLI fallback)                      │
│      renders agent status · owns the human approve/deny decision       │
└───────────────┬──────────────────────────────────────▲─────────────────┘
                │ advance() / decision                 │ status, LLM response
                ▼                                      │
┌──────────────────────────────────────────────────────┴─────────────────┐
│                               AGENT CORE                               │
│                                                                        │
│  ┌──────────────────┐   ┌──────────────────┐   ┌────────────────────┐  │
│  │  State machine   │   │  Tool dispatch   │   │  Context manager   │  │
│  │                  │──►│                  │   │                    │  │
│  │  RUNNING         │   │  list_dir        │   │  message history   │  │
│  │  WAITING_APPROVAL│◄──│  read_file       │   │  + truncation      │  │
│  │  DONE            │   │  run_command     │   │                    │  │
│  └────────┬─────────┘   └────────┬─────────┘   └────────────────────┘  │
│           │                      │                                     │
│           │    pydantic in/out validation on every tool call           │
└───────────┼──────────────────────┼─────────────────────────────────────┘
            │                      │
            ▼                      ▼
┌──────────────────────┐ ┌───────────────────────────────────────────────┐
│    MODEL BACKEND     │ │              SANDBOX ENVIRONMENT              │
│                      │ │                                               │
│  llama.cpp server    │ │  ┌────────────┐       ┌────────────────────┐  │
│  qwen3.8-27b         │ │  │  Executor  │──────►│  Target container  │  │
│  OpenAI-compatible   │ │  │  container │       │  (disposable,      │  │
│  /v1/chat/           │ │  └────────────┘       │   seeded flags)    │  │
│    completions       │ │                       └────────────────────┘  │
│                      │ │          isolated Docker network              │
└──────────────────────┘ └───────────────────────────────────────────────┘
```

> **Core Architectural Rule:** The Gradio user interface (`app/ui.py`) is totally independent from `ModelClient` and other backend logic. It delegates all operations to the `Agent` class in `src/agent/loop.py`. The agent in turn calls the client `ModelClient` in `src/llm/openai_compat.py` with a function `generate`.

## Model

- **Model used:** Qwen3.8-27B
- **Selection rationale:** Strong agentic and reasoning capabilities for a fairly small open source model, decent performance and context on a wide variety of consumer hardware.

## Additional AI capability

- [ ] RAG (Retrieval-Augmented Generation)
- [x] Tools / External API integration
- [ ] Model Context Protocol (MCP)
- [x] Agentic workflow (Model-selected actions based on observations)
- [x] Memory / Persistent state
- [ ] Multimodal interaction (Text + Images)
- [ ] Other: ______________________

### Capability justification

The main capability is agentic behavior via tool calling. The agent executes a command based on the goal, analyzes the output, and plans its next move based on it. Memory is needed in order to consider the previous outputs and actions when planning. Implementing a persistent sessions could be implemented, which could allow the user to resume sessions later.

## Setup

### 1. Create and activate the virtual environment

Note: Python version `3.14.8` was used for this project.

```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
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

Ensure `.env` contains valid values for `OPENAI_BASE_URL` and `MODEL_NAME`. Ensure the URL matches the URL of your llama.cpp server:

```env
OPENAI_BASE_URL=http://localhost:8080
MODEL_NAME=Qwen3.8-27B
```

### 4. Download the model and start llama.cpp

Make sure `llama.cpp` is installed, then download the model of your choice into the `models` directory. You can do this with either with either with `hf-cli` or manually:

```bash
hf download unsloth/<HF_REPO> <FILE>.gguf --local-dir models
```

As an example, the Qwen3.8-27B quant I used:

```bash
hf download hf://unsloth/Qwen3.8-27B-GGUF/Qwen3.8-27B-UD-IQ4_XS.gguf --local-dir models
```

Start the server. Note that the configured flags and which model you can run depend on your system! For example, the configuration I used:

```bash
llama-server \                                                                                
    -c 55000 \
    -m models/Qwen3.8-27B-UD-IQ4_XS.gguf \  
    --cache-type-k q8_0 \
    --cache-type-v q4_0 \
    -ngl 99 \
    -ts 10,8 \
    -np 1 \
    --no-mmproj \
    --flash-attn on \
    -ub 128 \
    -b 512 \
    --temp 1 \
    --top-p 0.95 \
    --min-p 0.0 \
    --top-k 20 \
    --presence_penalty 0.0 \
    --no-reasoning-preserve \
    --port 8080 \
    --jinja
```

Then, verify the server is running:

```bash
curl http://127.0.0.1:8080/v1/models
```

### 5. The Docker environment

Make sure Docker and Docker compose are installed and running. You can check this with:

```bash
docker ps
```

**Linux:** Ensure your user is in the `docker` group, so Docker can execute commands in the containers without sudo:

```bash
sudo usermod -aG docker $USER
```

Then, start a simple scenario. This pulls the required image from Docker, starts it, and runs the `01-easy-flag` script to seed it:

```bash
make executor S=01-easy-flag
```

You can test that the container is working by listing it and opening a shell session:

```bash
docker ps
docker exec -it command_executor bash
```

If you wish to try another scenario, just recreate it with:

```bash
make executor S=03-base64
```

Shutting down:

```bash
make down
```

### 6. Run the application

Run the application from the root directory of the project (`-u` flag activates the UI):

```bash
python run.py -u
```

Then open your browser at `http://localhost:7860`.

## Evaluation summary

The system was evaluated with 8 scenarios in total, which were all focused on the post-exploitation phase on an attack (local enumeration, privilege escalation, CTF hunting and so on). The scenarios contained 3 easy challenges, 3 difficult challenges and 2 impossible challenges with no solution. The model solved all of the easy and difficult challenges with no problems, but failed on the impossible challenges due to not being able to give up without a flag. Overall, the model demonstrated strong reasoning capabilities, and was able to follow even the more complex clue chains without falling for traps, such as prompt injection or false flags. The evaluation cases can be found in [`evaluation/test_cases.json`](evaluation/test_cases.json).

## Known limitations

- **No "second" exit:** The agent is configured for finding a flag no matter what. As noted in the evaluation scenarios, the agent will keep trying indefinitely if no flag can be found.
- **No policy engine:** Currently, user approval is the only mechanic for approving and denying commands.
- **No persistent sessions:** Each session is self contained. The state needed to implement persistence exists, but is not implemented yet.
- **Context truncation can drop early clues:** For longer multi-step chains, truncation and dropping of old messages remains a challenge.

## Future improvements

- **A second exit:** Create a real exit other than finding the flag. Modifying the system prompt was attempted, but a separate tool might be needed, such as `return_without_flag(reason)`.
- **Decrease repetition:** Implement "nudges" for the model when repeating commands are identified.
- **A policy engine:** Implement a policy engine what would allow for automatic denying/approving of commands based on heuristics.
- **Persistent sessions:** Implement storing the sessions in a database, which could allow users to resume/return to sessions later.

## Technical video presentation

[Youtube](https://youtu.be/VqxNmZgBQE0)
