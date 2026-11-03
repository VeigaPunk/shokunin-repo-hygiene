# S57reviewer02 — C2 receipt revision-binding attacks

Recommendation: **ATTACK-FOUND**. This is a reviewer recommendation, not an admission or a change to frozen claims. Axes: C2 operability; calibration of acceptance/rejection. Preregistration was read first. Frozen C2 bytes exercised: SHA256 `174d7b8a3c105875f1757f9137f26ed54e38ac11c963a134015bce8a9dd16ec2`, matching preregistration line 34.

## Findings, by severity

### Medium — annotated tag object accepted as the measured commit

`census/round-57/c2-counter.py:86-100` tests `rev + '^{commit}'`, which peels annotated tags, rather than requiring the supplied object's type to be `commit`. `merge-base` and `git show REV:tool.py` also peel the tag. A receipt carrying tag-object OID `653e8aef78ebb95bac5bb95db8a2712b1cc93938` and the peeled commit's correct pin exited **0**, `SUMMARY receipts=1 findings=0`. Fixture `git cat-file -t` returned **tag**, not commit. This contradicts the gate's documented `RECEIPT-REV-ABSENT` contract (lines 16, 88) for a full40 token naming no commit object, and the measured-revision interpretation in preregistration C2 T4. Expected refusal, observed acceptance: **HARM**. An annotated tag is durable and immutable; this is an object-identity/type defect, not evidence that tag reachability itself is unsafe.

### Medium — manifest receipt paths escape the declared root-relative surface

`census/round-57/c2-counter.py:103-110,158-168` joins `root / rel` without containment validation. An absolute receipt pathname and `../outside.txt` each read the file outside the fixture repository and exit **0**, findings empty. The external file still lived within this seat's scratch. Both violate the docstring's root-relative manifest path contract (lines 29-30). Preregistration line 88 describes receipts under the round's records directory but does **not** define a path-escape finding or a path-confinement target. **HARM against the documented manifest boundary; not independently a named C2 T1–T6 falsifier.** No secret or non-seat file was read in this experiment.

### Low — first-token selection rejects a valid later binding, but ignores invalid later tokens

`census/round-57/c2-counter.py:58,111-124` uses `REV_RE.search`, so `good; bad` passes and `bad; good` fails. Preregistration specifies no duplicate precedence or uniqueness rule. Under its literal existence rule (“carries no durable full-40-hex rev”), both examples contain a valid binding; rejecting `bad; good` is **OVER-STRICT** under that interpretation. Under an unambiguous-single-header policy both should instead be rejected. This ambiguity is disclosed, not silently added to the frozen kill predicate. Recorder lines 28-32 put the real header before arbitrary command output, so later `rev=` tokens can be legitimate output; rejecting every duplicate would itself change that caller's contract.

## Execution and evidence

Command actually run:

```text
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-57/w1/S57reviewer02/attack.py
```

Harness retained at `.ufo/waves/round-57/w1/S57reviewer02/attack.py`; complete commands, manifest bytes, stdout, stderr, exits, fixture identities and Git setup transcript at `.ufo/waves/round-57/w1/S57reviewer02/observed.json`.

Every gate invocation was:

```text
TMPDIR=/fast/scratch/hyaku/souji-r57/S57reviewer02 python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-57/c2-counter.py --root /fast/scratch/hyaku/souji-r57/S57reviewer02/repo --manifest /fast/scratch/hyaku/souji-r57/S57reviewer02/<case>.tsv --scratch /fast/scratch/hyaku/souji-r57/S57reviewer02
```

All setup Git mutations named `-C` explicitly, with repository-toplevel assertion before the first commit. No lane/fleet Git mutations, other runtimes, subagents, background jobs, installs or upgrades. Harness `finally` removed the scratch tree before returning. Only report/evidence files were retained in the assigned paths.

Fixture identities:

