# SwarmCritic26 — M1 record-contract guard (attack)

## Status
STATUS: PARTIAL — both required arms reproduce byte-for-byte from committed blobs and the red arm is red for the right reason (value-set membership, not key drift); but the guard is scoped to lines that literally begin `RESULT ` in *both* readers, so a D1 recurrence one character off the prefix (`RESULT:`, `RESULT_`, leading space) passes the tool **and** all six record-reading C3 legs (`bad=0`, exit 0), and L14 is an independent reimplementation of the tool, not the tool. The fix is sound for the r31 shape and for this round; it is not yet a general guard.

## Evidence

Lane tip `4e56c48b8fc828f9aba2746e324dc46aa538bdbf`; artifacts unchanged since landing:
`git rev-parse 3ec84fc:census/round-32/c3-contract.txt master:... = 660d6fd0…` (same);
`…:records/jj-mtime-clock-run.txt a92e1aa master = 6de8f4b8…` (same);
`…:census/round-31/records/jj-object-clock-run.txt 85b61a1 master = 63502d12…` (same);
`git show 3ec84fc:tools/souji-record-contract.py | sha256sum` = working tree = `a242b43a…33f9`.

1. Required arm A — r32 record × `census/round-32/c3-contract.txt`:
```
$ python3 -B tools/souji-record-contract.py --record census/round-32/records/jj-mtime-clock-run.txt \
      --contract census/round-32/c3-contract.txt
lines=22 bad=0
exit=0
```
2. Required arm B — r31 record × reconstructed r31 contract (`census/round-32/m1-r31-contract.txt`), re-run from committed blobs (`git show 3ec84fc:…` of tool and contract) rather than the working tree:
```
BAD 16 arm=reflog-only outside descendant|solo
BAD 17 arm=reflog-only outside descendant|solo
BAD 18 arm=reflog-only outside descendant|solo
BAD 19 arm=reflog-only outside descendant|solo
lines=17 bad=4
exit=1
```
Matches `census/round-32/records/m1-red-before.txt` exactly (receipt blob `aac7f6b4…` unchanged since `3ec84fc`).
3. Reconstruction faithfulness: `grep -o 'RESULT arm=<solo|descendant>[^`]*' census/round-31/records/preregistration.txt` prints at **line 20** `RESULT arm=<solo|descendant> step=<name> keep_refs=<n> target_keep=<yes|no> reflog_hits=<n> object_present=<yes|no>` — the file header's provenance claim is true, and the record lines 14-19 carry exactly those six keys in that order (`step`/`keep_refs`/`reflog_hits` present), so the four `BAD` lines fail on value membership only, not on a mis-keyed reconstruction. Right reason.
4. Five crafted records (scratch, contract = `c3-contract.txt`):
```
c1-extra-key      BAD 1 keys [... 'object_present', 'extra'] != [... 'object_present']  exit=1
c2-missing-key    BAD 1 keys [... 'where'] != [... 'where', 'object_present']            exit=1
c3-reordered      BAD 1 keys ['step','arm',…] != ['arm','step',…]                       exit=1
c4-value-outside  BAD 1 arm=reflog-only outside mixed|never|nocruft|old|recent          exit=1
c5-double-space   lines=1 bad=0                                                          exit=0
```
Extra checks: empty record `lines=0 exit=1`; bare `RESULT` `lines=0 exit=1`; `RESULT RESULT …` `BAD 1 field without '='`; `RESULT\t…` `lines=0 exit=1`; `arm=` empty → `BAD 1 arm= outside …`; `object_present=yes=` → `BAD … outside no|yes`; contract with no prefix line / no key line / malformed `arm:` line / missing file → `COULD-NOT-EVALUATE …`, exit 2. Tool writes nothing (no `open(...,'w')`; stdout only).
5. Attack (reproduced) — prefix smuggling, one correct `RESULT` line present plus one violating line:
```
s1 near-prefix   RESULT_ arm=reflog-only …   lines=1 bad=0 exit=0
s2 leading space  ␣RESULT arm=reflog-only …  lines=1 bad=0 exit=0
s3 lowercase      result arm=reflog-only …   lines=1 bad=0 exit=0
s8 colon          RESULT: arm=reflog-only …  lines=1 bad=0 exit=0
```
and the same record through L14's committed predicate (imported from a copy, `-B`, no bytecode):
```
rec-clean    raw=24 RESULT=22 L14_bad=[] L14_ok=True
rec-smuggled raw=25 RESULT=22 L14_bad=[] L14_ok=True     # RESULT_ arm=reflog-only appended
```
6. Duplicate-authority divergence — tool vs L14 on a wildcard contract:
```
tool on w-contract.txt (step: *, keep_refs: #):  lines=1 bad=0  exit=0
L14 contract_bad on the same line:               ['RESULT arm=solo step=x keep_refs=0 …']
```
7. Wildcard laundering: with `keep_refs: #`, the tool accepts `keep_refs=1²` and `keep_refs=١٢` (`lines=1 bad=0`, exit 0) because `str.isdigit()` is not ASCII-only.
8. No automated caller: `grep -rn souji-record-contract` over `.py/.sh/.md` hits only the tool itself and docs (`SKILL.md:254`, `PROVINCE.md:257`, `corpus/README.md:759`); `tools/souji-landing-gate.py` cites `SKILL.md` only to check registered paths exist (`LG-MISSING-REG`), it does not execute gate rows.

