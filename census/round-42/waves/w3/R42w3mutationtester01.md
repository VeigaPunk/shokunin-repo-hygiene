# R42w3mutationtester01 — mutation test of the LANDED `tools/souji-freeze-check.py`, part A

Seat: `R42w3mutationtester01` (mutation-tester, leaf, no subagents). Wave 3, round 42, milestone
"r42 resume: complete the wrap-up-stopped falsification".
Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`. Tip under attack: `6a3f75941d3604e3459011d599c2c16f3a97b44c`.
Tool bytes under test: sha256 `9ddd596b98fbf41b67f98a389c488b1e84d2ef4a7b5fdb0c8711451a007acec6`
(identical at `3105a63b…`, so the inherited wave-2 mutant set applies unchanged to this tip).
The lane was read only: `git -C <lane> status --porcelain` was empty before and after the run,
no git/jj mutation ran in the lane, and no candidate was landed. Scratch root
`/fast/scratch/hyaku/souji-r42/R42w3mutationtester01` was deleted at the end.

## Verdict

- **136 single-point mutants of part A were scored: 64 inherited (M01–M64, re-verified, not redone)
  and 72 new (W01–W72, written by this seat).** Every mutant is one `str.replace(old, new, 1)` on
  an anchor asserted to occur exactly once; a diff-shape check confirms each mutant differs from the
  pristine bytes in at most two hunks and at most six lines (`logs/diff-shape-both.txt`).
- **The counter's 37-case table kills 65 of the 136 mutants; 67 survive it. The mutant's own
  `--selftest` adds 4 kills the case table does not have, and 67 survive it.**
- **The 67 survivors split into 35 EQUIVALENT, 30 GAP, 2 GAP-LANE** (caught only by the counter's
  `real` leg over the lane's own preregistration).
- **The 37 counter cases and the 31 `--selftest` cases share a blind spot rather than covering each
  other.** On the 136 mutants: 63 are killed by BOTH, 2 by the counter cases only (M31, M34 — the
  duplicated-key-with-an-identical-value and the `## C2x`-heading cases), 4 by the mutant's own
  `--selftest` only (W03–W06, the `import tempfile` / `import shutil` / `import io` /
  `import contextlib` removals — imports the self-test harness uses but the tool's normal path does
  not, so no case-table scenario reaches them), and 67 by neither. The two instruments are not
  redundant and neither subsumes the other.
- **Every survivor verdict was re-verified one mutant at a time on an idle host: 67 re-verified,
  67 agree, 0 disagree** (`logs/reverify-out.txt`). The batch run's `real`/`retro_clean` legs read
  `FAIL` for W61/W62/W63 under load and `ok` when re-run serially; the case-table column was stable
  throughout (this is the same load-sensitivity the round lesson records as E-1 for C3).
- **The 30 GAP survivors are the named coverage limits of C2.** The 37 cases are a closed public set
  (the lesson's N-C2a) and do not observe 30 distinct behaviour changes of the landed tool.
- No frozen file was edited. Every finding below is a finding for the L1 to route.

Survivor count: **67** = 35 equivalent + 30 gaps no leg observes + 2 gaps the counter's `real` leg observes.

## What was reused and what was redone

| part | source | disposition |
|---|---|---|
| mutant set M01–M64 | the inherited wave-2 seat `R42w2mutationtester01` (`census/round-42/waves/w2/R42w2mutationtester01/mutants/`, `manifest.tsv`) | **REUSED and RE-VERIFIED**: copied into this seat's scratch and re-scored from scratch with this seat's own runner; the kill/survive column reproduced exactly (39 / 0 / 25) |
| runner | `scripts/run.py` (this seat) | **REDONE**: written for this seat; reads the counter's case-table column and the mutant's own `--selftest` separately |
| mutant set W01–W72 | `scripts/mutants.py` (this seat) | **REDONE**: written from the landed bytes, independent of the inherited set. New anchors: the import block (lines 31–41), the git environment whitelist (62–65), `Repo.run`/`commit`/`blob`/`is_symlink` (67–88), `parse_claims` (97–112), `freeze_rev` (117–119), `dispatch_findings` (124–142), `check_path_sha` (153–172), `evaluate` (178–188). Where an anchor line was already attacked by M01–M64, a DIFFERENT defect on that line was used |
| survivor triage | `scripts/probe.py`, `probe2.py` … `probe7.py` (this seat) | **REDONE**: seven probe scripts, written for this seat, each building a synthetic git repo that exercises the mutated branch and diffing the pristine tool against the mutant (exit code + sorted FINDING lines) |
| M-survivor classification | the inherited seat's `scripts/classify.py` EVID map, committed at `census/round-42/waves/w2/R42w2mutationtester01/scripts/classify.py` | **REUSED** (transcribed verbatim into `logs/inherited-survivor-classification.tsv` with the committed log paths), and re-verified here by re-running each M mutant's scoring |
| the counter | `census/round-42/c2-counter.py` sha256 `fa44392d11338daa73b3b4b9b2fc8f89879c099e9bf278d7b45fa55dea5d0ac1` | **FROZEN, unmodified**; reached only through `census/round-42/score-candidate.sh` |

**A discrepancy the L1 must route.** The round lesson (`corpus/lessons/round-42.md`, "Wave 2 errata
and honest-stop record") records that the wave-2 mutation tester on the C2 tool
`R42w2mutationtester01` left **no report**. It did: `census/round-42/waves/w2/R42w2mutationtester01.md`
is committed (43 087 bytes, at `d39e3453`) and is byte-identical to
`.ufo/waves/round-42/w2/R42w2mutationtester01.md`. The report has the full 64-mutant table, a verdict,
and 13 named coverage limits. The lesson's sentence is wrong on the letter; the seat finished before
the operator's wrap-up (the seat directory's last write is 2026-10-28 22:57, the stop is ~23:35).
This seat therefore **re-issued the item** rather than repeating it, and its 64-mutant results were
re-derived from scratch and reproduced exactly. The lesson's text is a tracked file and was not edited
here.

## Method

1. **Axes.** The surface changed is the tool (C2 operability). The judged instruments are the frozen
   counter's **case table only** (the `cases=` / `pass=` / `fail=` tokens of the counter's `SUMMARY`
   line) and the mutant's **own `--selftest`** (run directly, `SELFTEST cases=31 pass=P fail=F`).
2. **Mutants.** `scripts/mutants.py` writes 72 mutants; each asserts its anchor occurs exactly once
   in the landed source and that the result differs from the source. `logs/diff-shape-both.txt` shows
   every one of the 136 mutants (M and W) differs in at most two hunks / six lines and none is
   identical to the pristine bytes.
3. **Scoring.** `scripts/run.py` runs, per mutant: the counter over the lane tip plus the mutant via
   `bash census/round-42/score-candidate.sh c2 <scratch> tools/souji-freeze-check.py=<mutant>`, and
   `python3 -B <mutant> --selftest`. The kill decision uses only the case-table column and the
   mutant's own self-test. The other counter legs (`real`, `retro`, `retro_clean`, `patches`) are
   recorded in `results.tsv` and `counter-summaries.txt`.
4. **Survivor triage.** Each survivor gets a directed probe (`scripts/probe.py`, `scripts/probe2.py`, … `scripts/probe7.py`): a synthetic git
   repo that exercises the mutated branch, run through the pristine tool and the mutant, comparing
   the exit code and the sorted FINDING lines. `DIFFER=True` → GAP; `DIFFER=False` → EQUIVALENT
   (with the reason recorded). Agreement on probed inputs is evidence, not a proof over all inputs.
5. **Re-verification.** `scripts/reverify.py` re-runs the counter and the self-test for every
   survivor **one at a time** on an idle host and compares against the batch verdict.

## Commands actually run and their output

All paths are absolute; every fixture lives under the seat scratch root, which was deleted at the end.

| # | command (abridged) | output (verbatim where short) | receipt |
|---|---|---|---|
| 1 | `sha256sum <lane>/tools/souji-freeze-check.py`; `git -C <lane> show 6a3f759…:tools/souji-freeze-check.py \| sha256sum` | both `9ddd596b98fbf41b67f98a389c488b1e84d2ef4a7b5fdb0c8711451a007acec6` | `logs/pristine-tool.sha256` |
| 2 | `git -C <lane> status --porcelain` (before and after) | no output (lane clean) | (this report) |
| 3 | `bash census/round-42/score-candidate.sh c2 <scratch>` (tip, no pairs) | `SUMMARY cases=37 pass=37 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red retro_clean=ok selftest=ok patches=3/3 tool_sha=9ddd596b98fb` | (this report) |
| 4 | `python3 -B scripts/mutants.py` | `mutants=72 out=/fast/scratch/hyaku/souji-r42/R42w3mutationtester01/mutants` | (this report) |
| 5 | `python3 -B scripts/run.py` (6 workers, 136 mutants, M and W together) | `TOTAL=136 killed_by_counter=65 killed_only_selftest=4 survivors=67` | `logs/results.tsv` |
| 6 | `python3 -B scripts/reverify.py` (67 survivors, 2 workers, one at a time) | `re-verified=67 agree=67 disagree=0` | `logs/reverify-out.txt` |
| 7 | `python3 -B scripts/probe.py` … `probe7.py` (the triage probes) | the DIFFER lines quoted in the table below | `logs/probe-out.txt`, `probe2-out.txt`, … `probe7-out.txt` |
| 8 | diff-shape check over all 136 mutants (difflib opcodes) | `inherited M: mutants=64 not_single_point=[] identical_to_pristine=[]` / `new W: mutants=72 not_single_point=[] identical_to_pristine=[]` | `logs/diff-shape-both.txt` |
| 9 | `python3 -B scripts/classify.py` | `total=136 killed_by_counter_cases=65 killed_only_selftest=4 survivors=67` / `survivor split: equivalent=35 gap=30 gap_lane_only=2` | `table.md` |
| 10 | the lane's own r42 preregistration at the tip, pristine and the lane-leg survivors | pristine `rc=0` no findings; M61/M62 `rc=1` with `FINDING C3 KEY-DUPLICATE Base \| … \| Target` (DIFFER=True); W61/W62/W63/W08/W13 `rc=0` (DIFFER=False) | `logs/lane-out.txt` |
| 11 | `python3 --version`; `git --version`; `command -v git` | Python 3.14.8; git version 2.56.0; `/usr/bin/git` | (this report) |

