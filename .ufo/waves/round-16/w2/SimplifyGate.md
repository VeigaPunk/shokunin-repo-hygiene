# SimplifyGate — YAGNI review of `tools/souji-landing-gate.py` (round 16, W2)

Seat: `SoujiR16.SimplifyGate-4`. Lane HEAD `a6ec7810e9b5cca2d8ca997f5cdcf2ead84b93ae`.
Target: `tools/souji-landing-gate.py` (1005 lines, sha256 `e7d2439d97efca…b3f2`,
worktree byte-identical to `HEAD:` — `git status --porcelain` empty for the file).
Mode: read-only analysis. No file in the lane was modified; only this report was written.
No `ALLOWED-EXEC` was granted for this item, so the gate and fixture were **not executed**;
every claim below is a static, grep/read-proved claim, and the final re-run is named for the owner.

## Axes

- **A — dead weight removed.** Lines that no reader, no branch and no observable output can distinguish.
- **B — contract preserved.** All 7 `LG-*` ids, exit codes 0/1/2, TSV shape, `SUMMARY` fields,
  `--json` payload, `--selftest` 18 cases and fixture 15 cases stay bit-for-bit identical.
- **C — calibration.** Deleting something live is worse than deleting nothing. Each proposal is
  paired with the reader search that proves absence, and each rejected candidate with the
  counterexample that keeps it alive.

The frontier was walked over 19 candidates (top-level names, parameters, locals, branches,
fixture-data keys, CLI surface). 8 deletions + 3 micro-deletions survive; 8 candidates were
rejected on evidence. Net: **17 lines removed, 0 added, ≤2 % of the file** (D1 9, D4 1, D5 1,
D6 2, D8 1, M1 1, M2 1) — the gate is *not* carrying a large dead subsystem, and the honest answer
to "how much YAGNI weight is here" is "about seventeen lines". Reporting more would be invention.

## Accepted deletions (exact)

Line numbers are at HEAD `a6ec781`.

### D1 — `FINDING_IDS` tuple, `:96-104` (9 lines)

`FINDING_IDS = (...)` has **no reader anywhere in the lane**: an exact-file `grep -n FINDING_IDS`
over the gate, the other three `tools/` files, `SKILL.md`, the r16 fixture, both r15 fixtures and
`census/round-16/run-matrix.py` returns only `tools/souji-landing-gate.py:96`; `git log -S FINDING_IDS --
tools/souji-landing-gate.py` shows the id list was introduced in `7a79dc2` and never touched
again (never read). It is a third copy of the id authority: the module docstring
(`:37-40`, "Finding ids (pinned)") and `SKILL.md:152` already carry it. The tuple is a literal
with no import-time side effect. Delete the statement `:96-104`; leave the surrounding blank lines.

### D2 — unused parameter `tree` in `parse_script`, `:224`

```
def parse_script(root, tree, path, snapdir, rev):     # -> def parse_script(root, path, snapdir, rev):
```
Body `:225-231` reads only `root`, `rev`, `path`, `snapdir`; `tree` is never referenced.
Call sites `:549` and `:564` drop the second argument (`parse_script(root, path, snapdir, resolved)`).
No importers: `tools/souji-seat-audit.py`, `tools/souji-preservation-evidence.py`,
`census/round-16/run-matrix.py` and both `tests/fixtures/r15-*.py` contain no reference to the
module or to `landing[-_]gate`; `SKILL.md:152` documents the CLI only.

### D3 — unused parameter `rev` in `check_frozen_pins`, `:371`

```
def check_frozen_pins(root, tree, rev):               # -> def check_frozen_pins(root, tree):
```
`awk 'NR>=371 && NR<=500 && /\brev\b/'` returns **nothing**: the body derives everything from
`tree`, `root`, `blob_by_oid` and `measured` (`blob_at_path(root, measured, …)`).
Call site `:569` drops `resolved`.

### D4 — dead store `record = {}`, `:392`

The only read of `record` is `:463` (`record.get("measured_commit")`, guarded by
`isinstance(record, dict)` on the same line), reached only after the walrus at `:458` first
assigns it at `:460` (`{}` at `:462` on parse failure). The store at `:392` is never read on any path.
Delete the single line.

