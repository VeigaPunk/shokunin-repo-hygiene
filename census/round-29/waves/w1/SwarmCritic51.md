# SwarmCritic51 — attack on the K2 stale-statement mechanism and the correction discipline

Seat: critic, round 29 `/home/vgpnk/Projects/shokunin/souji-shokunin`, base `691dd29211c53d0ef94fa072394cb9c8a69fe92e`, frozen prereg `b8cb4b31ce80e2e3314b88e85d40ea9873180804`. All experiments ran in a throwaway clone under `/var/tmp/souji-r29-SwarmCritic51/`; no lane byte was written.

## Status

STATUS: FAIL — K2 as frozen is satisfiable without any true correction. All nine junk states I constructed score `k2=0` under the frozen tool, including an empty-content marker (`R29-CORRECTION LOG.md:1758` and nothing else), a marker that *denies* the defect, and a state that keeps the pinned phrase verbatim while inverting the sentence around it. The lane's own frozen control already records this: `C1-junk1(markers only)` → `k2=0` with the marker text `junk marker`. A stricter-only second condition is specified below and tested: it rejects all nine, accepts a fact-carrying append, and leaves the base control at 10.

Axes impacted: **calibration** (the measuring instrument itself). No attack here touches operability or coverage counters; none requires an axis score change.

## Evidence

Tool under test: `tools/souji-registry-agreement.py` at `b8cb4b3` (sha256 `51131fe74faa95a1488ad6957d90b272a22c52171c257d9b97bb27c305b09801`), stale list `census/round-29/stale-statements.tsv` (sha256 `dccc57f235ff210ab19cc306afc75c9daf57e7ac069984e8132be14de61116fa`), both matching `census/round-29/records/frozen-digests.txt`. Lane working-tree digests equal HEAD for the tool, the stale list and `c2-counter.py` (`sha256sum` of working tree vs `git show HEAD:<path>` — identical), so the recorded base control is over frozen bytes today; the only dirty path is `.ufo/waves/round-26/w1/ScribeGateDraft.md`.

Base, frozen tool, `--list-rev b8cb4b3`:

```
$ python3 -B tools/souji-registry-agreement.py --root <scratch> --rev b8cb4b31ce80e2e3314b88e85d40ea9873180804 --list-rev b8cb4b31ce80e2e3314b88e85d40ea9873180804
K2 uncorrected LOG.md:1758 K2 uncorrected SCORECARD.md:23 K2 uncorrected corpus/lessons/round-28.md:22 K2 uncorrected corpus/lessons/round-28.md:40
SUMMARY k1=6 k2=4 mismatches=10 rev=b8cb4b31ce80e2e3314b88e85d40ea9873180804
```

Frozen statement list (`census/round-29/stale-statements.tsv:1`): `LOG.md	1758	two newline-containing path rows are improperly formatted`. The other three rows are `SCORECARD.md	23	2 malformed newline-path records`, `corpus/lessons/round-28.md	22	improperly formatted`, `corpus/lessons/round-28.md	40	two malformed newline-path records`.

Lane's own junk control (`census/round-29/records/controls.tsv:5`): `C1-junk1(markers only)	c1	SUMMARY k1=6 k2=0 mismatches=6` — the four markers it writes are `\nR29-CORRECTION {f}:{n} junk marker\n` (`census/round-29/controls.sh:28`). That row is a committed admission that K2 forces no content.

The accepted correction test (`tools/souji-registry-agreement.py:96`): `if not any(x.startswith('R29-CORRECTION ') and tag in x for x in lines[ln:]):`. It tests a prefix and a substring; it never reads the statement, the observed facts, or any receipt.

Facts the correction ought to carry, both derivable from frozen bytes at `b8cb4b3`:

```
$ git -C c show b8cb4b3:census/round-26/waves/manifest.sha256 | wc -l
1382
$ python3 -B census/round-29/c2-counter.py --root . --rev b8cb4b31ce80e2e3314b88e85d40ea9873180804
r26 records=1382 failed=152 uncovered=14 floor_violation=0
SUMMARY manifests=3 failed=152 uncovered=14 floor_violations=0 rev=b8cb4b31ce80e2e3314b88e85d40ea9873180804
```

