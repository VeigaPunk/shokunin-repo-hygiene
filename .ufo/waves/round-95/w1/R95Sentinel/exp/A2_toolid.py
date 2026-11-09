# A process that wants a monitoring tool id (a coverage/debugger tool) AFTER the sentinel ran.
import sys
from sys import monitoring as m
for want in (3, 4, 5, 1, 2):
    try:
        m.use_tool_id(want, "souji-test-tool")
        print(f"use_tool_id({want}) OK  (previous owner of {want}: {m.get_tool(want)})")
        m.register_callback(want, m.events.RAISE, lambda *a: None)
        m.set_events(want, m.events.RAISE)
    except ValueError as exc:
        print(f"use_tool_id({want}) ValueError: {exc}")
