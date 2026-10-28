# R40executor27 — r40 w1: attack on the frozen C3 coverage claim

Seat: R40executor27 (executor, godspeed). Item: independent attack of the frozen C3 claim in
`census/round-40/preregistration.txt`, on committed r39 artifacts, no production writes, frozen
claims untouched. Distinct item 27 angle — **named below as "the decode-policy kill contract of
the invalid-UTF-8 branch"**: a kill-rule × mutant-policy failure mode that none of the three
named C3 branches (duplicate/multiple TOTAL rows, `--skip-unrecorded`, invalid UTF-8 *as a
behavior*) covers.

Freeze provenance measured before any run:

```
git -C /home/vgpnk/Projects/shokunin/souji-shokunin log --oneline -1
  -> be4cb61 round-39 verifier spot-check (integrator, hyaku): non-author admit/reject
git -C <lane> show 0242085909fb6a4ee041c5443d76316ac6d59d4b:tools/souji-worktree-drift.py | sha256sum
  -> e48ed08e672824e225e165a34d5659b244babfa1ea55cb88721059fa6a0c2f76
sha256sum <lane>/tools/souji-worktree-drift.py -> identical (worktree == r40 base bytes)
```

The r39 C3 instrument is green at the r40 base revision and byte-matches the r39 receipt
(`census/round-39/records/c3-after.txt`):

```
cd <lane> && TMPDIR=$S python3 -B census/round-39/c3-counter.py --root . \
  --rev 0242085909fb6a4ee041c5443d76316ac6d59d4b --base-rev 0242085909fb6a4ee041c5443d76316ac6d59d4b \
  --scratch $S/counter-sanity
MUTANT M11 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
MUTANT M12 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
MUTANT M13 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
MUTANT M14 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=7 tool_sha=e48ed08e6728 fixture_sha=567c37a679f5
rc=0
```

