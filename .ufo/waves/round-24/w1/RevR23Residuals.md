# RevR23Residuals — round-23 C1/C2 residual limits vs round-24 C3

Seat: L1Souji24.RevR23Residuals (revenger, read-only). Lane revision
`f9db2181647d91470a724a12d626bd6106805076` (HEAD, branch master). Preregistration read first:
`.ufo/waves/round-24/preregistration.txt` blob `26d00b07`.

## Status

STATUS: PASS — both requested facts are confirmed from the committed code and by an executed probe: (i) `cmd_verify` never calls `durable_rev`, and (ii) `tool=` is never compared with `cmd=`. I list 21 residual limits for C1/C2. C3 fully closes 1, partially closes 6, and leaves 12 open; 2 were already closed in r23. None of them needs an operator ruling.

## Evidence

Sources were read as committed bytes (`git show HEAD:<path>`). Blob ids at HEAD:

| path | HEAD blob | worktree |
|---|---|---|
| corpus/lessons/round-23.md | 7e188da2 | same |
| LOG.md | 9d91a32d | same |
| SCORECARD.md | 4c143440 | same |
| .ufo/waves/round-23/w2/W2C2Verify.md | 2e866ad9 | same |
| .ufo/waves/round-23/w2/W2K1.md | e2fb2bef | **a8faff4c (uncommitted edit, not mine)** |
| .ufo/waves/round-23/w1/MutReceipt.md | cdb16775 | same (the brief puts it in w2; it is in w1) |
| tools/souji-receipt-run.py | a7eeb43c (sha256 e13d0c83…) | same |
| tools/souji-record-agreement.py | 3a90ddc6 (sha256 dd53c228…) | same |
| tests/fixtures/r23-receipt-run.py | ba4347ca | same |

The findings use the committed W2K1 text. Where only the uncommitted revision names something, the finding says so.

### Code read: `cmd_verify` and `durable_rev` (tools/souji-receipt-run.py at HEAD)

`git show HEAD:tools/souji-receipt-run.py | grep -nE 'durable_rev|\["cmd"\]|header\["tool"\]'` returned:

```
126:def durable_rev(root: str, rev: str) -> bool:
152:    if not durable_rev(root, rev):
272:    tool = header["tool"]
```

- **(i)** `durable_rev` is defined at line 126 and called only at line 152, inside `cmd_run`. `cmd_verify` (lines 259–282) does four things in order: `parse_receipt`, the `REV_RE` shape check (270), `blob_sha_bytes(root, rev, tool)` (273), and the `COUNTS_RE` search (279). Its refusal codes are RECEIPT-UNREADABLE, -MALFORMED, -REV-MALFORMED, -TOOL-ABSENT, -TOOL-DIGEST-MISMATCH and -COUNTS-ABSENT. There is no durability refusal. Line 270 quote: "if not REV_RE.match(rev):".
- **(ii)** `header["cmd"]` is not read anywhere in the file. `cmd` occurs only in `HEADER_ORDER` (62), where it is used for header order and presence. `cmd_run` also never compares `--tool` with `args.command` (lines 154–166). The digest comes from `os.path.join(tree, tool)` (208), whatever program actually runs. Line 272 quote: "tool = header["tool"]".

### Executed probe (scratch `/var/tmp/souji-r24-RevR23Residuals/`, synthetic `git init` repo, removed)

- Runner and record-agreement bytes were extracted with `git show f9db218:<path>` (sha256 `e13d0c83…` and `dd53c228…`). Versions: git 2.56.0, Python 3.14.8.
- Repo setup: commit A on master holds `tools/t.py` and `tools/other.py`. N is a `commit-tree` child of A that no ref reaches; later a `refs/jj/keep/probe` ref is pointed at N.

