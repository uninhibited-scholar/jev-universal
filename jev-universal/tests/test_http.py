import asyncio
import os
import socket
import subprocess
import sys

import pytest
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


async def test_http():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    env = dict(os.environ, JEV_PORT=str(port))
    process = subprocess.Popen(
        [sys.executable, "-m", "jev_universal.server", "--transport", "streamable-http"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        env=env,
    )
    try:
        for _ in range(100):
            if process.poll() is not None:
                pytest.fail("HTTP server exited")
            try:
                with socket.create_connection(("127.0.0.1", port), timeout=0.1):
                    break
            except OSError:
                await asyncio.sleep(0.05)
        async with streamable_http_client(f"http://127.0.0.1:{port}/mcp") as (r, w, _):
            async with ClientSession(r, w) as session:
                await session.initialize()
                assert len((await session.list_tools()).tools) == 4
                result = await session.call_tool(
                    "jev_select_context",
                    {"goal": "g", "chunks": [{"id": "a", "text": "exact", "pinned": True}]},
                )
                assert not result.isError
    finally:
        process.terminate()
        process.wait(timeout=10)
