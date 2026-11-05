# S65ReviewerDesign — post-freeze design adjudication report (round 65)

Seat: S65ReviewerDesign. Lane repo `/home/vgpnk/Projects/shokunin/souji-shokunin`. Base `4a43a4d919c5b51ae9be859a1266ce4b11337b0b`,
freeze `d2850b3eb160ae65c1c65b93753dfec7f4153b45`, L1 seat `SoujiR65`. Measured writer tip at assignment reading:
`16da2445088ccca15aa32c66841d878ee57a8706` (sha256 `6be46a05358aa8f3fc97402ffbeeda05ba010efbef568693b1f3ca40b0ef6cf0`).
Lane master has since moved past the freeze (write+SKILL landing `022cf979`, wrap fix `40a371d8`, chronology arm `16da2445`,
docstring key-scope `af81553f` — writer bytes unchanged at `6be46a05…` through it, source row commit `a3f98054`, lesson `ef00ac57`); all probes here ran against the landed bytes at `16da2445` and the tip now confirms those bytes via `git show`.

All fixtures and drivers were built in `/fast/scratch/hyaku/souji-r65/S65ReviewerDesign/` only; nothing outside
the deliver dir and the scratch root was written; no mutating git/jj in the lane (two `git commit`s inside a
scratch clone only); no subagent dispatch. No tools were installed or upgraded. Scratch cleanup is in this turn's
final step (`rm -rf --` on the scratch root after receipts are copied into the deliver dir). Probe scripts and
per-run stderr/out-existence evidence are preserved in the deliver dir under `probes/`.

## Reproduction baseline

- Writer selftest at tip: `SELFTEST cases=30 pass=30 fail=0`, exit 0 (deliver `probes/selftest.txt`).
- C2 counter at `16da2445`: `MARKERS flag=1 inrun=1 env=1 unmerged=1`, `SUMMARY rows=4 findings=0 verdict=PASS`, `EXIT=0` (deliver `probes/c2-rerun.txt`).
- SHA verification: `c1-counter.py` `6401b35d…`, `c1-matrix.tsv` `a521170c…`, `c2-counter.py` `afd4cb54…`, `c2-statements.tsv` `0291e1d3…` — all match the frozen prereg pins (deliver `probes/shas.txt`).
- Per-row ground truth from `census/round-65/records/c1-after.txt` matched against fresh-fixture reruns (deliver `probes/repro6.txt`): all 11 re-probed defect/honest rows reproduce the frozen outcome for both slots. `class_mismatches` semantics confirmed: only the NEW slot's token is judged.

## Numbered findings

### Findings routed to round lesson / next round (post-freeze ≠ amendment authority)

1. **HIGH — Mode-payload granularity: sub-`0o777` privilege bits are invisible.**
   `_snapshot_entry` records `oct(os.stat(full).st_mode & 0o777)` (`tools/souji-receipt-write.py` line 161 at
   `16da2445`). The sticky, setgid and setuid bits are outside the recorded byte. These bits matter operationally:
   setuid on an instrument-adjacent interpreted script is a privilege-escalation primitive, and git's own
   `core.fileMode` semantics model only the executable bit, so the `0o777` mask is a defensible choice — but the
   MOD row claim and the SKILL wording do not disclose it. Probes (deliver `probes/attack9.txt`):
   `chmod 4755→0755`-in-run = **accept**; `0755→4755`-in-run = **accept**; `0755→1755` (sticky) = **accept**;
   `0755→2755` (setgid) = **accept**; `1775→0775` (sticky drop) = **accept**. Payload-visible flips still refuse:
   `755→755 chmod` churn = accept; `644→600` refuses with `mode tools/notes.txt`. The memory and the writer
   docstring say "records each regular file's mode beside its digest" — a reader will assume the full mode word.
   Severity HIGH on the disclosure axis (a genuinely hidden in-run modification class), NOT HIGH on exploit
  家家 value (needs caller-controlled privilege context).

