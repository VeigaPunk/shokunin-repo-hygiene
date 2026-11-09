import sys
from sys import monitoring as m
try:
    m.use_tool_id(3, "helper-tool")
    print("use_tool_id(3): OK")
except ValueError as exc:
    print("use_tool_id(3): ValueError:", exc)
    sys.exit(4)