- A (main commit): `e2da4bf368bcde07ce2aefabac23136903198669`; tool.py SHA256 `14f95ddd9b99cb81615382a0f25f9baf3e69eba017dcac92a30281f16b42d572`.
- B (different instrument): `626055df211021a22f1d983572f771b040dbd502`; SHA256 `55a7d5d738359d1897ddd89a51c78ab2dcf27ca5b5d185ca21a447aae6cee408`.
- Annotated tag OID: `653e8aef78ebb95bac5bb95db8a2712b1cc93938`; object type `tag`, peels to B.
- `git for-each-ref --contains=B` returned only `refs/tags/durable`, establishing B's tag-only reachability.

The default receipt is `rev=A`, `instrument=tool.py`, matching A pin and `EXIT=0`, one field per line. Bad revision below means `HEAD`. Findings in the tables are the **full ordered finding ID list**; complete details are in observed.json. Every exit-0 row printed `SUMMARY receipts=1 findings=0`; every exit-1 row printed `SUMMARY receipts=1 findings=1`. No findings were omitted.

## Grammar attacks

Expected verdicts follow the frozen literal token rule, not an invented Markdown parser. “Unspecified” marks grammar not explicitly resolved by preregistration; expectations there are interpretations, not additional kill criteria.

| Case / receipt shape | Expected by frozen rule | Observed exit; ordered findings | Verdict |
|---|---|---|---|
| honest control | accept | 0; [] | AGREE |
| duplicate-good-bad: valid A header, then `rev=HEAD` | accept under existence rule; duplicate semantics unspecified | 0; [] | AGREE, ambiguity limit |
| duplicate-bad-good: `rev=HEAD`, then valid A header | accept under existence rule; duplicate semantics unspecified | 1; [RECEIPT-REV-NOT-FULL40] (`rev=HEAD`) | OVER-STRICT under existence reading |
| trailing-punctuation: `rev=A,` | refuse: token not full40 | 1; [RECEIPT-REV-NOT-FULL40] | AGREE |
| spaces: `rev = A` | refuse: no literal `rev=` token | 1; [RECEIPT-REV-MISSING] | AGREE |
| fenced-only: only revision occurs in triple-backtick example | accept under literal token rule; no hidden-text exclusion named for C2 | 0; [] | AGREE; semantic/example ambiguity limit |
| crlf: all receipt lines CRLF | accept: full40 token and EXIT line preserved | 0; [] | AGREE |
| different-revision-pin: rev=A, pin=B | refuse: mismatching committed instrument bytes | 1; [RECEIPT-INSTRUMENT-DIGEST-MISMATCH] | AGREE |
| symlink receipt -> honest receipt | refuse: docstring QUALITY-scope rule; prereg points to finding IDs | 1; [RECEIPT-SYMLINK] | AGREE |
| tag-only-commit: rev=B with pin=B and EXIT=0 | accept: durable tag reachability, genuine commit OID | 0; [] | AGREE |
| annotated-tag-object: rev=tag OID with pin=B | refuse under documented commit-object requirement | 0; [] | HARM |
| no-execution-forgery: manually written honest control bytes | accept on byte-binding predicate; execution not proved | 0; [] | AGREE; residual limit |
| missing-pin control | refuse | 1; [RECEIPT-INSTRUMENT-PIN-MISSING] | AGREE |
| missing-exit control | refuse | 1; [RECEIPT-EXIT-MISSING] | AGREE |

## Manifest abuse

| Case / row | Expected | Observed exit; full finding list or diagnostic | Verdict; prereg coverage |
|---|---|---|---|
| manifest-three-columns: `honest.txt TAB tool.py TAB extra` | cannot evaluate, docstring lines 32-34 | 2; []; `CANNOT-EVALUATE manifest line 2: 3 columns` (no SUMMARY) | AGREE; not specifically named in prereg |
| manifest-missing-file: `absent.txt TAB tool.py` | refuse missing receipt | 1; [RECEIPT-MISSING] | AGREE; not specifically named in prereg or finding-ID docstring |
| manifest-instrument-dash: `manifest-instrument-dash.txt TAB -`, receipt has A and EXIT only | accept: explicit docstring pin exemption | 0; [] | AGREE; `-` exemption not stated in prereg |
| manifest-absolute: absolute external receipt TAB tool.py | refuse under root-relative docstring contract | 0; [] | HARM boundary violation; no explicit prereg refusal rule |
| manifest-escape: `../outside.txt TAB tool.py` | refuse under root-relative docstring contract | 0; [] | HARM boundary violation; no explicit prereg refusal rule |