2. **MED — The N4 dual-seed fixture masks a real writer resolution behavior, and the counter's instrument
   resolution is tested against seed-shaped bytes, not against deployment-shaped bytes.**
   Probes (deliver `probes/n4vary.txt`, `probes/n4deploy.txt`):
   - Dual copies identical (frozen shape): base accept / new refuse, as frozen.
   - Dual copies with the `tools/instr.sh` copy differing from the root copy (two non-equal blobs at one rev):
     base refuses `worktree instr.sh differs from committed bytes`; new refuses
     `RECEIPT-INDEX-FLAG-CONCEALED` on README.md. So the new writer reaches the flag-gate BEFORE the instrument
     check in the same run under --allow-dirty false order: **the flag gate fires first and the instrument
     divergence is never observed**. The dual-seed mask therefore is real: a non-uniform dual-copy fixture makes
     the new writer's instrument-divergence check dead code on this row's path, and the counter sees only the
     flag refusal as evidence.
   - Deployment-shaped repo (a "real" `tools/instr.sh` whose bytes are the launch instrument, a root-level copy
     matching the counter's SEED bytes, `--instrument tools/instr.sh`): third probe row was invalid at build —
     `--root tools` with `--instrument instr.sh` resolves to the ROOT copy; a deployment-shaped run on the real
     repo would have the instrument resolved from the root and would refuse on the divergence if the root copy is
     further from the instrument bytes. This is the resolution-debt shape the r64 M1 dispute surfaced; the
     dual-seed fixture freezes it as an enabler for one specific test-path, but the underlying resolution debt
     (bare-basename instrument resolution relative to root) remains a real, probed behavior difference that a
     non-counter caller in a non-dual-seed repo hits: `refused: worktree instr.sh differs from committed bytes at
     <rev>` for a legitimate run.
   The prereg's frozen claim — "the dual-seed shape is the realizable shape (base=accept, candidate refuses)" —
   is literally reproducible and true, so the frozen predicate stands. What the fixture shape MASQUERADES is
   that the counter's seed-equality creates an artificial resolution success that real repos (no seeded dual
   copy) do not get; the counter would not detect a writer whose instrument resolution was seed-shaped because
   the counter always supplies the seed shape. Reproduce at the next round: one counter slot on a `--root
   <subdir>` repo with no dual copies (probe `n4vary.py` lastrow: both slots refuse at instrument resolution
   `instr.sh absent at …`), or with byte-varying dual copies (probe above: instrument divergence invisible
   because the flag gate precedes the instrument check in the run order).

3. **MED — Named-limit adequacy: the frozen env-redirect list names one set of redirects but not the full set
   of caller-controllable git environment variables.**
   Probes (deliver `probes/attack15.txt`, `attack16.txt`): `GIT_OBJECT_DIRECTORY=/nonexistent` both slots
   refuse (`fatal: not a git repository`) — safe-fail. `GIT_ALTERNATE_OBJECT_DIRECTORIES=/nonexistent/alt`
   (new) = **accept** — the objdir-based alternate store does not exist, but the alternate path only ADDS
   objects; a nonexistent one is silently ignored. `GIT_REPLACE_REF_BASE=refs/replace-fake` both slots refuse.
   `GIT_COMMON_DIR=/nonexistent/common` both slots refuse; `GIT_COMMON_DIR=<other repo>` both slots refuse (cat-file
   refuses with `fatal: git cat-file: could not get object info`). None of these breaks an honest run.
   **Adequacy verdict**: the named limits ARE sufficient for the shapes probed — the redirects either hard-fail
   git (safe refuse) or act additively (alternate objects cannot shadow; named-object digest checks still bind
   the parent-repo bytes; alternate *stores* do not redefine sha-addressed objects). The prereg's named-limit
   sentences state this class honestly. Residual: `GIT_ALTERNATE_OBJECT_DIRECTORIES` is silently inert when
   pointing at a nonexistent path — worth one sentence in the memory if the next round touches env redirects:
   an environment variable the writer does not scrub that silently no-ops is NOT a concealment risk, but a
   caller could leverage a VALID alternate store to make blobs resolvable that were... no — the cat-file blob
   digest is compared against the worktree bytes, not against an expected content — the sha-object network is
   bound to the parent repo's own rev, so a valid alternate cannot forge a DIFFERENT content at the same rev:path.
   Confirm with one probe on the next round if the memory sentence is added.

