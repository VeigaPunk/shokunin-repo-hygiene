# W1ExecC2Repro — reproduce the two C2 defects from committed bytes (round 39, wave 1)

role: executor
base revision: `ed30b7f5b77939c9073348d810730bc4f355708d`
lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`
scratch: `/fast/scratch/hyaku/souji-r39/W1ExecC2Repro/` (probe driver + extracted tool bytes; still on disk — see §Scratch)
frozen contract read first: `census/round-39/preregistration.txt` (C2, legs L1-L6; Amendment A1)

Verdict up front: **both C2 defects reproduce at base; neither is closed at base.** Every claim in the
frozen C2 paragraph matches the observed bytes, with one measured nuance recorded in §Nuance.

## 1. Byte extraction (committed bytes only)

```
$ git show ed30b7f5b77939c9073348d810730bc4f355708d:tools/souji-citation-reconcile.py > /fast/scratch/hyaku/souji-r39/W1ExecC2Repro/new.py
$ git show ed30b7f5b77939c9073348d810730bc4f355708d:tools/souji-worktree-drift.py    > /fast/scratch/hyaku/souji-r39/W1ExecC2Repro/drift-base.py
$ sha256sum new.py drift-base.py
56866ea8f832332c2f69dcba4ddcd9ba5d7894bf9a2e82715962e2fb19bfcbe8  new.py
14e9c0f77d7e817df96b8ed656bfc18c879bb838a5036d1b7fc2f864c510d194  drift-base.py
```

Both digests' 12-hex prefixes (`56866ea8f832/14e9c0f77d7e`) equal the `tool_sha=` field of the frozen
control receipt `census/round-39/records/c2-before.txt`, i.e. the bytes I probed are the bytes the
control was measured on. Blob id used for leg L2, from committed bytes:

```
$ git -C .../souji-shokunin rev-parse ed30b7f5b77939c9073348d810730bc4f355708d:corpus/SOURCES.md
37b3bb73b930b7602922e2febba5036d4f58b0b8
```

## 2. Commands run (exact) and observed output lines

All cited-tool runs use the register `census/round-38/cells.tsv` (10 rows, header present) and are
read-only (`git show` / `cat-file` / `merge-base` only). Driver:
`TMPDIR=/fast/scratch/hyaku/souji-r39/W1ExecC2Repro python3 -B probe.py` (raw transcript kept at
`/fast/scratch/hyaku/souji-r39/W1ExecC2Repro/probe.out`).

### C2(a) R11 — `tools/souji-citation-reconcile.py` never resolves `--rev`

CIT-1 — unresolvable `--rev` (all-zero 40-hex):

```
$ python3 -B new.py --root /home/vgpnk/Projects/shokunin/souji-shokunin \
    --rev 0000000000000000000000000000000000000000 \
    --register census/round-38/cells.tsv --register-rev ed30b7f5b77939c9073348d810730bc4f355708d
RC 1
MISMATCH R38-C1-1 FILE-ABSENT SCORECARD.md at 0000000000000000000000000000000000000000
MISMATCH R38-C1-1 RECEIPT-REV-NOT-ANCESTOR census/round-37/records/c2-after.txt at 02b43398ffd295a399c7097ab0d8b2eb70fb490a
... (20 MISMATCH lines, 10 FILE-ABSENT + 10 RECEIPT-REV-NOT-ANCESTOR) ...
SUMMARY cells=10 mismatches=20
stderr: (empty)
```

CIT-2 — `--rev` naming a blob (same class):

```
$ python3 -B new.py --root .../souji-shokunin --rev 37b3bb73b930b7602922e2febba5036d4f58b0b8 \
    --register census/round-38/cells.tsv --register-rev ed30b7f5b77939c9073348d810730bc4f355708d