## Forgery requirements and residual limit

The requested statement that the gate “cannot be satisfied by editing only the receipt” is **not true** if it means proving execution. The no-execution-forgery case writes four honest-looking metadata lines without running tool.py and passes. No invented execution claim is warranted.

With an unchanged manifest naming an instrument, a forger must supply a receipt file (not a direct symlink), a first recognized `rev=` token accepted by `durable_kind`, an `EXIT=<digits>` line, and a recognized 64-lowercase-hex pin equal to SHA256 of `git show REV:INSTRUMENT`. These bytes are all publicly derivable without executing the instrument. The instrument name field is optional; when present it must agree with the manifest. With manifest instrument `-`, no pin is required at all.

What each forgery encounters in canonical logic (`c2-counter.py:103-145`):

- No recognized rev => `RECEIPT-REV-MISSING` (early return); short => `RECEIPT-REV-SHORT`; symbolic/malformed => `RECEIPT-REV-NOT-FULL40`.
- Full40 absent/non-durable object => `RECEIPT-REV-ABSENT`; jj keep-only => `RECEIPT-REV-KEEP-ONLY` (`durable_kind`, lines 86-100). These IDs were inspected, not separately exercised in this scoped attack run.
- Missing/malformed pin => `RECEIPT-INSTRUMENT-PIN-MISSING`; instrument absent at revision => same ID with `absent at rev`; another revision's different bytes => `RECEIPT-INSTRUMENT-DIGEST-MISMATCH` (exercised).
- Missing EXIT => `RECEIPT-EXIT-MISSING` (exercised). A nonzero EXIT is still a valid recorded result: this is not a success-only gate.
- Conflicting instrument field => `RECEIPT-INSTRUMENT-NAME-MISMATCH` (inspected, not exercised).
- Direct receipt symlink => `RECEIPT-SYMLINK`; absent receipt => `RECEIPT-MISSING` (both exercised).

**Residual limit: the gate binds bytes, not execution.** A matching committed instrument digest does not establish that those instrument bytes ran, that the named revision was checked out, that output is genuine, that the working tree matched that revision, or that the revision was the intended measured revision. Copying a valid revision/pin and fabricating output is sufficient to pass by receipt-only editing. Different revisions containing identical instrument bytes legitimately share the digest. Duplicate tokens and fenced examples have no semantic provenance protection. These limits must not be represented as execution attestation or honest saturation.

## Review scope and verification gaps

Reviewed the actual base-to-freeze diff for the new gate and recorder. Recorder is the affected producer; its output header order and unfiltered command output explain why token precedence matters. Literal caller search was limited to round-57 and found preregistration commands and a recorded C2-before invocation; that is not semantic caller proof. `xd://lsp` was requested and unavailable (“No such tool”); no LSP status/references/definition/diagnostics could run, so text inspection was explicitly the fallback. No full standing suite, selftest, matrix, official after manifest, runtime/resume preflight or same-identity routing behavior was exercised by this seat. No claims about their status or fleet admission follow from this report. Frozen files were not changed.

Self-evaluation: accuracy 4 (ambiguous grammar explicitly separated from hard object-type evidence); completeness 5 (all assigned shapes and residual premise covered); clarity 4 (raw detail retained separately); actionability 4 (exact canonical lines and reproducer provided, no frozen repair attempted); conciseness 4 (tables preserve scope but report remains detailed). Overall 4.2/5. Improvement: next-round grammar should state duplicate precedence and provenance treatment explicitly; this recommendation does not alter this round's contract.