Tools: none installed or upgraded. Python 3.14.8, git 2.56.0 and `/usr/bin/git` were already on the
host; nothing was written to `~/.local/bin` or any PATH directory.

## Split by set

| set | mutants | killed by the counter's 37 cases | killed only by `--selftest` | survive both |
|---|---|---|---|---|
| M01–M64 (inherited, re-verified) | 64 | 39 | 0 | 25 |
| W01–W72 (new, this seat) | 72 | 26 | 4 (W03, W04, W05, W06) | 42 |
| **total** | **136** | **65** | **4** | **67** |

The M-set numbers reproduce the inherited report's `39 / 0 / 25` exactly (its `table.md`, row verdicts
and `logs/classify.txt`).

## The table (136 rows)

The full row-per-mutant table is `table.md` (same directory as this report): columns
`mutant | line / kind | change (old -> new) | counter cases pass/fail | --selftest | verdict | evidence / reason`.
The **counter cases** column is the frozen counter's own `SUMMARY cases=37 pass=N fail=M`, read from
a scoring run over the lane tip plus the mutant (`N/M` = the counter's `pass`/`fail`).
The **`--selftest`** column is the mutant's own self-test, written `pass/cases` (e.g. `31/31` means
`SELFTEST cases=31 pass=31 fail=0`); in `table.md` the same column is written in the long form
`cases=31 pass=31 fail=0`. The 30 GAP survivors are listed in "Named coverage limits" below with
their probes.

### Kill overlap (all 136 mutants)

| | killed by the counter's 37 cases | killed by the mutant's own `--selftest` |
|---|---|---|
| killed by **both** | 63 | 63 |
| killed by the counter's cases **only** | 2 (M31, M34) | — |
| killed by `--selftest` **only** | — | 4 (W03, W04, W05, W06) |
| **survives both** | 67 | 67 |
| **total** | 136 | 136 |

### W-set survivors (42) — the ones this seat found

| mutant | line / kind | change (old -> new) | counter cases | --selftest | verdict | probe evidence |
|---|---|---|---|---|---|---|
| W08 | L43 regex | `FULL40 = re.compile(r"^[0-9a-f]{40}$")` -> `re.compile(r"^\w{40}$")` | 37/0 | 31/31 | **GAP** | `logs/probe-out.txt`: upper-case Base hex resolves (pristine BASE-UNRESOLVED, mutant clean) |
| W11 | L46 regex | `):[ \t]*(.*?)[ \t]*$")` -> `): *(.*?)[ \t]*$")` | 37/0 | 31/31 | **GAP** | `logs/probe2-out.txt`: a TAB after the key colon makes the key line unread (pristine clean, mutant 4× FIELD-MISSING) |
| W12 | L47 regex | `sha256=([0-9a-f]{64})$")` -> `sha256=([0-9a-f]{32,64})$")` | 37/0 | 31/31 | **GAP** | `logs/probe2-out.txt`: a 32-hex digest is accepted (pristine COUNTER-DIGEST "no sha256", mutant a hash comparison) |
| W13 | L48 regex | `Round:[ \t]*(\d+)[ \t]*` -> `Round:[ \t]*(\d*)[ \t]*` | 37/0 | 31/31 | **GAP** | `logs/probe-out.txt`: `Round:` with no digits is accepted, so the dispatch tree becomes `.ufo/waves/round-/` (pristine FIELD-MISSING Round, mutant clean) |
| W14 | L49 regex | `^EXIT=(\d+)$` -> `^EXIT=(\d+)\s*$` | 37/0 | 31/31 | EQUIVALENT | the control lines are already stripped by `[x.strip() for x in …]` before the match (`logs/probe2-out.txt`) |
| W15 | L50 const | `KEYS = ("Base","Counter","Population","Control","Target","Kill")` -> reversed order | 37/0 | 31/31 | EQUIVALENT | `main()` sorts the FINDING lines before printing (`logs/probe2-out.txt`, `probe5-out.txt`) |
| W16 | L64 env | drop `"GIT_CONFIG_SYSTEM": os.devnull,` | 37/0 | 31/31 | EQUIVALENT | `GIT_CONFIG_NOSYSTEM=1` is still whitelisted, so the system config stays unread (`logs/probe-out.txt`) |
| W17 | L63 env | `"GIT_TERMINAL_PROMPT": "0"` -> `"1"` | 37/0 | 31/31 | EQUIVALENT | the tool runs no network command (`logs/probe2-out.txt`) |
| W18 | L62 env | `"LC_ALL": "C"` -> `"C.UTF-8"` | 37/0 | 31/31 | EQUIVALENT | a non-ASCII symlink path is detected identically (`logs/probe4-out.txt`) |
| W19 | L69 args | drop `"-c", "core.quotePath=false", ` | 37/0 | 31/31 | EQUIVALENT | quotePath affects only how git prints a path; `ls-tree`'s mode prefix (the only field read) is unchanged (`logs/probe4-out.txt`) |
| W21 | L70 env | `env=self.env, check=False)` -> `env=None, check=False)` | 37/0 | 31/31 | **GAP** | `logs/probe-out.txt`: a caller-set `GIT_DIR` redirects the tool to another repository (pristine rc=0, mutant rc=2) |
| W22 | L70 args | `stderr=subprocess.PIPE` -> `stderr=subprocess.DEVNULL` | 37/0 | 31/31 | EQUIVALENT | the tool reads git's stdout and returncode only (`logs/probe5-out.txt`) |
| W26 | L87 args | drop `"--full-tree",` from ls-tree | 37/0 | 31/31 | EQUIVALENT | only the `120000 ` mode prefix is read (`logs/probe5-out.txt`) |
| W28 | L97 index | `enumerate(text.splitlines(), 1)` -> `…, 0)` | 37/0 | 31/31 | **GAP** | `logs/probe2-out.txt`: the HEADING-MALFORMED line numbers shift by one (pristine line=11, mutant line=10) |
| W29 | L97 expr | `text.splitlines()` -> `text.split("\n")` | 37/0 | 31/31 | **GAP** | `logs/probe-out.txt`: a CRLF file keeps its CR, so five spurious findings appear |
| W30 | L102 cond | add `or line.startswith("###")` | 37/0 | 31/31 | **GAP** | `logs/probe2-out.txt`: a `### ` sub-heading closes the claim, so the keys after it are lost (pristine 4× FIELD-MISSING, mutant 5) |
| W32 | L117 args | drop `"--full-history",` | 37/0 | 31/31 | **GAP** | `logs/probe7-out.txt`: history simplification prunes the side branch, so the freeze moves to another commit (2 "A" commits vs 1) and the digest verdict changes (pristine FROZEN-EDITED, mutant COUNTER-DIGEST) |
| W33 | L117 args | drop `"--no-renames",` | 37/0 | 31/31 | EQUIVALENT | for a single-FILE pathspec git does not detect the rename, so the freeze log is byte-identical (`logs/probe7-out.txt`: both 2 commits). The only case where it differs is a DIRECTORY pathspec (`logs/probe6-out.txt`: 2 vs 1) and the tool refuses a directory before `freeze_rev` runs (rc=2) — an unreachable difference |
| W35 | L141 const | `base.endswith(("-spec.json","-results.json"))` -> adds `".json"` | 37/0 | 31/31 | **GAP** | `logs/probe2-out.txt`: every `.json` under the wave tree becomes a dispatch file (pristine clean, mutant DISPATCH-BEFORE-FREEZE) |
| W36 | L138 expr | `commit = line[1:].strip()` -> `…strip()[:12]` | 37/0 | 31/31 | EQUIVALENT | the detail already prints `c[:12]` and the ancestry test accepts an abbreviated id (`logs/probe2-out.txt`) |
| W37 | L154 expr | `(value.split()[0] …, None)` -> `("", None)` | 37/0 | 31/31 | **GAP** | `logs/probe-out.txt`: a Counter value with no sha256 is not checked at all (pristine COUNTER-DIGEST, mutant clean) |
| W38 | L155 branch | delete `if not path: return None` | 37/0 | 31/31 | EQUIVALENT | the branch is unreachable: a whitespace-only Counter value is already an empty value, caught by KEYLINE's strip (`logs/probe5-out.txt`) |
| W40 | L158 cond | `if at_freeze is None:` -> `if at_freeze is None or not at_freeze:` | 37/0 | 31/31 | **GAP** | `logs/probe4-out.txt`: an EMPTY blob at the freeze counts as missing (pristine clean, mutant COUNTER-MISSING) |
| W41 | L161 call | `repo.is_symlink(freeze, path)` -> `repo.is_symlink(rev, path)` | 37/0 | 31/31 | **GAP** | `logs/probe-out.txt`: the symlink test runs at REV, not FREEZE (pristine COUNTER-SYMLINK, mutant COUNTER-DIGEST + FROZEN-EDITED) |
| W45 | L178 expr | `parse_claims(text)` -> `parse_claims(text.replace('\r\n','\n'))` | 37/0 | 31/31 | EQUIVALENT | `splitlines()` already splits on `\r\n` and KEYLINE's trailing `[ \t]*$` strips the CR (`logs/probe5-out.txt`) |
| W46 | L179 expr | `for n in bad)` -> `for n in bad[:1])` | 37/0 | 31/31 | **GAP** | `logs/probe-out.txt`: only the FIRST malformed heading is reported (pristine line=11 and line=12, mutant line=11) |
| W49 | L183 order | `sorted(dups)` -> `sorted(dups, reverse=True)` | 37/0 | 31/31 | EQUIVALENT | `main()` sorts the FINDING lines before printing (`logs/probe5-out.txt`) |
| W53 | L53 class | `class Refusal(Exception):` -> `class Refusal(BaseException):` | 37/0 | 31/31 | EQUIVALENT | the tool catches `except Refusal` explicitly, so the base class does not matter (`logs/probe5-out.txt`) |
| W54 | L59 expr | `self.root = root` -> `self.root = root + '/.'` | 37/0 | 31/31 | EQUIVALENT | `git -C` accepts it and the root path is never printed in a finding (`logs/probe5-out.txt`) |
| W55 | L62 env | `os.environ.get("PATH", …)` -> `"/usr/bin:/bin"` | 37/0 | 31/31 | EQUIVALENT | on this host git IS `/usr/bin/git`, so both tools find it; with git reachable only from a non-standard directory both still agree (`logs/probe6-out.txt`) |
| W56 | L76 args | drop `"-q",` from rev-parse | 37/0 | 31/31 | EQUIVALENT | `-q` only suppresses git's error text on stderr; stdout and the return code are the same (`logs/probe5-out.txt`) |
| W57 | L87 args | drop `"--",` from ls-tree | 37/0 | 31/31 | **GAP** | `logs/probe4-out.txt`, `probe6-out.txt`: a path that starts with `-` is taken as an option (pristine COUNTER-SYMLINK, mutant COUNTER-DIGEST) |
| W58 | L98 call | `HEADER.match(line)` -> `HEADER.search(line)` | 37/0 | 31/31 | EQUIVALENT | the pattern is anchored with `^`, so search and match agree on a line (`logs/probe5-out.txt`) |
| W59 | L104 cond | `BADHEAD.match(line)` -> `BADHEAD.search(line)` | 37/0 | 31/31 | EQUIVALENT | the pattern is anchored with `^` (`logs/probe5-out.txt`) |
| W62 | L119 expr | drop `if FULL40.match(x)` from the freeze-id filter | 37/0 | 31/31 | EQUIVALENT | `git log --format=%H` prints full 40-hex ids only (`logs/probe5-out.txt`) |
| W63 | L136 expr | `splitlines()` -> `split("\n")` on the dispatch log | 37/0 | 31/31 | EQUIVALENT | git's `--name-only` output has no other line terminator (`logs/probe5-out.txt`) |
| W64 | L139 cond | `elif line and commit:` -> `elif line:` | 37/0 | 31/31 | EQUIVALENT | git always prints the `%x01%H` header before that commit's names (`logs/probe5-out.txt`) |
| W66 | L153 cond | `PATH_SHA.match(value)` -> `PATH_SHA.match(value.strip())` | 37/0 | 31/31 | EQUIVALENT | the value comes from KEYLINE, which already stripped it (`logs/probe5-out.txt`) |
| W67 | L159 class | `found.append((label, missing, …))` -> `missing.upper()` | 37/0 | 31/31 | EQUIVALENT | the class names are already upper case (`logs/probe5-out.txt`) |
| W68 | L166 cond | `!= want:` -> `!= want.lower():` | 37/0 | 31/31 | EQUIVALENT | PATH_SHA's group is `[0-9a-f]{64}`, already lower case (`logs/probe5-out.txt`) |
| W70 | L181 detail | the NO-CLAIMS detail text changes | 37/0 | 31/31 | **GAP** | `logs/probe2-out.txt`: the class is unchanged but the printed finding differs |
| W71 | L183 class | `key` -> `key.upper()` in the KEY-DUPLICATE finding | 37/0 | 31/31 | **GAP** | `logs/probe2-out.txt`: `KEY-DUPLICATE TARGET` instead of `KEY-DUPLICATE Target` |

