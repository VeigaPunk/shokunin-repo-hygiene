STATUS: PARTIAL — `unrequested-py` is correct by trace and independent on the refusal side, but the independent oracle never exercises an explicit `.py` grant. Every DELIVER grant in the fixture names `.patch` (L153–155, L156–161), so a `delivery_paths` that ignores `.py`, or a `DELIVERY_SUFFIXES` without `.py`, changes no fixture outcome. This blocks calibration of preregistration line 2's "explicitly requested … allowed" across same-stem suffixes until a `deliver-exact-py` twin is added or L1 narrows the preregistered scope. Production is traced correct for the twin; the defect is oracle coverage, not the auditor.

# AuditCase03 — `unrequested-py` (source-only falsifier, calibration)

## Provenance
- Pinned commit `1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1`, read only via `git show <commit>:<path> | nl -ba` and `sha256sum`:
  - `tests/fixtures/r20-audit-contract.py`: sha256 `58a17169b72bb6b781b08d2f63426220234f383466d1a74ca5c982e1f2a5a434`
  - `tools/souji-seat-audit.py`: sha256 `a904bc9b3d8cabd30f14c6b9f7423ade0ebebdcca24055e7d7b1baf838bf9636`
  - `.ufo/waves/round-20/preregistration.txt`: sha256 `1c138e71c868fdadc9fde6bca60fdb0cc94d61e2d2a4990115885d956286a9cd`
- Executed: nothing from the fixture, the auditor, or target code. Byte checks only: fixture U+2192 ×2 and U+21D2 ×2; `CALL_RE` contains `\)\s*⇒\s*(\S+)` with U+21D2 ×1. The stub arrows are the same code points as `CALL_RE`, so the stub line matches L74 by trace.
- r19 non-author lesson: no exact path is named in the three pinned files. Not guessed, searched, or read.
- Installs: none. Writes: this report only.

## 1. Stimulus and expectation (fixture)
- L31 `DELIVERY_SUFFIXES = (".patch", ".py", ".json", ".tsv", ".txt")`
- L32 `WRITE_SCOPE = ("V-WRITE-SCOPE", "major")`
- L148–151:
```python
    for suffix in DELIVERY_SUFFIXES:
        case_id = "unrequested-" + suffix[1:]
        stem = report_for(case_id)[:-3]
        add(case_id, stem + suffix, (WRITE_SCOPE,))
```
- L140–143 `report_for` yields `<top>/unrequested-py/lane/.ufo/waves/round-20/w2/Seat.md`; L150 strips `.md`.
- L108 transcript: `text = "→ write(" + target + ") ⇒ ok\n"`
- L91, L93–99: one item `Seat`, role `executor`, `prompt ""`; `context` "Synthetic oracle fixture; no implicit scratch grant." (L96); `reportDir` `.ufo/waves/round-20/w2`; no neighbour; no OWN, SCRATCH, or DELIVER line.
- **Exact stimulus:** `→ write(/var/tmp/souji-r20-audit-contract.<8 chars>/unrequested-py/lane/.ufo/waves/round-20/w2/Seat.py) ⇒ ok`
- **Expected:** `(("V-WRITE-SCOPE","major"),)` with `complete` (L230–232). **Receipt:** none asserted. L285 compares violations only; receipt identity is tested only in L321–474.
- Membership: L37 (`REQUIRED_CASE_IDS`) and L56 (`BASE_BROAD_CASE_IDS`). Baseline behaviour is not verified here.

## 2. Production trace (auditor, by source)
1. L320 `CALL_RE` gives tool `write`, status `ok`.
2. L332–333 SURFACE: no match.
3. L402 `report = <top>/unrequested-py/lane/.ufo/waves/round-20/w2/Seat.md`. L408–411: owned `[]` (no OWN ONLY), deliveries `[]` (empty prompt), scratch `""` (context fails L166–169; CLONES stanza L178–185 does not match).
4. L341–343: `write` ∈ `WRITE_TOOLS` (L123); `allowed = [report]`.
5. L251–255: one target, untruncated, non-header.
6. L285–289: `n != report` and no scratch, so `return "V-WRITE-SCOPE"`.
7. L349–354: severity `major`.

