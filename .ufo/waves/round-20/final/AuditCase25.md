# AuditCase25: `receipt-spec-transcript-alias`

Source-only falsifier. Pin `1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1`. Lane `/home/vgpnk/Projects/shokunin/souji-shokunin`. Author-side advisory, not non-author closure.

Blocking finding: none. The gap in §4.2 and the counterexample in §5 are non-blocking.

## 1. Verdict

- **Named mechanism holds (static trace).** A second read of one resolved path whose bytes differ from the first read is refused before any result or receipt exists. Production lines: `tools/souji-seat-audit.py` L378–380 and L408.
- **Independent at world and state level.** It is not independent of implementation wording: the success predicate hard-codes production text and a read count (§4.1).
- **Non-vacuous for two of three mutations.** Removing the repeated-read check, and single-read caching, both FAIL the case. An unresolved-key regression (`key = str(path)` at L378) PASSES it (§4.2).
- **Permission-neutral.** The stimulus carries no grant and no write. It shows only that drift yields no result; it does not show that explicit permissions survive drift (§4.3).
- **Proposed counterexample (§5).** `receipt-spec-transcript-alias-spelled-flipflop` FAILs the unresolved-key regression and FAILs removal and caching as well. It is not added to the lane.

## 2. Evidence basis

Executed, read-only:
- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1:<path> | cat -n` for `tests/fixtures/r20-audit-contract.py`, `tools/souji-seat-audit.py`, and `.ufo/waves/round-20/preregistration.txt`. Each returned complete output with no error.
- Preregistration lines 2–4 were truncated in the first view. I read them whole from the tool's spilled artifact.
- `git rev-parse --verify '1988860…^{commit}'`, `git rev-parse <commit>:<path>`, and `git show <commit>:<path> | sha256sum` for the three files:

| Path (at pin) | Blob | SHA-256 |
|---|---|---|
| `tests/fixtures/r20-audit-contract.py` | `6987ebec65c891f4888a4236cd4451c26067d583` | `58a17169b72bb6b781b08d2f63426220234f383466d1a74ca5c982e1f2a5a434` |
| `tools/souji-seat-audit.py` | `4e90f7d4d770aeeb84419c933efb8e8833d633f0` | `a904bc9b3d8cabd30f14c6b9f7423ade0ebebdcca24055e7d7b1baf838bf9636` |
| `.ufo/waves/round-20/preregistration.txt` | `87892655fe73c29e1ec329c81b80345a6b38c51d` | `1c138e71c868fdadc9fde6bca60fdb0cc94d61e2d2a4990115885d956286a9cd` |

Not executed: the fixture, the auditor, any mutation, any test. Every behavioral statement below is a static trace, labelled [TRACE]. Assumptions are labelled [INFERENCE].

Not opened: the pinned r19 non-author lesson. Its path is not named in the three pinned files and I did not guess one. The baseline auditor was not opened (outside "inspect ONLY"). No lane, fleet, or census root was listed, globbed, or searched.

Tooling: none installed or updated.

## 3. Case identity and exact stimulus

Case ID registered at fixture L52; the case block is L443–474.

```
443  alias_world = make_world(top, "receipt-spec-transcript-alias",
444                           receipt_transcript=True)
445  alias_path = alias_world["transcript"].resolve()
446  transcript_path = (alias_world["tdir"] / "Seat.txt").resolve()
447  spec_json = alias_world["spec_path"].read_bytes()
448  transcript_bytes = alias_path.read_bytes()
452  def alias_read(path):
453      if path.resolve() == alias_path:
454          alias_reads["count"] += 1
455          if alias_reads["count"] == 1:
456              return spec_json
457          return transcript_bytes
458      return original_alias_read(path)
462  with patch.object(Path, "read_bytes", alias_read):
463      auditor.run(alias_path, alias_world["tdir"], str(alias_world["lane"]))
466  alias_ok = (alias_path == transcript_path and alias_reads["count"] == 2
467              and alias_refusal is not None
468              and "audit input changed during repeated read" in alias_refusal)
469  record("receipt-spec-transcript-alias", alias_ok,
```

Stimulus, from `make_world` (L80–122, receipt branch L105–106):
- `spec.json` is the sorted compact JSON `{"context":"Synthetic oracle fixture; no implicit scratch grant.","items":[{"name":"Seat","prompt":"","role":"executor"}],"reportDir":".ufo/waves/round-20/w2","schema":"ufo-swarm-wave-v1","wave":"souji-r20w2-audit-contract"}` plus LF (L91–101).
- `MANIFEST.sha256` is `synthetic fixture manifest; no target inputs` plus LF (L103).
- `transcripts/Seat.txt` is `→ read(/var/tmp/souji-r20-synthetic-input) ⇒ ok` plus LF (L106). It contains no write and no grant.
- The call passes the transcript file as the spec path (L463).
- The patched `Path.read_bytes` returns the real spec bytes on read #1 of that file and the transcript bytes on read #2 and later (L452–458).

Expected outcome:
- Violation class and severity: none. This is a refusal assertion, not a `violations()` row. The `expected` machinery (L280–289) is not used.
- Receipt: none. A `ValueError` must propagate before `input_sha256` is built (L431).
- Predicate (L466–468): `alias_path == transcript_path`, and exactly 2 reads, and a refusal whose text contains `audit input changed during repeated read`.
- CLI analogue: `main()` catches the `ValueError`, writes "could not evaluate" to stderr, and returns 2 (L658–662). `--json` is never created (L664 onward is unreached). The docstring defines exit 2 as "usage/unreadable" (L57). Any gate must treat exit 2 as not-passed.

## 4. Attacks

### 4.1 Independence

Passes at world and state level:
- The world is created under `top` at L443 and is referenced by no other case. The case does not touch `rw`, `original_receipt`, or any other world.
- The `with patch.object` block (L462) restores `Path.read_bytes` on exit. `original_alias_read` is captured at L450, after the earlier drift patches have exited.
- `load_auditor` shares one module object across cases. `run()` keeps no global mutable state; `AUDITOR_SOURCE_SHA256` (L72) is a constant.

Coupling (over-pinned, not wrong today):
- L466–468 hard-code production wording and a read count of 2. A correct refusal with different wording fails the case. So does a correct refusal that happens before any read, which yields count 0 or 1.
- Preregistration (line 3) lists the enumerated C1 rows explicitly. This case is not one of them. It sits under the provenance clause ("detects post-read drift"). Whether it was added after implementation output cannot be determined from the three pinned files [INFERENCE].

### 4.2 Non-vacuity

| Production mutation (static trace) | Case result |
|---|---|
| M1: delete L379–380 (no repeated-read check). L381 overwrites with K, the audit runs clean, and the final loop at L422–425 sees K==K. No refusal. | FAIL (detected) |
| M2: second consumer returns cached spec bytes with no re-read. Count stays at 1. | FAIL (detected) |
| M3: L378 becomes `key = str(path)` (unresolved). The spec argument is pre-resolved (L445) and the transcript path is textually identical, so keys coincide and L379 fires. | PASS (not detected) |
| M4: a correct upfront alias refusal before any read, with different wording. | FAIL (over-pinned) |

M3 is the gap. The case never presents one file under a second spelling, so the resolved-key mechanism at L378 is never exercised.

[INFERENCE] The M3 blindness assumes `tempfile.mkdtemp(dir="/var/tmp")` (L274) returns a path with no symlinked component. If it did, the pre-resolved spec path would differ textually from `tdir/Seat.txt`, and M3 would fail for an accidental reason.

Exception-channel note: the outer handler at L472 catches only `OSError`, `ValueError`, `KeyError`, and `TypeError`. A `RuntimeError` from `run()` would abort the harness rather than record FAIL. The current production does not raise one here.

### 4.3 Explicit permissions

Neutral, so unproven:
- The stimulus has no grant (`prompt=""` at L91, `context` at L96 states "no implicit scratch grant") and no write. The case cannot show that a grant from one snapshot is never applied to actions from another.
- Production design [TRACE]: grants come only from the spec parse (L386, L407, L411). Actions come only from the transcript read (L408). A drifted pair is refused before classification, so no row can pair the two. The refusal path is permission-preserving by construction, but this case does not exercise that property.

### 4.4 Receipt binding

Passes for drift: no receipt is produced on a refusal. Silent for consistent aliases (see R2 in §6).

## 5. Proposed stronger counterexample (not added; source-only)

ID (proposed): `receipt-spec-transcript-alias-spelled-flipflop`.

Why this one: it exercises the one mechanism the case never touches (two spellings of one file meeting at L378). It also puts a granted write on the transcript side, so a silent pass shows up as a permission-visible clearance.

Stimulus, in fixture style:

```python
flip = "receipt-spec-transcript-alias-spelled-flipflop"
lane_path = str(top / flip / "lane")
flip_world = make_world(
    top, flip,
    prompt="DELIVER: " + lane_path + "/" + REPORT_DIR + "/Seat.patch\n",
    target=lane_path + "/" + REPORT_DIR + "/Seat.patch")
real = (flip_world["tdir"] / "Seat.txt").resolve()
spelled = flip_world["tdir"] / ".." / "transcripts" / "Seat.txt"  # same file, other spelling
spec_b = flip_world["spec_path"].read_bytes()   # J: spec carrying the DELIVER grant
tx_b = flip_world["transcript"].read_bytes()    # K: transcript carrying the granted write
seq = {1: spec_b, 2: tx_b, 3: spec_b}           # flip-flop; reads 4 and later return tx_b
# Patch Path.read_bytes: when path.resolve() == real, return seq.get(count, tx_b).
# Call: auditor.run(spelled, flip_world["tdir"], str(flip_world["lane"]))
# Expect: ValueError containing "audit input changed during repeated read", exactly 2 reads, no result.
```

Outcomes (static [TRACE]):

| Implementation | Outcome | Case result |
|---|---|---|
| Current production (L378 resolved) | L408 compares J≠K and raises at read #2 | PASS |
| M3 (L378 `str(path)`) | Keys differ, so L379 never compares them. L422–425 reads J (#3) and K (#4), both equal to stored bytes. The write is cleared by the DELIVER grant read from J (L343, L411). `violations == []` for Seat. `input_sha256` lists two digests for one file, and `inputs_unchanged_during_run: True` (L433). | FAIL: silent clearance across snapshots |
| M1 (L379–380 deleted) | L381 overwrites with K and the write is cleared. L424 reads J (#3) ≠ K and raises "changed during read". | FAIL (by wording) |
| M2 (cached spec bytes) | Count stays at 1. | FAIL |

Adoption notes: if adopted, add the ID to `REQUIRED_CASE_IDS` (L35–54) so the inventory check stays exact. The case inherits the wording coupling in §4.1.

## 6. Residuals (non-blocking; not closed by this case or by production)

- **R1, identity-level alias.** A hardlink to the spec placed as a transcript resolves to a distinct key, so L379 never compares it. A flip-flop (J, K, J, K) on that inode is accepted silently, with the same receipt outcome as M3. This needs a writer that toggles bytes at exact read points, so I rate it low-likelihood [INFERENCE]. The proposed case does not cover it. Keying by `(st_dev, st_ino)` would. Adopt only if C1 is to claim identity-level snapshot consistency; the preregistered wording (lines 2–3) does not state that.
- **R2, stable alias (by design).** Identical re-reads never trip L379. A transcript path equal to the spec path, with unchanged bytes, audits as the spec JSON: zero `→` lines, `calls=0`, clean row. This is operator misuse. The auditor does not reject zero-call transcripts anywhere. Outside this case.
- **R3, incidental, outside this item.** L412 assigns `result["seats"][name]`, so duplicate item names silently overwrite earlier seat results. L413 then sums only the survivor. Not executed.
- **R4, gate note.** Refusal exits 2 (L660–662). See §3.

## 7. Calibration fixes to the case text (suggested, non-blocking)

- L466 `alias_path == transcript_path` is tautological. Both sides are `<tdir>/Seat.txt` resolved (L445–446). Remove it, or assert on the spelled path.
- L466–468: prefer "refusal raised, no result returned, reads ≤ 2" over a wording match.
- Add the §5 case.

## 8. Checks for L1 (not run by me)

- After integration: `python3 tests/fixtures/r20-audit-contract.py --tool tools/souji-seat-audit.py`, once.
- If §5 is adopted: confirm that M3 fails it, in a throwaway clone only.

Report path, relative to `/home/vgpnk/Projects/shokunin/souji-shokunin`: `.ufo/waves/round-20/final/AuditCase25.md`