### W-set mutants killed by the counter's 37 cases (26), and the four killed only by `--selftest`

Killed by the counter's 37 cases (26): W01 W02 W07 W09 W10 W20 W23 W24 W25 W27 W31 W34 W39 W42 W43
W44 W47 W48 W50 W51 W52 W60 W61 W65 W69 W72.
(The failing counter case is named per row in `table.md`.)

| mutant | line / kind | change (old -> new) | counter cases pass/fail | --selftest | verdict | failing counter case(s) |
|---|---|---|---|---|---|---|
| W01 | L33 import | `import hashlib\n` -> `` | 3/34 | cases=cases=31 pass=pass=3 fail=fail=28 | killed by counter cases | clean,clean-dispatch-after,field-missing-base,field-missing-counter,field-empty-target,base-unresolved,base-not-ancestor,counter-missing,counter-digest,population-missing,population-digest,population-empty,control-missing,control-not-red,frozen-edited-counter,frozen-edited-population,dispatch-before-freeze,two-claims-one-bad,dup-base-differs,dup-counter-identical,dup-target,heading-nospace,heading-lowercase,heading-spaced-digit,heading-suffix,heading-valid-tail,dispatch-spec-before,dispatch-attempts-before,dispatch-dispatched-before,dispatch-results-before,dispatch-names-after,dispatch-notes-before,counter-symlink,population-symlink |
| W02 | L36 import | `import posixpath\n` -> `` | 3/34 | cases=cases=31 pass=pass=3 fail=fail=28 | killed by counter cases | clean,clean-dispatch-after,field-missing-base,field-missing-counter,field-empty-target,base-unresolved,base-not-ancestor,counter-missing,counter-digest,population-missing,population-digest,population-empty,control-missing,control-not-red,frozen-edited-counter,frozen-edited-population,dispatch-before-freeze,two-claims-one-bad,dup-base-differs,dup-counter-identical,dup-target,heading-nospace,heading-lowercase,heading-spaced-digit,heading-suffix,heading-valid-tail,dispatch-spec-before,dispatch-attempts-before,dispatch-dispatched-before,dispatch-results-before,dispatch-names-after,dispatch-notes-before,counter-symlink,population-symlink |
| W07 | L31 import | `import argparse\n` -> `` | 0/37 | (none) | killed by counter cases | clean,clean-dispatch-after,no-claims,field-missing-base,field-missing-counter,field-empty-target,base-unresolved,base-not-ancestor,counter-missing,counter-digest,population-missing,population-digest,population-empty,control-missing,control-not-red,frozen-edited-counter,frozen-edited-population,dispatch-before-freeze,two-claims-one-bad,dup-base-differs,dup-counter-identical,dup-target,heading-nospace,heading-lowercase,heading-spaced-digit,heading-suffix,heading-valid-tail,dispatch-spec-before,dispatch-attempts-before,dispatch-dispatched-before,dispatch-results-before,dispatch-names-after,dispatch-notes-before,counter-symlink,population-symlink,unresolved-rev,absent-prereg |
| W09 | L44 regex | `HEADER = re.compile(r"^## C(\d+)(?: \|$)")` -> `HEADER = re.compile(r"^## C(\d+)(?:  \|$)")` | 3/34 | cases=cases=31 pass=pass=30 fail=fail=1 | killed by counter cases | clean,clean-dispatch-after,field-missing-base,field-missing-counter,field-empty-target,base-unresolved,base-not-ancestor,counter-missing,counter-digest,population-missing,population-digest,population-empty,control-missing,control-not-red,frozen-edited-counter,frozen-edited-population,dispatch-before-freeze,two-claims-one-bad,dup-base-differs,dup-counter-identical,dup-target,heading-nospace,heading-lowercase,heading-spaced-digit,heading-suffix,heading-valid-tail,dispatch-spec-before,dispatch-attempts-before,dispatch-dispatched-before,dispatch-results-before,dispatch-names-after,dispatch-notes-before,counter-symlink,population-symlink |
| W10 | L45 regex | `BADHEAD = re.compile(r"^##(?!#) *[Cc] *\d")` -> `BADHEAD = re.compile(r"^##(?!#) *[Cc]?\d")` | 36/1 | cases=cases=31 pass=pass=30 fail=fail=1 | killed by counter cases | heading-spaced-digit |
| W20 | L70 branch | `check=False)` -> `check=True)` | 28/9 | cases=cases=31 pass=pass=23 fail=fail=8 | killed by counter cases | clean-dispatch-after,base-unresolved,base-not-ancestor,counter-missing,population-missing,control-missing,dispatch-names-after,unresolved-rev,absent-prereg |
| W23 | L76 args | `rev + "^{commit}"` -> `rev` | 36/1 | cases=cases=31 pass=pass=30 fail=fail=1 | killed by counter cases | base-unresolved |
| W24 | L77 expr | `out = p.stdout.decode("utf-8", "replace").strip()` -> `out = p.stdout.decode("utf-8", "replace")` | 2/35 | cases=cases=31 pass=pass=2 fail=fail=29 | killed by counter cases | clean,clean-dispatch-after,no-claims,field-missing-base,field-missing-counter,field-empty-target,base-unresolved,base-not-ancestor,counter-missing,counter-digest,population-missing,population-digest,population-empty,control-missing,control-not-red,frozen-edited-counter,frozen-edited-population,dispatch-before-freeze,two-claims-one-bad,dup-base-differs,dup-counter-identical,dup-target,heading-nospace,heading-lowercase,heading-spaced-digit,heading-suffix,heading-valid-tail,dispatch-spec-before,dispatch-attempts-before,dispatch-dispatched-before,dispatch-results-before,dispatch-names-after,dispatch-notes-before,counter-symlink,population-symlink |
| W25 | L84 branch | `return p.stdout if p.returncode == 0 else None` -> `return p.stdout` | 34/3 | cases=cases=31 pass=pass=28 fail=fail=3 | killed by counter cases | counter-missing,population-missing,control-missing |
| W27 | L91 branch | `return self.run("merge-base", "--is-ancestor", a, b).returncode == 0` -> `return self.run("merge-base", "--is-ancestor", a, b).returncode in (0, 1)` | 34/3 | cases=cases=31 pass=pass=29 fail=fail=2 | killed by counter cases | clean-dispatch-after,base-not-ancestor,dispatch-names-after |
| W31 | L109 cond | `if m.group(1) in cur[1]:` -> `if m.group(1) in cur[1] and cur[1][m.group(1)] != m.group(2):` | 36/1 | cases=cases=31 pass=pass=31 fail=fail=0 | killed by counter cases | dup-counter-identical |
| W34 | L124 call | `m = ROUND.search(text)` -> `m = ROUND.match(text)` | 2/35 | cases=cases=31 pass=pass=31 fail=fail=0 | killed by counter cases | clean,clean-dispatch-after,no-claims,field-missing-base,field-missing-counter,field-empty-target,base-unresolved,base-not-ancestor,counter-missing,counter-digest,population-missing,population-digest,population-empty,control-missing,control-not-red,frozen-edited-counter,frozen-edited-population,dispatch-before-freeze,two-claims-one-bad,dup-base-differs,dup-counter-identical,dup-target,heading-nospace,heading-lowercase,heading-spaced-digit,heading-suffix,heading-valid-tail,dispatch-spec-before,dispatch-attempts-before,dispatch-dispatched-before,dispatch-results-before,dispatch-names-after,dispatch-notes-before,counter-symlink,population-symlink |
| W39 | L157 call | `at_freeze = repo.blob(freeze, path)` -> `at_freeze = repo.blob(rev, path)` | 35/2 | cases=cases=31 pass=pass=30 fail=fail=1 | killed by counter cases | frozen-edited-counter,frozen-edited-population |
| W42 | L162 class | `key.upper() + "-SYMLINK"` -> `key.lower() + "-SYMLINK"` | 35/2 | cases=cases=31 pass=pass=29 fail=fail=2 | killed by counter cases | counter-symlink,population-symlink |
| W43 | L170 branch | `if at_rev != at_freeze:` -> `if at_rev is not at_freeze:` | 3/34 | cases=cases=31 pass=pass=3 fail=fail=28 | killed by counter cases | clean,clean-dispatch-after,field-missing-base,field-missing-counter,field-empty-target,base-unresolved,base-not-ancestor,counter-missing,counter-digest,population-missing,population-digest,population-empty,control-missing,control-not-red,frozen-edited-counter,frozen-edited-population,dispatch-before-freeze,two-claims-one-bad,dup-base-differs,dup-counter-identical,dup-target,heading-nospace,heading-lowercase,heading-spaced-digit,heading-suffix,heading-valid-tail,dispatch-spec-before,dispatch-attempts-before,dispatch-dispatched-before,dispatch-results-before,dispatch-names-after,dispatch-notes-before,counter-symlink,population-symlink |
| W44 | L171 class | `FROZEN-EDITED, "%s differs between freeze %s and %s"` -> `FROZEN-EDITED-X, "%s differs between freeze %s and %s"` | 35/2 | cases=cases=31 pass=pass=30 fail=fail=1 | killed by counter cases | frozen-edited-counter,frozen-edited-population |
| W47 | L180 cond | `if not claims:` -> `if not claims and bad:` | 36/1 | cases=cases=31 pass=pass=30 fail=fail=1 | killed by counter cases | no-claims |
| W48 | L182 expr | `for label, f, dups in claims:` -> `for label, f, dups in claims[:1]:` | 35/2 | cases=cases=31 pass=pass=30 fail=fail=1 | killed by counter cases | two-claims-one-bad,heading-valid-tail |
| W50 | L184 loop | `        for key in KEYS:\n            if key not in f:` -> `        for key in KEYS[:-1]:\n            if key not in f:` | 35/2 | cases=cases=31 pass=pass=29 fail=fail=2 | killed by counter cases | two-claims-one-bad,heading-valid-tail |
| W51 | L186 class | `found.append((label, "FIELD-MISSING", key))` -> `found.append((label, "FIELD-ABSENT", key))` | 33/4 | cases=cases=31 pass=pass=29 fail=fail=2 | killed by counter cases | field-missing-base,field-missing-counter,two-claims-one-bad,heading-valid-tail |
| W52 | L146 class | `DISPATCH-BEFORE-FREEZE, "%s first added at %s, not after freeze %s"` -> `DISPATCH-BEFORE-FREEZE-X, "%s first added at %s, not after freeze %s"` | 32/5 | cases=cases=31 pass=pass=27 fail=fail=4 | killed by counter cases | dispatch-before-freeze,dispatch-spec-before,dispatch-attempts-before,dispatch-dispatched-before,dispatch-results-before |
| W60 | L110 stmt | `cur[2].add(m.group(1))` -> `cur[2].add(m.group(1).lower())` | 34/3 | cases=cases=31 pass=pass=30 fail=fail=1 | killed by counter cases | dup-base-differs,dup-counter-identical,dup-target |
| W61 | L112 expr | `cur[1][m.group(1)] = m.group(2)` -> `cur[1][m.group(1)] = m.group(2) or 'x'` | 36/1 | cases=cases=31 pass=pass=30 fail=fail=1 | killed by counter cases | field-empty-target |
| W65 | L150 stmt | `    out = []\n` -> `` | 2/35 | cases=cases=31 pass=pass=2 fail=fail=29 | killed by counter cases | clean,clean-dispatch-after,no-claims,field-missing-base,field-missing-counter,field-empty-target,base-unresolved,base-not-ancestor,counter-missing,counter-digest,population-missing,population-digest,population-empty,control-missing,control-not-red,frozen-edited-counter,frozen-edited-population,dispatch-before-freeze,two-claims-one-bad,dup-base-differs,dup-counter-identical,dup-target,heading-nospace,heading-lowercase,heading-spaced-digit,heading-suffix,heading-valid-tail,dispatch-spec-before,dispatch-attempts-before,dispatch-dispatched-before,dispatch-results-before,dispatch-names-after,dispatch-notes-before,counter-symlink,population-symlink |
| W69 | L169 call | `at_rev = repo.blob(rev, path)` -> `at_rev = repo.blob(rev, path + '.orig')` | 3/34 | cases=cases=31 pass=pass=3 fail=fail=28 | killed by counter cases | clean,clean-dispatch-after,field-missing-base,field-missing-counter,field-empty-target,base-unresolved,base-not-ancestor,counter-missing,counter-digest,population-missing,population-digest,population-empty,control-missing,control-not-red,frozen-edited-counter,frozen-edited-population,dispatch-before-freeze,two-claims-one-bad,dup-base-differs,dup-counter-identical,dup-target,heading-nospace,heading-lowercase,heading-spaced-digit,heading-suffix,heading-valid-tail,dispatch-spec-before,dispatch-attempts-before,dispatch-dispatched-before,dispatch-results-before,dispatch-names-after,dispatch-notes-before,counter-symlink,population-symlink |
| W72 | L185 cond | `if key not in f:` -> `if key not in f and key != 'Kill':` | 35/2 | cases=cases=31 pass=pass=29 fail=fail=2 | killed by counter cases | two-claims-one-bad,heading-valid-tail |