Neither integer occurs anywhere in the three pinned files at base: `git grep -c '152' b8cb4b3 -- SCORECARD.md LOG.md corpus/lessons/round-28.md` → no output (0 matches in all three).

All attack revs below are commits in the scratch clone; every scored run used the frozen tool with `--rev <attack rev> --list-rev b8cb4b3`.

## Attack log

### A1 — empty-content marker passes (the assignment's test case)
`LOG.md` receives one appended line `R29-CORRECTION LOG.md:1758`, `SCORECARD.md` one `R29-CORRECTION SCORECARD.md:23`, `round-28.md` two lines naming `:22` and `:40`; no words, no facts, no receipt.
```
rev=82cb099758706629a9e22add062c1d44fe8e6a18
SUMMARY k1=6 k2=0 mismatches=6
```
Counterexample: the four corrections may be zero-byte statements. **Impacted axis:** calibration. **Smallest safe correction:** require the correction to carry the two derived integers (S3 below).

### A2 — marker that asserts the opposite and cites a nonexistent receipt
Markers read `R29-CORRECTION LOG.md:1758 no records are missing; the statement stands as written, see census/round-29/records/c1-after.tsv` (that path does not exist at `b8cb4b3`).
```
rev=0f6387308bc0c14fdae6470e3934f85959e2ccda
SUMMARY k1=6 k2=0 mismatches=6
```
Counterexample: a denial is accepted as a correction, and a dangling receipt pointer is not checked. **Impacted axis:** calibration. **Correction:** S3 (facts) + S4 (the named receipt must resolve at REV and be a derivation source) below.

### A3 — one marker line satisfies two statements; substring tags satisfy non-existent lines
One line in `round-28.md` naming `corpus/lessons/round-28.md:22 and corpus/lessons/round-28.md:40` satisfies both rows (4 statements covered by 3 lines): `SUMMARY k1=6 k2=0 mismatches=6` (rev `190110a1576a7490efc3ba6134f2c88f1ac02638`). Markers naming `LOG.md:17580`, `SCORECARD.md:230`, `round-28.md:220`, `round-28.md:400` — none of which exists — also score zero: `SUMMARY k1=6 k2=0 mismatches=6` (rev `91f8c2f8bf03de7147d1b4994a8148e34099f339`).
Counterexample: `tag in x` is a substring test, so the pointer names a line that does not exist. **Impacted axis:** calibration. **Correction:** delimit the tag (`(?<![0-9A-Za-z._/-])tag(?![0-9])`); the collapse itself is harmless (one line may name both lines of the same file) and stays allowed.

### A4 — keep the pinned phrase, invert the conclusion around it (false provenance)
`LOG.md:1758` is rewritten so the exact frozen phrase survives but the claim becomes "…two newline-containing path rows are improperly formatted (rc 0) **but every record is present and the receipt is complete**; r27 verifies cleanly"; `SCORECARD.md:23` is edited to "…(rc 0) **but no record is absent; receipt complete**, r27 clean". Four vacuous markers appended.
```
rev=d70534db9e3338e340214a7a5e9beb24edbdc319
SUMMARY k1=6 k2=0 mismatches=6
LOG.md:1758 -> "…(rc 0) but every record is present and the receipt is complete; r27 verifies cleanly."
grep -c 152 on that line -> 0
```
Counterexample: `phrase in lines[ln-1]` only pins the substring, so the sentence around it is freely rewritten and the record ends up *more* false than at base while the counter reports 0. This is the decisive one: it defeats the in-place-edit control the prereg relies on ("a repair that edits a stale phrase in place"). **Impacted axis:** calibration, plus the honesty of the correction it is supposed to enforce. **Correction:** S1 (byte-prefix append-only) + S2 (pinned line byte-identical to the frozen line, appearing exactly once).

### A5 — the append-only rule is not verified for any line but the pinned one
One earlier, unpinned historical line of `LOG.md` is rewritten (line 100, "completed / 15 failed on staggered waits — redundancy covered all critical" → "- rewritten history line (unpinned)") and four empty markers are appended:
```
rev=7f3a41ff58fda74a811a3a8a75eb06e1635dfd21
SUMMARY k1=6 k2=0 mismatches=6
```
A4 is the same hole applied to the pinned line; nothing compares base bytes with REV bytes, so any line may be rewritten as long as one line per file still carries its phrase and a marker follows. Base precedent that appending is the lane's own pattern: `LOG.md:1765` `### Round 28 wave result correction (2026-10-25)` is an appended section.
**Impacted axis:** calibration. **Correction:** S1 for every file named in the stale list.