4. **LOW — `_delta_label` has a mode-vs-content misclassification edge.**
   `_delta_label` (writer lines 165-184 at `16da2445`) infers "mode" by parsing the recorded payload
   `0o…:<64 hex>` with `rpartition(b":")`. A path whose recorded payload is exactly `nonregular` (a
   path is a regular file → in-run fifo/socket/device/file-the-writer-cannot-open) can be mislabeled if the
   parsed `qm` happens to start with `0o` and the digest happens to be 64 hex — practically impossible on
   `nonregular` (no `:` separator, `qs` is `nonregular` ≠ 64 hex), so the misclassification lands only on
   `mode-unreadable:` paths, which the function already special-cases. **The mislabel does not change the
   verdict** — both `mode` and `content` rows produce `RECEIPT-STATE-CHANGED-DURING-RUN` and the same exit 2 —
   only the refusal text's leading row label. Probe: none; static reading of `_delta_label`, non-exploitable
   because the label differs only in the text after the refusal token.

5. **LOW — V1/V2 polarity: the writer's `status.showUntrackedFiles=all` override is applied uniformly on all
   four status reads but `-c` loses to GIT_CONFIG_COUNT environment pairs.**
   Probes (deliver `probes/attack5.txt`): caller env `GIT_CONFIG_COUNT=1
   GIT_CONFIG_KEY_0=status.showUntrackedFiles GIT_CONFIG_VALUE_0=no` on a dirty-allowed untracked-dir fixture,
   honest baseline = **accept** (correct). Same env, in-run new-file plant inside the untracked dir = **refuse**
   (`RECEIPT-STATE-CHANGED-DURING-RUN: worktree status (git status --porcelain) and content
   tools/extra/planted.txt changed`). So a caller-injected env config pair does NOT defeat the new writer: the
   per-call `-c status.showUntrackedFiles=all` out-ranks the env pair (git treats command-line `-c` as finally
   winning over env ≤ most config scopes, and the probe empirically shows porcelain still lists the planted
   file). No prereg claim names the env-config-pair class; the frozen predicate is silent on it — no overclaim.
   Severity LOW (a behavior present but undisclosed; refusal behavior is safe in the direction probed).

