# FinalHeldAuthority — round-20 final falsification, F5 held authority

STATUS: PARTIAL — blocking for the read-before-redact boundary only. At `tools/souji-proc-census.sh:243, 346–349, 353–354, 367–368, 375` the `reason` column prints argv- and fd-derived scratch paths after control-byte replacement only (`:188–190`): no secret-shape redaction (redaction runs on `cmd` alone, `:364–365`, rules `:192–227`) and no length bound. The un-superseded safety text says secret-shaped argv is redacted before printing (`corpus/knowledge/process-residue-observations.md:58–59`; `corpus/QUALITY.md:81`; `SKILL.md:135`; `SCORECARD.md:59`), and the fixture's canaries never reach that column (`tests/fixtures/r18-proc-census.sh:395–396, 434–436, 444–445, 451–452`; its secret checks at `:306–313` read `cmd` only). The held F5 reap/NAMESPACE requests, self/descendant exclusion and the other-uid boundary are agreed below, with scoped residuals.

## Scope and provenance

- Pinned build `1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1`. All pointers are `<path>:<line>` at that commit. Bytes were read only through `git show`; `sha256sum` was run on those bytes; a read-only Python print of anchored lines from the same `git show` output located the line numbers. Nothing was built, run, installed, signalled or cloned; this report is the only write.
- Not opened: process data, transcripts, the operator-sweep directory, and `census/round-18/proc-census-live-1721.tsv` (named at `corpus/README.md:242`). Beyond the listed set I read only `tools/souji-proc-census.sh` and `tests/fixtures/r18-proc-census.sh` (both named by SKILL and QUALITY Q32/Q42) and the three F5 seat reports. `tools/souji-seat-audit.py` was not read, and `census/round-18/leak-count.py` was digested only.
- Seat selection: the item named no seat. I used the three F5 recovery reports the pinned authorities cite: `.ufo/waves/round-20/recovery/F5Enumeration.md` (QUALITY Q43), `F5Redaction.md` (status catalog) and `F5Authority.md` (R20-M16). None appears in the dead-seat list of `census/round-20/recovery-seat-outcomes.json`.
- Author-side advisory. Not non-author closure, not promotion, no SHONEN marks, no score. Certification OFF; K5 HELD; F5 reap and NAMESPACE_SHA256 round-18 requests HELD and untouched.

## F-1 — `reason` is an unredacted, unbounded argv/fd path channel that the authority describes as redacted

Mechanism, pinned `tools/souji-proc-census.sh`:

1. `:332–337` apply the self-tree, own-uid and age gates. Only after them does `:345` run `read_process_argv`, which reads the complete raw `cmdline` into `CMD_RAW` (`:255`). This happens for every surviving same-uid process, whether or not it is printed.
2. `:240–243`: an absolute argv element, or a `--opt=/abs` element, whose path is absent and whose top-level under a prefix is absent (`:168–185`) sets `PROC_GONE_PATH=$candidate`. The value is raw.
3. `:346–348` set `reason="argv-path-gone:$SAFE_FIELD"`. `:350–354` set `fd-path-gone:` from readlink targets (`:258–`). `cwd-deleted` (`:343`) prints no path, so the channel is argv and fd only.
4. `:188–190`, `sanitize_field`, maps bytes `\001–\037` and `\177` to spaces and nothing else.
5. `:357` drops rows without a reason. `:364–365` redact and truncate `cmd` only (truncation `:227`). `:367–368` and `:375` print `reason` after control-byte replacement only, with no length bound. The tool's own header says it: `:5–6` "… reason, and redacted cmd".

Counterexample, source-derived and not executed. A process has `--workspace=/var/tmp/ghp_<synthetic-token>/w`, and `/var/tmp/ghp_<synthetic-token>` no longer exists. `:240–243` accept it. The row's `reason` is `argv-path-gone:/var/tmp/ghp_<synthetic-token>/w`, while its `cmd` is `…--workspace=/var/tmp/ghp_[REDACTED]/w` (`:204–207`). One row carries the same token redacted in column 10 and raw in column 9. The same holds for `AKIA…`, `xoxb-…`, `sk-…` and `password=…` components (`:208–225`). `--prefix /` is accepted (`:37`, `:162–165`), which widens the channel to any absolute argv path whose top-level is absent.

Why this is an authority overclaim, not only a disclosed limit:

- Unqualified claims: `corpus/knowledge/process-residue-observations.md:58–59` ("Secret-shaped argv … is redacted before printing"), `corpus/QUALITY.md:81` (Q32, "redacts secret-shaped argv"), `SKILL.md:135`, and `SCORECARD.md:59` ("redacted argv").
- Correct hedges, which do not say the channel is unredacted: `knowledge:124–125` (`reason` "has separate sanitation"; the leak is "[INFERENCE]"), `SKILL.md:328`, and QUALITY Q42 `:101`, whose test column reads "keep any reason-field redaction concern explicitly inference unless a harmless synthetic witness establishes it".
- The code settles the open question differently than the hedges imply. No redaction exists on that channel, so there is no unknown sanitation. What remains open is only whether a secret-shaped path occurs in a real row.

Fixture blindness. The canaries sit outside the gone-path element: `--password=`+CANARY as its own element (`:395–396`), Bearer and canary elements (`:434–436`), and AWS and Slack canaries as bare elements (`:444–445`, `:451–452`). `redacted_argv_row` checks `reason` equality (`:312`) and secret absence in `cmd` only (`:309`, `:313`). No case asserts that a canary is absent from the serialized row.

