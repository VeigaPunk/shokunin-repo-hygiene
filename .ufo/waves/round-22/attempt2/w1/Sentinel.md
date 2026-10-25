STATUS: PASS

All three assigned surfaces reviewed at lane tip `af73b8b` (`round-22: review-driven hardening of
gate-check…`), base `4edb25dfe262515d0da63224bbba71e02e36cba5`. No credential material anywhere, no
execution path from crafted SCORECARD/Gate text, no new deletion authority in the round. One
**medium** defect (symlink escape in the C2 counter's snapshot containment) was live when this review
began and was fixed by `af73b8b` while it ran; the fix is verified by an executed before/after. Six
low findings and five informational observations remain. Evidence:
`.ufo/waves/round-22/attempt2/w1/evidence/Sentinel.md` (209-file census at 06:48:30Z plus a 224-file
addendum at 06:54:07Z, per-file sha256, every finding located).

Read-only throughout: no tool installed, no package manager, no git/jj write, no commit, no cleanup,
no signalling, no deletion. The only writes are the evidence file and this report. Both counters were
executed with `python3 -B` (stdout only; lane tree unchanged afterwards). `--selftest` was **not**
executed — it writes and removes `/var/tmp` trees — so every selftest statement is source-read and
marked as such.

## Item verdicts

1. **Snapshot secret census — `finding:low`.** No `C`/`K` class hit in 224 files: no `op://` ref, no
   `gh*_`/`github_pat_`/`AKIA`/`sk-`/`xox*`/`AIza` token, no PEM key, no JWT, no `Authorization:
   Bearer`, no `Set-Cookie`/`Cookie`. Low findings: one per-request Cloudflare NEL token, one
   third-party profile JSON, and host paths in 18 evidence files. Upstream colophon addresses in the
   vendored man pages / Trash spec are the documents' own text and are *not* defects — stripping them
   would falsify byte-exact snapshots whose sha256 the round publishes.
2. **Candidate-tool authority — `clean` for execution, `finding:low` for test integrity.** Neither
   committed tool contains `eval`/`exec`/`compile`/`__import__`, `shell=True`, `os.system`,
   `os.popen`, `chmod`, `os.remove`, `os.unlink`, or any network import (`socket`, `urllib`,
   `requests`, `http.client`). Imports are `argparse, fnmatch|io, hashlib, os, re, subprocess, sys,
   tempfile` (plus `shutil` in the hardened gate-check, used for one selftest copy). Subprocess is
   confined to git plumbing with fixed argv and to `--selftest`.
3. **Deletion authority — `clean`, one `finding:low` note.** The round adds no `.sh`, no
   quarantine/move/rename helper, and does not modify `tools/souji-quarantine.sh`. The only new
   removal calls are two `rm -rf` of a `tempfile.mkdtemp` path inside `--selftest`. Quarantine-before-
   delete is untouched; the round's own text states the policy without changing the tool.

## Executed evidence

```
$ python3 -B tools/souji-declared-evidence.py --root . --file SCORECARD.md --rev HEAD --format counts
assertions=59 resolved=59 skipped=36 mismatches=0                                    rc=0
$ python3 -B tools/souji-gate-check.py --root . --round-date 2026-10-25 \
    --entries corpus/knowledge/quarantine-staging-no-copy-r23.md \
              corpus/knowledge/quarantine-origin-record-fields-r24.md \
    --snapshot-dir census/round-22/attempt2/sources \
    --slice census/round-22/attempt2/quarantine-slice \
    --slice-verdicts census/round-22/attempt2/slice-verdicts.tsv
entries=2 ok=2 slice_verdicts=8 slice_total=8 fail=0                                 rc=0
```

E1 before/after (same command, same fixture, two tool shas — the hunk in `af73b8b` is the difference):

```
# tool d85c2696… (state when the review opened)
$ python3 -B tools/souji-gate-check.py --root .ufo/.../evidence/gatefix --round-date 2026-10-25 \
    --entries entries/symlinkesc.md --snapshot-dir census/sources \
    --slice census/slice --slice-verdicts census/verdicts-good.tsv
entries=1 ok=1 slice_verdicts=2 slice_total=2 fail=0                                 rc=0
# tool 5b8025a8… (af73b8b)
FAIL entries/symlinkesc.md check4-snapshot-outside-dir-line-6
FAIL entries/symlinkesc.md check3-no-located-quote-with-snapshot
FAIL entries/symlinkesc.md check6-row-without-reason
entries=1 ok=0 slice_verdicts=2 slice_total=2 fail=3                                 rc=1
```

The fixture is a symlink `gatefix/census/sources/link-out.txt → ../elsewhere/y.txt`; the entry
grounds a quote in bytes that live outside `--snapshot-dir`.

Grep over both committed tools: `eval\(|exec\(|compile\(|shell=True|os\.system|os\.popen|urllib|socket|requests|http\.client|os\.chmod|os\.remove|os\.unlink` → no match. `git diff --stat 4edb25d..af73b8b`
adds no `.sh` and no mutation helper.

## Findings

**F1 — `fixed:verified` (was `medium`) — symlink escape defeated the frozen "under --snapshot-dir"
rule.** Was live at `tools/souji-gate-check.py` sha `d85c2696…`, where the containment test used
`os.path.normpath` only, so a symlink planted inside the snapshot directory satisfied check 4 with
bytes read from elsewhere (`E1` before: `ok=1`, rc=0). `af73b8b` resolves both sides —
`os.path.realpath(spath)` / `os.path.realpath(snap_root)` at `:101-103` — and the same fixture is now
rejected (`check4-snapshot-outside-dir`, rc=1). No further action; keep `gatefix/entries/symlinkesc.md`
as a committed regression fixture rather than scratch.

**F2 — `finding:low` — kill-rule fixture 6 is byte-exact but synthetic, and its guard is an `assert`.**
`tools/souji-gate-check.py:243-255` writes `pkg/staged-entry.md` itself, copies it byte-exactly to
`entries/no-gate.md`, and guards the copy with `assert sha(staged) == sha(copy)`. The frozen kill rule
names "a byte-exact copy of **the staged package entry** (no Gate)"; the shipped fixture is byte-exact
with respect to a file the test just authored, not to the package, so the frozen wording is still not
met. The real package binding exists only in the uncommitted staging copy (F5). An `assert`
disappears under `python3 -O`, so the byte-exactness guarantee silently disappears with it.
Impact: a reader cannot reproduce from the committed tool that the *package* entry is rejected; and an
optimised interpreter run would drop the byte-exactness check while still printing `selftest=…`.
Minimal fix: vendor the staged package bytes into the lane (e.g.
`census/round-22/attempt2/staged-package/quarantine-staging-no-copy-r23.md`), copy from that
repo-relative path, record its sha256 in the selftest output, and replace the `assert` with an
explicit failure branch appended to `fails`.

**F3 — `finding:low` — both stored receipts are stale; neither binds the bytes at HEAD.**
`impl-gate/inputs.sha256` records r23 `80a6a895…`, r24 `8a21704d…`, verdicts `12cad84e…`;
`impl-gate/counts-latest.txt` records r23 `80a6a895…`, r24 `f47efc7b…`, verdicts `12cad84e…`. HEAD is
r23 `de5f27f5…`, r24 `015d4293…`, verdicts `9eb1d406…` (the two later commits edited both entries and
the verdicts). The counter reproduces green at HEAD (executed above), so no claim is false — but no
stored receipt proves it, and the two files disagree with each other.
Minimal fix: regenerate one receipt after the final edit, including the tool's own sha256, and delete
the superseded one; a receipt whose digests do not match HEAD should be labelled `superseded`, not
left looking current.

**F4 — `finding:low` — two new `rm -rf` calls are new removal power (temp-scoped).**
`tools/souji-declared-evidence.py:287` and `tools/souji-gate-check.py:286`:
`subprocess.run(["rm","-rf",base])` with `base = tempfile.mkdtemp(prefix="souji-…", dir="/var/tmp")`.
Not reachable from a flag, stdin, SCORECARD text, Gate text, or the network, and never in counter
mode; but "no new removal power" is a round commitment and an external `rm` is its broadest form.
Minimal fix: `with tempfile.TemporaryDirectory(prefix=…, dir="/var/tmp") as base:` — identical
cleanup, no external binary, no argument that a later edit can widen.

**F5 — `finding:info` — hardcoded cross-repo path in the uncommitted C2 candidate.**
`impl-gate/souji-gate-check.py:56-59` embeds
`/home/<user>/Projects/shokuknow/merge/souji/knowledge/corpus/knowledge/quarantine-staging-no-copy-r23.md`
as `STAGED_ENTRY`, and fails closed when absent (`staged-entry-missing`,
`control=FALSE-GREEN-UNMEASURED`). It cannot go green without the foreign bytes, but a promoted
counter would not run on another host.
Minimal fix: feed the staged entry from a CLI argument or the vendored copy F2 proposes; keep the
fail-closed branch.

**F6 — `finding:low` — per-request token in a stored header dump.**
`evidence/rev-doi-S118.headers:13` stores `report-to: {… "url":"https://a.nel.cloudflare.com/report/v4?s=<REDACTED>"}`
— an opaque correlation token minted for this fetch, not a credential to any account. It must not
enter the corpus. Minimal fix: strip `report-to` and `nel` before keeping headers (status, date,
content-type suffice).

**F7 — `finding:low` — third-party personal data in a stored API response.**
`evidence/rev-qiita-item.json` carries the author's `name`, `id`, `github_login_name`,
`twitter_screen_name`, `location`, `website_url`, `profile_image_url`, `permanent_id` (values not
reproduced here). Minimal fix: keep `id`, `url`, `title`, `body`, `created_at`, `updated_at`; drop
`user`. S138's check uses `body`, so nothing is lost.

**F8 — `finding:low` — absolute host paths in durable text.**
Evidence side (18 files): `slice124-noreplace-probe.out:2-3`, `slice133-renameat2-probe.out:2`,
`slice123-trigger-prune.out:3,13,21,88`, `slice131-worktree-census.out:10`,
`slice114-git-prune.txt:5`, `ScoutCensusMirror.txt` (15 lines), `ScoutCollision.txt:8-9`,
`Connector.md:12,61,91,96,120`, `DraftEntryNoCopy.md:5`, `DraftEntryOrigin.md:8`,
`DraftGateLesson.md:93`, `DraftGates.md:115`, `DraftMistakes.md:4`, `DraftSourcesRows.txt:13,15,193-194,288,406`,
`RevGate.md:10`, `RevImplA.md:253`, `RevRows.candidate-SOURCES.md:129`, `CritC1Predicate.md:86`,
`CritC2Coverage.md:50`, `CritC2Counter/INDEX.md:5`, `CritC2Counter/attack-log.json:10`,
`control/transcript-always-zero.txt:1`, `control/transcript-impl.txt:6`, `impl-rows/transcript.txt:3`,
`impl-a/tip-70af563.tsv:59`, `gatefix/entries/staged-copy.md:19`, `impl-gate/souji-gate-check.py:57`.
Committed side: `census/round-22/attempt2/sources/vendor-noreplace-probe.out:2-3`,
`corpus/knowledge/quarantine-staging-no-copy-r23.md:40-41`, `corpus/SOURCES.md:129`,
`corpus/README.md:425`. Class: local username + directory layout; pre-existing convention
(`LOG.md`, older lessons), so no new class — roughly a dozen new tracked lines.
Minimal fix: use mount labels (`<fleet-root>`, `/var/tmp`, `/dev/shm`, `/tmp`) in prose. Do **not**
edit the vendored probe: S109 and the entry cite its byte-exact sha256 `1634d206…8bb5`, which matches
the committed file. If the paths must go, re-vendor a redacted copy and update the S109 row and the
entry's digest in the same commit.

**F9 — `finding:info` — the C1 measurement inherits the caller's git environment.**
`tools/souji-declared-evidence.py:54-57` runs `subprocess.run([...])` with no `env=`, so `GIT_DIR`,
`GIT_WORK_TREE`, `GIT_OBJECT_DIRECTORY`, `GIT_INDEX_FILE` from the invoking shell can redirect the
plumbing that "re-derives from committed bytes"; the fixture builder at `:206` inherits them too.
Not reachable from SCORECARD content — only from the environment, which is precisely the confusion a
calibration claim must exclude. `control/fixture-gate.py:62-82` is the model: pin `HOME`,
`GIT_CONFIG_GLOBAL=/dev/null`, `GIT_CONFIG_NOSYSTEM=1`, `GIT_TERMINAL_PROMPT=0`.

**F10 — `finding:info` — the traversal-shaped token is inert today and must stay inert.**
Class-C path tokens go through `PATH_RE`, which accepts `../../../../etc/passwd.md`. The committed
tool resolves them only as `git show <rev>:<path>`, which git refuses outside the tree, so there is no
filesystem read. `MutDigest-mutant.py:161-162` (declared and killed in `MutDigest.md`) adds
`open(os.path.join(repo.root, a["path"]))`, which would turn such a token into an arbitrary-file read
plus a sha256 oracle. Recorded so the tempting repair for a digest mismatch — "compare the working
tree instead" — is not adopted without `realpath` containment under the repo root.

**F11 — `finding:info` — the manifest marks locally derived text as fetched.**
`evidence/snapshot-manifest.tsv` records `http-code 200` for all twelve files, but the six `.txt`
files are local html→text extractions (the `.raw` files carry 167–595 `<`, the `.txt` 0–12). Its
`bytes`/`sha256` columns do match the files. Fix: a `derived` marker on the `.txt` rows; keep `200` on
the `.raw` rows.

**F12 — `finding:info` — the printed "control" in the C2 selftest cannot fail.**
`tools/souji-gate-check.py:280-284` computes `control_survives = green.startswith("entries=1 ok=1 …")
and score("no-gate")[1].startswith(…)` where `green` is a literal string; the first conjunct is True
by construction, so the line only ever reports `FALSE-GREEN-REJECTED` because the *real* tool rejects
`no-gate`. It is a decoration, and `MutQuote.md` reproduced it as `PASS … FALSE-GREEN-REJECTED` for
that reason. The fixture set does the real work, so the counter is not false-green — but a reader who
trusts that line is trusting nothing. Minimal fix: make the control an executable stub as
`tools/souji-declared-evidence.py:270-278` already does (a script that prints the green line and must
be rejected by the fixtures), or drop the line.

**F13 — `finding:info` — divergent implementations exist for both counters.**
C1: `tools/…` `58ddbfef…` vs `impl-a/…` `61916d7f…` (`--no-optional-locks`, no env scrub,
`shutil.rmtree:412`) vs `impl-b/…` `a833daba…` (scrubbed `env=git_env():94`, `os.remove` inside its
own scratch repo `:414`, `shutil.rmtree`). C2: `tools/…` `5b8025a8…` vs `impl-gate/…` `66c7af71…`
(writes fixture files `:367,:441`, `shutil.rmtree:486`, foreign absolute path). Both committed
counters reproduce the recorded counts independently (executed above), so no claim rests on an
uncommitted binary — but every promotion must be re-reviewed for these authority deltas, and
`impl-b`'s `os.remove` would be a third removal call.

## Also observed (not a security verdict)

`tools/__pycache__/souji-declared-evidence.cpython-314.pyc` and `…/souji-gate-check.cpython-314.pyc`
(mtime 03:47) are untracked residue from a seat running a counter without `-B`; every command here
used `-B`. `git status` also shows a tracked deletion
(`census/round-10/__pycache__/S13-candidate-battery.cpython-314.pyc`) and modifications under
`tests/vault/…` that none of my commands touch — concurrent sibling activity, for the lane's own
hygiene census to attribute.

## Not claimed

No verdict on C1/C2 acceptance, on the counter exit codes as claim results, or on any absent-defect
register row: those are the preregistration's predicates and the main agent's verification. Selftest
results are source-read (plus the seats' own receipts), never run here. The 06:48:30Z census is a
snapshot of a directory that was still being written; the 06:54:07Z addendum lists the fifteen files
that appeared after it, and `Sentinel.md` self-matches the C/K/T/P patterns only because its own
legend names them.
