 # shlex-based classification -> allow / deny / ask + reason

def ask_approval_simple(tool_call):
    print(f"LLM suggests: {tool_call.name}, {tool_call.args}")
    allow = input(f"Allow? (Y/N): ")
    
    if allow.lower() == "y":
        return True
    else:
        return False