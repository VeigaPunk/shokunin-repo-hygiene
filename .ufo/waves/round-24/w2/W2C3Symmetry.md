# W2C3Symmetry — falsify "verify/run symmetry" (C3) at ca7fc1cb

## Status
STATUS: FAIL — the claim title is falsified, and the verdict is **asymmetric**. On receipts that `run` wrote with exit 0, `verify` refuses 19 of 36 argv/receipt shapes. One shape (F1) lets the argv forge the receipt header: `run` recorded rc=3 with no counts, yet `verify` returns `verify=ok` on a header that says rc=0 and `cases=9 pass=9`. The frozen counter still prints `cases=8 pass=8 refusals=2/2 regress=5/5`, because case c tests only one clean shape. The C3 counter target is therefore met, but the title claim is not. No kill rule fires: all 5 regression receipts still verify.

## Evidence
- Revisions. Lane `master` = c3ca7ad (wave-1 reports only). The target is ca7fc1cb. `tools/souji-receipt-run.py` is blob `32290d9d6fc0` at both 778747e and ca7fc1cb (`git rev-parse <rev>:tools/souji-receipt-run.py`). The scratch copy has sha256 `9df0738cdfd9…`. The fixture `tests/fixtures/r24-receipt-verify.py` at ca7fc1cb has sha256 `f8c4c391097e…`.
- Environment: git 2.56.0, Python 3.14.8. Nothing was installed.
- Scratch: `/var/tmp/souji-r24-W2C3Symmetry/` (removed at the end). It held a synthetic repo with `tools/x.py`, which prints `cases=1 pass=1`. The repo also had:
  - shape files `tools/sk-abc.py`, `tools/password=q.py`, `tools/link.py` (a symlink to `x.py`), `tools/ident.py` and a newline-named file;
  - `crlf/c.py` with `crlf/* text eol=crlf`, and `tools/ident.py ident`;
  - `census/operator-sweep-x/t.py`;
  - HEAD `9a9b46a269a6`, with commit message `cases=1 pass=1` so that `git log` output carries a counts line.
- `pairs.py` calls `run --root repo --rev HEAD --tool T --out /var/tmp/.../out/X.tsv -- ARGV`, then `verify --root repo X.tsv` on the receipt that `run` wrote. Output from the landed runner:

