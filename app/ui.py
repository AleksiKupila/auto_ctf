import gradio as gr
from src.services.ai_service import AgentSession

AGENTS = {}
def render(event, history):

    if event.kind == "assistant" and event.data["data"]:
        history.append({"role": "assistant", "content": event.data["data"]})

    elif event.kind == "tool" and event.data["output"] and event.data["call"]:
        output, call = event.data["output"], event.data["call"]
        stdout = output.stdout or ""
        args = call.args.get("cmd")

        history.append({"role": "assistant",
                        "content": stdout,
                        "metadata": {"title": f"{'✅' if output.status else '❌'} {call.name}: {call.args.get("cmd") or call.args.get("path")}"}
                        })
    elif event.kind == "finish" and event.data["data"]:
        history.append({"role": "assistant", "content": f'**Final analysis**\n\n{event.data["data"]}'})

    return history

def drive(agent, history):
    while not agent.done:

        req = agent.advance()
        for ev in agent.drain_events():
            history = render(ev, history)
    
        if req: # Update with approval request
            yield history, gr.update(visible=True), req.tool_call.args.get("cmd", "")
            return

        yield history, gr.update(visible=False), gr.update()

def start(goal, request: gr.Request):

    try: 
        session = AgentSession()
    except Exception as e:
        print(f"Failed to start new session, aborting... {e}")
        return

    agent = session.new_agent(goal)
    if agent:
        AGENTS[request.session_hash] = agent
        yield from drive(agent, [{"role": "user", "content": goal}])

def approve(history, request: gr.Request):
    agent = AGENTS[request.session_hash]
    agent.current_request.decision = True
    yield from drive(agent, history)

def deny(history, request: gr.Request):
    agent = AGENTS[request.session_hash]
    agent.current_request.decision = False
    yield from drive(agent, history)

def build_ui():
    with gr.Blocks() as demo:
        chat = gr.Chatbot(height=650)

        with gr.Group(visible=False) as approval:
            cmd = gr.Code(label="Command awaiting approval", language="shell")

            with gr.Row():
                yes = gr.Button("Approve", variant="primary")
                no = gr.Button("Deny", variant="stop")
        goal = gr.Textbox(label="Goal", placeholder="Find the flag in /home/target…")

        outs = [chat, approval, cmd]
        goal.submit(start, goal, outs)
        yes.click(approve, chat, outs)
        no.click(deny, chat, outs)

    return demo
