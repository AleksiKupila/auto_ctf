import requests
from src.config import config
# step/token budgets, repetition detection, nudges

def count_tokens(text, url=config.openai_base_url):
    r = requests.post(f"{url}/tokenize", json={"content": text, "add_special": False})
    return len(r.json()["tokens"])