### A6 — the stale list is read at REV unless `--list-rev` is passed, and the flag is optional
`tools/souji-registry-agreement.py:104` declares it as `revision to read the stale list from (default: --rev)`, and the frozen C1 paragraph writes it bracketed (`[--list-rev <prereg-commit>]`). Two scored-run trivialisations, both at a rev whose statements are untouched:
- Emptyed list: `printf '# emptied\n' > census/round-29/stale-statements.tsv` → `SUMMARY k1=6 k2=0` without the flag (rev `8fda36cbdb5dad4b5d45a7d2506e0c3e4d961309`); with the flag `k2=4`.
- Emptied *and* re-pointed list (`LOG.md	1	` with an empty phrase column, `R29-CORRECTION LOG.md:1 vacuous` appended): `k2=0` without the flag (rev `0f7e5ff8aeeee3683369a02aacd9da194d44465b`), while `grep -c 'improperly formatted'` on LOG.md:1758 is still 1 — the real statement is untouched.
Counterexample: `phrase in line` is true for an empty phrase, and `lines[ln:]` is satisfied by any marker further down. **Impacted axis:** calibration. **Correction:** make `--list-rev` mandatory (argparse `required=True`) and read the list only there.

### A7 — the C1 kill rule names a fixture that does not exist
The frozen kill rule (prereg `:5`) includes `the fixture (`tests/fixtures/r29-registry-agreement.py`) accepts an always-zero emitter`. `git ls-tree --name-only b8cb4b3:tests/fixtures/` lists no `r29-*` file, and `git log --all -- 'tests/fixtures/r29*'` is empty: the control cannot fire, and if it is authored after data by the seat that landed the repair it is a self-serving control. `census/round-29/records/frozen-digests.txt` pins six artefacts and does not include it.
**Impacted axis:** calibration (an unrun check reported as a kill rule). **Correction:** the anti-triviality property must live in the counter (S3/S4 are mechanically derivable and need no fixture), or the fixture must be committed and digested in a stricter-only amendment before the C1 landing commit.

### A8 — line drift: the round's own SCORECARD edit trips the counter
`SCORECARD.md` is newest-first in its measurement sections (`### Round 28` at 17, `### Round 27` at 27, `### Round 25` at 36), so the natural Round 29 edit inserts a block *above* line 23. With an honest, fact-carrying correction appended and a 6-line Round 29 block inserted after line 16:
```
rev=cdffea6e9dd2a7222b19f2668084ff567cd2017e
K2 phrase-moved-or-edited SCORECARD.md:23
SUMMARY k1=6 k2=1 mismatches=7
phrase now at line 29
```
Counterexample against the lane: an honest correction plus a legitimate insertion yields a non-zero score, and the exact finding string the C1 kill rule keys on is raised on a seat that did nothing wrong. Note the file already appends out of order (`### Round 26 append-only corrections` at 259, `### Round 26 measurements` at 284, below Round 23), so appending the Round 29 section at the end violates no existing convention. **Impacted axis:** calibration (false positive). **Correction:** S1 makes drift impossible and reports the true cause (`rewrote-not-appended`); the L1 appends the Round 29 SCORECARD block instead of inserting it.

### A9 — the same falsehood exists in unpinned lines
Phrase-family sweep at `b8cb4b3` (`git grep -nE 'newline-path|newline-containing|malformed newline' b8cb4b3 -- SCORECARD.md LOG.md corpus/lessons/round-28.md`) returns five lines, only four of which are in the stale list. Unpinned: `SCORECARD.md:25` — `C3 has an independently unverifiable pair of newline-path manifest rows` — which repeats the same two-record framing. An honest append-only correction can score `mismatches=0` while that sentence still stands. **Impacted axis:** calibration. **Correction:** add `SCORECARD.md:25` to the stale list in a stricter-only logged amendment (it is the same defect, and the list predates the data, so no predicate is weakened). `corpus/lessons/round-28.md:8` and `:26` make a *different*, defensible claim ("tool-internal generation/recheck alone does not establish an independently consumable manifest") and should stay unpinned.