Killed only by `--selftest` (4) — the counter's case table passes all 37 and the mutant's own
self-test fails. The counter's case table reaches only the tool's normal path, which never uses
these four imports; the self-test harness does, so it is the only instrument that sees them:

| mutant | line / kind | change | counter cases | `--selftest` (own run) |
|---|---|---|---|---|
| W03 | L41 import | delete `import tempfile` | 37/0 | no `SELFTEST` line; rc=1, `NameError: name 'tempfile' is not defined` (the tool crashes before the self-test can run) |
| W04 | L38 import | delete `import shutil` | 37/0 | no `SELFTEST` line; rc=1, `NameError: name 'shutil' is not defined` (crash at import) |
| W05 | L34 import | delete `import io` | 37/0 | `cases=31 pass=0 fail=31` (rc=1) |
| W06 | L32 import | delete `import contextlib` | 37/0 | `cases=31 pass=0 fail=31` (rc=1) |

(Killed by both instruments: 63 mutants. Killed by the counter's case table only: 2 — M31 and M34.
See `table.md` for every row.)

### M-set mutants killed by the counter's 37 cases (39)

| mutant | line / kind | change (old -> new) | counter cases pass/fail | --selftest | verdict | failing counter case(s) |
|---|---|---|---|---|---|---|
| M01 | L43 const | `FULL40 = re.compile(r"^[0-9a-f]{40}$")` -> `FULL40 = re.compile(r"^[0-9a-f]{39}$")` | 2/35 | cases=cases=31 pass=pass=2 fail=fail=29 | killed by counter cases | clean,clean-dispatch-after,no-claims,field-missing-base,field-missing-counter,field-empty-target,base-unresolved,base-not-ancestor,counter-missing,counter-digest,population-missing,population-digest,population-empty,control-missing,control-not-red,frozen-edited-counter,frozen-edited-population,dispatch-before-freeze,two-claims-one-bad,dup-base-differs,dup-counter-identical,dup-target,heading-nospace,heading-lowercase,heading-spaced-digit,heading-suffix,heading-valid-tail,dispatch-spec-before,dispatch-attempts-before,dispatch-dispatched-before,dispatch-results-before,dispatch-names-after,dispatch-notes-before,counter-symlink,population-symlink |
| M04 | L44 regex | `HEADER = re.compile(r"^## C(\d+)(?: \|$)")` -> `HEADER = re.compile(r"^## C(\d+)")` | 36/1 | cases=cases=31 pass=pass=30 fail=fail=1 | killed by counter cases | heading-suffix |
| M05 | L44 regex | `HEADER = re.compile(r"^## C(\d+)(?: \|$)")` -> `HEADER = re.compile(r"^##  C(\d+)(?: \|$)")` | 3/34 | cases=cases=31 pass=pass=3 fail=fail=28 | killed by counter cases | clean,clean-dispatch-after,field-missing-base,field-missing-counter,field-empty-target,base-unresolved,base-not-ancestor,counter-missing,counter-digest,population-missing,population-digest,population-empty,control-missing,control-not-red,frozen-edited-counter,frozen-edited-population,dispatch-before-freeze,two-claims-one-bad,dup-base-differs,dup-counter-identical,dup-target,heading-nospace,heading-lowercase,heading-spaced-digit,heading-suffix,heading-valid-tail,dispatch-spec-before,dispatch-attempts-before,dispatch-dispatched-before,dispatch-results-before,dispatch-names-after,dispatch-notes-before,counter-symlink,population-symlink |
| M06 | L45 regex | `BADHEAD = re.compile(r"^##(?!#) *[Cc] *\d")` -> `BADHEAD = re.compile(r"^##(?!#) *[C] *\d")` | 36/1 | cases=cases=31 pass=pass=30 fail=fail=1 | killed by counter cases | heading-lowercase |
| M07 | L45 regex | `BADHEAD = re.compile(r"^##(?!#) *[Cc] *\d")` -> `BADHEAD = re.compile(r"^##(?!#) *[Cc] +\d")` | 34/3 | cases=cases=31 pass=pass=28 fail=fail=3 | killed by counter cases | heading-nospace,heading-lowercase,heading-suffix |
| M08 | L46 regex | `KEYLINE = re.compile(r"^(Base\|Counter\|Population\|Control\|Target\|Kill):[ \t]*(.*?)[ \t]*$")` -> `KEYLINE = re.compile(r"^(Base\|Counter\|Population\|Control\|Target):[ \t]*(.*?)[ \t]*$")` | 3/34 | cases=cases=31 pass=pass=4 fail=fail=27 | killed by counter cases | clean,clean-dispatch-after,field-missing-base,field-missing-counter,field-empty-target,base-unresolved,base-not-ancestor,counter-missing,counter-digest,population-missing,population-digest,population-empty,control-missing,control-not-red,frozen-edited-counter,frozen-edited-population,dispatch-before-freeze,two-claims-one-bad,dup-base-differs,dup-counter-identical,dup-target,heading-nospace,heading-lowercase,heading-spaced-digit,heading-suffix,heading-valid-tail,dispatch-spec-before,dispatch-attempts-before,dispatch-dispatched-before,dispatch-results-before,dispatch-names-after,dispatch-notes-before,counter-symlink,population-symlink |
| M10 | L47 regex | `PATH_SHA = re.compile(r"^(.+?)[ \t]+sha256=([0-9a-f]{64})$")` -> `PATH_SHA = re.compile(r"^(.+?)[ \t]+sha256=([0-9a-f]{63})$")` | 3/34 | cases=cases=31 pass=pass=3 fail=fail=28 | killed by counter cases | clean,clean-dispatch-after,field-missing-base,field-missing-counter,field-empty-target,base-unresolved,base-not-ancestor,counter-missing,counter-digest,population-missing,population-digest,population-empty,control-missing,control-not-red,frozen-edited-counter,frozen-edited-population,dispatch-before-freeze,two-claims-one-bad,dup-base-differs,dup-counter-identical,dup-target,heading-nospace,heading-lowercase,heading-spaced-digit,heading-suffix,heading-valid-tail,dispatch-spec-before,dispatch-attempts-before,dispatch-dispatched-before,dispatch-results-before,dispatch-names-after,dispatch-notes-before,counter-symlink,population-symlink |
| M11 | L47 regex | `PATH_SHA = re.compile(r"^(.+?)[ \t]+sha256=([0-9a-f]{64})$")` -> `PATH_SHA = re.compile(r"^(.+?)[ \t]+sha256:([0-9a-f]{64})$")` | 3/34 | cases=cases=31 pass=pass=3 fail=fail=28 | killed by counter cases | clean,clean-dispatch-after,field-missing-base,field-missing-counter,field-empty-target,base-unresolved,base-not-ancestor,counter-missing,counter-digest,population-missing,population-digest,population-empty,control-missing,control-not-red,frozen-edited-counter,frozen-edited-population,dispatch-before-freeze,two-claims-one-bad,dup-base-differs,dup-counter-identical,dup-target,heading-nospace,heading-lowercase,heading-spaced-digit,heading-suffix,heading-valid-tail,dispatch-spec-before,dispatch-attempts-before,dispatch-dispatched-before,dispatch-results-before,dispatch-names-after,dispatch-notes-before,counter-symlink,population-symlink |
| M12 | L48 regex | `ROUND = re.compile(r"^\ufeff?Round:[ \t]*(\d+)[ \t]*\r?$", re.M)` -> `ROUND = re.compile(r"^\ufeff?Round:[ \t]*(\d+)[ \t]*\r?$")` | 2/35 | cases=cases=31 pass=pass=3 fail=fail=28 | killed by counter cases | clean,clean-dispatch-after,no-claims,field-missing-base,field-missing-counter,field-empty-target,base-unresolved,base-not-ancestor,counter-missing,counter-digest,population-missing,population-digest,population-empty,control-missing,control-not-red,frozen-edited-counter,frozen-edited-population,dispatch-before-freeze,two-claims-one-bad,dup-base-differs,dup-counter-identical,dup-target,heading-nospace,heading-lowercase,heading-spaced-digit,heading-suffix,heading-valid-tail,dispatch-spec-before,dispatch-attempts-before,dispatch-dispatched-before,dispatch-results-before,dispatch-names-after,dispatch-notes-before,counter-symlink,population-symlink |
| M16 | L50 const | `KEYS = ("Base", "Counter", "Population", "Control", "Target", "Kill")` -> `KEYS = ("Base", "Counter", "Population", "Control", "Target")` | 35/2 | cases=cases=31 pass=pass=29 fail=fail=2 | killed by counter cases | two-claims-one-bad,heading-valid-tail |
| M17 | L50 const | `KEYS = ("Base", "Counter", "Population", "Control", "Target", "Kill")` -> `KEYS = ("Base", "Counter", "Population", "Control", "Kill")` | 35/2 | cases=cases=31 pass=pass=29 fail=fail=2 | killed by counter cases | field-empty-target,heading-valid-tail |
| M23 | L88 const | `p.stdout.startswith(b"120000 ")` -> `p.stdout.startswith(b"100644 ")` | 3/34 | cases=cases=31 pass=pass=3 fail=fail=28 | killed by counter cases | clean,clean-dispatch-after,field-missing-base,field-missing-counter,field-empty-target,base-unresolved,base-not-ancestor,counter-missing,counter-digest,population-missing,population-digest,population-empty,control-missing,control-not-red,frozen-edited-counter,frozen-edited-population,dispatch-before-freeze,two-claims-one-bad,dup-base-differs,dup-counter-identical,dup-target,heading-nospace,heading-lowercase,heading-spaced-digit,heading-suffix,heading-valid-tail,dispatch-spec-before,dispatch-attempts-before,dispatch-dispatched-before,dispatch-results-before,dispatch-names-after,dispatch-notes-before,counter-symlink,population-symlink |
| M25 | L91 branch | `return self.run("merge-base", "--is-ancestor", a, b).returncode == 0` -> `return self.run("merge-base", "--is-ancestor", a, b).returncode != 0` | 6/31 | cases=cases=31 pass=pass=4 fail=fail=27 | killed by counter cases | clean,clean-dispatch-after,field-missing-counter,field-empty-target,base-not-ancestor,counter-missing,counter-digest,population-missing,population-digest,population-empty,control-missing,control-not-red,frozen-edited-counter,frozen-edited-population,dispatch-before-freeze,two-claims-one-bad,dup-counter-identical,dup-target,heading-nospace,heading-lowercase,heading-spaced-digit,heading-suffix,heading-valid-tail,dispatch-spec-before,dispatch-attempts-before,dispatch-dispatched-before,dispatch-results-before,dispatch-names-after,dispatch-notes-before,counter-symlink,population-symlink |
| M26 | L91 args | `self.run("merge-base", "--is-ancestor", a, b)` -> `self.run("merge-base", "--is-ancestor", b, a)` | 7/30 | cases=cases=31 pass=pass=5 fail=fail=26 | killed by counter cases | clean,clean-dispatch-after,field-missing-counter,field-empty-target,counter-missing,counter-digest,population-missing,population-digest,population-empty,control-missing,control-not-red,frozen-edited-counter,frozen-edited-population,dispatch-before-freeze,two-claims-one-bad,dup-counter-identical,dup-target,heading-nospace,heading-lowercase,heading-spaced-digit,heading-suffix,heading-valid-tail,dispatch-spec-before,dispatch-attempts-before,dispatch-dispatched-before,dispatch-results-before,dispatch-names-after,dispatch-notes-before,counter-symlink,population-symlink |
| M27 | L117 args | `--format=%H, rev, "--", prereg)` -> `--format=%h, rev, "--", prereg)` | 2/35 | cases=cases=31 pass=pass=2 fail=fail=29 | killed by counter cases | clean,clean-dispatch-after,no-claims,field-missing-base,field-missing-counter,field-empty-target,base-unresolved,base-not-ancestor,counter-missing,counter-digest,population-missing,population-digest,population-empty,control-missing,control-not-red,frozen-edited-counter,frozen-edited-population,dispatch-before-freeze,two-claims-one-bad,dup-base-differs,dup-counter-identical,dup-target,heading-nospace,heading-lowercase,heading-spaced-digit,heading-suffix,heading-valid-tail,dispatch-spec-before,dispatch-attempts-before,dispatch-dispatched-before,dispatch-results-before,dispatch-names-after,dispatch-notes-before,counter-symlink,population-symlink |
| M32 | L129 path | `tree = ".ufo/waves/round-%s/" % m.group(1)` -> `tree = ".ufo/waves/round-%s/w1" % m.group(1)` | 32/5 | cases=cases=31 pass=pass=27 fail=fail=4 | killed by counter cases | dispatch-before-freeze,dispatch-spec-before,dispatch-attempts-before,dispatch-dispatched-before,dispatch-results-before |
| M33 | L140 expr | `base = line.rsplit("/", 1)[-1]` -> `base = line.split("/")[0]` | 32/5 | cases=cases=31 pass=pass=27 fail=fail=4 | killed by counter cases | dispatch-before-freeze,dispatch-spec-before,dispatch-attempts-before,dispatch-dispatched-before,dispatch-results-before |
| M34 | L141 cond | `if "-dispatch" in base or ".ready" in base or base.endswith(("-spec.json", "-results.json")):` -> `if ".ready" in base or base.endswith(("-spec.json", "-results.json")):` | 35/2 | cases=cases=31 pass=pass=30 fail=fail=1 | killed by counter cases | dispatch-before-freeze,dispatch-attempts-before |
| M35 | L141 const | `.ready in base` -> `.readyx in base` | 36/1 | cases=cases=31 pass=pass=30 fail=fail=1 | killed by counter cases | dispatch-dispatched-before |
| M36 | L141 const | `base.endswith(("-spec.json", "-results.json"))` -> `base.endswith(("-spec.json",))` | 36/1 | cases=cases=31 pass=pass=30 fail=fail=1 | killed by counter cases | dispatch-results-before |
| M37 | L145 cond | `if c == freeze or repo.is_ancestor(c, freeze):` -> `if c == freeze:` | 32/5 | cases=cases=31 pass=pass=27 fail=fail=4 | killed by counter cases | dispatch-before-freeze,dispatch-spec-before,dispatch-attempts-before,dispatch-dispatched-before,dispatch-results-before |
| M38 | L145 args | `repo.is_ancestor(c, freeze)` -> `repo.is_ancestor(freeze, c)` | 30/7 | cases=cases=31 pass=pass=26 fail=fail=5 | killed by counter cases | clean-dispatch-after,dispatch-before-freeze,dispatch-spec-before,dispatch-attempts-before,dispatch-dispatched-before,dispatch-results-before,dispatch-names-after |
| M42 | L154 expr | `path, want = (m.group(1), m.group(2)) if m else (value.split()[0] if value.split() else "", None)` -> `path, want = (m.group(2), m.group(1)) if m else (value.split()[0] if value.split() else "", None)` | 3/34 | cases=cases=31 pass=pass=3 fail=fail=28 | killed by counter cases | clean,clean-dispatch-after,field-missing-base,field-missing-counter,field-empty-target,base-unresolved,base-not-ancestor,counter-missing,counter-digest,population-missing,population-digest,population-empty,control-missing,control-not-red,frozen-edited-counter,frozen-edited-population,dispatch-before-freeze,two-claims-one-bad,dup-base-differs,dup-counter-identical,dup-target,heading-nospace,heading-lowercase,heading-spaced-digit,heading-suffix,heading-valid-tail,dispatch-spec-before,dispatch-attempts-before,dispatch-dispatched-before,dispatch-results-before,dispatch-names-after,dispatch-notes-before,counter-symlink,population-symlink |
| M44 | L159 class | `found.append((label, missing, "%s not present at freeze %s"` -> `found.append((label, digest, "%s not present at freeze %s"` | 35/2 | cases=cases=31 pass=pass=29 fail=fail=2 | killed by counter cases | counter-missing,population-missing |
| M45 | L161 cond | `if repo.is_symlink(freeze, path):` -> `if False:` | 35/2 | cases=cases=31 pass=pass=29 fail=fail=2 | killed by counter cases | counter-symlink,population-symlink |
| M46 | L162 class | `key.upper() + "-SYMLINK"` -> `key.upper() + "-SYMLINKS"` | 35/2 | cases=cases=31 pass=pass=29 fail=fail=2 | killed by counter cases | counter-symlink,population-symlink |
| M47 | L164 cond | `if want is None:` -> `if True:` | 3/34 | cases=cases=31 pass=pass=3 fail=fail=28 | killed by counter cases | clean,clean-dispatch-after,field-missing-base,field-missing-counter,field-empty-target,base-unresolved,base-not-ancestor,counter-missing,counter-digest,population-missing,population-digest,population-empty,control-missing,control-not-red,frozen-edited-counter,frozen-edited-population,dispatch-before-freeze,two-claims-one-bad,dup-base-differs,dup-counter-identical,dup-target,heading-nospace,heading-lowercase,heading-spaced-digit,heading-suffix,heading-valid-tail,dispatch-spec-before,dispatch-attempts-before,dispatch-dispatched-before,dispatch-results-before,dispatch-names-after,dispatch-notes-before,counter-symlink,population-symlink |
| M48 | L166 branch | `elif hashlib.sha256(at_freeze).hexdigest() != want:` -> `elif hashlib.sha256(at_freeze).hexdigest() == want:` | 3/34 | cases=cases=31 pass=pass=3 fail=fail=28 | killed by counter cases | clean,clean-dispatch-after,field-missing-base,field-missing-counter,field-empty-target,base-unresolved,base-not-ancestor,counter-missing,counter-digest,population-missing,population-digest,population-empty,control-missing,control-not-red,frozen-edited-counter,frozen-edited-population,dispatch-before-freeze,two-claims-one-bad,dup-base-differs,dup-counter-identical,dup-target,heading-nospace,heading-lowercase,heading-spaced-digit,heading-suffix,heading-valid-tail,dispatch-spec-before,dispatch-attempts-before,dispatch-dispatched-before,dispatch-results-before,dispatch-names-after,dispatch-notes-before,counter-symlink,population-symlink |
| M49 | L166 call | `!= want:` -> `!= hashlib.sha1(at_freeze).hexdigest():` | 3/34 | cases=cases=31 pass=pass=3 fail=fail=28 | killed by counter cases | clean,clean-dispatch-after,field-missing-base,field-missing-counter,field-empty-target,base-unresolved,base-not-ancestor,counter-missing,counter-digest,population-missing,population-digest,population-empty,control-missing,control-not-red,frozen-edited-counter,frozen-edited-population,dispatch-before-freeze,two-claims-one-bad,dup-base-differs,dup-counter-identical,dup-target,heading-nospace,heading-lowercase,heading-spaced-digit,heading-suffix,heading-valid-tail,dispatch-spec-before,dispatch-attempts-before,dispatch-dispatched-before,dispatch-results-before,dispatch-names-after,dispatch-notes-before,counter-symlink,population-symlink |
| M50 | L169 call | `at_rev = repo.blob(rev, path)` -> `at_rev = repo.blob(freeze, path)` | 35/2 | cases=cases=31 pass=pass=30 fail=fail=1 | killed by counter cases | frozen-edited-counter,frozen-edited-population |
| M51 | L170 branch | `if at_rev != at_freeze:` -> `if at_rev == at_freeze:` | 5/32 | cases=cases=31 pass=pass=4 fail=fail=27 | killed by counter cases | clean,clean-dispatch-after,field-missing-base,field-missing-counter,field-empty-target,base-unresolved,base-not-ancestor,counter-missing,counter-digest,population-missing,population-digest,population-empty,control-missing,control-not-red,dispatch-before-freeze,two-claims-one-bad,dup-base-differs,dup-counter-identical,dup-target,heading-nospace,heading-lowercase,heading-spaced-digit,heading-suffix,heading-valid-tail,dispatch-spec-before,dispatch-attempts-before,dispatch-dispatched-before,dispatch-results-before,dispatch-names-after,dispatch-notes-before,counter-symlink,population-symlink |
| M52 | L178 assign | `claims, bad = parse_claims(text)` -> `bad, claims = parse_claims(text)` | 3/34 | cases=cases=31 pass=pass=3 fail=fail=28 | killed by counter cases | clean,clean-dispatch-after,field-missing-base,field-missing-counter,field-empty-target,base-unresolved,base-not-ancestor,counter-missing,counter-digest,population-missing,population-digest,population-empty,control-missing,control-not-red,frozen-edited-counter,frozen-edited-population,dispatch-before-freeze,two-claims-one-bad,dup-base-differs,dup-counter-identical,dup-target,heading-nospace,heading-lowercase,heading-spaced-digit,heading-suffix,heading-valid-tail,dispatch-spec-before,dispatch-attempts-before,dispatch-dispatched-before,dispatch-results-before,dispatch-names-after,dispatch-notes-before,counter-symlink,population-symlink |
| M53 | L179 class | `found.extend(("C0", "HEADING-MALFORMED", "line=%d" % n) for n in bad)` -> `found.extend(("C0", "HEADING-MALFORM", "line=%d" % n) for n in bad)` | 33/4 | cases=cases=31 pass=pass=27 fail=fail=4 | killed by counter cases | heading-nospace,heading-lowercase,heading-spaced-digit,heading-suffix |
| M54 | L180 cond | `if not claims:` -> `if False:` | 36/1 | cases=cases=31 pass=pass=30 fail=fail=1 | killed by counter cases | no-claims |
| M55 | L181 class | `found.append(("C0", "NO-CLAIMS", "no '## C<digits>' block in %s" % prereg))` -> `found.append(("C0", "NO-CLAIM", "no '## C<digits>' block in %s" % prereg))` | 36/1 | cases=cases=31 pass=pass=30 fail=fail=1 | killed by counter cases | no-claims |
| M56 | L183 class | `found.extend((label, "KEY-DUPLICATE", key) for key in sorted(dups))` -> `found.extend((label, "KEY-DUP", key) for key in sorted(dups))` | 34/3 | cases=cases=31 pass=pass=30 fail=fail=1 | killed by counter cases | dup-base-differs,dup-counter-identical,dup-target |
| M58 | L185 cond | `if key not in f:` -> `if key in f:` | 3/34 | cases=cases=31 pass=pass=3 fail=fail=28 | killed by counter cases | clean,clean-dispatch-after,field-missing-base,field-missing-counter,field-empty-target,base-unresolved,base-not-ancestor,counter-missing,counter-digest,population-missing,population-digest,population-empty,control-missing,control-not-red,frozen-edited-counter,frozen-edited-population,dispatch-before-freeze,two-claims-one-bad,dup-base-differs,dup-counter-identical,dup-target,heading-nospace,heading-lowercase,heading-spaced-digit,heading-suffix,heading-valid-tail,dispatch-spec-before,dispatch-attempts-before,dispatch-dispatched-before,dispatch-results-before,dispatch-names-after,dispatch-notes-before,counter-symlink,population-symlink |
| M60 | L109 cond | `if m.group(1) in cur[1]:` -> `if m.group(1) not in cur[1]:` | 3/34 | cases=cases=31 pass=pass=3 fail=fail=28 | killed by counter cases | clean,clean-dispatch-after,field-missing-base,field-missing-counter,field-empty-target,base-unresolved,base-not-ancestor,counter-missing,counter-digest,population-missing,population-digest,population-empty,control-missing,control-not-red,frozen-edited-counter,frozen-edited-population,dispatch-before-freeze,two-claims-one-bad,dup-base-differs,dup-counter-identical,dup-target,heading-nospace,heading-lowercase,heading-spaced-digit,heading-suffix,heading-valid-tail,dispatch-spec-before,dispatch-attempts-before,dispatch-dispatched-before,dispatch-results-before,dispatch-names-after,dispatch-notes-before,counter-symlink,population-symlink |
| M64 | L100 expr | `cur = ("C" + m.group(1), {}, set())` -> `cur = ("C0" + m.group(1), {}, set())` | 16/21 | cases=cases=31 pass=pass=15 fail=fail=16 | killed by counter cases | field-missing-base,field-missing-counter,field-empty-target,base-unresolved,base-not-ancestor,counter-missing,counter-digest,population-missing,population-digest,population-empty,control-missing,control-not-red,frozen-edited-counter,frozen-edited-population,two-claims-one-bad,dup-base-differs,dup-counter-identical,dup-target,heading-valid-tail,counter-symlink,population-symlink |

