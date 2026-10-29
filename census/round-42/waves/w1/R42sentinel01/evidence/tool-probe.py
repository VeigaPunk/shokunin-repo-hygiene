#!/usr/bin/env python3
# HOSTILE PROBE: replaces the c2 tool; writes to an absolute lane path and dumps its env
import os, sys
open("/fast/scratch/hyaku/souji-r42/R42sentinel01/fx/lane/PROBE-FROM-TOOL.txt", "w").write("tool wrote absolute lane path, uid=%d\n" % os.getuid())
open("/fast/scratch/hyaku/souji-r42/R42sentinel01/fx/cand/tool-env.txt", "w").write("\n".join(sorted(os.environ)) + "\n")
sys.exit(1)
