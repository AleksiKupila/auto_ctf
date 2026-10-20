from src.tools.registry import execute
from src.config import config
import pytest, json
from pathlib import Path

CASES = json.loads((Path(__file__).parent / "toolcall_cases.json").read_text())

def _params():
    for case in CASES:
        marks = [pytest.mark.slow] if case.get("slow") else []
        yield pytest.param(case, id=case["id"], marks=marks)


@pytest.mark.parametrize("case", _params())
def test_tool_case(case):
    fn = case["function"]
    raw = fn.get("raw_arguments", json.dumps(fn.get("arguments", {})))
    tc = {
        "id": case["id"],
        "type": "function",
        "function": {"name": fn["name"], "arguments": raw},
    }
    out = execute(tc, config.executor_container)
    exp = fn["expect"]

    assert out.status == exp["status"], f"stdout={out.stdout!r} stderr={out.stderr!r}"
    if "stdout_contains" in exp:
        assert exp["stdout_contains"] in out.stdout