### M-set survivors (25) — re-verified here, classified by the inherited seat's own evidence

| mutant | line / kind | change | counter cases | --selftest | verdict | evidence (committed w2 receipt) |
|---|---|---|---|---|---|---|
| M02 | L43 const | FULL40 accepts `[0-9a-fA-F]` | 37/0 | 31/31 | **GAP** | `census/round-42/waves/w2/R42w2mutationtester01/logs/probe2.txt` |
| M03 | L43 const | FULL40 loses its `$` | 37/0 | 31/31 | **GAP** | `…/logs/m03-confirm.txt` |
| M09 | L46 regex | KEYLINE drops its trailing `[ \t]*$` | 37/0 | 31/31 | **GAP** | `…/logs/probe1.txt` |
| M13 | L48 regex | ROUND drops its BOM tolerance | 37/0 | 31/31 | **GAP** | `…/logs/probe2.txt` |
| M14 | L49 regex | EXIT_LINE drops its `^` | 37/0 | 31/31 | EQUIVALENT | `…/logs/probe2.txt` |
| M15 | L49 regex | EXIT_LINE drops its `$` | 37/0 | 31/31 | **GAP** | `…/logs/probe2.txt` |
| M18 | L65 env | drop `GIT_NO_REPLACE_OBJECTS` | 37/0 | 31/31 | **GAP** | `…/logs/probe2.txt` |
| M19 | L63 env | drop `GIT_CONFIG_NOSYSTEM` | 37/0 | 31/31 | EQUIVALENT | `…/logs/probe5-equiv.txt` |
| M20 | L69 args | drop `-c log.mailmap=false` | 37/0 | 31/31 | EQUIVALENT | `…/logs/probe2.txt` |
| M21 | L78 branch | drop the `FULL40.match(out)` re-check | 37/0 | 31/31 | EQUIVALENT | `…/logs/probe5-equiv.txt` |
| M22 | L81 guard | delete the NUL guard in `Repo.blob` | 37/0 | 31/31 | **GAP** | `…/logs/probe3.txt` |
| M24 | L88 call | drop `posixpath.normpath` | 37/0 | 31/31 | EQUIVALENT | `…/logs/probe5-equiv.txt` |
| M28 | L117 args | drop `--reverse` | 37/0 | 31/31 | **GAP** | `…/logs/probe2.txt` |
| M29 | L120 index | `ids[0]` -> `ids[-1]` | 37/0 | 31/31 | **GAP** | `…/logs/probe2.txt` |
| M30 | L120 branch | drop the `returncode == 0` check | 37/0 | 31/31 | EQUIVALENT | `…/logs/probe5-equiv.txt` |
| M31 | L128 class | the missing-Round class becomes FIELD-EMPTY | 37/0 | 31/31 | **GAP** | `…/logs/m31-lane-r40.txt` |
| M39 | L138 expr | drop `.strip()` on the dispatch commit | 37/0 | 31/31 | EQUIVALENT | `…/logs/probe5-equiv.txt` |
| M40 | L142 expr | `first[line] = commit` -> `first.setdefault(...)` | 37/0 | 31/31 | **GAP** | `…/logs/probe2.txt` |
| M41 | L153 call | `PATH_SHA.match` -> `.search` | 37/0 | 31/31 | EQUIVALENT | `…/logs/probe4-equivalence.txt` |
| M43 | L154 expr | the fallback takes the whole value | 37/0 | 31/31 | **GAP** | `…/logs/probe1.txt` |
| M57 | L183 order | `sorted(dups)` -> `dups` | 37/0 | 31/31 | EQUIVALENT | `…/logs/probe4-equivalence.txt` |
| M59 | L187 stmt | delete the `del f[key]` loop | 37/0 | 31/31 | **GAP** | `…/logs/probe3.txt` |
| M61 | L103 stmt | `cur = None` -> `pass` on the plain `## ` branch | 37/0 | 31/31 | **GAP (lane leg only)** | `…/logs/probe3.txt`; the lane's own r42 prereg gains 5× KEY-DUPLICATE (`logs/lane-out.txt`), so the counter's `real` leg is FAIL |
| M62 | L102 cond | drop `line.startswith("## ")` | 37/0 | 31/31 | **GAP (lane leg only)** | `…/logs/probe3.txt`; same lane effect as M61 (`logs/lane-out.txt`) |
| M63 | L111 expr | add `.strip()` to the key value | 37/0 | 31/31 | EQUIVALENT | `…/logs/probe4-equivalence.txt` |