```
run --rev A --tool tools/t.py -- python3 -B tools/t.py          -> rc=0 ; verify -> verify=ok rc=0
run --rev N ...                                                 -> REV-NOT-DURABLE rc=2, r-N.tsv not written
verify <A receipt relabelled rev=N>                             -> verify=ok rc=0           # (i) asymmetry
refs containing N: refs/jj/keep/probe ; run --rev N             -> REV-NOT-DURABLE rc=2
verify <relabelled rev=N> (jj ref only)                         -> verify=ok rc=0           # Q37 read side open
run --tool tools/t.py -- python3 -B tools/other.py              -> receipt cmd=python3 -B tools/other.py, stdout entries=9 ok=9 fail=0
verify <that receipt>                                           -> verify=ok rc=0           # (ii) label unbound
verify <A receipt with cmd= hand-edited to tools/other.py>      -> verify=ok rc=0
run --tool tools/t.py -- python3 -B tools/other.py tools/t.py   -> tool_in_argv=True, stdout entries=9 (other.py ran); verify=ok rc=0
verify <A receipt, empty stdout fence, counts only in stderr>   -> verify=ok rc=0
record-agreement counts_of(<stdout mismatches=7, then after stderr fence mismatches=0>)
  -> ('assertions=63 resolved=63 skipped=40 mismatches=0', '9301d98c…')
```

### Regression baseline for C3 case d (lane root, read-only `verify` only, at f9db218)

I verified each of the five receipts (`census/round-23/records/<r>.tsv`) with the committed runner. I also checked whether each rev is reached by a durable ref (`for-each-ref --contains`) and whether each `tool=` path appears as an element of `shlex.split(cmd)`:

```
declared-evidence-after      verify=ok  durable(refs/heads/master,origin/*)  tool_in_argv=True
gate-check-at-first-landing  verify=ok  durable                               tool_in_argv=True
gate-check-at-lane-base      verify=ok  durable                               tool_in_argv=True
gate-check-c3                verify=ok  durable                               tool_in_argv=True
agreement-after              verify=ok  durable                               tool_in_argv=True
```

Case d therefore does not conflict with cases a and b at the current refs.

## Findings

Each finding gives: the quote, whether it is actable without an operator ruling, and the C3 verdict. None of these residuals touches deletion authority, F5 reap, K5, NAMESPACE or certification, so every one is **actable without an operator ruling**. R5 and R19 are exceptions in a different sense: they are design bounds that can be disclosed but not closed by any instrument.

**C2 instrument (tools/souji-receipt-run.py)**

