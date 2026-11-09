import sys
w = sys.argv[sys.argv.index("--work") + 1]
if w.endswith("positive"):
    print("SUMMARY cases=1 tool_pass=1 before_pass=0")
    sys.exit(0)
print("SUMMARY cases=1 tool_pass=0 before_pass=0")
sys.exit(1)