## Named coverage limits of C2 (the 30 GAP survivors)

Each item names the input that exposes it, the pristine output and the mutant output. None is a
finding against a frozen file; each is a limit for the L1 to route. The 13 inherited gaps and the 2
lane-leg gaps are listed above; the 17 new ones this seat found are:

1. **Upper-case and other `\w` hex in a Base** (W08). A Base written in upper case resolves
   (pristine BASE-UNRESOLVED, mutant clean). No case uses a non-lower-case hex name.
2. **A TAB after a key's colon** (W11). `KEYLINE`'s `[ \t]*` is narrowed to a space, so `Base:<TAB>…`
   is not a key line at all and the claim loses every key (pristine clean, mutant 4× FIELD-MISSING).
   No case uses a tab after the colon.
3. **A truncated digest** (W12). `PATH_SHA` accepts 32 hex, so a Counter value carrying a 32-hex
   digest is digest-compared instead of rejected (pristine "no sha256=<64 hex>", mutant a hash
   comparison). No case carries a wrong-length digest.
4. **`Round:` with no digits** (W13). `ROUND`'s `(\d*)` accepts it, so the dispatch tree becomes
   `.ufo/waves/round-/` (pristine FIELD-MISSING Round, mutant clean). No case has a digit-less Round.
5. **The git environment whitelist** (W21). `env=None` lets a caller-set `GIT_DIR` redirect the tool
   to another repository (pristine rc=0, mutant rc=2 COULD-NOT-EVALUATE). This is the r41
   hardening the tool's own comment claims; no case sets a hostile environment.
