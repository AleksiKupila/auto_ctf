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
    raw = case.get("raw_arguments", json.dumps(case.get("arguments", {})))
    out = execute(case["tool"], raw, config.executor_container)
    exp = case["expect"]

    assert out.status == exp["status"], f"stdout={out.stdout!r} stderr={out.stderr!r}"
    if "stdout_contains" in exp:
        assert exp["stdout_contains"] in out.stdout
    if "stdout_not_contains" in exp:
        assert exp["stdout_not_contains"] not in out.stdout
    if "stderr_contains" in exp:
        assert exp["stderr_contains"] in out.stderr
    if "stdout_max_len" in exp:
        assert len(out.stdout) <= exp["stdout_max_len"]