RC 1
MISMATCH R38-C1-1 FILE-ABSENT SCORECARD.md at 37b3bb73b930b7602922e2febba5036d4f58b0b8
... (same 20 MISMATCH lines) ...
SUMMARY cells=10 mismatches=20
stderr: (empty)
```

CIT-3 — unresolvable `--register-rev` (harm leg L3):

```
$ python3 -B new.py --root .../souji-shokunin --rev ed30b7f5b77939c9073348d810730bc4f355708d \
    --register census/round-38/cells.tsv --register-rev 0000000000000000000000000000000000000000
RC 2
stderr: REFUSAL USAGE: register census/round-38/cells.tsv is not at 0000000000000000000000000000000000000000
```

CIT-4 — control, both flags resolvable (must stay green after the fix):

```
$ python3 -B new.py --root .../souji-shokunin --rev ed30b7f5... --register census/round-38/cells.tsv --register-rev ed30b7f5...
RC 0
SUMMARY cells=10 mismatches=0
```

Mechanism (committed bytes, `run()`): `--rev` is only shape-checked by `REV.match(args.rev)`; the sole
rejection is `REFUSAL USAGE: --rev must be 40-hex` (exit 2) for non-40-hex input. A 40-hex value that
does not resolve never reaches a `cat-file -e REV^{commit}` test, so `git_show` returns `None` per row
and the run degrades into `FILE-ABSENT` findings plus `RECEIPT-REV-NOT-ANCESTOR` (because
`merge-base --is-ancestor X <unresolvable>` also fails) → exit 1.

### C2(b) R10 — `tools/souji-worktree-drift.py` record classes vs its own docstring

| # | trigger | class printed | rc | docstring says |
|---|---|---|---|---|
| (a) | non-existent record path | `RECORD-MALFORMED: <path> is not a regular file` | 2 | `RECORD-MISSING the record path cannot be read` |
| (b) | `chmod 000` record file (EACCES) | `RECORD-MISSING: [Errno 13] Permission denied: '<path>'` | 2 | `RECORD-MISSING` (literal text matches) |
| (c) | directory as record path | `RECORD-MALFORMED: <path> is not a regular file` | 2 | `RECORD-MALFORMED a line does not match the schema…` |

```
$ python3 -B drift-base.py --root .../souji-shokunin --record /fast/scratch/.../rec-absent.tsv --timeout 20
RC 2
REFUSAL RECORD-MALFORMED: /fast/scratch/hyaku/souji-r39/W1ExecC2Repro/rec-absent.tsv is not a regular file

$ chmod 000 rec-locked.tsv && python3 -B drift-base.py --root .../souji-shokunin --record .../rec-locked.tsv --timeout 20
RC 2
REFUSAL RECORD-MISSING: [Errno 13] Permission denied: '/fast/scratch/hyaku/souji-r39/W1ExecC2Repro/rec-locked.tsv'

