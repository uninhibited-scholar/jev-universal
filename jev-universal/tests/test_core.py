import json

import httpx
import pytest
from jev_universal import server
from jev_universal.core import Question, evaluate
from pydantic import ValidationError

Q = {"x": Question(type="noul", instructions="Is there evidence?")}


async def test_request_and_uncertainty(monkeypatch):
    monkeypatch.setenv("TYPESAFE_API_KEY", "test-secret")

    def handler(r):
        assert r.url == "https://api.typesafe.ai/v1/systemone"
        assert r.headers["authorization"] == "Bearer test-secret"
        assert json.loads(r.content)["questions"]["x"]["type"] == "noul"
        return httpx.Response(200, json={"answers": {"x": {"type": "noul", "noul": 0.51}}})

    result = await evaluate("evidence", Q, transport=httpx.MockTransport(handler))
    assert result["review_required"] == ["x"]


@pytest.mark.parametrize(
    "answer", [{}, {"x": {"type": "noul", "noul": 2}}, {"x": {"type": "choice"}}]
)
async def test_reject_bad_response(monkeypatch, answer):
    monkeypatch.setenv("TYPESAFE_API_KEY", "test")
    with pytest.raises(ValueError):
        await evaluate(
            "x",
            Q,
            transport=httpx.MockTransport(lambda r: httpx.Response(200, json={"answers": answer})),
        )


async def test_no_key(monkeypatch):
    monkeypatch.delenv("TYPESAFE_API_KEY", raising=False)
    with pytest.raises(ValueError, match="TYPESAFE_API_KEY"):
        await evaluate("x", Q)


async def test_error_does_not_echo_secret(monkeypatch):
    monkeypatch.setenv("TYPESAFE_API_KEY", "secret")
    with pytest.raises(ValueError, match="HTTP 401") as err:
        await evaluate(
            "x", Q, transport=httpx.MockTransport(lambda r: httpx.Response(401, text="secret"))
        )
    assert "secret" not in str(err.value)


@pytest.mark.parametrize(
    "kind,criteria", [("score", ["only"]), ("choice", ["a", "b"]), ("noul", {})]
)
def test_bad_questions(kind, criteria):
    with pytest.raises(ValidationError):
        Question(type=kind, instructions="q", criteria=criteria)


async def test_context_keeps_pinned_and_uncertain(monkeypatch):
    async def fake(*args):
        return {
            "answers": {
                "1": {"choice": "omit", "confidence": 0.6},
                "2": {"choice": "omit", "confidence": 0.99},
            }
        }

    monkeypatch.setattr(server, "evaluate", fake)
    result = await server.jev_select_context(
        "goal",
        [
            server.Chunk(id="a", text="instruction", pinned=True),
            server.Chunk(id="b", text="uncertain", pinned=False),
            server.Chunk(id="c", text="noise", pinned=False),
        ],
    )
    assert [c["id"] for c in result["kept"]] == ["a", "b"]
    assert result["omitted_ids"] == ["c"]


async def test_mcp_schema():
    tools = await server.mcp.list_tools()
    assert {t.name for t in tools} == {
        "jev_evaluate",
        "jev_route",
        "jev_check",
        "jev_select_context",
    }
    assert all(t.annotations.openWorldHint for t in tools)


@pytest.mark.parametrize(
    "kind,criteria,answer",
    [
        (
            "choice",
            {"a": "A", "b": "B"},
            {
                "type": "choice",
                "choice": "a",
                "probabilities": {"a": 0.9, "b": 0.1},
                "confidence": 0.8,
            },
        ),
        (
            "score",
            ["low", "high"],
            {
                "type": "score",
                "score": 0.75,
                "probabilities": {"0": 0.25, "1": 0.75},
                "confidence": 0.6,
            },
        ),
    ],
)
async def test_other_primitives(monkeypatch, kind, criteria, answer):
    monkeypatch.setenv("TYPESAFE_API_KEY", "test")
    result = await evaluate(
        "evidence",
        {"q": Question(type=kind, instructions="q", criteria=criteria)},
        transport=httpx.MockTransport(
            lambda r: httpx.Response(
                200, json={"answers": {"q": answer}, "secret": "do not forward"}
            )
        ),
    )
    assert result["answers"]["q"]["type"] == kind
    assert "secret" not in result


async def test_request_budget(monkeypatch):
    monkeypatch.setenv("TYPESAFE_API_KEY", "test")
    with pytest.raises(ValueError, match="budget"):
        await evaluate("大" * 100000, Q)


async def test_response_budget(monkeypatch):
    monkeypatch.setenv("TYPESAFE_API_KEY", "test")
    with pytest.raises(ValueError, match="size limit"):
        await evaluate(
            "x",
            Q,
            transport=httpx.MockTransport(lambda r: httpx.Response(200, content=b"x" * 1000001)),
        )


async def test_redirect_not_followed(monkeypatch):
    monkeypatch.setenv("TYPESAFE_API_KEY", "test")
    with pytest.raises(ValueError, match="HTTP 302"):
        await evaluate(
            "x",
            Q,
            transport=httpx.MockTransport(
                lambda r: httpx.Response(302, headers={"location": "https://evil.example"})
            ),
        )


async def test_network_failure(monkeypatch):
    monkeypatch.setenv("TYPESAFE_API_KEY", "test")

    def fail(r):
        raise httpx.ReadTimeout("must-not-echo-request")

    with pytest.raises(ValueError, match="network failure") as err:
        await evaluate("x", Q, transport=httpx.MockTransport(fail))
    assert "must-not-echo" not in str(err.value)


async def test_duplicate_chunk_ids():
    with pytest.raises(ValueError, match="unique"):
        await server.jev_select_context(
            "g",
            [
                server.Chunk(id="a", text="a", pinned=False),
                server.Chunk(id="a", text="b", pinned=False),
            ],
        )
