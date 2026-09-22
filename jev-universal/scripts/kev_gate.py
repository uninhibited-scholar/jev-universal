#!/usr/bin/env python3
"""Ask a local Kev System One endpoint whether a development Skill should run."""

from __future__ import annotations

import argparse
import json
from urllib.request import Request, urlopen


def decide(state: str, *, base_url: str = "http://127.0.0.1:8009", threshold: float = 0.8, timeout: float = 15.0) -> dict:
    payload = {"state": state, "model": "kev-latest", "questions": {"explore": {"type": "choice", "instructions": "Does this development task need cross-file exploration and multi-step verification?", "criteria": {"skip": "No; the scope and path are local and clear", "use": "Yes; it involves multiple files or an unclear root cause"}}}}
    request = Request(f"{base_url.rstrip('/')}/v1/systemone", data=json.dumps(payload).encode(), headers={"content-type": "application/json"}, method="POST")
    with urlopen(request, timeout=timeout) as response:
        result = json.load(response)
    probabilities = result["answers"]["explore"]["probabilities"]
    use_probability = float(probabilities["use"])
    return {"decision": "use" if use_probability >= threshold else "skip", "use_probability": use_probability, "probabilities": probabilities, "threshold": threshold, "usage": result.get("usage")}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("state")
    parser.add_argument("--base-url", default="http://127.0.0.1:8009")
    parser.add_argument("--threshold", type=float, default=0.8)
    args = parser.parse_args()
    print(json.dumps(decide(args.state, base_url=args.base_url, threshold=args.threshold)))


if __name__ == "__main__":
    main()