$ python3 -B drift-base.py --root .../souji-shokunin --record .../rec-dir --timeout 20
RC 2
REFUSAL RECORD-MALFORMED: /fast/scratch/hyaku/souji-r39/W1ExecC2Repro/rec-dir is not a regular file
```

Docstring lines as derived from the base bytes via `ast.get_docstring` (the same derivation the C2
counter's L4 uses):

```
RECORD-MISSING         the record path cannot be read
RECORD-MALFORMED       a line does not match the schema, duplicates a name,
```

`parse_record` source in the same bytes: `except OSError as exc: if exc.errno == errno.ENOENT: raise
Refusal("RECORD-MALFORMED: %s is not a regular file" % path)` then `raise Refusal("RECORD-MISSING: %s"
% exc)` for every other `OSError` — the swap is one `if`. All three triggers refuse at `run()` line
279, before any git measurement, so rc 2 and the class are the whole surface.

## 3. Verdicts

| check | frozen expectation for base | observed | verdict |
|---|---|---|---|
| L1 unresolvable `--rev` | rc 1 with findings, no `REV-UNRESOLVED` | rc 1, 20 MISMATCH lines, stderr empty, `REV-UNRESOLVED` absent | **DEFECT REPRODUCED** |
| L2 `--rev` = blob | same class as L1 | rc 1, 20 MISMATCH lines, stderr empty | **DEFECT REPRODUCED** |
| L3 `--register-rev` unresolvable | rc 2 both revisions (harm leg) | rc 2 `REFUSAL USAGE: register … is not at 000…` | **HARM ABSENT at base** |
| L4a missing record | base must differ from its docstring | `RECORD-MALFORMED`, docstring names that trigger under `RECORD-MISSING` | **DEFECT REPRODUCED** |
| L4b EACCES record | base must differ from its docstring | `RECORD-MISSING` | see §Nuance — the literal docstring text does not contradict this |
| L4c directory record | not a docstring trigger at all | `RECORD-MALFORMED … is not a regular file` | undocumented-but-defensible class (same class as (a)) |
| control both flags resolvable | green | rc 0, `SUMMARY cells=10 mismatches=0` | **GREEN** |

No check was left unrun. The three drift and four citation commands above are the complete set; the
driver also re-derived the docstring via `ast`, quoted in §2.

## 4. Nuance for the L1 (measured, advisory)

The frozen C2 text says "a missing path raises `RECORD-MALFORMED: ...` **and** an unreadable (EACCES)
path raises `RECORD-MISSING`" as if both were docstring contradictions. Only the **missing-path**
case contradicts the docstring as written: the base docstring's `RECORD-MISSING` row reads "the record
path cannot be read", and an EACCES path genuinely cannot be read — so (b) is consistent with the
literal text, while (a) is not (`MALFORMED` is documented as a schema/duplicate/TOTAL defect and the
string "not a regular file" is not a schema defect).

The C2 counter's L4 does not test the literal docstring text; it requires the docstring line for the
**observed** class to name its trigger — `missing` for (a) and the literal token `EACCES` for (b) — in
both revisions. At base both mapping predicates are therefore false (`new_maps=False old_maps=False`,
matching `c2-before.txt`), but the *reason* for (b) is a **stricter documentation demand than the
base docstring ever made**, not a reproduced inconsistency. Consequence for the fix: L4 is only
simultaneously satisfiable if the repaired docstring keeps `RECORD-MISSING` for the missing path, adds
the EACCES wording to that class's row, and keeps `RECORD-MALFORMED` schema-only — and (a)/(c) then
print two different classes, which the repair must actually implement rather than re-document. If the
L1 prefers the narrower reading, the C2 paragraph and L4's `"EACCES"` clause are the bytes to amend;
the counter as currently written will not pass on a docstring-only repair of (a).

Also measured: the base `--rev` rejection surface is *shape-only* (`REFUSAL USAGE: --rev must be
40-hex`), so a repair that adds another regex cannot satisfy L1/L2 — the check has to be
`cat-file -e <rev>^{commit}` (resolvability), independent of the 40-hex gate. Legs L1 and L2 are then
distinguished only by which non-commit 40-hex value is passed; both must land on the same refusal.

## 5. Scratch / hygiene

- Scratch root used: `/fast/scratch/hyaku/souji-r39/W1ExecC2Repro/` (passed as `TMPDIR`). Contents:
  `new.py`, `drift-base.py` (extracted committed bytes), `probe.py`, `probe.out` (raw transcript).
  **Still on disk** — retained deliberately so the L1 can re-run `probe.py` against the landed bytes
  by swapping the two tool paths. `rec-absent.tsv`, `rec-locked.tsv`, `rec-dir` were removed after the
  run (`chmod` restored to 0600 before unlink).
- No git fixture was created; no `git init`, no mutating git/jj command was run anywhere. Read-only git
  used: `git show`, `git rev-parse`, and the tools' own `cat-file`/`merge-base`/`show` children.
- No tool was installed or upgraded (nothing needed; `python3` sufficed).
- Files written: this report only. No lane source, frozen receipt, spec, preregistration or
  `*-items.tsv` byte was touched.