Documentary conflict on the same boundary: `PROVINCE.md:36–37` says "never reads secret content", and `SKILL.md:67` says "souji cites paths and modes only". The tool reads raw argv of every same-uid, non-self process (`:345`). `PROVINCE.md:148–149` acknowledges "Reading raw argv before output redaction is part of the actual tool boundary", but `:37` is not amended.

Secondary, `cmd` column, same boundary, disclosed only generically:

- The shape rules are enumerated (`:196–225`). The value patterns stop at the first whitespace (`:196`, `:200`, `:212`), so `--password=pass phrase` prints ` phrase`.
- `Authorization: Basic …`, `--password VALUE` and `--api-key VALUE` are not matched. Only Bearer (`:196–199`) and separate-argv `--token` (`:249–253`) are handled.

Why blocking, for this item only: the unqualified redaction claims, read as covering argv-derived output, are contradicted by the code on the `reason` surface, and the only fixture that claims redaction cannot observe that surface. F-1 does not affect the held reap, the exclusion rule or the other-uid boundary.

Required disposition, for L1. Nothing was edited here.

1. Oracle: extend `tests/fixtures/r18-proc-census.sh` with a synthetic case that places each enumerated canary shape inside a removed `/var/tmp` path element. Assert that no canary substring appears in any of the ten columns, and that the reason prefix stays `argv-path-gone:`. Predicted FAIL on `1988860` from the path above; not run.
2. Fix or scope, one of: pass the reason path through the same shape rules with a length bound; or state in SKILL, the knowledge entry, QUALITY Q32 and SCORECARD that `reason` is an unredacted path channel, and that F5 output must not be committed or shared without a secret-shape scan.
3. Amend `PROVINCE.md:37` and `SKILL.md:67` to name the in-memory raw-argv read of same-uid processes, or change the read.
4. `census/round-18/proc-census-live-1721.tsv` was not opened. Whether it already holds a reason-channel value is unknown. L1 should scan it with an approved secret-shape scanner before relying on it.

## Scoped agreements (verified at pinned bytes)

- A1, no reap, signal or deletion in census mode. `census()` (`:294–376`) contains no `kill` and no `rm`. `kill` appears only in the `unset` list (`:9`) and in selftest cleanup (`:416–417`, guarded by `selftest_pid_is_current`). `rm` appears at `:425, 428, 431, 434` (selftest cleanup, path-guarded) and `:571` (selftest only). The string `environ` does not occur in the file. The held requests are consistent across `SKILL.md:335`, `PROVINCE.md:156`, `corpus/README.md:329`, `SCORECARD.md:97` and `LOG.md:1101`.
- A2, self/descendant exclusion is sound in census mode. `is_self_tree` (`:135–140`, 512-hop bound at `:137`) runs at `:332`, before any argv read, so self-tree argv is never read. Snapshot membership (`:327`) means processes created after the first pass are not iterated. Identity is rechecked at `:330` and `:373–374`. Residual: a chain longer than 512 hops, or broken by an exited intermediate parent (`:140` `break`), is not excluded. Census mode has no persistent children, so this is not a reachable self-nomination path on this code. The wording agrees: `PROVINCE.md:148`, `corpus/README.md:321` and `SKILL.md:328` state the snapshot-recognized exclusion; `knowledge:140` says "can be excluded" (weaker, harmless); Q43 (`QUALITY.md:102`) scopes Q42's categorical `:101`. The F5Enumeration STATUS is resolved at pinned by the added SKILL section (`:324–328`); the older r19 bullet at `:133–135` still lacks the exclusions.
- A3, other uids. Real-uid equality at `:333–334`. `PROVINCE.md:153`, `SKILL.md:333`, `corpus/README.md:325` and QUALITY Q42 (`:101`, "No finding assigns all other-uid work to another lane") agree. Residual wording: `knowledge:82–83` ("Other uids and host-wide liveness are mori's ground") is unqualified, contradicts its own correction at `:129`, and conflicts with Q42. Rewrite it or mark it superseded. It is wording, not a grant.
- A4, same-uid scope is uid-wide, not lane-wide. Sibling-lane processes under the same uid are nominable. Only operator approval and a fresh `(pid, starttime, boot_id)` recheck stand between a nomination and a kill. The authority has no lane-ownership rule for processes, analogous to PROVINCE's artifact refusal. Residual for the operator; no grant.
- A5, digests. `sha256sum` of pinned bytes: `tools/souji-proc-census.sh` = `37c3316a1fd8cdda18cbefdc7692d3d3f388e5783e8fe19085f5d932a8ceba64`; `tests/fixtures/r18-proc-census.sh` = `01995f8d79f128b07dfab50ca317c13069adcd1ed933fd9325295610d56758be`; `census/round-18/leak-count.py` = `a26530199434ecddf4b36d2513730765bb0ae7487fa3c007f9c04d33244ebb3b` (content not read). All three match the knowledge correction table; the baseline `12516f7` tool digest is identical.

## Not verified and residuals

- `tools/souji-seat-audit.py` is outside my read set. F5Authority F-1 (four unflagged signal shapes) is recorded OPEN in `census/round-20/recovery-status-catalog.json`. The lesson (`corpus/lessons/round-20.md`, final classifier scope) says C1 fixed them. Unverified here.
- P7 traces `kill`, `tkill`, `tgkill` and `pidfd_send_signal` only. `rt_sigqueueinfo` and `rt_tgsigqueueinfo` are outside that set. The census code has no path to them (bash builtins only), so this is probe coverage, not a found gap.
- Nothing was executed. No installs or updates. The only write is this report.