Scratch (removed before this report's yield): `/fast/scratch/hyaku/souji-r40/R40executor27`
(explicit `TMPDIR` on every command; the counter's `--scratch` needs a pre-created dir — it
`mkdtemp`s *under* it, `census/round-39/c3-counter.py:125-129`). Tooling: none installed. No git
mutation anywhere; only read-only `git show`/`log`/`status` on the lane. All mutant tools, the
probe fixture and the driver lived only in scratch; the lane got exactly one new file: this report.

## Named item-27 failure mode: the decode-policy kill contract

`parse_record` decodes the record once, at `tools/souji-worktree-drift.py:147`:

```python
raw = b"".join(chunks).decode("utf-8", "replace")
```

The frozen C3 branch "invalid UTF-8 record bytes" will be enforced by *some* declared
single-defect mutant of this line, killed by the r40 fixture under the inherited kill rule
(`census/round-39/c3-counter.py:82-93`: a kill needs the fixture's own `fail>0`, **no traceback**,
exit 1). I built the four single-token decode-policy mutants of that line on the committed base
bytes and scored them with that exact `score()` semantics against both committed fixtures plus a
scratch probe fixture modeled line-for-line on `tests/fixtures/r39-drift-record-rules.py`
(same `run_case` argv `--root/--record/--timeout 30`, same `SUMMARY cases=… pass=… fail=…`,
exit 1 contract). Probe cases: invalid byte in a TOTAL numeric field, in a REPO name, a
rendering-token case (`ABSENT\tal\ufffdpha`), both `--skip-unrecorded` polarities on a fleet with
an unrecorded repo, and duplicate-TOTAL in both orders.

Matrix run: `TMPDIR=$S python3 -B $S/attack_matrix.py` (from `$S`):

```
tool           | r38-base(committed)                 | r39-cand(committed)                 | probe(scratch)
base           | survived [rc=0 fails=0 crash=False] | survived [rc=0 fails=0 crash=False] | KILLED [rc=1 fails=2 crash=False]
t-strict       | survived [rc=0 fails=0 crash=False] | survived [rc=0 fails=0 crash=False] | survived [rc=1 fails=5 crash=True]
t-ignore       | survived [rc=0 fails=0 crash=False] | survived [rc=0 fails=0 crash=False] | KILLED [rc=1 fails=5 crash=False]
t-backslash    | survived [rc=0 fails=0 crash=False] | survived [rc=0 fails=0 crash=False] | KILLED [rc=1 fails=3 crash=False]
t-surrogate    | survived [rc=0 fails=0 crash=False] | survived [rc=0 fails=0 crash=False] | ?? [NO-SUMMARY rc=1]
t-skip-never   | survived [rc=0 fails=0 crash=False] | survived [rc=0 fails=0 crash=False] | KILLED [rc=1 fails=3 crash=False]
t-skip-always  | survived [rc=0 fails=0 crash=False] | survived [rc=0 fails=0 crash=False] | KILLED [rc=1 fails=3 crash=False]
d-cand         | survived [rc=0 fails=0 crash=False] | survived [rc=0 fails=0 crash=False] | survived [rc=0 fails=0 crash=False]
```

(`base` "KILLED" on the probe is by design: the probe carries candidate-only duplicate-TOTAL
cases. `d-cand` = base bytes + a duplicate-TOTAL refusal inserted before the last-wins assignment
at line 164 — it passes both committed fixtures 10/10 and 7/7, so adding the r40 branch breaks no
committed case and the pristine-candidate control is reachable.)

**Finding 1 — the strict-decode trap (concrete falsifier of the natural mutant choice).** The
classic single-token mutant `"replace"` → `"strict"` cannot be killed under the frozen kill rule:
on any invalid-byte case it dies with `UnicodeDecodeError` (rc 1, traceback), and both committed
fixtures echo the tool's output far enough (`r39-drift-record-rules.py:88` prints
`out.replace("\n"," ")[:160]`; `r38-drift-record.py:93` prints `out.splitlines()[:3]`) that the
counter's `crash` guard (`c3-counter.py:91`) sees it. Probe verdict for t-strict:
`rc=1 fails=5 crash=True` → **not a kill** → `survived=0` unsatisfiable if r40 declares strict.
Direct demo (`TMPDIR=$S python3 -B $S/demos.py`): byte `0x80` in a TOTAL regs field →

```
== invalid byte in TOTAL regs, t-strict mutant -> rc=1
   stderr[:100]: 'Traceback (most recent call last):\n  File ".../t-strict.py",'
```

**Finding 2 — the policy-alias escape.** `"backslashreplace"` and `"surrogateescape"` are
observable-identical to the pristine `"replace"` on every rc/class-token assertion:

```
== invalid byte in TOTAL regs, t-surrogate mutant -> rc=2
   stderr[:100]: 'REFUSAL RECORD-MALFORMED: line 3 does not match the census schema\n'
```

— the same rc and class the pristine tool prints, so no schema-refusal case can kill them.
`backslashreplace` *is* killable, but only by a case that pins the rendered name: pristine prints
`DRIFT\tABSENT\tal\ufffdpha` for an invalid byte in a REPO name (the `utf8-name-render` token
`ABSENT\tal\ufffdpha` is what flipped t-backslash to KILLED). `surrogateescape` is **unkillable by
construction**: on the rendering path the probe *fixture itself* crashed decoding the tool's
output — `probe.py --tool t-surrogate.py` → rc 1, **empty stdout** (→ `NO-SUMMARY`, not a kill)
with a traceback in fixture stderr (→ `crash=True` even if a summary existed). Both score()
failure paths block the kill. So the frozen sentence "each declared single-defect mutant is
killed" is satisfiable only for a policy-restricted mutant set; declared-but-unkillable policies
would make the r40 C3 predicate fail on its own rule.

**Finding 3 — the duplicate-TOTAL order trap.** The pristine base bytes resolve multiple TOTAL
rows last-wins (`total = {…}` overwrite, line 164). Direct demos on committed bytes:

```
TOTAL(repos=9) then TOTAL(repos=2)  -> rc=0  SUMMARY … drift_rows=0        # bad-FIRST ACCEPTED
TOTAL(repos=2) then TOTAL(repos=9)  -> rc=2  REFUSAL RECORD-MALFORMED: TOTAL repos=9 but 2 REPO rows
TOTAL(repos=2) then TOTAL(repos=2)  -> rc=0  (identical duplicates silently accepted)
```

The order-dependence is the teeth: a r40 duplicate-TOTAL case written in the natural
"agreeing TOTAL first, disagreeing TOTAL last" shape (the shape of r38's own `total-*` cases) is
**passed by the last-wins revert mutant** (it also refuses). The kill requires the disagreeing
row FIRST or an explicit duplicates class token (`d-cand` prints `duplicates TOTAL`).

**Finding 4 — the control clause holds, measured.** Frozen control: "r39 fixture/counter has no
cases for these branches and kills none of the new mutants". Confirmed on committed bytes: the
r39 candidate fixture's 7 cases (good, trailing-space, total-before-rows, crlf, outside-root,
indented-comment, comments-total-only, `r39-drift-record-rules.py:77-112`) and the r38 base
fixture's 10 cases (`r38-drift-record.py:101-122`) contain no duplicate-TOTAL case, no
`--skip-unrecorded` anywhere in either `run_case` argv, and no non-ASCII record bytes; every
natural new-branch mutant survives both (matrix rows 2-7); and the committed r39 counter's
`MUTANTS` tuple (`c3-counter.py:39-50`) contains only M11-M14, so it cannot score a new mutant.
Additionally both skip polarity mutants are equivalent on every committed input — the branch is
inert there (fixtures record every repo they build; no unrecorded repo exists in any case), which
is stronger evidence than "no case" for the r40 fixture needing a genuinely unrecorded fleet.

**Finding 5 — the frozen r40 text is weaker than r39's.** r39's C3 predicate pinned
`cases>=6` and named M11-M14 with anchors; the r40 C3 text names no mutant set, no anchor
count, and carries no case-count floor — a 3-case fixture with one trivial mutant per branch
satisfies it as written.

## Bounded measurement plan (advisory; the L1 owns any contract change)

1. Declare the UTF-8 mutant as `"replace"` → `"ignore"` (killable: byte in a numeric field turns
   a refusal into rc 0). Do not declare `"strict"` (unkillable, traceback) or
   `"surrogateescape"` (NO-SUMMARY/alias) as kills; `"backslashreplace"` only with the
   rendering-token case `ABSENT\tal\ufffdpha`.
2. The duplicate-TOTAL case must place the disagreeing TOTAL row FIRST, or assert the duplicate
   refusal class token; ideally both orders.
3. `--skip-unrecorded` needs a fleet with an actual unrecorded repo and both polarities: flag set
   → rc 0 with no `UNRECORDED`; flag absent → rc 1 with `UNRECORDED` naming the repo.
4. Restore a `cases>=N` floor in the r40 counter's pristine arm (r39 had `cases>=6`).

## Verdict

- Frozen C3 control clause: **confirmed empirically** on committed r39 artifacts (no committed
  fixture reaches any of the three branches; no natural new-branch mutant is killed by the r39
  base fixture or the r39 candidate fixture; the r39 counter cannot score them).
- Frozen C3 predicate as written: **not falsified outright, but trap-bound** — satisfiable only
  with Finding 1/2/3's constraints; the natural strict-decode mutant and a disagreeing-last
  duplicate-TOTAL case would each independently sink it. Findings 1-3 are the concrete falsifiers
  of the *obvious* implementations, with executed evidence above.
- Residual limits: the r40 counter/fixture/tool bytes do not exist yet, so the declared mutant
  set is unknown; my mutant set is the natural single-token class of the one decode site and the
  one flag site, not exhaustive. The probe fixture is scratch-only evidence of killability
  bounds, not a proposed lane artifact.
