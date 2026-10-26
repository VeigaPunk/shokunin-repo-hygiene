# SwarmCritic36 — attack on M1 (record-contract guard, r32 wave 1)

STATUS: PARTIAL — the M1 receipt is honest and reproducible, the reconstructed r31 contract is faithful to its frozen line, and the named dodge "contract edited at REV" is blocked; but the guard pair (tool + C3 L14) is narrower than the frozen catalog it enforces, and one reproduced record shape carries out-of-contract values past all fourteen legs.

## Evidence

Lane root `/home/vgpnk/Projects/shokunin/souji-shokunin` at `7a6667cd27652baf8d704b5cdb8e3200bd6e27a1`; frozen prereg `3ec84fc81b3243429c834a051880b0bcde06291c`; base `85b61a151923986e7e6b48f7084b9122561b5f3d`. Scratch `/fast/scratch/hyaku/souji-r32/AttackM1/` (removed after writing this report; `TMPDIR` created and exported there). No tool installs.

**1. Red-before reproduces byte-identically and fails for the right reason.**

```
$ python3 -B tools/souji-record-contract.py --record census/round-31/records/jj-object-clock-run.txt \
    --contract census/round-32/m1-r31-contract.txt
BAD 16 arm=reflog-only outside descendant|solo
BAD 17 arm=reflog-only outside descendant|solo
BAD 18 arm=reflog-only outside descendant|solo
BAD 19 arm=reflog-only outside descendant|solo
lines=17 bad=4
exit=1
```

`diff` of lines 2-6 of `census/round-32/records/m1-red-before.txt` against this rerun: empty (`RECEIPT-BYTES-MATCH`). BAD lines 16-19 are exactly the four `arm=reflog-only` lines of `census/round-31/records/jj-object-clock-run.txt:16-19`; no other line is flagged, so the failure is the frozen-contract violation, not a parse artefact. The r31 record blob is unchanged from its landing commit to HEAD (`git rev-parse 85b61a1:…` and `HEAD:…` both `63502d12a74b532da887d0a05da2c1f5b1f98786`), so the red-before audits the landed record, not a later edit.

**2. The reconstruction is faithful to the frozen r31 line.** `census/round-31/records/preregistration.txt:20` freezes the RESULT grammar as `arm=<solo|descendant> step=<name> keep_refs=<n> target_keep=<yes|no> reflog_hits=<n> object_present=<yes|no>`. `census/round-32/m1-r31-contract.txt:4-10` maps that one-to-one: same six keys, same order, `solo`/`descendant` literal, `step` to `*`, the two counts to `#`, both yes/no fields literal. No key is added, dropped or reordered.

**3. Positive control — the tool discriminates.** Lines 1-15 of the same record (keys + the 13 conforming RESULT lines) give `lines=13 bad=0`, exit 0. So "shown able to fail" is not an always-fail instrument.

**4. Named dodges, tested.**

- *Contract edited at REV*: blocked. In a scratch clone, `--list-rev 3ec84fc…` against a rev that appends one comment line to `census/round-32/c3-contract.txt` prints `L14 FAIL lines=8 contract_unchanged=False bad=[]`; unchanged-rev control prints `L14 PASS lines=8 contract_unchanged=True bad=[]`.
- *Extra spaces*: pass L14 (`L14 PASS`) and the tool, and no value escapes — benign, see F3.
- *Second record*: `L14 PASS` with an out-of-contract `census/round-32/records/jj-mtime-clock-extra.txt` present at REV; the tool over that same blob prints `BAD 1 arm=reflog-only outside mixed|never|nocruft|old|recent`, `lines=1 bad=1`, exit 1. L14 opens only `RUN` (`c3-counter.py:52,:236`).

**5. The escape (reproduced).** A RESULT line whose separator is not one ASCII space is outside both implementations' scope but inside the frozen contract's wording.

```
$ python3 -B tools/souji-record-contract.py --record r8-c3-mixed.txt --contract census/round-32/c3-contract.txt
lines=2 bad=0          # 2 valid lines + "RESULT\tarm=bogus …" + BOM-prefixed bogus line
exit=0

$ python3 -B tools/souji-record-contract.py --record r9-bare.txt --contract census/round-32/c3-contract.txt
lines=1 bad=0          # 1 valid line + bare "RESULT" + "RESULT\tarm=bogus …"
exit=0
```

Counter-side confirmation through its own functions (`results` + `contract_bad` imported from `census/round-32/c3-counter.py`): `in_scope_lines: 1 contract_bad: []` for the same blob. End-to-end: a scratch rev whose RUN is a clean 8-line record plus an appended `RESULT\tarm=reflog-only …` line prints `L14 PASS lines=8 contract_unchanged=True bad=[]` and `SUMMARY legs=14 fail=12` — the same fail count as the clean control, i.e. the appended violated line moves no leg.

**6. Wildcard over-acceptance in the tool (reproduced).**

```
$ … --record r4-unidigit.txt --contract census/round-32/m1-r31-contract.txt
lines=1 bad=0   exit=0     # keep_refs=²  reflog_hits=٣  both accepted under "#"
$ … --record r5-stareq.txt  --contract census/round-32/m1-r31-contract.txt
lines=1 bad=0   exit=0     # step=abandon=extra accepted under "*"
$ … --record r6-emptyval.txt --contract <contract whose object_present line ends with "yes|no|">
lines=1 bad=0   exit=0     # object_present= (empty value) accepted
$ … --record r7-reordered.txt --contract census/round-32/m1-r31-contract.txt
BAD 1 keys […] != […]  lines=1 bad=1  exit=1
```