## Findings

1. **The fix is correctly "shown able to fail" and for the right reason.** `census/round-32/records/m1-red-before.txt` (committed at `3ec84fc`, pre-data) fails the r31 record on `arm` membership at `tools/souji-record-contract.py:56`, with all 17 `RESULT` lines counted and only the 4 `reflog-only` lines flagged — the failure is the D1 shape, not a reconstruction artifact (evidence 2-3). The green arm (evidence 1) is post-data by nature and pins to `a92e1aa`; both arms reproduce at the current tip.
2. **ATTACK — the guard's scope is literal-prefix, so D1 can recur one character away.** `tools/souji-record-contract.py:44` (`if not line.startswith(prefix + " ")`) and `census/round-32/c3-counter.py:75-76` / `c3-counter-v2.py:92-93` (`results()` = `startswith("RESULT ")`) *exclude* near-prefix lines from the check instead of flagging them. With at least one correct `RESULT` line present, `RESULT: arm=reflog-only …`, `RESULT_ arm=reflog-only …` or `␣RESULT arm=reflog-only …` yields `lines=N bad=0`, exit 0 (evidence 5). Impacted axis: coverage (C3's own record check). Calibration/operability untouched; the measured C3 target (`legs=14 fail=0 f1_entries=5`) is not moved by this — it is a guard-strength gap, not a target miss.
3. **Bound on finding 2 (why it is PARTIAL and not FAIL):** a *uniformly* drifted prefix is fail-closed — `lines=0` → exit 1 (`s4-tab`, `s5-no-prefix`, `s6-bare-prefix`, empty record). The hole therefore needs a mixed record: one conforming `RESULT` line plus a violating near-prefix line. That is a narrower but entirely realistic shape (a hand-added annotation line, a colon after the prefix, a second fixture arm writing its own summary).
4. **Duplicate authority: L14 is a copy of the tool, and the copy is what actually runs.** `census/round-32/c3-counter.py:83-104` (duplicated verbatim at `c3-counter-v2.py:100-121`) reimplements `load_contract`+`check` without the tool's `*`/`#` wildcards and hard-coded to `prefix == "RESULT"`; divergence is reproduced in evidence 6 (tool exit 0, L14 flags the same line). No counter, fixture or gate invokes `tools/souji-record-contract.py` (evidence 8), so "the fix" is two implementations that a future round must keep in sync by hand — the same drift hazard that produced r31's predecessor checks.
5. **`#` wildcard is not ASCII:** `tools/souji-record-contract.py:56` uses `v.isdigit()`, so `keep_refs=1²` / `١٢` pass (evidence 7). Latent today (r32's contract has no `#`); becomes live the moment L14 is replaced by the tool (finding 4's fix), which is precisely the direction the lane should move.
6. **Doc nit — identity overstatement:** `SKILL.md:254` describes the tool's green arm as "the r32 C3 counter's L14". For `c3-contract.txt` the predicates agree on all 22 lines, but they are independent code with different wildcard/prefix generality (finding 4); `corpus/README.md:765-769` and `PROVINCE.md:256-258` are accurate (they claim only that the tool fails the r31 shape and that L14 holds *this* record).
7. **Temporal binding lives only in L14, not in the tool.** `--record PATH --contract PATH` accepts any contract with no frozen-at revision; the only freeze is `c_list == c_rev` in the counter, and that equality is satisfied by *any* one contract appearing at both the caller-supplied `--list-rev` and REV — i.e. it detects an edit between those two commits, not a contract authored before data. [INFERENCE from the code path `c3-counter.py:270-274`; not exercised against a rewritten contract.] This is an input-trust bound on the caller, not a reproduced defect, and the L1 supplies both revs.
8. **No-harm check on the landed artifacts:** tool and both contracts are byte-identical to their landing commits, the r31 record is untouched since base, and running the tool writes nothing (evidence 4).

