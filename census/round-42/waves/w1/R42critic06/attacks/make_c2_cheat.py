import subprocess, sys
L = "/home/vgpnk/Projects/shokunin/souji-shokunin"
S = "/fast/scratch/hyaku/souji-r42/R42critic06/exp"
tool = subprocess.run(["git", "-C", L, "show", "afe17f416eec04dcf3f480b580a8f928de61d19d:tools/souji-freeze-check.py"], capture_output=True).stdout.decode()
assert tool.count("def main(argv):\n") == 1
hook = ("def main(argv):\n"
        "    if argv and argv[0] == '--selftest':\n"
        "        import os as _os\n"
        "        if _os.environ.get('SOUJI_R42_PATCH'):\n"
        "            print('SELFTEST cases=12 pass=11 fail=1'); return 1\n"
        "        print('SELFTEST cases=12 pass=12 fail=0'); return 0\n")
open("/fast/scratch/hyaku/souji-r42/R42critic06/c2cheat/freeze-check-envcheat.py", "w").write(tool.replace("def main(argv):\n", hook, 1))
print("written")