### Non-attack (checked, clean)
- No line-splitting hazard: `LOG.md`, `SCORECARD.md`, `corpus/lessons/round-28.md` contain no `\r`, `\x0b`, `\x0c`, `\x1c`-`\x1e` or `\x85` at base (`grep -cP` → 0 each), so `str.splitlines()` and a text reader agree on the pinned numbers today.
- Pre-seeded markers are not a hole: the base control pins `k2=4` at `691dd29`/`b8cb4b3`, so a marker committed before the repair would already reduce the recorded base.
- `blob()` decodes with `errors='replace'` (`tools/souji-registry-agreement.py:28`); any new byte-exact condition must compare bytes, not decoded text.

## Proposal — strictest feasible K2 (tested)

Four conditions, each stricter-only, plus a mandatory flag. Implemented in scratch as `strict.py` (a copy of the frozen tool with `k2` replaced) and scored against every attack rev.

- **S1 append-only by bytes.** For each file named in the stale list: `blobbytes(rev, path).startswith(blobbytes(list_rev, path))`, else `K2 rewrote-not-appended <path>`. This is what "append-only" means; it makes line drift impossible, so the `file:line` pin stays exact forever, and it closes A4/A5. It constrains only the revs measured this round (C1 landing commit and final tip) — it is not a permanent ledger lock.
- **S2 statement integrity.** Line `ln` at REV must be byte-identical to line `ln` at `list_rev`, and that exact line must occur exactly once in the file (`statement-moved-or-edited`, `statement-duplicated`).
- **S3 facts.** The correction line must contain, as delimited decimal tokens, the two integers derived mechanically from frozen bytes — **not typed by the author**: run the digest-pinned `census/round-29/c2-counter.py` at `list_rev` and take the r26 line's `records=` and `failed=` (here `1382` and `152`); refuse to evaluate if the executed counter's sha256 differs from `census/round-29/records/frozen-digests.txt`.
- **S4 provenance.** The correction line must name (a) the delimited `path:line` tag and (b) at least one repo path that resolves to a blob at REV **and is one of the derivation sources** (`census/round-29/c2-counter.py`, `census/round-29/records/frozen-digests.txt`, `census/round-26/waves/manifest.sha256`). Numbers typed without citing their derivation are rejected.
- **S0 flag.** `--list-rev` becomes `required=True`; the tool never reads the list at the measured rev.

Scored results (frozen tool vs strict double, `--list-rev b8cb4b3`):

| state | rev | frozen | strict |
|---|---|---|---|
| base do-nothing | `b8cb4b3` | `k1=6 k2=4 mismatches=10` | `k1=6 k2=4 mismatches=10` |
| A1 empty marker | `82cb0997…` | `k2=0` | `k2=4` |
| A2 denial | `0f638730…` | `k2=0` | `k2=4` |
| A3 collapse / substring tags | `190110a1…`, `91f8c2f8…` | `k2=0` | `k2=4` |
| A4 reword around phrase | `d70534db…` | `k2=0` | `k2=6` (`rewrote-not-appended`, `statement-moved-or-edited`) |
| A5 unpinned earlier line rewritten | `7f3a41ff…` | `k2=0` | `k2=5` |
| A8 drift + insert above the pin | `cdffea6e…` | `k2=1` | `k2=5` |
| A6 emptied list at REV | `8fda36cb…`, `0f7e5ff8…` | `k2=0` (no flag) | `k2=4`; without the flag argparse exits 2 |
| numbers but wrong receipt (`census-start.txt`) | `dc5b85fe…` | `k2=0` | `k2=4` |
| honest append (states 152 and 1382, cites the counter and the manifest, Round 29 table appended at the end) | `a1fa7db8…` | `k2=0` | `k2=0` |
| honest append with the Round 29 table inserted above line 23 | `670ac65d…` | `k2=1` | `k2=5` |
| `c2-counter.py` edited at the measured rev | `74f01a13…` | — | facts unchanged (executed from `list_rev`), `k2=4` |

The patch, as tested (insertion points in the frozen tool: replace `def k2` at `:75` and the `--list-rev` argument at `:104`):