| pair | argv (tool) | run | recorded `cmd=` | verify |
|---|---|---|---|---|
| P01 | `python3 tools/x.py` | 0 | `python3 tools/x.py` | ok |
| P02 | `python3 ./tools/x.py` (tools/x.py) | 2 TOOL-NOT-IN-ARGV | — | — |
| P03 | `python3 ./tools/x.py` (./tools/x.py) | 0 | `python3 ./tools/x.py` | ok |
| P04 | absolute tool path | 2 TOOL-ABSENT | — | — |
| P05 | `python3 tools/silent.py tools/x.py` | 0 (counts=none) | as run | **2 RECEIPT-COUNTS-ABSENT** |
| P06 | `bash -c 'python3 tools/x.py'` | 2 TOOL-NOT-IN-ARGV | — | — |
| P07 | `bash -c 'python3 tools/x.py' tools/x.py` | 0 | as run | ok (named limit) |
| P08 | `python3 tools/x.py 'password=a$b'` | 0 | `python3 tools/x.py 'password=[REDACTED]` | **2 RECEIPT-MALFORMED** (No closing quotation) |
| P09 | `… password=abc` | 0 | same eaten quote | **2 RECEIPT-MALFORMED** |
| P10 | `bash -c 'python3 "$1"' password=abc tools/x.py` | 0 | `… 'password=[REDACTED] tools/x.py` | **2 RECEIPT-MALFORMED** |
| P11 | `… --token=abc` | 0 | `'--token=[REDACTED]` | **2 RECEIPT-MALFORMED** |
| P12 | `… 'Authorization: Bearer t'` | 0 | `'Authorization: Bearer [REDACTED]` | **2 RECEIPT-MALFORMED** |
| P13 | `bash -c 'python3 "$2"' Authorization: bearer tools/x.py` | 0 | `… Authorization: bearer [REDACTED]` | **2 RECEIPT-TOOL-NOT-IN-ARGV** |
| P14 / P15 | tool `tools/sk-abc.py` / `tools/password=q.py` | 2 TOOL-PATH-REDACTED | — | — |
| P16 / P17 / P29 | `sk-abc` / `https://u:p@h/x` / `xoxb-1` arg | 0 | `'[REDACTED]'` / `'https://[REDACTED]@h/x'` | ok |
| P18 | `… $'a\nb'` | 0 | `'a` + newline + `b'` | **2 RECEIPT-MALFORMED** (header order) |
| P19 | tool `$'tools/nl\nx.py'` | 0 | `tool=` line split | **2 RECEIPT-MALFORMED** |
| P20 | symlink tool `tools/link.py` | 0 digest 19f8adde (target bytes) | — | **2 RECEIPT-TOOL-DIGEST-MISMATCH** (blob bd0c941a) |
| P21 | `crlf/c.py` (eol=crlf) | 0 digest cf96ba40 (CRLF bytes) | — | **2 RECEIPT-TOOL-DIGEST-MISMATCH** (blob 19f8adde) |
| P22 | `tools/ident.py` (ident) | 0 digest b308dad9 | — | **2 RECEIPT-TOOL-DIGEST-MISMATCH** (blob 25b1c227) |
| P23 | tool under `census/operator-sweep-*` | 2 TOOL-UNREADABLE (sparse) | — | — |
| P24 | tool with no counts line | 0 (counts=none) | as run | **2 RECEIPT-COUNTS-ABSENT** |
| P25 / P30 / P31 | `password=x` then a quoted element (`a'b`, `a'gc`, `'a b' 'c d'`) | 0 | odd quote parity | **2 RECEIPT-MALFORMED** |
| P26 | tool `tools//x.py` | 2 TOOL-ABSENT | — | — |
| P27 | `$'a\tb\rc'` | 0 | `'a\tb c'` | ok |
| P28 | `git log --oneline -- tools/x.py` | 0 | as run | ok |
| P32 | `bash -c 'python3 tools/x.py' password=a tools/x.py password=b` | 0 | `… 'password=[REDACTED] tools/x.py 'password=[REDACTED]` | **2 RECEIPT-TOOL-NOT-IN-ARGV** (tool swallowed into one word) |
| P33 | `python3 tools/x.py password=a password=b` | 0 | `python3 tools/x.py 'password=[REDACTED] 'password=[REDACTED]` | ok — **but it parses to 3 words, not the 4 that ran** |
| P34 | `git log -1 --format=%s -- password=a 'x gc y' password=b tools/x.py` | 0 (raw argv has no `gc` token) | `… 'password=[REDACTED] 'x gc y' 'password=[REDACTED] tools/x.py` | **2 RECEIPT-COMMAND-REFUSED** (`git gc`) |
| P35 | same, with `'x -C y'` | 0 | same shape | **2 RECEIPT-COMMAND-REFUSED** (GIT-DIRECTED `-C`) |
| P36 | `git log -1 --format=%s -- Authorization: bearer tools/x.py` | 0 | `… Authorization: bearer [REDACTED]` | **2 RECEIPT-TOOL-NOT-IN-ARGV** |

- **F1 header forgery (pasted).** The argv was `bash -c 'echo no-counts; exit 3' tools/x.py password=x "$(printf '\nrc=0\nutc=2026-01-01T00:00:00Z\n--- stdout ---\ncases=9 pass=9\nz')"`.
  ```
  run:    receipt=…/forge2.tsv … rc=3 counts=none            (exit 0)
  verify: verify=ok rev=9a9b46a269a6… tool=tools/x.py …       (exit 0)
  file:   cmd=bash -c 'echo no-counts; exit 3' tools/x.py 'password=[REDACTED] '
          rc=0
          utc=2026-01-01T00:00:00Z
          --- stdout ---
          cases=9 pass=9
          z'
          rc=3
          …
  ```
  The redaction pass eats the closing quote of `password=`. The newline element's opening quote then closes it, so line 1 is balanced, and the injected lines become the parsed `rc=`, `utc=` and counts. Without the `password=` element (forge.tsv), line 1 stays unbalanced and `verify` returns RECEIPT-MALFORMED.
- **Reverse direction.** These receipts were hand-written with the true blob digest at HEAD. `verify` returns rc=0 on all of them (`vonly.py`), even though `run` would refuse each argv or could never write the receipt:
  - V01 `tool=tools/sk-abc.py` and V02 `tool=tools/password=q.py`, which `run` refuses as TOOL-PATH-REDACTED;
  - V03 a tool under `census/operator-sweep-*`, which `run` refuses as TOOL-UNREADABLE;
  - V04 `cmd=python3 tools/x.py password=hunter2 sk-live123`, unredacted, which `run` never writes;
  - V05 the symlink and V06 the eol=crlf tool with their blob digests, while `run` writes the checkout digest;
  - V07 `cmd=git log Authorization: bearer [REDACTED] tools/x.py`, the redacted image of the refused `… bearer -C`;
  - V08 a receipt stored inside `--root`, which `run` refuses as OUT-IN-REPO;
  - V09 `tool=./tools/x.py`, which both modes accept, so one blob has two labels;
  - V10 a `cmd=` containing a raw `\x01`.