6. **LOW — The untracked-walk's `.git` skip applies at EVERY depth, so a nested repository under an untracked
   directory contributes no fingerprint rows.**
   Probes (deliver `probes/attack13.txt`): a seeded nested `.git` with a HEAD + one commit accepts (stable);
   an in-run append to the nested repo's `refs/heads/main` ref file also accepts. Neither churns the fingerprint,
   both are honest-shape positives. The `?? tools/extra/` porcelain row shows only the directory and the walk
   replaces it with per-file rows. The docstring discloses the ":git" skip explicitly (writer lines 187-197).
   Severity LOW (disclosure matches the code; a nested repo's internal churn is invisible by design — a caller
   accepting a dirty tree that contains a live repo can churn inside it without the writer noticing; the writer
   is a receipt, not a filesystem guard, and the caller's own tree being dirty is disclosed in the receipt).

### Frozen-predicate reproductions (supporting evidence, not defects)

7. Per-row re-probes on fresh scratch fixtures reproduced the frozen outcomes for 11 rows × both slots
   (deliver `probes/repro6.txt`, `probes/n4n2.txt`):
   V1 new=refuse with `lane worktree is dirty`, base=accept · V2 both accept · MOD new=refuse
   (`mode tools/notes.txt`), base=accept · SY1 both accept · SY2 new=refuse (`content tools/extra/link`),
   base=accept · P13 new=refuse `RECEIPT-INDEX-ENV-SET`, base=accept · N2 new=refuse (`…content
   tools/extra/new.txt…`), base=accept · N4 counter-exact `[rootsub=tools, instrument=instr.sh]` shape: base
   accept, new refuse `RECEIPT-INDEX-FLAG-CONCEALED` · A/B/T4 both accept. My first repro runs (repro.py,
   repro4.py, repro5.py) contained driver-side path bugs (wrong `out` directory nesting); the corrected
   repro6/n4n2 runs are the authoritative reproductions, matching `census/round-65/records/c1-after.txt` row
   for row — cite the corrected runs, not the earlier ones.

8. N4 dual-seed variant responses (deliver `probes/n4vary.txt`): no-dual reviewer shape (R) both refuse at
   instrument resolution (`instr.sh absent at <rev>`); dual-with-different-bytes new refuse at the flag gate
   BEFORE the instrument check; dual-with-identical-bytes base accept / new refuse — matching
   `census/round-65/probes/n4-n2-dispute-results.txt`: `N4-R base rc=2 … N4-R new rc=2 … N4-C base rc=0
   … N4-C new rc=2`. The probe file's own stderr capture shows `head: cannot open … out.err` lines — a probe
   plumbing defect (stderr file written under `$WORK` but copied to `$out.err` whose dirname may not exist for
   the out.txt path used; stderr content lost for the N4 rows), disclosed here for the closure judge: the
   recorded rc/out_exists values are correct, the stderr text columns in that receipt file are empty for
   plumbing reasons, not because the writers printed nothing.

9. C2 kill-power (deliver `probes/c2kill2.txt`): dead-token mutant (all refusal needles moved out of emitting
   lines into a trailing comment) → `MARKERS flag=0 inrun=0 env=0 unmerged=0`, `SUMMARY rows=4 findings=4
   verdict=FAIL` — the counter rejects the dead-carrier bytes. `if False:`-gated refuse calls → markers all
   1, `findings=0 verdict=PASS` — exactly the disclosed named limit: the lexical live-marker cannot see
   reachability; the C1 matrix's kill covers that class. Both match the prereg's mutually-assured-coverage
   statement.

10. Honest-Run false-refusal audit (item 7 of the target): rows A, B, T4, V2, SY1 against both slots — all
    accept, matching the recorded `c1-after.txt`. Additions beyond the counter rows (deliver `probes/attack2.txt`,
    `attack.txt`, `attack3.txt`, `attack14.txt`): a committed `.gitignore` with an ignored file present =
    accept (both slots; ignored entries are not untracked and the writer's `-c all` override does NOT
    un-ignore them — identical to base behavior); `status.showUntrackedFiles=normal` with untracked files =
    base accepts, new refuses (the delta-by-design the V1 row freezes); stable symlinks to outside-repo
    targets, dangling symlinks, symlinked directories under untracked dirs = accept (recorded by name+target,
    never followed); a stable symlink pointing INSIDE the untracked dir = accept; out-file collision inside
    an untracked dir = accept (receipt written after the post-run reads; no false refusal); mtime-only churn =
    accept; untracked-file content restore-before-post-read = accept. **No false refusal of any honest shape
    probed.**

## Verification gaps

- Not probed: an alternate-object-store-forge in `GIT_ALTERNATE_OBJECT_DIRECTORIES` against a real repo with a
  deliberately-detached blob (the writer's digest check reads the parent repo's own rev-bound blob bytes; a
  mixed-store shape would need a fixture whose own object is deleted mid-run — race-shaped, out of scope for
  the seat boundary of not mutating anything under the lane tree).
- Not probed: `setfacl`-based mode-unreadable paths (non-root fixtures cannot remove read permission from a
  file the writer owns in scratch without an `os.chmod` churn, which refuses by design; the
  `mode-unreadable:` payload branch stays unexercised).
- Not probed: `GIT_INDEX_FILE` pointing at a valid index that is a SUBSET of the fixture index (callers can
  already refuse at N3 regardless of content; the writer refuses on presence alone, so no knowledge gap).
- The lane master moved past the freeze during the seat window (two post-freeze commits touch SKILL.md wording,
  one touches the writer docstring only). The key-scope commit `af81553f` changes writer-bytes-not; its sha
  identity was verified (`6be46a05…` both pre and post). The report's shots at SKILL wording hold against the
  commit `af81553f` wording (docstring only, SKILL.md not consulted for the wording beyond what `census/c2`
  pinned at the counter's reads).

## Residual risk

The round's C1/C2 frozen claims are operated exactly as preregistered and reproduce. The two findings above
(#1, #2) route to the round lesson, not to a run-time fix: #1 is a disclosure-completeness debt (add one
sentence to the memory naming the mask, naming the setuid/sticky/gid class, naming why `& 0o777` matches
git's own fileMode view of mode-tracked changes), #2 is a fixture-shape disclosure (one sentence that the
counter's instrument resolution is only exercised against seed-shaped dual copies and that non-dual
deployment-shaped repos exercise a different path the current counter cannot see). No finding invalidates the
frozen predicate text as written.
