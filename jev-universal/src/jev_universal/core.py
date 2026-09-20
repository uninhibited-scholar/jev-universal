"""Bounded TypeSafe HTTP client. Never logs evidence or upstream error bodies."""

import json
import math
import os
from pathlib import Path
from typing import Annotated, Literal

import httpx
from pydantic import BaseModel, ConfigDict, Field, model_validator

MAX_REQUEST_BYTES = 200_000
MAX_RESPONSE_BYTES = 1_000_000
ENDPOINT = "https://api.typesafe.ai/v1/systemone"
NonEmpty = Annotated[str, Field(min_length=1, max_length=8000)]


class Question(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    type: Literal["choice", "score", "noul"]
    instructions: NonEmpty
    criteria: dict[NonEmpty, NonEmpty] | list[NonEmpty] | None = None

    @model_validator(mode="after")
    def check_criteria(self):
        if not self.instructions.strip():
            raise ValueError("instructions must not be blank")
        if self.type == "choice" and not (
            isinstance(self.criteria, dict) and 2 <= len(self.criteria) <= 255
        ):
            raise ValueError("choice requires 2–255 options")
        if self.type == "score" and not (
            isinstance(self.criteria, list) and 2 <= len(self.criteria) <= 10
        ):
            raise ValueError("score requires 2–10 ordered levels")
        if self.type == "noul" and self.criteria is not None:
            raise ValueError("this adapter uses noul without criteria")
        return self


Questions = Annotated[dict[NonEmpty, Question], Field(min_length=1, max_length=64)]


def api_key():
    """Read only an explicitly configured secret; never search user files."""
    key = os.getenv("TYPESAFE_API_KEY", "").strip()
    if not key and os.getenv("TYPESAFE_API_KEY_FILE"):
        try:
            key = Path(os.environ["TYPESAFE_API_KEY_FILE"]).read_text().strip()
        except OSError:
            raise ValueError("Cannot read TYPESAFE_API_KEY_FILE") from None
    if not key or any(c.isspace() for c in key) or len(key) > 8192:
        raise ValueError("Set a valid TYPESAFE_API_KEY or TYPESAFE_API_KEY_FILE")
    return key


def number(value, low=0, high=1):
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(value)
        or not low <= value <= high
    ):
        raise ValueError("Invalid upstream numeric result")
    return value


def validate_answers(data, questions):
    """Return an allowlisted result; never forward arbitrary upstream fields."""
    if not isinstance(data, dict) or not isinstance(data.get("answers"), dict):
        raise ValueError("Malformed TypeSafe response")
    if set(data["answers"]) != set(questions):
        raise ValueError("Upstream answer IDs do not match request")
    answers = {}
    for key, q in questions.items():
        a = data["answers"][key]
        if not isinstance(a, dict) or a.get("type") != q.type:
            raise ValueError("Upstream answer type mismatch")
        if q.type == "noul":
            answers[key] = {"type": "noul", "noul": number(a.get("noul"))}
            continue
        confidence = number(a.get("confidence"))
        expected = (
            set(q.criteria) if q.type == "choice" else {str(i) for i in range(len(q.criteria))}
        )
        p = a.get("probabilities")
        if not isinstance(p, dict) or set(p) != expected:
            raise ValueError("Upstream probability keys mismatch")
        if abs(sum(number(v) for v in p.values()) - 1) > 0.02:
            raise ValueError("Invalid upstream probability distribution")
        answer = {"type": q.type, "confidence": confidence, "probabilities": p}
        if q.type == "choice":
            choice = a.get("choice")
            if not isinstance(choice, str) or choice not in expected:
                raise ValueError("Unknown upstream choice")
            if p[choice] + 0.001 < max(p.values()):
                raise ValueError("Choice contradicts upstream probabilities")
            answer["choice"] = choice
        else:
            answer["score"] = number(a.get("score"), 0, len(q.criteria) - 1)
            answer["legend"] = {str(i): level for i, level in enumerate(q.criteria)}
        answers[key] = answer
    result = {"answers": answers}
    model = data.get("model")
    if isinstance(model, str) and len(model) <= 128:
        result["model"] = model
    usage = data.get("usage")
    if isinstance(usage, dict):
        result["usage"] = {
            k: v
            for k, v in usage.items()
            if k in {"input_tokens", "output_tokens"} and type(v) is int and v >= 0
        }
    return result


async def evaluate(state, questions, threshold=0.7, transport=None):
    questions = {k: Question.model_validate(v) for k, v in questions.items()}
    if not 1 <= len(questions) <= 64:
        raise ValueError("Supply 1–64 questions")
    number(threshold)
    payload = {
        "model": os.getenv("JEV_MODEL", "jev-latest"),
        "state": state,
        "questions": {k: v.model_dump(exclude_none=True) for k, v in questions.items()},
    }
    body = json.dumps(payload, ensure_ascii=False, allow_nan=False).encode()
    if len(body) > MAX_REQUEST_BYTES:
        raise ValueError("Request exceeds local 200 KB budget; select smaller evidence")
    key = api_key()
    try:
        async with (
            httpx.AsyncClient(
                timeout=httpx.Timeout(30, connect=10),
                transport=transport,
                follow_redirects=False,
            ) as client,
            client.stream(
                "POST",
                ENDPOINT,
                content=body,
                headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            ) as response,
        ):
            if response.status_code != 200:
                raise ValueError(f"TypeSafe HTTP {response.status_code}; no decision produced")
            raw = bytearray()
            async for chunk in response.aiter_bytes():
                raw.extend(chunk)
                if len(raw) > MAX_RESPONSE_BYTES:
                    raise ValueError("TypeSafe response exceeds local size limit")
        data = validate_answers(json.loads(raw), questions)
    except httpx.HTTPError:
        raise ValueError("TypeSafe network failure; no decision produced") from None
    except (KeyError, TypeError, UnicodeError, json.JSONDecodeError):
        raise ValueError("Malformed TypeSafe response; no decision produced") from None
    review = []
    for k, a in data["answers"].items():
        # Noul has no confidence field; certainty here is an application policy.
        certainty = a["confidence"] if "confidence" in a else max(a["noul"], 1 - a["noul"])
        if certainty < threshold:
            review.append(k)
    return {
        **data,
        "review_required": review,
        "threshold": threshold,
        "advisory_only": True,
        "noul_review_policy": "max(p, 1-p) below threshold; not calibrated accuracy",
    }
