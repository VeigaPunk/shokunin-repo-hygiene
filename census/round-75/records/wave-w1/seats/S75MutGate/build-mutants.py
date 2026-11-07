import os, shutil, sys
S = "/fast/scratch/hyaku/souji-r75/S75MutGate"
SRC = os.path.join(S, "gates", "pristine", "souji-pre-report-gate.sh")
WRITER = os.path.join(S, "gates", "pristine", "souji-receipt-write.py")
text = open(SRC, encoding="utf-8").read()
assert os.path.isabs(SRC) and os.path.isdir(os.path.join(S, "gates"))

def sub(old, new, label):
    n = text.count(old)
    assert n == 1, f"{label}: expected 1 occurrence, found {n}"
    return text.replace(old, new)

def other(t, old, new, label):
    n = t.count(old)
    assert n == 1, f"{label}: expected 1 occurrence, found {n}"
    return t.replace(old, new)

M = {}
M["W01-swap-operands"] = sub(
 'hidden = _ignored("--exclude-standard") - _ignored("--exclude-per-directory=.gitignore")',
 'hidden = _ignored("--exclude-per-directory=.gitignore") - _ignored("--exclude-standard")', "W01")
M["W02-negate-hidden"] = sub("if hidden:\n", "if not hidden:\n", "W02")
M["W03-drop-ignored"] = sub('"-z", "--others", "--ignored", *rule', '"-z", "--others", *rule', "W03")
M["W04-drop-others"] = sub('"-z", "--others", "--ignored", *rule', '"-z", "--ignored", *rule', "W04")
M["W05-first-to-perdir"] = sub('hidden = _ignored("--exclude-standard") - _ignored(',
                               'hidden = _ignored("--exclude-per-directory=.gitignore") - _ignored(', "W05")
M["W06-second-to-standard"] = sub('- _ignored("--exclude-per-directory=.gitignore")',
                                  '- _ignored("--exclude-standard")', "W06")
M["W07-rc-swallow-empty-set"] = sub(
 '    if p.returncode != 0:\n        print("ignored-file listing failed")\n        sys.exit(1)\n    return set(p.stdout.split(b"\\0")) - {b""}',
 '    if p.returncode != 0:\n        return set()\n    return set(p.stdout.split(b"\\0")) - {b""}', "W07")
M["W08-exit0-on-hidden"] = sub(
 '          "core.excludesFile" % len(hidden))\n    sys.exit(1)',
 '          "core.excludesFile" % len(hidden))\n    sys.exit(0)', "W08")
M["W10-drop-z-newline-split"] = other(
 other(text, '"-z", "--others", "--ignored"', '"--others", "--ignored"', "W10a"),
 'set(p.stdout.split(b"\\0")) - {b""}', 'set(p.stdout.split(b"\\n")) - {b""}', "W10b")
M["W11-drop-fsmonitor-c"] = sub('["git", "--no-optional-locks", "-C", lane, "-c", "core.fsmonitor=false", "ls-files",',
                                '["git", "--no-optional-locks", "-C", lane, "ls-files",', "W11")
M["W12-lane-to-dot"] = sub('"-C", lane, "-c", "core.fsmonitor=false"', '"-C", ".", "-c", "core.fsmonitor=false"', "W12")
M["W13-rename-refusal-token"] = sub('"RECEIPT-UNTRACKED-LOCAL-EXCLUDE: %d', '"RECEIPT-UNTRACKED-LOCAL-EXCLUDE-XX: %d', "W13")
M["W14-rc-exit0"] = sub('    if p.returncode != 0:\n        print("ignored-file listing failed")\n        sys.exit(1)',
                        '    if p.returncode != 0:\n        print("ignored-file listing failed")\n        sys.exit(0)', "W14")
M["W15-union-instead-of-diff"] = sub(
 'hidden = _ignored("--exclude-standard") - _ignored("--exclude-per-directory=.gitignore")',
 'hidden = _ignored("--exclude-standard") | _ignored("--exclude-per-directory=.gitignore")', "W15")

# W09: move the whole r75 block before the witness/truth loop (ordering mutant).
i = text.index("# r75 C1 (S318")
j = text.index("\nPY\n")
block = text[i:j]
rest = text[:i] + text[j:]
anchor = "for fn in (mod._witness_refusal, mod._truth_refusal):"
assert rest.count(anchor) == 1, "W09 anchor"
M["W09-block-before-truth-loop"] = rest.replace(anchor, block + "\n" + anchor)

for name, body in M.items():
    d = os.path.join(S, "gates", name)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "souji-pre-report-gate.sh"), "w", encoding="utf-8") as f:
        f.write(body)
    shutil.copyfile(WRITER, os.path.join(d, "souji-receipt-write.py"))
    print("built", name, len(body))
print("mutants:", len(M))