6. **The line numbers in a HEADING-MALFORMED finding** (W28). The counter compares the finding's
   CLASS, never its detail, so an off-by-one line number is invisible (pristine line=11, mutant
   line=10).
7. **A CRLF preregistration** (W29). `split("\n")` keeps the CR, so five spurious findings appear.
   No case uses CRLF.
8. **A `### ` sub-heading** (W30). It closes the claim block, so the keys after it are lost
   (pristine 4× FIELD-MISSING, mutant 5). No case places a sub-heading inside a claim.
9. **History simplification** (W32). Dropping `--full-history` lets git prune a side branch, so the
   freeze moves to a different commit and the digest verdict changes (pristine FROZEN-EDITED, mutant
   COUNTER-DIGEST). No case merges the preregistration.
10. **Any `.json` under the wave tree** (W35). `notes.json` is read as a dispatch file (pristine
    clean, mutant DISPATCH-BEFORE-FREEZE). No case has a `.json` wave file that is not
    `-spec.json`/`-results.json`.
11. **A Counter value with no sha256** (W37). The fallback yields an empty path, so the Counter is
    not checked at all (pristine COUNTER-DIGEST, mutant clean). The counter's own
    `counter-digest` case uses a wrong digest, not a missing one.
12. **An empty blob at the freeze** (W40). An empty Counter file counts as missing (pristine clean,
    mutant COUNTER-MISSING). No case has an empty file at the freeze.
