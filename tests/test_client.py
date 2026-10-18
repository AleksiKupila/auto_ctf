import json
from pathlib import Path

import pytest

from src.llm.openai_compat import ModelClient          
from src.tools.registry import tool_schemas

CASES = json.loads((Path(__file__).parent / "llm_cases.json").read_text())


@pytest.fixture(scope="module")
def client_with_tools():
    return ModelClient(tools=tool_schemas())


@pytest.fixture(scope="module")
def client_no_tools():
    return ModelClient(tools=None)


@pytest.mark.parametrize("case", CASES, ids=[c["id"] for c in CASES])
def test_llm_case(case, client_with_tools, client_no_tools):
    client = client_with_tools if case["tools"] else client_no_tools
    exp = case["expect"]

    if exp.get("error"):
        with pytest.raises(ConnectionError):
            client.generate(case["messages"])
        return

    response = client.generate(case["messages"])
    assert response.choices, "response has no choices"
    msg = response.choices[0].message
    content = msg.content or ""
    calls = msg.tool_calls or []

    if exp.get("no_tool_calls"):
        assert not calls, f"unexpected tool calls: {calls}"

    if "content_contains_any" in exp:
        assert any(s.lower() in content.lower() for s in exp["content_contains_any"]), content

    if "tool_call" in exp:
        spec = exp["tool_call"]
        assert calls, f"expected a tool call, got content: {content!r}"
        call = calls[0]
        assert call.function.name in spec["names"], call.function.name
        args = json.loads(call.function.arguments)   # must be valid JSON
        assert any(all(k in args for k in keys) for keys in spec["args_required_any"]), args

    if "content_or_args_contains" in exp:
        haystack = content + " ".join(c.function.arguments for c in calls)
        assert exp["content_or_args_contains"] in haystack, haystack


def test_unreachable_server_raises():
    client = ModelClient(base_url="http://127.0.0.1:1/v1", tools=None)
    with pytest.raises(ConnectionError):
        client.generate([{"role": "user", "content": "hi"}])