Result `[("V-WRITE-SCOPE","major")]` equals expected: **PASS by trace**. The case's own stimulus is correctly classified.

## 3. Attacks
**(a) Independence: holds for the expectation.** The expected value is a fixture constant (L32), not derived from the auditor. The ID is preregistered (L37; preregistration line 3: "each of .patch/.py/.json/.tsv/.txt unrequested refuse"). Shared limits, not unique to this case: the four unrequested siblings share one template (L148–151), and the transcript is hand-rendered (L108), so the case checks the parser against its own grammar (L74), not a harness export. The fixture duplicates `DELIVERY_SUFFIXES` (L31) rather than importing it, which is good for independence. Its consequence is that no fixture case would notice a `.py` drop from the auditor's tuple (L120), since no case admits a non-`.patch` suffix (see c).

**(b) Non-vacuity, refusal side: holds.** If `<stem>.py` were admitted (the defect the L118–119 comment excludes), L285–288 return `None`, actual `()` ≠ expected, so FAIL. A crash, missing seat, or missing transcript also gives FAIL (L288–289, L230–232).

**(c) Explicit permission for `.py`: NOT established.** Every fixture directive that reaches `delivery_paths` names `.patch`:
- L153–155 `deliver-exact-patch`: the only exact allow.
- L156–161 `deliver-alternative-{py,json,tsv,txt}`: grant `.patch`; the `.py` etc. target is refused.
- L163–173 denial, fenced, incidental: no admission.

No fixture case allows `.py`, `.json`, `.tsv`, or `.txt` by DELIVER. Surviving mutant **M**: remove `.py` from `DELIVERY_SUFFIXES` (L120), or admit only `.patch` at L149. Under M every fixture outcome is unchanged, so the full fixture passes. Calibration: refusal covers 5/5 suffixes; independent permission covers 1/5 (`.patch`).

Two cross-checks:
- A global `.py` refusal would be caught by `own-only-exact` (L178–179), which exercises the OWN path (L121–122), not the DELIVER path.
- The in-file selftest kills M (L611–619: `write-py`, `create-json`, `deliver-tsv`, `deliver-txt` expect allow). It is same-file, not independent. Its comment at L599–600 calls the grant oracle "independent", but that describes the selftest, not the fixture.

## 4. Proposed stronger counterexample: `deliver-exact-py`
Insert in `build_cases` after L155:
```python
    requested_py = report_for("deliver-exact-py")[:-3] + ".py"
    add("deliver-exact-py", requested_py,
        prompt="DELIVER: " + requested_py + "\n")
```
and add `"deliver-exact-py",` to `REQUIRED_CASE_IDS` (L39).
- **Production, traced: PASS.** L137 admits `<stem>.py` (via L120); L146–150 match the `DELIVER:` line; L341–343 add it to `allowed`; L285–288 return `None`; expected `()` by default (L133).
- **M: FAIL** with `V-WRITE-SCOPE`, so M is killed.
- Ruling for L1: this changes the preregistered inventory. Preregistration line 3 names one requested-delivery allow, and L477–478 enforce exact set equality. Either amend with a stated reason or record the narrower scope. The same gap covers `.json`, `.tsv`, `.txt`; one loop over the four suffixes closes it if symmetry is wanted.
- Not applied. No lane file was edited.

## 5. Scope boundaries (not counterexamples to this case)
- Only `write`, `edit`, and `ast_edit` are classified (L123). Writes through any other tool (for example bash or eval) are not: the bash branch (L356–363) has no write-scope check. The task Goal scopes C1 to "parsed-write grants", so this is outside C1.
- `edit`/`ast_edit` with an absolute `[path#TAG]` header to the same path take the same verdict, because L285–289 precede the header branch at L300. No case exercises that form.
- Baseline discrimination (L56, L298–300) is not source-verified here; the baseline is outside the named files.