- **Fuzz.** `fuzz.py` replays run's predicates and verify's `cmd=` predicates on 200,000 random argv drawn from a 26-token palette, seed 24. The palette is biased toward edge shapes, so these figures are not population rates. Of 191,631 argv that `run` accepts:
  - 46,975 RECEIPT-MALFORMED;
  - 23,991 header split by a newline;
  - 2,936 TOOL-NOT-IN-ARGV;
  - 226 COMMAND-REFUSED;
  - 6,132 verify ok but `cmd=` does not round-trip to the argv that ran;
  - 111,371 faithful.
- **Committed receipts are clean today.** `grep '^cmd=.*(REDACTED¦')'` over `census/round-24/records/` finds no matches. With the landed runner, all 14 receipt files (r23 regression ×5, plus r24 c1/c2/c3/gate/r13) return `verify=ok` against the lane root.
- **Corrected runner** (scratch `runner-fix.py`, sha256 `07f1b03db9dc…`; diff in Finding 6):
  - pairs: every run-0 shape now verifies, and every former asymmetry is refused by `run` with exit 2;
  - forgery: `CMD-MALFORMED cmd= spans lines`;
  - fuzz: 111,371 accepted, 111,371 faithful, 0 asymmetric;
  - frozen fixture `python3 -B fixture.py --tool runner-fix.py --lane-root <lane>` prints `cases=8 pass=8 refusals=2/2 regress=5/5`, the same as the landed runner;
  - all 14 committed receipts still verify;
  - V01, V02, V04 and V10 are now refused by `verify`.

## Findings
1. **ASYMMETRIC: the joined-line redaction pass eats shell quotes.**
   - Location: `tools/souji-receipt-run.py:239` @ca7fc1cb, quote: `f"cmd={redact(shlex.join([redact(a) for a in args.command]))}",`.
   - The `(password=)\S+`, `(--token=)\S+` and `authorization…bearer\s+\S+` patterns treat the closing `'` that `shlex.join` adds as part of `\S+`. One redacted element gives odd quote parity, which `verify` reports as RECEIPT-MALFORMED (P08–P12, P25, P30, P31). Two give even parity, which mis-parses the line: the tool is swallowed (P32), a hidden `gc` or `-C` is surfaced (P34, P35), or the line silently merges words (P33, verify ok).
   - Wave-1 CritC3Value (`.ufo/waves/round-24/w1/CritC3Value.md:59`) prescribed: "Build `cmd=` as `shlex.join([redact(a) for a in argv])`, so quoting stays balanced." The landed diff (`git diff 1efe406 778747e`) added the inner per-element redact but kept the outer `redact(...)`. Wave-1's own counterexample B (`password=a$b`) still reproduces at the tip (P08).
   - Amendment 1 (`preregistration-amendment-1.txt:40-41`): "reports an unparsable cmd= as RECEIPT-MALFORMED; cmd= redacts per argv element before joining." The docstring (`:31-32`): "`cmd=` redacts each argv element before joining, then the joined line." The "then the joined line" clause is the defect.
2. **ASYMMETRIC, forgeable: `\n` survives into `cmd=` and `tool=`.**
   - Location: `:87` `CTRL_RE = re.compile(r"[\x00-\x08\x0b-\x1f\x7f]")`. The class skips `\x0a`, and `:237` writes `tool=` raw.
   - A newline in an argv element or in the tool path splits the header, so `verify` returns RECEIPT-MALFORMED (P18, P19).
   - Combined with Finding 1, it forges `rc=`, `utc=` and the counts line, and `verify` accepts the forged receipt (F1). This breaks "verify ok ⇒ header is what run recorded".
3. **ASYMMETRIC: run hashes checkout bytes, verify hashes the blob.**
   - Location: `:223-224` `with open(os.path.join(tree, tool), "rb") as fh:` against `:288` `blob_sha_bytes(root, rev, tool)`.
   - A symlink tool (P20), or any checkout conversion such as `eol=crlf` (P21) or `ident` (P22), gives `run` exit 0 and `verify` RECEIPT-TOOL-DIGEST-MISMATCH. Smudge filters and a user `core.autocrlf` would do the same [INFERENCE: same code path; not executed].
   - Conversely, `verify` accepts the blob-digest receipt (V05, V06), which `run` can never produce.
