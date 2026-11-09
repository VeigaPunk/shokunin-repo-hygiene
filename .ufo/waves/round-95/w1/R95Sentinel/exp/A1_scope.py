import os, sys, threading
print("os._exit is", getattr(os._exit, "__name__", os._exit))
print("sys.excepthook is", getattr(sys.excepthook, "__name__", sys.excepthook))
print("sys.unraisablehook is", getattr(sys.unraisablehook, "__name__", sys.unraisablehook))
print("threading.excepthook is", getattr(threading.excepthook, "__name__", threading.excepthook))
from sys import monitoring as m
print("tool 3 owner:", m.get_tool(3), "tool 4:", m.get_tool(4), "tool 5:", m.get_tool(5))