`str.isdigit()` is true for `²` and for Arabic-Indic digits, so `#` admits non-count tokens; `*` admits any non-empty token, including one containing `=`; a trailing `|` in a contract line puts the empty string in the set, and an empty field then satisfies membership. None of these touches r32: `census/round-32/c3-contract.txt:6-11` uses literal members only, and the counter's parser (`contract_bad`, `c3-counter.py:83-104`) has no wildcard branch, so a wildcard contract would fail closed there.

**7. Full leg report for the escape chain's last hop.** `c3-counter.py:253` `spans = re.findall(r"`(RESULT [^`]+)`", e)`: a tab-quoted span yields `[]`, a space-quoted span yields the span. So an entry quoting a tab-separated RESULT line has that span neither captured nor checked against RUN.

## Findings

1. **The in-scope test is narrower than the frozen contract (defect, reachable).** `census/round-32/c3-contract.txt:3-4` says: "Every line of the record that starts with `prefix` must carry exactly these keys". `tools/souji-record-contract.py:44` (`line.startswith(prefix + " ")`) and `census/round-32/c3-counter.py:76` (`l.startswith("RESULT ")`) require the extra space. A line beginning `RESULT` followed by a tab, or a bare `RESULT`, is therefore both in the contract's scope and invisible to the guard; the tab line can carry any values, including `arm=reflog-only`. Impacted axis: coverage (C3's D1 guard). This is the one case where the M1 class reproduces after the fix.
2. **Two parsers, one wired, and the demonstrated one is the weaker.** `tools/souji-record-contract.py` is referenced by no script in the lane (grep for `souji-record-contract` over `*.py`/`*.sh` returns only the file itself); the live guard is L14's re-implementation. This matches the prereg's wording ("the tool plus L14") but means the tool's wildcard leniency is untested against C3. Sibling `deliver-cross-claim.md` F5 records the parity and the drift; it treats the pair as equivalent today, which is true — the tab/bare hole is shared, so parity does not imply safety.
3. **The r31 reconstruction drops one clause of the same frozen sentence.** `census/round-31/records/preregistration.txt:20` also freezes "no hashes or timestamps on RESULT lines". `step: *` admits `step=deadbeef`; nothing in `m1-r31-contract.txt` models that clause. The r31 defect (arm) is unaffected, but the tool cannot be cited as a complete checker of the r31 sentence.
4. **Non-RUN records are unread (scope, matching the frozen text).** `c3-contract.txt` scopes to "a record" (singular) and `RUN` is hard-coded; L14, L8, L9, L10, L12 and L13 all filter through `results()`. A second record with out-of-contract values passes every leg (evidence 4). If the C3 entry cites such a file in its Gate, no leg objects.
5. **No cross-field constraint (frozen, unfixable by contract edit).** A scratch record with `arm=recent … where=absent object_present=no` and `arm=old … where=loose object_present=yes` prints `L14 PASS lines=2 bad=[]`. L8/L13 constrain which lines must exist and how mutants shift counts, but no leg checks field consistency against the entry's prose. `c3-contract.txt` is byte-compared to `--list-rev`, so tightening it in place would itself fail L14; L10's three quoted spans are the only prose-to-record bridge.
6. **Tool latent over-acceptance (no live impact).** `²`/`٣` under `#`, `=` inside a `*` value, empty value under a trailing-pipe contract set (evidence 6). The r32 contract uses no wildcard and no trailing pipe.

## Attack log

- **Attack A1 (filed, reproduced): tab-or-bare-prefix RESULT line escapes the M1 guard.** State: scratch rev `e8f7f9c60fae95e3cc9292335bb6d635027d2709` (RUN = 8 clean lines + one appended `RESULT\tarm=reflog-only step=start obj=B mtime=recent where=loose object_present=yes`) → `L14 PASS`, `SUMMARY legs=14 fail=12`, identical to the clean control `5288067a8fa7f7b76022e7f4c6d4f7f781c954d2`. Same blob through `tools/souji-record-contract.py` with the r32 contract: `lines=8 bad=0`, exit 0. Minimal fix, stricter-only: define in-scope as `line.split(None, 1)[0] == "RESULT"` in both parsers (a bare prefix line then matches zero keys and is BAD); an added line whose first token is RESULT but which fails the space-separated form is flagged. Because the counters were frozen at `3ec84fc`, this must ship as `census/round-32/c3-counter-v2.py` with both v1 and v2 required to print `legs=14 fail=0` — exactly the A0 shape already logged in `census/round-32/records/amendments.txt` — and it must land before `census/round-32/records/jj-mtime-clock-run.txt` first commits. If the record has already landed, the residual must be stated in the C3 landing text and handed to wave 2 as a byte scan of every line whose first whitespace-delimited token is `RESULT`.
- **Attack A2 (filed, latent): wildcard values.** Smallest safe correction: `re.fullmatch(r"[0-9]+", v)` for `#`; reject empty members at contract parse (exit 2). No r32 counter movement.
- **Dodges that hold:** contract edited at REV → `L14 FAIL contract_unchanged=False`; reordered or duplicate keys → BAD; missing `=` → BAD; record without any RESULT line → tool exit 1. Extra internal spaces are admitted by both parsers but cannot change a value, so they are not a dodge.
- **Not an attack:** the second-record hole (F4) matches the frozen contract's singular scope; it becomes a defect only if the entry cites a non-RUN record, which wave 2 can check by diffing entry-cited record paths against `RUN`.

## Deliveries

- `.ufo/waves/round-32/w1/SwarmCritic36.md` (this report). No code, contract, counter or record touched; scratch removed.

Report: .ufo/waves/round-32/w1/SwarmCritic36.md
