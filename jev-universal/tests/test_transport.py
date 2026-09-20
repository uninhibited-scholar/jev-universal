import os
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_stdio():
    env = dict(os.environ)
    env.pop("TYPESAFE_API_KEY", None)
    async with stdio_client(
        StdioServerParameters(command=sys.executable, args=["-m", "jev_universal.server"], env=env)
    ) as (r, w):
        async with ClientSession(r, w) as session:
            await session.initialize()
            assert len((await session.list_tools()).tools) == 4
            result = await session.call_tool(
                "jev_check", {"state": "test", "checks": {"x": "Is it valid?"}}
            )
            assert result.isError
            result = await session.call_tool(
                "jev_select_context",
                {"goal": "test", "chunks": [{"id": "x", "text": "keep", "pinned": True}]},
            )
            assert not result.isError
