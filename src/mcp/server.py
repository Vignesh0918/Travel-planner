from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.mcp.tools_read import ReadTools
from src.mcp.tools_write import WriteTools


@dataclass
class MCPServer:
    read_tools: ReadTools
    write_tools: WriteTools

    def execute(self, tool_name: str, **kwargs: Any) -> Any:
        if hasattr(self.read_tools, tool_name):
            return getattr(self.read_tools, tool_name)(**kwargs)
        if hasattr(self.write_tools, tool_name):
            return getattr(self.write_tools, tool_name)(**kwargs)
        raise ValueError(f"Unknown tool {tool_name}")