1. **R1 — verify accepts a non-durable rev.**
   - Source: corpus/lessons/round-23.md:159 "`verify` still accepts a non-durable rev while `run` refuses it (asymmetry, disclosed)". Also W2C2Verify.md:236, F3: "`cmd_verify` never calls `durable_rev` (`:123`), so the Q37 rule ("refs/jj/* never counts") is enforced on the write side and not on the read side."
   - State at HEAD: confirmed (Evidence (i), plus the probe).
   - Actable: yes. Adding the check is behaviour-neutral for the five receipts, which all name durable revs.
   - C3: **closes** it on the frozen letter (case a). There is a gap on the `refs/jj/*` sub-shape; see attack A2.
2. **R2 — `tool=` is not bound to argv.**
   - Source: lesson:160 "the `tool=` label is not bound to argv (disclosed)". Also W2C2Verify.md:269–271, P6: "A receipt naming `tool=tools/souji-gate-check.py` while its `cmd=` ran `tools/souji-record-agreement.py` verifies."
   - State at HEAD: confirmed (Evidence (ii), plus the probe).
   - Actable: yes.
   - C3: **partially closes** it. Case b's predicate ("does not occur as an argv element") is met by a command where the tool appears only as an operand while a different program runs. The probe shows `tool_in_argv=True`, `verify=ok`, and other.py's stdout. See attack A1.
3. **R3 — the docs overstate what the digest binds.**
   - Source: W2C2Verify.md:271–272, F4: "`SCORECARD.md:92` and `report-draft.md:25` say "tool sha256 of the bytes the command ran against" — false as written."
   - State at HEAD: the sentence is still present at SCORECARD.md:92 and LOG.md:1588 ("tool sha256 of the bytes the command ran against").
   - Actable: yes (a one-sentence fix).
   - C3: **leaves it open**. The fix is not a counter case, and after case b lands the sentence is still false (A1).
4. **R4 — `rev=` can be relabelled to another durable rev that holds the same tool bytes, and still verify.**
   - Source: W2C2Verify.md:198, P2/F2: "So `verify=ok` proves the *tool bytes* at rev, not that the receipt was produced there."
   - State at HEAD: no `tree=` binding exists. SCORECARD:30–31 discloses only "a receipt binds bytes, not execution"; the relabel shape is not named in SCORECARD or LOG (`git grep -i relabel` turned up only older rounds).
   - Actable: yes (disclose it, or add `tree=`).
   - C3: **partially closes** it. Case a refuses relabels to non-durable revs only. Relabels to durable revs with identical bytes (18 of 30 in W2C2Verify's matrix) still pass.
5. **R5 — a receipt binds bytes, not execution.**
   - Source: lesson:40 "Receipts bind bytes, not execution — a typed receipt passes `verify`, and that is why Q55 exists." Also LOG.md:1595–1596.
   - Actable: it can be disclosed; no instrument can close it. This is a design bound, not an operator matter.
   - C3: **partially closes** it (narrows only). Case b refuses typed receipts whose `cmd=` omits the tool path. Every other typed field still passes.
6. **R6 — edits to `cmd`, `rc`, `utc` and `stdout` still verify.**
   - Source: W2C2Verify.md:245–248, P5, e.g. "cmd= rewritten to a different tool → rc=0" and "rc=0 → rc=7 → rc=0". This was accepted as pre-disclosed (F7).
   - State at HEAD: the probe's cmd edit returns `verify=ok`.
   - C3: **partially closes** it. Only a `cmd=` edit that drops the tool path will be refused. Edits to `rc`, `utc` and `stdout` stay open.
7. **R7 — verify finds a counts line in stderr, so an empty stdout fence still verifies.**
   - Source: W2C2Verify.md:255–256, P5/F5: "`parse_receipt` stores `_body` from the stdout fence onward (`:234`) and the counts check searches that whole body".
   - State at HEAD: runner lines 255 and 279 are unchanged, and the probe returns `verify=ok`.
   - Actable: yes.
   - C3: **leaves it open**.
8. **R8 — a nonexistent rev is reported as tool absence.**
   - Source: W2C2Verify.md:283, P7: "the code misattributes the cause (a rev that does not exist is not a tool problem)".
   - State at HEAD: line 275 is unchanged.
   - C3: **leaves it open**. [INFERENCE] If the durability check runs before the digest compare, a nonexistent rev would surface as RECEIPT-REV-NOT-DURABLE, because `for-each-ref --contains` fails on it. The preregistration does not fix that order.
9. **R9 — the replace hardening has no fixture case.**
   - Source: W2C2Verify.md:126–127: "extend `tests/fixtures/r23-receipt-run.py` with a case-9 that creates a `refs/replace` ref and expects `RECEIPT-TOOL-DIGEST-MISMATCH`".
   - State at HEAD: the code is hardened (`blob_sha_bytes` lines 134–136 set GIT_NO_REPLACE_OBJECTS/GIT_NO_LAZY_FETCH, which closes W2C2Verify F1, F8 and the lazy-fetch residual). The fixture `CASES` (lines 482–489) still holds only cases 1–8.
   - C3: **leaves it open**.
10. **R10 — nothing kills mutant M05 (digest read from the working tree instead of the tree at rev).**
    - Source: lesson:132 "Disclosed as a fixture coverage limit, not repaired." Also MutReceipt.md:95–96.
    - Actable: yes. MutReceipt.md:112–114 specifies the case: `reset --soft`, then `run --rev rev1`.
    - C3: **leaves it open**. Case c is a clean run where the working tree equals rev, so it cannot separate the two.
11. **R11 — 17 of 26 runner mutants are uncovered.**
    - Source: MutReceipt.md:3–4 "26 mutants over 21 clauses … 9 killed, **uncovered=17**". The uncovered list (MutReceipt.md:171–174) is M01, M03/M03b, M08, M11, M12, M15/M16, M18–M21, M23 and C13.
    - C3: **partially closes** it. Case a adds a verify-side durability clause, but M03/M03b mutate the *run*-side check (line 152), which neither case a nor case c exercises. Everything else stays open.
12. **R12 — the "verbatim" capture claim is false.**
    - Source: MutReceipt.md:137–140: "`\r` is still replaced … `rstrip("\n")` … still drops trailing newlines".
    - State at HEAD: the docstring says "<verbatim>" (lines 23 and 25), while `CTRL_RE.sub` (81), `text=True` (214) and `rstrip("\n")` (228, 230) rewrite the bytes. The non-UTF-8 abort is fixed (`errors="replace"`, lines 212–215).
    - Actable: yes (fix the docs or the code).
    - C3: **leaves it open**.
13. **R13 — the clone call has no environment scrub.**
    - Source: MutReceipt.md:164–166: "this `git` invocation is the only one without the environment scrub and `-c maintenance.auto=false`".
    - State at HEAD: lines 178–179 still pass no `env=` and no `-c maintenance.auto=false`. The sparse-checkout and checkout calls (184–197) also inherit `GIT_*`.
    - Actable: yes.
    - C3: **leaves it open**.
14. **R14 — the read-only check misses transient writes.**
    - Source: MutReceipt.md:150–151: "M09 (a scratch directory created inside `--root` and removed in the `finally`) is not" killed. Plain `--porcelain` also misses ignored paths and anything inside `.git/`.
    - C3: **leaves it open**.

**C1 instrument (tools/souji-record-agreement.py)**

15. **R15 — K1 decoy line: K1 is not anchored to the calibration row.**
    - Source: committed W2K1.md:86, F2: "the binding is not anchored to the C1 calibration row; any line anywhere satisfies it". Named as a limit at lesson:145–146: "K1 binds per line".
    - State at HEAD: K1 (lines 172–205) still counts any scoped line.
    - Actable: yes, as a new-round repair of the r23 counter. That is not a predicate change inside r24.
    - C3: **leaves it open**. It is outside C3's surface.
16. **R16 — K1 ignores `tool_sha256`.**
    - Source: committed W2K1.md:115–116, F5: "K1 binds value+rev text; receipt integrity is verify's job". The lesson's disposition (lines 145–146): "`verify` remains the authority on tool digests".
    - C3: **leaves it open**, as designed. C3 strengthens `verify`, which is the authority K1 defers to.
17. **R17 — K1 counts parsing: last-wins admits a trailing shadow, and this residual is NOT named in the committed record.**
    - Background: committed W2K1 F4 (first match taken anywhere) is closed by last-wins (record-agreement lines 121–126). But the docstring at lines 118–119 says "Only the header region before the `--- stdout ---` fence is a receipt's own claim", while the code is `matches = COUNTS_RE.findall(text)` … `m = matches[-1]` over the whole receipt.
    - Probe: stdout `mismatches=7`, then `mismatches=0` after the stderr fence, gives `counts_of` → `mismatches=0`.
    - The lesson (lines 142–146) names only F2 and F5 as limits. This shape appears only in the *uncommitted* W2K1 revision (blob a8faff4c, F4 "trailing shadow").
    - Divergence: the code contradicts its docstring, and the committed record does not carry the residual.
    - Actable: yes.
    - C3: **leaves it open**.
18. **R18 — K4 is a live-worktree observation.**
    - Source: lesson:41 "K4 is a live-worktree observation, not a revision snapshot." Also SCORECARD:30.
    - This is a design bound.
    - C3: **leaves it open**.
19. **R19 — 28 record-agreement mutants are uncovered.**
    - Source: lesson:131 "28 are uncovered by the fixture's 9 cases".
    - Actable: yes (fixture cases). Committed W2K1:63–67 also names the missing token-moved, decoy and shadow cases.
    - C3: **leaves it open**.
20. **R20 — the after-receipt is not bound to the closing tip.**
    - Source: committed W2K1.md:130–131: "`agreement-after.tsv` binds 3b72bea, not the current tip 466f539 … the round should re-bind at the final landing rev". It now binds `eb1aa49`.
    - The non-author spot-check (corpus/lessons/round-23-verifier-spotcheck.md:16) re-ran K1 at `2f96bf4` and got `mismatches=0`, so the gap is closed for r23.
    - SCORECARD:134 plans to "re-run the r23 counters at the new tip". C3 case d *re-verifies* the receipt bytes; it does not re-run the counter.
    - C3: **partially closes** it relative to SCORECARD:134.
21. **Closed in r23 itself (no action).**
    - Committed W2K1 F1 (unbound tuple) is closed at record-agreement:197–202 (`unbound-tuple`).
    - Committed W2K1 F3 (rev not resolved) is closed at lines 170–171 (`receipt-rev-object`).
    - W2C2Verify F1, F8 and the lazy-fetch residual are closed by `blob_sha_bytes` lines 134–136.

**Tally (R1–R20):**
- Closes: 1 (R1).
- Partially closes: 6 (R2, R4, R5, R6, R11, R20).
- Leaves open: 12 (R3, R7, R8, R9, R10, R12, R13, R14, R15, R17, R18, R19).
- Open by design, with C3 strengthening the authority it defers to: 1 (R16).
- Already closed in r23: item 21 (2 K1 findings plus the verify-hardening group).

## Attack log

These are reported as ATTACKS. I propose no change to the frozen counter.

- **A1 (C3 case b is gameable by operand placement).** The case-b predicate is "`tool=` path does not occur as an argv element of its `cmd=`". On the committed runner, `run --tool tools/t.py -- python3 -B tools/other.py tools/t.py` writes a receipt with `tool_in_argv=True` and stdout from other.py, and `verify=ok`. A runner that satisfies case b exactly still leaves W2C2Verify P6 ("the `--tool` digest does not bind the executed program") true. `refusals=2/2` must not be reported as closing P6. The most it can claim is "label present in argv".
- **A2 (C3 case a does not pin the Q37 `refs/jj/*` shape).** Case a requires "a full commit reachable from no durable ref". A fixture commit reachable from *no ref at all* would also pass a verify-side check that wrongly counts every ref, including `refs/jj/*`, as durable. The probe shows that a jj-only ref is a distinct live shape: run refuses it, while verify today returns `verify=ok`. Unless the case-a fixture uses a `refs/jj/*`-only commit, the "refs/jj/* never counts" half of R1 is untested.
- **A3 (control and regression values checked).** At base, verify accepts both case-a and case-b shapes (probe), which matches "the base runner -> refusals=0/2". All five regression receipts are durable and tool-in-argv at f9db218, so `regress=5/5` is reachable without tension. Durability depends on the refs present when it is checked: case d is evaluated "against the lane root", so deleting or rewinding refs/heads/master or refs/remotes/origin/* would flip it. [INFERENCE] No such operation is planned in any byte I read.
- **A4 (scope calibration).** The preregistration header routes "residual C1/C2 limits of r23", and SCORECARD:134 says "close the residual C1/C2 limits named above". C3 takes 2 of the 20 residuals (R1, R2). A round-24 record that says "r23 residuals closed" without naming R3–R20 would overstate, which is a calibration harm on the lowest axis.

No tool was installed or upgraded (git 2.56.0 and Python 3.14.8 were already present). The scratch directory `/var/tmp/souji-r24-RevR23Residuals/` was removed. The only file this seat wrote in the lane is this report.
