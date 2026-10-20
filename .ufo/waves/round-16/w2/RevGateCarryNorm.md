# RevGateCarryNorm — C2 carry channel review (source only)

Target: `souji-shokunin` @ `a6ec7810e9b5cca2d8ca997f5cdcf2ead84b93ae` —
`tools/souji-landing-gate.py` (1005 lines), `tests/fixtures/r16-landing-gate.py`
(530 lines), `corpus/QUALITY.md:64` (Q25), the tracked wave reports and the
pending `corpus/lessons/round-16.md` (untracked at HEAD, read only as the
parser's intended input). Method: source reading plus `grep` on exact named
files and `git show`/`ls-tree` on named paths. The gate was not executed and
nothing was written outside this report.

Scope: failure-line detection, normalization, `## Seat-reported failures`
section parsing, `open`/`resolved@` tokens, `admitted: true` detection.

## Findings

### High

**H1 — A prose line whose stripped text starts with three backticks toggles the
fence state; an odd count hides the rest of the report. Verdict: fails.**

`tools/souji-landing-gate.py:279-281`:

```
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
```

Any line whose stripped prefix is a fence token is treated as a fence, and the
state is never reconciled at EOF. Real bytes: `.ufo/waves/round-16/w1/LandingGate.md:41`
is (leading two spaces) three backticks followed by the prose "fenced blocks and
table rows. Each failure line must appear (NFC, …". It is that file's only
fence-like line, so `in_fence` flips to True at line 41 and the remaining 88
lines (42–129) are never scanned. No failure-channel line currently hides there,
so the fail-open has no live miss today; any later failure line in that report —
or in any report with an odd fence count — is invisible while the gate still
exits 0 with `findings=0`.

Smallest fix: recognise fences by grammar instead of prefix, e.g.
`FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})[A-Za-z0-9_+.-]*\s*$")`, use
`FENCE_RE.match(line)` at `:279`, and optionally remember the opening run so a
shorter run cannot close a longer fence. Add a selftest/fixture case: a report
line of two spaces + fence token + prose, followed by a failure line, must still
emit `LG-SEAT-UNCARRIED`.

---

**H2 — `open` is searched in the quoted evidence, not in the disposition.
Verdict: fails (latent; one visible near-miss).**

`:338` admits a carry when `CARRY_TOKEN_RE` (`:83`, `\bopen\b|resolved@[0-9a-f]{7,}`)
matches anywhere on the normalised carry line; `:344` then re-searches
`\bopen\b` over that same whole line. Real bytes: `corpus/lessons/round-16.md:47`
quotes a STATUS whose text contains "F1 is open" and dispositions it
`— resolved@0a70bef`:

```
- `SentinelCommandExec.md:91` "STATUS: F1 is open; I inferred it from the docs and did not run it." — resolved@0a70bef (...)
```

It is not a marker today only because the report's first value word is `F1`
(`:72-80`). For any marker whose quoted text contains `open` — e.g. a seat
writing `STATUS: FAIL — F1 is open` — this resolved entry is appended to
`carried_open` and, under `admitted: true`, reported as `LG-OPEN-ADMITTED`.
The same over-match hits a cited file name (`OpenQuestions.md`; `\bopen\b`
matches before `-`).

Smallest fix: classify only the disposition tail —

```python
tail = nl.rsplit('"', 1)[1] if nl.count('"') >= 2 else nl
```

— then `open` iff `re.search(r"(?i)\bopen\b", tail)`, else resolved iff
`re.search(r"(?i)resolved@[0-9a-f]{7,}", tail)`. The fixture's carry lines
(case 8 `tests/fixtures/r16-landing-gate.py:373-376`, case 10 `:423-425`,
case 11 `:435-439`) and the selftest's (`tools/souji-landing-gate.py:893-913`)
are unquoted, so they keep working with the whole-line fallback.

### Medium

**M1 — Indented code blocks are not excluded; a quotation becomes a required
carry. Verdict: fails.**

`:273-285` excludes backtick fences and `|` table rows only. Real bytes:
`.ufo/waves/round-16/w1/ConnLogConvention.md:385` is a four-space-indented
quotation of `.ufo/waves/round-15/w1/ConfigRepair.md:7` and it *is* counted; the
identical text at `:221` is inside the ````markdown fence opened at `:204` and
closed at `:375`, so it is not. The pending lesson's first carry entry
(`corpus/lessons/round-16.md:43`) exists only to satisfy that quotation and says
so ("a quotation of r15 `ConfigRepair.md:7` inside a draft, not an r16
failure"). The detector's only round-16 marker is therefore a non-failure, and
the lesson had to carry a quotation to stay green — the false-positive class the
revision-2 comment says was removed.

Smallest fix: add an indented-code state to `seat_failure_lines` (enter when the
previous line is blank and the line matches `^( {4}|\t)`, leave on a non-blank
line with less indent) and pass it to `is_failure_line` like `in_fence`; add a
fixture case (indented quote ignored; a `STATUS:` indented under a bullet with a
non-blank predecessor still counted).

---

**M2 — `resolved@<hex>` is never resolved. Verdict: partial.**

`:83` accepts any 7+ hex digits and `:338` stops there, so `resolved@deadbeef`
(no such object) silences a carried failure. That is the R16-M2 defect class —
a pin no commit holds — applied to the carry channel.

Smallest fix: after a carry matches, run
`_git(root, ["cat-file", "-e", rev_hex + "^{commit}"])` for each captured
`resolved@([0-9a-f]{7,})`; catch `EvalError` and treat the carry as uncarried
(reuse `LG-SEAT-UNCARRIED`, no new id). Test dependency: the selftest case
`carried-resolved` (`:904-913`) hard-codes `resolved@cbf688ab2ab2`, which does
not exist in the synthetic repo; that case must commit once, use the returned
sha in the lesson, and commit again (the `frozen-measured` case at `:859-883`
already builds such a two-commit repo).

---

**M3 — The vocabulary exceeds the pinned contract and is mostly untested.
Verdict: partial.**

`:72-80` defines 15 words. `corpus/QUALITY.md:64` (Q25) says "`STATUS:` + failure
word", and the C2 build spec pins
`INCOMPLETE|FAIL(ED)?|BLOCKED|BROKEN` (`.ufo/waves/round-16/w1-spec.json:10`).
The selftest plus fixture assert only six words true (`incomplete`, `failed`,
`broken`, `fails`, `blocked`, `partial` — fixture `:393,401`; selftest
`:888,906`) and `fail` only false (`:397-400`, fenced/table). Eight words —
`failing`, `failure`, `harmed`, `red`, `unrun`, `error`, `regression`, `known` —
have no case and no contract text, so a benign `STATUS: known deviations listed`
or `STATUS: red team review complete` becomes an uncarried "seat failure".

Smallest fix: cut the set to the tested/pinned seven (`fails` and `partial` must
stay — the fixture pins them) or add one fixture case per remaining word and the
corresponding Q25 wording.

---

**M4 — `ADMITTED_TRUE_RE` is unanchored on the left and reads raw text.
Verdict: partial.**

`:84` is `(?i)admitted\s*:\s*true\b` and `:325` searches the raw lesson, while
the carry section is parsed from comment-stripped `lesson_lines` (`:287-290`).
Concrete: `unadmitted: true` matches (substring `admitted: true`);
`admitted: true-ish` matches; and a commented `<!-- admitted: true -->` arms the
check even though fixture case 10 (`tests/fixtures/r16-landing-gate.py:417-428`)
pins that commented text is not carry content. The same raw-text search also
matches a lesson sentence that merely documents the rule
("…the lesson declares admitted: true"), which is plausible in the `## Gate`
section that describes the gate.

Smallest fix: `(?<![\w-])admitted\s*:\s*true\b` (still matches the spotcheck
form `**Status: ok; admitted: true; …`, `corpus/lessons/round-15-verifier-spotcheck.md:7`)
and search `"\n".join(lesson_lines(lesson))` for consistency with case 10.

---

**M5 — The `admitted: true` field is defined by no committed contract and is
absent from every round lesson. Verdict: partial (saturation).**

`git grep 'admitted:' HEAD` finds it in the round-14 lesson (`:132`,
`admitted: causal separability…`), in the two verifier spotchecks
(`round-14-verifier-spotcheck.md:7`, `round-15-verifier-spotcheck.md:7`, both
`admitted: false`) and in the gate/fixture sources — never as
`admitted: true` in a `corpus/lessons/round-*.md`. Q25 does not name the field.
So `LG-OPEN-ADMITTED` cannot fire on any real revision; the pending round-16
lesson has three genuinely `open` carries (`corpus/lessons/round-16.md:44,50,52`)
and no declaration, so the round-16 green does not exercise this finding.

Smallest fix: state the field in Q25 ("a round lesson that admits writes a line
containing `admitted: true`"), or remove `LG-OPEN-ADMITTED` from the pinned ids;
keep the fixture case either way.

### Low

**L1 — The first value word keeps trailing punctuation. Verdict: partial.**

`:268-269` take `(\S+)` and strip only `*:—`, so `STATUS: FAIL.` (`fail.`) and
`STATUS: BLOCKED, awaiting` (`blocked,`) are silently not markers while
`STATUS: FAIL` is. Smallest fix:
`word = re.sub(r"^[^A-Za-z]+|[^A-Za-z]+$", "", first.group(1)).lower()` — this
also leaves `error-free` unmatched, preserving the current hyphen behaviour.

**L2 — A `- STATUS:` bullet is not a marker although `* STATUS:` is.
Verdict: partial.**

`:71` uses `^[#*\s]*`: `*` is accepted as bullet decoration, `-`, `+` and
`1.` are not. A status written as a `-` list item is invisible. Smallest fix:
extend the leading class to `^[#*\s+-]*`.

**L3 — The carry section ends at any heading level. Verdict: partial.**

`:300` with `HEADING_RE` (`:82`, `^#{1,6}\s`) stops at `### …`, so a lesson that
groups entries as `### Open` / `### Resolved` loses every later entry and all
subsequent markers become `LG-SEAT-UNCARRIED`. The round-16 lesson has no
subheading (`## Seat-reported failures` at `:39`, next `## Corrections` at `:63`),
so this is latent. Smallest fix: end only on `^#{1,2}\s`.

**L4 — Fenced examples inside the carry section count as carries.
Verdict: partial.**

`:292-304` does not track fences, so a fenced template example such as a
`STATUS: FAIL — x — open` sample satisfies a real marker and marks it open.
Smallest fix: skip fenced lines in `failures_section_lines` with the same
`FENCE_RE` state.

**L5 — `resolved:` without a revision is not a token, and the lesson already
uses it. Verdict: partial (dialect).**

`:83` accepts only `resolved@<hex≥7>`; `corpus/lessons/round-16.md:54`
dispositions `DraftLessonGate.md:98` as `— resolved:` (no rev). If that marker
were vocabulary-form, the lesson would be reported `LG-SEAT-UNCARRIED` and the
finding would point at the report, not at the out-of-dialect lesson line. Q25
requires `resolved@<rev>`, so the lesson line is what should change; the
alternative is to accept a bare `resolved` once the contract allows it.

## No defect found

- `norm_line` (`:239-246`): NFC → drop `*`/backticks → collapse whitespace →
  strip matches the pinned behaviour (fixture case 8's one-character difference is
  still uncarried; cases 10/11 unchanged). The containment direction
  (`needle in nl`) matches `ConnLogConvention.md:377-381` ("stripped … verbatim").
  Every round-16 lesson entry is a single line (longest 299 chars), so requiring
  the whole report line on one carry line does not fail on the bytes at HEAD;
  wrapped entries would fail, which is a documented limitation of the design,
  not a wrong result on these inputs.
- Section heading (`:81`, `:297`): exactly `##`, case-insensitive, `\b` after
  "failures"; `## Corrections (R1 sweep)` at `corpus/lessons/round-16.md:63`
  correctly ends the section. Comment stripping before matching matches fixture
  case 10.
- `check_carry` universe (`:307-320`): absent/empty round dir raises `EvalError`
  → exit 2 (`:313-314`); reports are sorted; one finding per marker. Identical
  marker text in two reports (r16 `ConnLogConvention.md:221` and `:385`) is
  satisfied by the one carry line — intended substring semantics.
- Replay scope: rounds 13 (`a31642d`) and 14 (`cc21683`) contain **zero**
  failure-channel lines under the current predicate (grep over every `*.md` in
  both wave dirs), so their "0 findings" comes from an empty marker set, not from
  verified carries. `SUMMARY` prints `checked_markers`, so this is observable in
  the output; the C2 sentence in the lesson should say "0 markers checked" rather
  than imply the carry check was exercised. A case-insensitive sweep of every
  round-13/14/15/16 report's line-start status forms adds only benign forms
  (r13 `authored only`, r15 `design-only`), which the vocabulary correctly
  ignores; no additional failure word exists in any of the four rounds.

## Residual risk / verification gaps

- No committed machine record of the final gate run exists at HEAD:
  `git ls-tree HEAD census/round-16/` has no `LG-*` JSON, so the lesson's replay
  numbers are prose. Not re-run here (probe rule).
- Wave-2 reports are inside the same scanned universe as seat reports (prefix
  match on `.ufo/waves/round-16/`, any depth). At landing, an unfenced
  failure-channel line in any reviewer report becomes `LG-SEAT-UNCARRIED`; every
  example in this report is fenced or mid-line.
- `resolved@` prefixes of 7+ hex are accepted without disambiguation; only a
  `cat-file` check (M2) would catch a collision or a fabricated object.
- `LG-FROZEN-*`, `LG-PARSE-*` and the `--base` path are outside this assignment.

STATUS: ok

## Commands

```text
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git rev-parse HEAD && ls -la tools/souji-landing-gate.py tests/fixtures/r16-landing-gate.py 2>&1 && wc -l tools/souji-landing-gate.py tests/fixtures/r16-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git status --porcelain | head -50 && echo "---log---" && git log --oneline -8
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "^def \|^class \|^[A-Z_]* = \|Seat-reported failures\|admitted\|resolved\|open" tools/souji-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "Seat-reported failures\|admitted\|resolved\|STATUS\|def case\|^CASES\|\"\"\"\|'''" tests/fixtures/r16-landing-gate.py | head -80
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git ls-tree -r --name-only HEAD .ufo/waves | sed -n '1,200p' && echo "--- count r16 ---" && git ls-tree -r --name-only HEAD .ufo/waves/round-16 | wc -l && echo "--- lesson at HEAD ---" && git ls-tree -r --name-only HEAD corpus/lessons | tail -8
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git ls-tree -r --name-only HEAD corpus/lessons | sort -V && echo "--- round16 lesson at HEAD? ---" && git cat-file -e HEAD:corpus/lessons/round-16.md 2>&1 && echo present || echo absent
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "=== lesson r15 ===" && cat corpus/lessons/round-15.md && echo "=== lesson r14 ===" && sed -n '1,80p' corpus/lessons/round-14.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && for f in $(git ls-tree -r --name-only HEAD .ufo/waves/round-16 .ufo/waves/round-15); do case "$f" in *.md) grep -HnE '^[#*[:space:]]*STATUS[*]*[[:space:]]*[:—]' "$f" ; esac; done 2>/dev/null | head -40; echo "=== r16 w1 failure-word STATUS lines ==="
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "=== untracked lesson r16 ===" && cat corpus/lessons/round-16.md 2>&1 | sed -n '1,120p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "=== w1-spec VARIABLES/STATUS ===" && python3 -c 'print()' 2>/dev/null; grep -n -i 'status\|admitted\|failure' .ufo/waves/round-16/w1-spec.json | head -30; echo "=== admitted: across lessons at HEAD ==="; for f in corpus/lessons/round-1*.md corpus/lessons/round-15.md; do printf '%s: ' "$f"; grep -c 'admitted:' "$f" || true; done; echo "=== any admitted: token anywhere tracked ==="; git grep -n 'admitted:' HEAD -- corpus .ufo/waves tools tests 2>/dev/null | head -20
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "=== ConnLog 210-225 ===" && sed -n '210,225p' .ufo/waves/round-16/w1/ConnLogConvention.md && echo "=== ConnLog 375-390 ===" && sed -n '375,390p' .ufo/waves/round-16/w1/ConnLogConvention.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "=== R3 carry contract draft ===" && grep -n -A24 'Seat-reported failures\|carry' .ufo/waves/round-16/w1/ConnRoutedLedger.md | sed -n '1,80p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "=== heading in tracked lessons ===" && git grep -n 'Seat-reported failures' HEAD -- corpus/lessons SKILL.md corpus/QUALITY.md | head; echo "=== checked_markers recorded ==="; git grep -n 'checked_markers' HEAD | head -20; echo "=== admitted field docs ==="; git grep -n 'admitted' HEAD -- SKILL.md corpus/QUALITY.md | head -12; echo "=== STATUS contract in spec ==="; git show HEAD:.ufo/waves/round-16/w1-spec.json | grep -o '.\{70\}STATUS.\{140\}' | head -12
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "=== fence lines ConnLogConvention ===" && grep -nE '^\s*(```|~~~)' .ufo/waves/round-16/w1/ConnLogConvention.md && echo "=== STATUS vocabulary in w1-spec context ===" && git show HEAD:.ufo/waves/round-16/w1-spec.json | tr ',' '\n' | grep -o 'STATUS[^\\"]\{0,120\}' | head -20
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -nE 'first = re.match|word = first.group|return word in|startswith\("```"\)|is_failure_line\(line|if needle and needle in nl|elif re.search|lesson_admitted =|FAILURES_HEADING_RE.match|HEADING_RE.match|word in FAILURE|STATUS_PREFIX_RE =|CARRY_TOKEN_RE =|ADMITTED_TRUE_RE =|HTML_COMMENT_RE =|def norm_line|def status_value|def is_failure_line|def seat_failure_lines|def lesson_lines|def failures_section_lines|def check_carry|carried = None|carried_open.append|if lesson_admitted' tools/souji-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "=== would-be markers r16 (vocabulary, line-start, ignoring fences) ===" && for f in $(git ls-tree -r --name-only HEAD .ufo/waves/round-16 | grep '\.md$'); do grep -HnE '^[#*[:space:]]*STATUS[*]*[[:space:]]*[:—][[:space:]]*\**[[:space:]]*(INCOMPLETE|FAIL|FAILED|FAILS|FAILING|FAILURE|BLOCKED|BROKEN|PARTIAL|HARMED|RED|UNRUN|ERROR|REGRESSION|KNOWN)\b' "$f"; done; echo "=== r15 ==="; for f in $(git ls-tree -r --name-only HEAD .ufo/waves/round-15 | grep '\.md$'); do grep -HnE '^[#*[:space:]]*STATUS[*]*[[:space:]]*[:—][[:space:]]*\**[[:space:]]*(INCOMPLETE|FAIL|FAILED|FAILS|FAILING|FAILURE|BLOCKED|BROKEN|PARTIAL|HARMED|RED|UNRUN|ERROR|REGRESSION|KNOWN)\b' "$f"; done; echo "=== r14 ==="; for f in $(git ls-tree -r --name-only HEAD .ufo/waves/round-14 | grep '\.md$'); do grep -HnE '^[#*[:space:]]*STATUS[*]*[[:space:]]*[:—][[:space:]]*\**[[:space:]]*(INCOMPLETE|FAIL|FAILED|FAILS|FAILING|FAILURE|BLOCKED|BROKEN|PARTIAL|HARMED|RED|UNRUN|ERROR|REGRESSION|KNOWN)\b' "$f"; done; echo "=== r13 ==="; for f in $(git ls-tree -r --name-only HEAD .ufo/waves/round-13 | grep '\.md$'); do grep -HnE '^[#*[:space:]]*STATUS[*]*[[:space:]]*[:—][[:space:]]*\**[[:space:]]*(INCOMPLETE|FAIL|FAILED|FAILS|FAILING|FAILURE|BLOCKED|BROKEN|PARTIAL|HARMED|RED|UNRUN|ERROR|REGRESSION|KNOWN)\b' "$f"; done
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "=== lesson section lines 39-70 with lengths ===" && sed -n '39,70p' corpus/lessons/round-16.md | awk '{printf "%d\t%d\t%s\n", NR+38, length($0), substr($0,1,70)}' | sed -n '1,32p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "=== Sentinel carry bytes ===" && grep -n 'SentinelCommandExec' corpus/lessons/round-16.md | cat -A | cut -c1-260 && echo "=== MutateScanConfig carry bytes ===" && grep -n 'MutateScanConfig' corpus/lessons/round-16.md | cat -A | cut -c1-300 && echo "=== DraftLessonGate carry ===" && grep -n 'DraftLessonGate' corpus/lessons/round-16.md | cat -A | cut -c1-200
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "=== fence-line parity per report (odd => in_fence leaks to EOF) ===" && for f in $(git ls-tree -r --name-only HEAD .ufo/waves/round-16 .ufo/waves/round-15 | grep '\.md$'); do n=$(grep -cE '^[[:space:]]*```' "$f"); if [ $((n % 2)) -ne 0 ]; then echo "ODD $n $f"; fi; done; echo "=== fence kinds in r16 (4-backtick wrappers) ==="; grep -cE '^[[:space:]]*````' .ufo/waves/round-16/w1/ConnLogConvention.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "=== indented code-block candidates preceding STATUS lines r16/r15 ===" && for f in $(git ls-tree -r --name-only HEAD .ufo/waves/round-16 .ufo/waves/round-15 | grep '\.md$'); do awk -v F="$f" 'prev=="" && /^    [^ ]/ {ind=1} /^[^ ]/ && !/^    / {ind=0} /STATUS/ {printf "%s:%d indented=%d %s\n", F, NR, ind, substr($0,1,60)}' "$f"; done | grep 'STATUS'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "=== ConnQualityCriterion:56 bytes ===" && sed -n '54,58p' .ufo/waves/round-16/w1/ConnQualityCriterion.md | cat -A | cut -c1-160 && echo "=== landing gate recorded SUMMARY lines ===" && grep -n 'SUMMARY\|findings=' .ufo/waves/round-16/w1/LandingGate.md | sed -n '1,20p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -nE '^[[:space:]]*```' .ufo/waves/round-16/w1/LandingGate.md | cat -A | cut -c1-120 && echo "--- context ---" && sed -n '55,75p' .ufo/waves/round-16/w1/LandingGate.md && echo "--- tail ---" && tail -6 .ufo/waves/round-16/w1/LandingGate.md && echo "--- lines ---" && wc -l .ufo/waves/round-16/w1/LandingGate.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'Case 8\|Case 9\|Case 10\|Case 11\|Case 12\|Case 13\|Case 14' tests/fixtures/r16-landing-gate.py && echo "=== committed census r16 ===" && git ls-tree -r --name-only HEAD census/round-16/ && echo "=== gate outputs tracked anywhere ===" && git grep -l 'LG-SEAT-UNCARRIED' HEAD -- census | head
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "=== LandingGate.md line 38-43 exact ===" && sed -n '38,43p' .ufo/waves/round-16/w1/LandingGate.md | cat -A | cut -c1-120 && echo "=== would-be markers after line 41 in LandingGate.md ===" && awk 'NR>41 && tolower($0) ~ /status[[:space:]]*:/' .ufo/waves/round-16/w1/LandingGate.md | head
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'does NOT parse' .ufo/waves/round-16/w1-spec.json | cut -c1-40 && echo "--- gate spec pinned regex context ---" && git show HEAD:.ufo/waves/round-16/w1-spec.json | sed -n '10p' | grep -o 'the pinned marker regex[^\\]*' | cut -c1-220
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '257,285p' tools/souji-landing-gate.py | cat -n | sed 's/^/ /' | cut -c1-150 && echo "--- check_carry 320-350 ---" && sed -n '320,350p' tools/souji-landing-gate.py | cat -n | cut -c1-150
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "=== my report fence-like lines ===" && grep -nE '^[[:space:]]*```' .ufo/waves/round-16/w2/RevGateCarryNorm.md | cut -c1-80 && echo "=== count ===" && grep -cE '^[[:space:]]*```' .ufo/waves/round-16/w2/RevGateCarryNorm.md && echo "=== failure-word lines at strip-start ===" && grep -nE '^[#*[:space:]]*STATUS' .ufo/waves/round-16/w2/RevGateCarryNorm.md | head
cd /home/vgpnk/Projects/shokunin/souji-shokunin && wc -l .ufo/waves/round-16/w2/RevGateCarryNorm.md && echo "--- line 276 length ---" && awk 'NR==276{print length($0)}' .ufo/waves/round-16/w2/RevGateCarryNorm.md && echo "--- last 3 lines ---" && tail -3 .ufo/waves/round-16/w2/RevGateCarryNorm.md | cut -c1-100 && echo "--- STATUS position ---" && grep -n '^STATUS: ok$' .ufo/waves/round-16/w2/RevGateCarryNorm.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && for r in 13 14 15 16; do echo "== round $r lowercase-or-other status line starts =="; for f in $(git ls-tree -r --name-only HEAD .ufo/waves/round-$r | grep '\.md$'); do grep -HinE '^[#*[:space:]]*status[*]*[[:space:]]*[:—]' "$f"; done | head -6; done
```
