# Project decisions

## 1. Model selection

**Decision:**
`Qwen3.8-27B` was the model of choice for the project.

**Alternatives considered:**

- Qwen3-Coder-30B
- Qwen3.6-35B-A3B
- Claude Opus (commercial)

**Why we chose this:**

The model was chosen due to its strong agentic, reasoning and tool-use capabilities. Although a bit tight fit, the Q4-IQ4-XS-GGUF quantized version fits into 18GB VRAM with a context length of 55-72k. With the used setup, the model ran at around 25-27tok/s, which is fairly decent.

---

## 2. The agentic loop

**Decision:**
The application uses a state machine agentic loop for completing the tasks.

**Why it is needed:**
The tasks, such as CTF challenges are often open-ended, and cannot be fulfilled with a single request or a static workflow. An agent with updating context is able to complete a wide variety of different tasks, as well as to adapt its strategy based on discovered information.

---

## 3. Tool usage

**Decision:**
The agent is able to interact with the sandbox environment with a set of tools created with Python.

**Why it is needed:**
The model being able to interact with the environment is essential in order for it to reach its goal. Models such as the chosen `Qwen3.8-27B` are trained with tool usage in mind. This enables a powerful and reliable way of adding new functionality for the model. Libraries such as Pydantic make validating the model's tool calls straightforward.

**Alternatives considered**
Another option would be to extract commands and arguments straight from the text content of model responses. However, this approach is significantly more unreliable, as malformed and/or faulty output is much more likely to occur.

---

## 4. LLama.cpp client

**Decision:**
LLama.cpp was chosen as the model hosting server.

**Why:**
LLama.cpp gives the user more direct control over the server without abstraction layers. It enables the usage of OpenAI-compatible endpoint. It is also more minimalistic, offering better performance.

---

## 5. The Docker sandbox environment

**Decision:**
The model completes its tasks in a contanerized sandbox environment.

**Why:**
The environment allows easy seeding of containers with preconfigured scenarios without affecting the host machine. The containers are lightweight, and can be started, stopped and reseted in seconds. While not entirely bulletproof, the sandbox also acts a security measure against potentially dangerous or destructive commands.

---

## 6. Tiered tool permissions/human approval

**Decision:**
The model is able to execute `list_dir`, `read_file` and `finish` autonomously, but custom commands called with `run_command` always need human approval.

**Why:**
It is harmless for the model to enumerate libraries or read files inside the container, but custom commands might be potentially dangerous. While the sandbox acts as a primary security layer, the user validating each custom command acts as a secondary layer. In the future, a policy layer could be implemented, which would allow for automatic denying/allowing of commands based on heuristics.
