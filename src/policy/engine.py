 # shlex-based classification -> allow / deny / ask + reason

def ask_approval_simple(suggestion):
    print(f"LLM suggests: {suggestion}")
    allow = input(f"Allow? (Y/N): ")
    
    if allow == "Y":
        return True
    else:
        return False