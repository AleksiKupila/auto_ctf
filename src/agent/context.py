# message building, output truncation, history trimming


class ContextManager:

    def __init__(self, system_message, goal, max_tokens, count_tokens, max_tool_chars=4000):

       self.head = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": goal}
       ]
       self.turns = []
       self.max_tool_chars = max_tool_chars
       self.count_tokens = count_tokens
       self.dropped = 0

    def add_assistant(self, msg: dict):
        self.turns.append([dict(msg)])

    def add_tool_result(self, msg: dict):
        '''
        Add tool result, truncate if length exceeds max_tool_chars
        '''
        c = msg["content"]

        if len(c) > self.max_tool_chars:
            half = self.max_tool_chars // 2
            c = f"{c[:half]}\n...[{len(c) - self.max_tool_chars} chars truncated]...\n{c[-half:]}"

        self.turns[-1].append({**msg, "content": c})

    def _size(self, messages):

        total = 0
        for m in messages:
            total += self.count_tokens(str(m.get("content", ""))) + 4

        return total

    def fetch_context(self):
        body = lambda: [m for t in self.turns for m in t]
        while len(self.turns) > 1 and self._size(self.head + body()) > self.max_tokens:
            self.turns.pop(0)
            self.dropped += 1

        head = list(self.head)

        return head + body()