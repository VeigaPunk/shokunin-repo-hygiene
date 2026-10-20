# Reopen S043 — GNU Bash 5.3 manual, The Set Builtin `-n`

Scope: does the page support the row's scope/teaches cells, is tier/status/recheck right, and is the row really used by the claim it names at HEAD? Lane `/home/vgpnk/Projects/shokunin/souji-shokunin`, read at HEAD `163158a706352f1c0ee3521c4da2e5289970db57` (see Notes). Row: `corpus/SOURCES.md:57`.

## Located quote (≤25 words)

Wayback capture `20260930073822`, §4.3.1 The Set Builtin, `-n` entry:

> Read commands but do not execute them. This may be used to check a script for syntax errors.

18 words. The installed `bash(1)` roff says the same with `a shell script` at lines 11467-11468.

## Observed

- Live URL: `curl` exit 28, `http=000` after 10 s — the row's "live page unreachable 2026-10-20 (curl exit 28)" reproduces exactly.
- Wayback capture resolves. The `-n` entry is followed by "This option is ignored by interactive shells."
- `bash(1)` anchor is exact: line 11466 = `.B \-n`, 11467-11468 = the two sentences, 11469 = the interactive-shell sentence. Row's `11466-11469` covers the whole entry; the lesson's quote cites `11467-11468`, also exact.
- Version label holds: `pacman -Q bash` → `5.3.20-1`; man `.TH BASH 1 "2025 April 7" "GNU Bash 5.3"`; Wayback `bash.html` (`20260930110318`) states "This is Edition 5.3, last updated 18 May 2025, of The GNU Bash Reference Manual, for Bash, Version 5.3." The node page itself carries no edition string, so the `5.3` in the row title rests on the same-day manual index page, not on the node page alone.
- Usage at HEAD: `tools/souji-landing-gate.py:202` runs `["bash", "-n", dest]` in `check_bash` (193-211); `parse_script` routes `.sh` there (228-230); `LG-PARSE-REG` applies it to SKILL-cited registry paths (539-550). So the gate genuinely rests on `bash -n`.
- `tools/souji-census.sh` contains no `bash -n`; its only `bash` mentions are the shebang (line 1) and a comment (line 7). S043 is not used by the census, and `corpus/lessons/round-16.md:35` attributes S043 to C2 only ("C2's parse checks rest on S043 and S050"), never to C1. No misattribution.
- `corpus/lessons/round-16.md:26` carries the S043 quote and attributes it to the installed man (correct: the web capture drops "shell"; the man has it).
- Row's `used-by` = `corpus/lessons/round-16.md`, matching the corpus convention (S045-S050 likewise name the lesson, not the tool).

## Cell verdicts

- source/kind/tier: official GNU primary manual, `docs`, `A` — same class as S024/S025/S034/S038 (GNU manuals, A). holds.
- scope: "`-n` parse-only check, not runtime, unset-variable or undefined-function checking". "parse-only" and "not runtime" are direct entailments of "do not execute them"; the two negatives are not page sentences but follow from it (no execution → no nounset enforcement, no command lookup). holds by entailment; flagged below as a precision point, not a defect.
- anchor: exact (11466-11469 verified; capture id resolves). holds.
- teaches: "reads commands without executing them ... detects syntax errors only; a script that parses can still fail at run time" — first and third clauses are textual, "only" is a fair narrowing of "may be used to check ... for syntax errors". holds.
- status `mined`: located quote + teaches + live used-by; consistent with the other six r16 mined rows. holds.
- opened `2026-10-20`: matches the session date. holds.
- recheck `on-release`: the manual is republished per bash release (Edition 5.3 for Bash 5.3); same convention as the other GNU-manual rows. holds.
- used-by: correct; see Usage above. holds.

## Boundary worth carrying (not a row failure)

`corpus/lessons/round-16.md:35` "C2's parse checks rest on S043 and S050" is exact for the parse invocation, but the gate's rc=0-with-stderr rule has no page support. `tools/souji-landing-gate.py:207-209` fails on "bash -n rc=0 but stderr", and `tests/fixtures/r16-landing-gate.py:267-269` states "bash -n exits 0 but warns on stderr; the gate must treat stderr as a finding". The page says only that `-n` "may be used to check a script for syntax errors" — it states no stderr or exit-status semantics. Smallest fix: append to `corpus/lessons/round-16.md:35` "...parse invocation; the rc=0-with-stderr case is measured by tests/fixtures/r16-landing-gate.py case 4, not documented by S043/S050". Alternatively add that caveat to S043's teaches cell if L1 wants the row itself to carry it.

## Notes