**Smallest safe correction (does not change any frozen predicate, target or item):**
- `tools/souji-record-contract.py:44` — flag instead of skip: take the line's first whitespace token; if `line.lstrip().startswith(prefix)` and that line is not a clean `<prefix> ` line, emit `BAD <n> prefix <tok> is not <prefix>` and count it. This makes `RESULT:`, `RESULT_`, leading-space and lowercase forms fail while leaving conforming and unrelated lines alone (uniform drift stays fail-closed via the same branch).
- `census/round-32/c3-counter.py` (and `-v2.py`) L14 — call the exported `exp/tools/souji-record-contract.py` (as the counter already does for `souji-coverage-agreement.py` and `souji-gate-check.py`), writing the `--list-rev` contract blob to a tmp file, and use its rc for `ok14`; delete `contract_bad()`. One authority, wildcard semantics included.
- `tools/souji-record-contract.py:56` — `#` becomes `re.fullmatch(r"[0-9]+", v)`.
- `SKILL.md:254` — say "the same check L14 runs" only after the wiring change; until then "an independent reimplementation, equivalent for `c3-contract.txt`".

## Attack log
- Tested: faithful reconstruction of the r31 contract (pass — line 20 verbatim, 6 keys, 17 lines counted).
- Tested: red-for-the-right-reason (pass — value membership, `lines=17 bad=4`).
- Tested: five crafted records, extra/missing/reordered key, value outside set, doubled spacing (all caught except benign doubled spacing).
- Tested: empty record, bare prefix, doubled prefix token, tab after prefix, empty value, `=`-suffixed value, malformed/missing contract (all fail-closed, exits 1/2 as documented).
- **Succeeded against the guard:** near-prefix smuggling `RESULT_`, `RESULT:`, leading space, lowercase, each with one conforming `RESULT` line present → tool `bad=0` exit 0 and L14 `bad=[]` on the same record (evidence 5).
- **Succeeded against the guard:** non-ASCII digits satisfy `#` (`1²`, `١٢`) (evidence 7).
- Failed to find: a way to make the tool accept a wrong key set, a wrong key order, an extra/missing field, a value outside an enumerated set, or a record with zero conforming lines.
- Failed to find: any automated caller that would run the tool without a human (landing gate checks only path registration).

## Deliveries
- `.ufo/waves/round-32/a2w1/SwarmCritic26.md` (this report). No other files; scratch `/fast/scratch/hyaku/souji-r32/AttackM1` removed.
- Seat deviation, disclosed: one `printf` ran with the shell cwd at the fleet root and created `/home/vgpnk/Projects/shokunin/s8-colon.txt` (164 B, my own file, created 10:04). Removed immediately; nothing else outside the lane was touched, read-only git only, no `git add/commit/push`, no `jj`, no signals, no tool installs.
