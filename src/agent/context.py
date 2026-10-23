from src.tools.handlers import ToolOutput
from src.agent.prompts import build_finish_message
from src.agent.heuristics import count_tokens
import json

# message building, output truncation, history trimming


class ContextManager:

    def __init__(self, system_message, goal, max_tokens, max_tool_chars=4000):

       self.head = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": goal}
       ]
       self.system_message = system_message
       self.finish_reason = None
       self.finish_status = None
       self.turns = []
       self.max_tokens = max_tokens
       self.max_tool_chars = max_tool_chars
       self.dropped = 0

    def add_assistant(self, msg):
        self.turns.append([msg])

    def add_user_message(self, content):
        self.turns.append([{
            "role": "user",
            "content": content,
        }])

    def add_tool_result(self, tool_message: ToolOutput):
        '''
        Add tool result in a format that the server accepts
        '''
        content = (
            f"status: {'success' if tool_message.status else 'failed'}\n"
            f"stdout \n{self._truncate(tool_message.stdout) or '(empty)'}\n"
            f"stderr \n{self._truncate(tool_message.stderr) or '(empty)'}\n"
        )
        self.turns[-1].append({
            "role": "tool",
            "tool_call_id": tool_message.id,
            "content": content,
        })

    def _truncate(self, text):
         
        if len(text) > self.max_tool_chars:
            half = self.max_tool_chars // 2
            text = f"{text[:half]}\n...[{len(text) - self.max_tool_chars} chars truncated]...\n{text[-half:]}"

        return text

    def _size(self, messages):

        total = 0
        for m in messages:
            text = str(m.get("content") or "")
            if m.get("tool_calls"):
                text += json.dumps(m["tool_calls"])
            total += count_tokens(str(text)) + 4

        return total

    def set_head(self, content):
        self.head = [
            {"role": "system", "content": self.system_message},
            {"role": "user", "content": content}
       ]

    def fetch_context(self):
        body = lambda: [m for t in self.turns for m in t]
        while len(self.turns) > 1 and self._size(self.head + body()) > self.max_tokens:
            self.turns.pop(0)
            self.dropped += 1

        return list(self.head) + body()

    def final_analysis_context(self):
        goal = self.head[1].get("content")
        body = lambda: [m for t in self.turns for m in t]
        reason, status = self.finish_reason, self.finish_status

        final_message = build_finish_message(goal, reason, status, body())


        return [{
            "role": "user",
            "content": final_message,
        }]