13. **A symlink at the freeze that is a file at the revision** (W41). The symlink test runs at REV,
    not FREEZE (pristine COUNTER-SYMLINK, mutant COUNTER-DIGEST + FROZEN-EDITED). No case changes a
    path's mode after the freeze.
14. **A second malformed heading** (W46). Only the first is reported (pristine line=11 and line=12,
    mutant line=11). Every counter heading case has exactly one malformed heading.
15. **A path that starts with `-`** (W57). Without the `--` separator, git takes the path as an
    option (pristine COUNTER-SYMLINK, mutant COUNTER-DIGEST). No case uses such a path.
16. **The NO-CLAIMS finding's detail text** (W70). The class is unchanged but the printed finding
    differs; the counter compares the class, never the detail.
17. **The key name in a KEY-DUPLICATE finding** (W71). `KEY-DUPLICATE TARGET` instead of
    `KEY-DUPLICATE Target`; again a detail the counter never reads.

## Interpretation for the L1

- **The C2 target `cases=37 pass=37 fail=0` holds at the tip, and the 37 cases are not a complete
  kill set for the tool's first half.** 30 distinct single-point behaviour changes of the landed tool
  are observed by no counter leg and no `--selftest` case. That is the sharpest statement of the
  lesson's N-C2a ("the 37 cases are a closed public set") that the round has.
- **The two instruments are complementary, not redundant.** Of 136 mutants, 63 are killed by both
  instruments, 2 by the counter's case table only (M31, M34), 4 by the tool's own `--selftest` only
  (the self-test-only imports), and 67 by neither. A candidate that scores `cases=37 pass=37` and
  `selftest=ok` has still left 30 behaviour changes unobserved.
- **The counter's `real` leg carries part of the kill load.** M61 and M62 survive the 37 cases and
  the self-test and are caught only over the lane's own r42 preregistration — the same shape as the
  inherited report's finding, reproduced here at the new tip.
- **The counter's legs are load-sensitive.** During the 6-worker batch run the `real` and
  `retro_clean` legs read `FAIL` for W61/W62/W63 and `ok` when the same mutants were re-scored one
  at a time on an idle host; the case-table column was stable in every reading. This is the C3
  lesson's E-1 in the C2 counter and should be routed with it.
- **A lesson erratum.** The wave-2 record says `R42w2mutationtester01` left no report; it did, and
  the report is committed at `census/round-42/waves/w2/R42w2mutationtester01.md` (`d39e3453`). Its
  64-mutant result was re-derived here and reproduced exactly.
- Under the preregistration's rules each gap is a named limit for the round lesson, not a reason to
  edit `census/round-42/c2-counter.py` or `tools/souji-freeze-check.py`. Nothing frozen was edited.

## Limits of this run

- Equivalence means agreement on the probed inputs (the three frozen preregistrations, the lane's
  own r42 preregistration, and the synthetic repositories named in each probe), not a proof over all
  inputs. Each EQUIVALENT row carries the reason it is believed equivalent.
- The M-set survivors are classified by the inherited seat's own committed probe receipts, which
  this seat did not re-run (the seat's mutants and scripts were reused, not rewritten). The M-set
  kill/survive column was re-derived from scratch here.
- The counter's `patches` leg was recorded but not used as a kill criterion; the assignment's
  classification uses the case table and the mutant's own `--selftest` only.
- The mutants cover lines 1–187 (the first half, the same boundary the inherited seat used). The
  `--selftest` machinery and `main` (lines 188–375) were not mutated.
- SHA-256 git repositories were not probed. M21 and W21 are argued equivalent only on SHA-1.
- The probes use one synthetic repository per mutant; a scenario that no probe builds is not
  excluded.

## Seat directory contents (all under `.ufo/waves/round-42/w3/R42w3mutationtester01/`)

- `scripts/mutants.py` — the 72 new mutant definitions (W01–W72)
- `scripts/run.py` — the scoring runner (counter case table + the mutant's own `--selftest`)
- `scripts/reverify.py` — the one-at-a-time survivor re-verification
- `scripts/probe.py`, `probe2.py` … `probe7.py` — the directed differential probes
- `scripts/classify.py` — the table builder
- `mutants/manifest.tsv` — the merged manifest (64 M + 72 W rows: id, line, kind, old, new, path)
- `results.tsv`, `counter-summaries.txt`, `table.md` — the per-mutant scores, every counter SUMMARY
  line verbatim, and the 136-row table
- `logs/` — every receipt cited above: the probe outputs, the re-verification log, the diff-shape
  check, the survivor classifications, the pristine tool digest, and the inherited manifest