```python
def blobbytes(root, rev, path):
    p = git(root, 'cat-file', 'blob', f'{rev}:{path}', check=False)
    return None if p.returncode else p.stdout

def facts(root, list_rev):
    import hashlib
    pins = blob(root, list_rev, 'census/round-29/records/frozen-digests.txt') or ''
    pinned = dict(reversed(l.split()) for l in pins.splitlines() if len(l.split()) == 2)
    src = blobbytes(root, list_rev, 'census/round-29/c2-counter.py')
    if src is None:
        raise RuntimeError('c2-counter.py unreadable at list_rev')
    if pinned.get('census/round-29/c2-counter.py') != hashlib.sha256(src).hexdigest():
        raise RuntimeError('c2-counter.py digest differs from the frozen pin')
    p = subprocess.run([sys.executable, '-B', '-', '--root', root, '--rev', list_rev], input=src, capture_output=True)
    for l in p.stdout.decode().splitlines():
        m = re.match(r'r26 records=(\d+) failed=(\d+)', l)
        if m:
            if m.group(2) == '0' or m.group(1) == '0':
                raise RuntimeError('derived facts are trivial')
            return m.group(2), m.group(1)          # absent, total
    raise RuntimeError('frozen counter produced no r26 line at list_rev')

TAGCHK = lambda path, ln: re.compile(r'(?<![0-9A-Za-z._/-])' + re.escape(f'{path}:{ln}') + r'(?![0-9])')
NUMTOK = lambda n: re.compile(r'(?<![0-9])' + re.escape(n) + r'(?![0-9])')
PATHTOK = re.compile(r'[A-Za-z0-9._][A-Za-z0-9._/-]*\.(?:tsv|txt|md|sha256|json)(?![A-Za-z0-9._/-])')
DERSRC = {'census/round-29/c2-counter.py', 'census/round-29/records/frozen-digests.txt',
          'census/round-26/waves/manifest.sha256'}

# inside k2(): before the per-row loop
        absent, total = facts(root, list_rev)

# inside the per-row loop of k2(), replacing lines 88-98 of the frozen tool:
        base = blob(root, list_rev, path)   # read alongside the existing body = blob(root, rev, path)
        bb, rb = blobbytes(root, list_rev, path), blobbytes(root, rev, path)
        if not rb.startswith(bb):
            out.append(f'K2 rewrote-not-appended {path}')
        want = base.splitlines()[ln - 1]
        if phrase not in want:
            raise RuntimeError(f'stale list phrase not at list_rev {path}:{ln}')
        if lines[ln - 1] != want:
            out.append(f'K2 statement-moved-or-edited {path}:{ln}'); continue
        if sum(1 for x in lines if x == want) != 1:
            out.append(f'K2 statement-duplicated {path}:{ln}'); continue
        if not any(x.startswith('R29-CORRECTION ') and TAGCHK(path, ln).search(x)
                   and NUMTOK(absent).search(x) and NUMTOK(total).search(x)
                   and any(c in DERSRC and blob(root, rev, c) is not None for c in PATHTOK.findall(x))
                   for x in lines[ln:]):
            out.append(f'K2 uncorrected-or-unevidenced {path}:{ln}')
```

Amendment bookkeeping the L1 owes if it adopts this (all stricter-only, none weakens a predicate): log the change in `corpus/lessons/round-29.md`, commit the amended tool **before** the C1 repair commit, record its new sha256 next to the frozen one (the frozen digest `51131fe7…` stays as the base instrument), and re-run the do-nothing control with the amended tool — expected `mismatches=10`, measured above. If the L1 instead keeps the frozen tool, the achievable evidence is strictly weaker: `k2=0` would then certify only that four lines starting with `R29-CORRECTION ` exist, which A1/A2/A4 show is not a correction.

## Residual limit of any mechanical fix

S1-S4 force the two observed integers *into* the record next to an unmodifiable stale statement and force the pointer to a derivation receipt; they cannot judge whether the appended prose contradicts itself. A correction that states "152 of 1382 absent" and then adds "the receipt is complete" would pass. That residue is a reviewer duty, but the pair (byte-frozen falsehood + fact-carrying correction in the appended tail) is auditable, whereas today's `k2=0` is not.

## Deliveries

- `.ufo/waves/round-29/w1/SwarmCritic51.md` (this report).

No lane file was written, no git/jj mutation outside the scratch clone (`/var/tmp/souji-r29-SwarmCritic51/d.zdlaCq`, removed), no tool installed or upgraded, no subagent dispatched.