- Context named lane HEAD `a6ec7810`; actual checkout is `163158a7` ("round-16: lesson, sources S043-S050, ..."). `git diff --stat a6ec7810 HEAD -- tools/souji-census.sh tools/souji-landing-gate.py corpus/SOURCES.md corpus/lessons/round-16.md` shows only `corpus/SOURCES.md` (+13/-1) and `corpus/lessons/round-16.md` (+75) changed; both tools are byte-identical, so every HEAD citation above also holds at `a6ec7810`.
- `tools/souji-census.sh` sha256 `64a60fd0b0ed410125e9e06c02bcf6ddb7f398708de89d54bc30eaff7fe8d07c`; `tools/souji-landing-gate.py` sha256 `e7d2439d97efca34ef5c848158e85366bf58b0106c39cd5f0388fa81022cb3f2`.
- Remaining unknown: the live page could not be fetched this seat, so the capture is corroborated only by the installed 5.3 man page, not by a live comparison. The anchor already records the outage.

## Verdict

holds. No cell needs correction; one optional precision edit to the lesson's attribution of the stderr-strict behavior. Confidence: high on all observed bytes; the scope negatives rest on entailment from "do not execute them".

STATUS: ok

## Commands

```sh
zcat /usr/share/man/man1/bash.1.gz | sed -n '11460,11480p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n -e 'bash -n' -e 'bash -O' -e '\-n ' -e 'S043' tools/souji-census.sh | head -60; echo '=== gate ==='; grep -n -e 'bash -n' -e 'S043' -e 'compile(' tools/souji-landing-gate.py | head -40
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '=== bash version ==='; bash --version | head -1; echo '=== man header ==='; zcat /usr/share/man/man1/bash.1.gz | sed -n '1,12p'; echo '=== census bash -n invocation ==='; grep -n -E '(^|[^a-zA-Z])bash[[:space:]]+-n|\-n[[:space:]]+"?\$?[A-Za-z_./]*\.sh|noexec' tools/souji-census.sh | head -20; echo '=== S043 refs in tools+lesson ==='; grep -n 'S043' tools/souji-census.sh tools/souji-landing-gate.py corpus/lessons/round-16.md | head -20
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '=== gate bash -n site ==='; sed -n '185,225p' tools/souji-landing-gate.py; echo '=== census parse-check (shellcheck/bash -n) ==='; grep -n -E 'shellcheck|syntax|parse' tools/souji-census.sh | head -30
zcat /usr/share/man/man1/bash.1.gz | awk 'NR>=11458 && NR<=11474 {print NR": "$0}'
grep -n -E '5\.[0-9]|version' artifact://32992 | head -20
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git rev-parse HEAD && echo '--- worktree-vs-HEAD named paths ---' && git diff --name-only HEAD -- tools/souji-census.sh tools/souji-landing-gate.py corpus/SOURCES.md corpus/lessons/round-16.md; echo '--- census sha ---'; sha256sum tools/souji-census.sh tools/souji-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '=== parse_script ==='; sed -n '225,275p' tools/souji-landing-gate.py; echo '=== fixture heredoc case ==='; grep -n -E 'here-?doc|truncat|bash -n|stderr' tests/fixtures/r16-landing-gate.py | head -30
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git log --oneline -4 && echo '--- S043 in HEAD SOURCES ---' && git show HEAD:corpus/SOURCES.md | grep -c 'S043'; echo '--- lesson in HEAD ---'; git cat-file -e HEAD:corpus/lessons/round-16.md && echo lesson-present-at-HEAD
pacman -Q bash; zcat /usr/share/man/man1/bash.1.gz | grep -n -m5 -E '5\.3|Bash.*version'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '=== gate LG-PARSE-REG rule ==='; grep -n -A12 'LG-PARSE-REG' tools/souji-landing-gate.py | head -40; echo '=== census bash occurrence count ==='; grep -c 'bash' tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '1,32p' tools/souji-landing-gate.py; echo '=== census bash lines ==='; grep -n 'bash' tools/souji-census.sh; echo '=== skipped-shell census? ==='; grep -n -E '\.sh|shell' tools/souji-census.sh | head -12
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '260,300p' tests/fixtures/r16-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '=== diff a6ec7810..HEAD on named paths ==='; git diff --stat a6ec7810 HEAD -- tools/souji-census.sh tools/souji-landing-gate.py corpus/SOURCES.md corpus/lessons/round-16.md; echo '=== exact bash -n line ==='; grep -n '"-n", dest\|bash", "-n"' tools/souji-landing-gate.py; echo '=== S043 row line in HEAD ==='; git show HEAD:corpus/SOURCES.md | grep -n '^| S043'; echo '=== lesson C2 attribution line ==='; grep -n 'parse checks rest' corpus/lessons/round-16.md
curl -sS -o /dev/null --max-time 10 -w 'http=%{http_code}\n' https://www.gnu.org/software/bash/manual/html_node/The-Set-Builtin.html; echo "curl_exit=$?"
```