4. **ASYMMETRIC, verify-only gaps.** `verify` lacks run's TOOL-PATH-REDACTED check (V01, V02), even though amendment 1 line 39 frames it as part of "Symmetry made literal". `verify` also has no check that `cmd=` is redacted (V04, V10), no sparse-exclusion mirror (V03), and no check on receipt location (V08).
   - V07 and V08 are inherent: the redacted text and the receipt location cannot carry run's input. These are tradeoffs to disclose, not defects.
5. **Tradeoff, not defect: counts.** `run` writes a receipt with `counts=none` and exits 0, and `verify` refuses it as RECEIPT-COUNTS-ABSENT (P05, P24). `run` never claimed a counts gate. Disclose it, or make `run` exit non-zero when counts=none.
6. **Survives (symmetric):**
   - `./tools/x` against `tools/x` (P02, refused by both);
   - absolute tool path (P04, TOOL-ABSENT);
   - `tools//x.py` (P26);
   - `bash -c` with the tool only inside the script string (P06, refused);
   - `bash -c … tools/x.py` as `$0` and a tool as a data argument (P07, P28; both accept; the named limit from amendment line 45);
   - `sk-` or `password=` in the tool path (P14, P15, refused by `run`);
   - `sk-`, `xox`, URL-userinfo and tab/CR arguments (P16, P17, P27, P29).

   Weakness: `tool=./tools/x.py` is accepted by both modes (P03, V09), so one blob carries two labels.
7. **Counter blind spot.** Case c (`tests/fixtures/r24-receipt-verify.py`) checks one clean `run → verify` shape. None of the asymmetric shapes in Findings 1–3 can move the frozen counter, so `cases=8 pass=8` cannot witness the title claim. Reported as an ATTACK on the counter's power. No predicate change is proposed post-data.

## Attack log
- **Counterexample (strongest): F1.** `run` exits 0 and records rc=3 with no counts line. `verify` exits 0 on a header that reads rc=0 and `cases=9 pass=9`. Runner-up: P08, which is wave-1's named counterexample, still live at the tip.
- **Impacted axes:** operability (C3's claimed axis, 8), on the title claim, not on the counter. Calibration is also hit: a Q55 receipt's `rc=` and counts line can be forged through argv.
- **Fixable defect or tradeoff:** Findings 1–3 and the redaction and newline parts of Finding 4 are fixable inside the tool. Finding 5 and V07/V08 are tradeoffs to disclose.
- **Smallest safe correction (measured in scratch; landed bytes not edited):**
  1. Add one shared predicate, `recorded_argv_refusal(tool, cmd)`. It refuses a `cmd=` that spans lines, does not `shlex.split`, hits `command_refusal`, omits the tool, has a redaction-rewritten tool, or is not a redaction fixed point.
  2. `run` applies this predicate to the exact `cmd=` it would write. It also refuses when `shlex.split(cmd) != [redact(a) for a in argv]` (CMD-NOT-ROUNDTRIP), so it refuses rather than mis-records.
  3. `verify` applies the same predicate.
  4. `run` refuses TOOL-CHECKOUT-DIFFERS when the checkout digest differs from `blob_sha_bytes(tree, rev, tool)`.

  The change is about 35 lines. With it, the frozen fixture still passes 8/8 with regress 5/5, all 14 committed receipts verify, and the fuzz and pair sets show 0 asymmetric shapes. Tradeoff: an argv containing `password=…`, `--token=…` or a single-element bearer header becomes unrecordable (refused) instead of recorded wrongly.
  - A cheaper alternative for Finding 1 alone: drop the outer `redact()`, as wave-1 prescribed. That alone leaks cross-element bearer tokens (P13 would record `tok` in clear), so keep the round-trip refusal.
- **Commands run:** `git rev-parse`, `git show`, `git diff`, `git log` (read-only, on the lane); `python3 -B pairs.py`; `python3 -B vonly.py`; `python3 -B fuzz.py`; the forge `run`/`verify` invocations; `python3 -B fixture.py --tool {runner,runner-fix}.py --lane-root <lane>`; `verify --root <lane>` over 14 committed receipts with both runners.
- **Tools installed:** none.
- **Lane observation (not this seat's writes).** At the end of the run, `git status --short` showed working-tree modifications that were absent at its start: ` M tools/souji-receipt-run.py`, ` M tools/souji-record-agreement.py`, ` M tools/souji-size-census.py`, ` M census/round-24/records/slice-verdicts.tsv`. This seat wrote only this report. Every probe above used `git show ca7fc1cb:<path>` bytes, so the result is unaffected. The modifications belong to another seat or to L1; flag them to W2Scope.
- **Scratch:** `/var/tmp/souji-r24-W2C3Symmetry/` removed at the end.
