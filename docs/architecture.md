# Architecture Documentation

## 1. Overview

The system drives a local LLM in an agentic loop, and conducts its tasks in a sandbox environment against a target container. The model is given a tasks, as well as a set of tools (`run_command`, `list_dir`, `read_file` and `finish`). The model uses its reasoning capabilities to reach its goal, and produces a final report in the end. Every state-altering command needs explicit human approval before being executed.

### Core Design Rules

1. **Separation of concerns:** The Gradio user interface (`app/ui.py`) is totally independent from `ModelClient` and other backend logic. It delegates all operations to the `Agent` class in `src/agent/loop.py`. The agent in turn calls the client `ModelClient` in `src/llm/openai_compat.py` with a function `generate`.
2. **Safety by design:** The agent performs its tasks using a preconfigured set of tools in a disposable, airgapped container. While the sandbox works as the real security boundary, no state-changing commands are executed without explicit human approval.
3. **Controlled Failure Handling:** The model client handles low-level runtime exceptions (e.g., connection errors or missing models). The service layer converts technical exceptions into structured, user-understandable responses.
4. **Each I/O is validated:** User inputs are validated using Pydantic model in `src/schemas/responses.py`. Models for LLM tool call validation are located in `src/schemas/tools.py`. Malformed input is rejected, and errors are returned back to the model so it can self-correct.
5. **Local-first:** The entire system runs on a single machine with no external dependencies.

---

## 2. Architecture

The system consists of four main parts:

1. **The model backend:** OpenAI-completions compatible endpoint.
2. **The agent core:** A state machine, tool dispatch and context management, which form the agentic loop.
3. **The sandbox environment:** A disposable, airgapped docker network with 2 containers: an executor and a target.
4. **The user interface:** A lightweight GUI, rendering agent state and owning the approval process.

### Stack diagram

```text
User
  ↓
Gradio UI (app/ui.py)
  ↓
Agent (src/agent/loop.py)
  ↓
Model Client (src/models/openai_compat.py)
  ↓
LLama.cpp (Local Inference Server)
  ↓
Local Model (Qwen3.8-27B-GGUF)
```

### Block diagram

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

---

## 3. Extension points/capabilities

- **Tools:** The harness has currently 4 tools implemented: `run_command`, `list_dir`, `read_file` and `finish`.
- **Agent Workflow:** The application uses a state machine agentic loop structure for solving the tasks in a contanerized sandbox environment.
- **Memory & Conversation State:** The agent stores and updates the context by using a separate context manager.

---

## 4. Known limitations

- **No "second" exit:** The agent is configured for finding a flag no matter what. As noted in the evaluation scenarios, the agent will keep trying indefinitely if no flag can be found.
- **No policy engine:** Currently, user approval is the only mechanic for approving and denying commands.
- **No persistent sessions:** Each session is self contained. The state needed to implement persistence exists, but is not implemented yet.
- **Context truncation can drop early clues:** For longer multi-step chains, truncation and dropping of old messages remains a challenge.