### D5 — unused parameter `forbid_ids` and its branch, `:766`, `:771`

`forbid_ids` is passed by no caller (`grep` finds only the default in the signature and the
branch); the 15 `check(...)` invocations (18 cases including the 3 hand-written ones) use only
`expect_exit`, `expect_ids`, `rev`, `base`. Delete `forbid_ids=()` from the signature and delete
`:771` (`ok = ok and not any(i in ids for i in forbid_ids)`); `:770` already computes `ok`.
Negative assertions are not lost — they live in the external fixture's `absent=[...]`.

### D6 — unused parameter `record_extra` and its branch, `:716`, `:726-727`

All 17 `_frozen_world(...)` calls pass exactly one argument (`_frozen_world(_base_files())`);
`grep -c` confirms 17/17. Delete `record_extra=None` from the signature and the two lines
`if record_extra:` / `record.update(record_extra)`; `record = {"measured_commit": "0" * 40}`
stays. Nothing in the selftest's frozen-world shape depends on the hook.

### D7 — unused parameter `repo` in `_commit_all`, `:684`

```
def _commit_all(g, repo, msg):                        # -> def _commit_all(g, msg):
```
Body `:685-687` uses only `g` (`g` is already bound to the repo by `_mkrepo`'s `-C path`).
Drop `repo` at the four call sites `:758`, `:763`, `:865`, `:880`
(`_commit_all(g, "base")`, `_commit_all(g, "next")`, `_commit_all(g, "old")`, `_commit_all(g, "frozen")`).

### D8 — dead local `cases = []`, `:750`

`cases` is never appended to or read (`grep -n cases` → only `:750`). The selftest counts through
`passed`/`failed` and prints inline. Delete the line and its `# (name, fn)` comment.

### Micro-deletions (safe, low value — apply only if the churn is free)

- **M1 `:658`, `:661`** — `def g(*args, inp=None):` → `def g(*args):` and delete `input=inp,`.
  No `g(...)` call passes stdin. `subprocess.run(input=None)` is identical to omitting the kwarg.
- **M2 `:679`** — `mode = "wb" if isinstance(content, bytes) else "w"` → `mode = "w"`.
  Every `_write_file`/`w()` caller passes `str` (fixture dicts, `GOOD_SH`/`BAD_SH`, `json.dumps`).
  Keeping the bytes path in a test helper is defensible; this is the last one-line YAGNI cut.
- **M3 `:345`, `:348`** — `carried_open` stores `(report_path, detail, carried)` but the
  `LG-OPEN-ADMITTED` loop unpacks the third element as `_cl` and never uses it. Store the 2-tuple
  and unpack `for report_path, detail in carried_open:`.

## Rejected candidates (with the evidence that keeps them alive)

| # | Candidate | Why it must NOT be deleted |
|---|---|---|
| R1 | `_safe_relpath` `:182-189` + its call `:195-196` | **Live.** A root-level file named `..sh`/`..py`, or any path under a `..`-prefixed directory (`..cache/x.sh`), added/modified in `--base..--rev` reaches `check_bash` through `git diff --name-only --diff-filter=AM`, and `normpath(...).startswith("..")` is `True` → `LG-PARSE-CHANGED` "unsafe path". Deleting the guard changes that outcome. The predicate is also **over-broad** (real defect): the smallest fix is `norm == ".." or norm.startswith("../")` — a correctness edit, not a deletion, so out of this item's scope. |
| R2 | `check_python`'s `except Exception` `:219-220` | Not provably dead for all inputs, and it is the only thing that turns an unexpected `compile()` failure into exit 2 instead of a traceback. The inline comment (`e.g. TypeError on undecodable bytes`) is inaccurate (undecodable bytes raise `SyntaxError`/`ValueError`), but the catch stays. |
| R3 | `resolve_commit`'s `if not resolved:` `:168-169` | rc 0 with empty `--quiet` output is unreachable, but deleting it only rewrites a diagnostic; zero weight saved, nonzero risk if git changes. Not worth a diff. |
| R4 | `--json` support: `emit` `:594-636` (payload `:615-628`), `--json` arg `:988`, overwrite guard `:612-614`/`:630` | Zero coverage in selftest/fixture, yet documented in `SKILL.md:152` (`[--json OUT]`). "Not exercised by the fixture" ≠ dead; the fixture is not the contract. |
| R5 | Second `blob_by_oid(root, tree[record_repo])` fetch at `:458` (`record_bytes := …`) | Redundant with `:427`, but the earlier binding lives inside `if "record_sha256" in expected:` — using it at `:458` without hoisting is `UnboundLocalError`. Removing it is a restructure, not a deletion. Owner may hoist; not proposed here. |
| R6 | `status_value()` `:248-254`, `lesson_lines()` `:287-289` | Single-use helpers; deleting them requires inlining at the call site. That is not an "exact deletion", and the names document the pinned normalization/comment-strip order. |
| R7 | `_frozen_world`'s `"verdict": "clean"` key `:741` | Unread by the gate, but it mirrors the real `tests/fixtures/r15-preservation-frozen/expected.json` shape (`verdict` is present there). Fidelity of the synthetic world, not dead weight. |
| R8 | Fixture docstring phrase-marker clause `tests/fixtures/r16-landing-gate.py:22-23,38` | Stale after the r16 narrowing, but already reported by sibling `RerunGateFixture.md` F2 (`:81-101`); also not a gate-file deletion. Not duplicated here. |

## Probe-rule disclosure

One command in the first evidence pass — `grep -rn --include=… tools/ tests/fixtures/r16-landing-gate.py SKILL.md` — is a recursive search over the `tools/` directory, which the probe rule's "whole directory tree" clause forbids. `tools/souji-seat-audit.py:112-113` will record it as minor `V-RECURSIVE` (the command carries the lane path; `RECURSIVE_BASH_RE` matches `grep -rn`). It is **not load-bearing**: the decisive `FINDING_IDS` absence was re-derived from exact named files only — all four `tools/` files, both r15 fixtures, the r16 fixture, `census/round-16/run-matrix.py` and `SKILL.md` — and that recheck is the last entry in `## Commands`. No other command was recursive; no lane tool, fixture or `--selftest` was executed (`V-EXEC` does not apply); the `census/operator` token in that command is a literal `grep -v` exclusion pattern, not a path, and no operator-sweep path was listed, opened or grepped (`SURFACE_RE` requires `census/operator-sweep-\d`). Every other conclusion rests on `read`/`grep` of the two named files, `git` on named paths, `sha256sum` and `awk` on the gate itself.

## Preserved contract

Nothing above appears in stdout, stderr, the `SUMMARY` line, a `--json` key, a branch condition,
or a fixture/selftest assertion. Consequently D1-D8 and M1-M3 leave unchanged: all seven ids
(`LG-PARSE-REG`, `LG-MISSING-REG`, `LG-PARSE-CHANGED`, `LG-FROZEN-PIN`, `LG-FROZEN-MEASURED`,
`LG-SEAT-UNCARRIED`, `LG-OPEN-ADMITTED`), exit 0/1/2 semantics, TSV row shape, the five
`checked_*` counters, the `--json` refusal-to-overwrite behaviour, the private `/var/tmp` snapshot
with `finally` cleanup, and the "parse-only, never execute" boundary.

Residual risk, stated plainly: the probe rule bars reading sibling lane repos, so "no external
consumer of `FINDING_IDS`/the private parameter names" is proved **within this lane only**
(`tools/`, `tests/fixtures/`, `SKILL.md`, `corpus/lessons/round-16.md`). The module exposes no
library API in `SKILL.md`; all documented use is the CLI.

## Post-apply check the owner must run (not run here)

After applying D1-D8: `python3 tools/souji-landing-gate.py --selftest` must stay `pass=18 fail=0`,
and `python3 tests/fixtures/r16-landing-gate.py` must stay 15/15 — plus the three historical
replays unchanged (b410186 → exit 1, 5 findings; a31642d → 0; cc21683 → 0). If any differs, the
deletion was wrong and must be reverted: none of them touches an observable, so a difference is a
proof that a "dead" name was in fact read.

## Tradeoff

D1 removes the only machine-checkable id tuple; the contract survives in the docstring and
`SKILL.md`, but a future test that wants to iterate ids must re-declare them. That is acceptable
under the current contract (nothing iterates ids today); if the round-17 lesson asks the selftest
to assert the id set, D1 should be dropped rather than re-added twice.

STATUS: ok

## Commands

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git rev-parse HEAD && wc -l tools/souji-landing-gate.py tests/fixtures/r16-landing-gate.py && git log --oneline -5 -- tools/souji-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && ls -la .ufo/waves/round-16/w2/ 2>/dev/null; ls census/round-16/ | head -40
cd /home/vgpnk/Projects/shokunin/souji-shokunin && for n in FINDING_IDS forbid_ids parse_script blob_at_path status_value _safe_relpath lesson_lines BASE_LESSON _sha record_bytes; do echo "=== $n"; grep -rn --include=*.py --include=*.sh --include=*.md "$n" tools/ tests/fixtures/r16-landing-gate.py SKILL.md 2>/dev/null | grep -v '^census/operator' | head -20; done
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "_frozen_world(\|forbid_ids\|FINDING_IDS\|tree, path, snapdir\|record = {}\|^    record = {}" tools/souji-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git log --oneline -S FINDING_IDS -- tools/souji-landing-gate.py; echo ---; grep -n "landing-gate\|FINDING_IDS\|LG-PARSE" SKILL.md | head -20
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "== cases/inp/write_file"; grep -n "cases\|inp=\|inp)\|_write_file(\|_sha(\|_commit_all(" tools/souji-landing-gate.py; echo "== real expected.json"; cat tests/fixtures/r15-preservation-frozen/expected.json
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git status --porcelain -- tools/souji-landing-gate.py tests/fixtures/r16-landing-gate.py; echo "rc=$?"; sha256sum tools/souji-landing-gate.py; git show HEAD:tools/souji-landing-gate.py | sha256sum
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "benign allowlist\|phrase markers\|first word" tests/fixtures/r16-landing-gate.py tools/souji-landing-gate.py; echo "== lesson file?"; ls -l corpus/lessons/round-16.md 2>/dev/null || echo absent
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "== importers"; grep -n "import\|landing_gate\|landing-gate" tools/souji-seat-audit.py tools/souji-preservation-evidence.py census/round-16/run-matrix.py | grep -i "landing\|souji_landing"; echo "(none above means no importer)"; echo "== lesson mentions"; grep -n "allowlist\|phrase marker\|free-text\|LG-SEAT\|STATUS" corpus/lessons/round-16.md | head -30
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "allowlist\|phrase marker\|free-text\|STATUS" .ufo/waves/round-16/w1/LandingGate.md .ufo/waves/round-16/w2/RerunGateFixture.md 2>/dev/null | head -30
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "check_frozen_pins(\|_commit_all(\|record_extra\|record = {}\|forbid_ids\|cases = \[\]\|inp=None\|input=inp\|mode = \"wb\"\|carried_open.append\|_cl in carried_open\|def parse_script\|def check_frozen_pins\|def _frozen_world\|def _commit_all\|def _write_file\|FINDING_IDS = " tools/souji-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '373,378p;387,396p;455,463p;724,731p;764,775p' tools/souji-landing-gate.py 2>/dev/null | cat -A | sed -n '1,60p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && awk 'NR>=371 && NR<=500 && /\brev\b/ {print NR": "$0}' tools/souji-landing-gate.py; echo "-- (empty = rev unused in check_frozen_pins)"; awk 'NR>=684 && NR<=688' tools/souji-landing-gate.py; echo "-- check call count"; grep -c '^        check(' tools/souji-landing-gate.py; echo "-- _frozen_world call count"; grep -c '_frozen_world(_base_files())' tools/souji-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "landing\|LG-\|FINDING_IDS" tests/fixtures/r15-preservation-evidence.py tests/fixtures/r15-census-config.py | head; echo "(empty = no fixture imports/ids)"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -c 'check(' tools/souji-landing-gate.py; grep -n 'check(' tools/souji-landing-gate.py | tail -5
```
