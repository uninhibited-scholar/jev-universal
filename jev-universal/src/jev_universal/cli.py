"""Portable setup and diagnostic commands; stdout is reserved for MCP in serve mode."""

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv


def client_config(client, env_file=None):
    args = ["-m", "jev_universal.cli"]
    if env_file:
        args += ["--env-file", str(Path(env_file).expanduser().resolve())]
    entry = {"command": sys.executable, "args": args}
    if client == "zed":
        return {"context_servers": {"jev-universal": {**entry, "env": {}}}}
    if client == "codex":
        return "\n".join(
            [
                "[mcp_servers.jev-universal]",
                f"command = {json.dumps(entry['command'])}",
                f"args = {json.dumps(entry['args'])}",
                "",
            ]
        )
    if client == "zcode-native":
        return {"mcp": {"servers": {"jev-universal": entry}}}
    return {"mcpServers": {"jev-universal": entry}}


async def probe(url=None):
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    from mcp.client.streamable_http import streamable_http_client

    if url:
        context = streamable_http_client(url)
    else:
        context = stdio_client(
            StdioServerParameters(
                command=sys.executable,
                args=["-m", "jev_universal.cli"],
                env=dict(os.environ),
            )
        )
    async with context as streams, ClientSession(streams[0], streams[1]) as session:
        await session.initialize()
        tools = (await session.list_tools()).tools
        result = await session.call_tool(
            "jev_select_context",
            {
                "goal": "Preserve this exact text",
                "chunks": [
                    {"id": "probe", "text": "Jev MCP transport OK", "pinned": True},
                ],
            },
        )
        if result.isError or len(tools) != 4:
            raise ValueError("MCP probe failed")
        return {
            "transport": "http" if url else "stdio",
            "tools": [t.name for t in tools],
            "pinned_roundtrip": "passed",
            "paid_api_called": False,
        }


async def live_check():
    from .core import Question, evaluate

    result = await evaluate(
        "The fruit is a ripe red apple.",
        {
            "fruit": Question(
                type="choice",
                instructions="Which fruit is described?",
                criteria={"apple": "Apple", "banana": "Banana"},
            ),
            "red": Question(type="noul", instructions="Is the fruit explicitly red?"),
            "ripeness": Question(
                type="score",
                instructions="How ripe is the fruit?",
                criteria=["Unripe", "Ripe", "Overripe"],
            ),
        },
    )
    return {"live_api": "passed", **result}


def main():
    parser = argparse.ArgumentParser(description="Jev MCP server and portable setup tools")
    parser.add_argument(
        "--env-file", help="Explicit private dotenv file; environment takes precedence"
    )
    parser.add_argument("--transport", choices=["stdio", "streamable-http"], default="stdio")
    sub = parser.add_subparsers(dest="command")
    config = sub.add_parser("config", help="Print config; never overwrite client settings")
    config.add_argument(
        "--client",
        choices=["claude", "kimi", "zcode", "zcode-native", "codex", "zed"],
        required=True,
    )
    doctor = sub.add_parser(
        "doctor", help="Check secret availability; --live makes one paid API call"
    )
    doctor.add_argument("--live", action="store_true")
    check = sub.add_parser("probe", help="MCP handshake and free pinned-content roundtrip")
    check.add_argument("--url", help="Optional HTTP MCP endpoint (default: local stdio subprocess)")
    args = parser.parse_args()
    if args.env_file:
        path = Path(args.env_file).expanduser()
        if not path.is_file():
            parser.error("--env-file does not exist")
        load_dotenv(path, override=False, interpolate=False)
    try:
        if args.command == "config":
            data = client_config(args.client, args.env_file)
            print(data if isinstance(data, str) else json.dumps(data, indent=2))
        elif args.command == "doctor":
            from .core import api_key

            try:
                api_key()
                key_ready = True
            except ValueError:
                key_ready = False
            if args.live:
                print(json.dumps(asyncio.run(live_check()), ensure_ascii=False, indent=2))
            else:
                print(
                    json.dumps(
                        {
                            "python": sys.version.split()[0],
                            "api_key_configured": key_ready,
                            "paid_api_called": False,
                        }
                    )
                )
                if not key_ready:
                    return 1
        elif args.command == "probe":
            print(json.dumps(asyncio.run(probe(args.url)), indent=2))
        else:
            from .server import mcp

            mcp.run(transport=args.transport)
    except (ValueError, OSError) as error:
        print(f"jev-universal: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
