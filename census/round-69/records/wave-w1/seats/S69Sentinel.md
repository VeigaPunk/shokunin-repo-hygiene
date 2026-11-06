# S69Sentinel — security review of the round-69 counter and battery as instruments

Seat: S69Sentinel (post-freeze falsification wave w1, lane souji).
Scope: `census/round-69/c1-counter.py` (sha256 `40757709e5adef00ef86c63fb4b554c03cce80e197747e389d76f58d4c2f5130`,
== `git show 1412037c9fac1cd18381075d22fefbac06ae5bac:census/round-69/c1-counter.py`), `census/round-69/battery/*`,
`census/round-69/records/*.txt`, `census/round-69/controls/*.txt`. Read-only; no lane tracked file edited, no git mutation.

Tooling: `strace 7.2` (`/usr/bin/strace`, preinstalled pacman `git-2.56.0-1` host) used for syscall-level write tracing.
No install performed; no tooling upgrade needed.

## Verdict per item

| # | Item | Verdict |
|---|------|---------|
| 1 | Counter writes only under `--work` / `--receipt` / own scratch | **PASS** (write-path set enumerated below) |
| 2 | No `/tmp`/`/var/tmp` write with TMPDIR unset | **PASS** (0 hits, strace-verified) |
| 3 | Committed receipts free of host-private values | **PASS** with 1 LOW (no tokens/secrets/env values; only lane+scratch paths) |
| 4 | No host sysctl change, no sudo | **PASS** (0 hits, strace-verified) |

## Item 1 — every write path (strace-verified, candidate arm, 108 200 syscalls)

Absolute write-intent destinations outside `--work` and outside the empty `HOME`: **none**.
The only non-`--work` opens were `/dev/null` (`O_RDWR`, the `GIT_CONFIG_GLOBAL` pin) and `/dev/tty`
(`O_RDWR|O_NONBLOCK`, git's own probe, `= -1 ENXIO`). Every relative-path write (`link`/`mkdir`/`unlink`
on `.git/...`) is git-internal inside a fixture repo, and `symlink("testing", ...)` targets are
`…/<case>/repo/.git/tXXXX` — all under `--work`.

Write-path roots, from source (`c1-counter.py`):
- `work/slots/base.py` (:840 `write_exec`, :1310-1312), `work/slots/new.py` (:1315)
- `work/regress/r60-receipt-write.py` (:857-859), `work/regress/{base,new}-r60/**` (:855, :963-968)
- `work/<LETTER>/{base,new}/{repo,main}/**` (:655-662 `build_case` → :356-398 `build_repo_at`)
- `work/<LETTER>/{base,new}/out/receipt.txt` (:916-917 `b_out`/`n_out`; writer `--out`)
- `work/<LETTER>/{base,new}/` sibling fixture files: `excludes.txt`, `global.gitconfig`,
  `excl-local.txt`, `global-mode.gitconfig`, `system-mode.gitconfig`, `commondir-copy/`,
  `gitdir-copy/`, `alias-git`, `forged-instr.sh`, `forge-idx` (:456-527)
- `work/battery/<name>/**` (:1353-1354), `work/selftest/**` (:1111-1121)
- `--receipt <path>` — the only caller-directed write outside `--work` (:1096-1102 `write_receipt`).
  Verified it truncates and overwrites an arbitrary pre-existing file (test file replaced in full).
  No `--receipt` path confinement exists (unlike `--work`, :1270-1282).

Guard behaviour re-checked: `--work` under `/tmp` → `C1-COUNTER-FATAL: work directory must not live under /tmp` (rc 2);
`--work` inside the lane root → refused (rc 2). Both hold.

## Item 2 — TMPDIR unset, HOME = empty scratch dir

```
env -u TMPDIR HOME=<empty dir> python3 -B census/round-69/c1-counter.py --selftest --root <lane> \
  --matrix census/round-69/c1-matrix.tsv --base-rev 36390879... --work <scratch>/stwork
```
Result: `SELFTEST cases=16 pass=16 fail=0`, `EXIT=0`.
Files created outside `--work`: **none**. `find /tmp -newer marker` and `find /var/tmp -newer marker` returned
only unrelated host noise (`/tmp/omh-tui-svpweq1c/session` — the agent TUI, not the counter; `/tmp/q.txt` — another
seat's git-version note); `find <empty HOME> -newer marker` returned nothing (HOME still empty).
Strace of the candidate arm under the same conditions: **0** syscalls touching `/tmp` or `/var/tmp`.
A run with `TMPDIR=<scratch dir>` also created **0** files in that dir.

## Item 3 — host-private values in committed receipts/controls

Scanned `records/*.txt` + `controls/*.txt` for absolute paths, tokens, env values.
- Absolute paths present are **only** under the lane root (`/home/vgpnk/Projects/shokunin/souji-shokunin`) and
  under the scratch root (`/fast/scratch/hyaku/souji-r69/...`). No third root, no `/etc`, `/root`, `/home/<other>`.
- Token/secret patterns (`ghp_`, `sk-`, `AKIA`, `BEGIN … PRIVATE KEY`, `password`, `secret`, `api_key`, `token`): **0 hits**.
- No `HOME=`, `XDG_CONFIG_HOME=`, `GIT_TRACE*` value or `.gitconfig` content is echoed into any receipt.
- No caller-supplied value (`GIT_INDEX_FILE=`, `GIT_COMMON_DIR=`) appears in any committed receipt — the D30
  no-echo surface holds in the artefacts.
- LOW: receipts carry the operator's home path prefix `/home/vgpnk/...` (lane root) and the scratch layout
  `/fast/scratch/hyaku/souji-r69/probe/...` (e.g. `records/c2-clean.txt:7`, `controls/c1-do-nothing.txt:7`).
  These are the lane's own and the scratch root's paths, i.e. inside the two roots the brief allows, but they
  do disclose the operator account name and the internal probe directory names in a committed artefact.

## Item 4 — no sysctl, no sudo

`grep -rnE 'sysctl|sudo|/proc/sys'` over `census/round-69/c1-counter.py`, `census/round-69/battery/`,
`census/round-69/mutate-writer.py`, `tools/souji-receipt-write.py`: **0 hits** (the only `/proc/sys` in the lane is a
read of `boot_id` in `tools/souji-proc-census.sh`, outside this instrument).
Strace `execve` census of a battery run: 41 distinct programs, **no `sudo`, no `sysctl`** — only
`git`, `/bin/echo`, `/usr/bin/sh`, `/usr/bin/sleep`, `/usr/bin/head`, `python3`, and the fixture's own
`silent-fsmonitor.sh` hook. No host namespace or sysctl change was needed or attempted.

## Findings

### F-1 — HIGH: ambient `GIT_TEMPLATE_DIR` executes arbitrary code inside the fixture and flips three verdicts
`clean_env()` (:319-340) scrubs a fixed list of `GIT_*` names plus `HOME`/`XDG_CONFIG_HOME`/`GIT_TRACE*`, and pins
`GIT_CONFIG_GLOBAL=os.devnull`, `GIT_CONFIG_NOSYSTEM=1` (:334-336). **`GIT_TEMPLATE_DIR` is not in the scrub list**
and is not pinned, so it survives into every `git init` the counter runs (:358). Git copies the template's
`hooks/` and `info/exclude` into each fresh fixture repo.

Exploit path (demonstrated): an operator (or anything that can set one env var for the counter's process) exports
`GIT_TEMPLATE_DIR=<dir>`; the counter's fixture build then runs `<dir>/hooks/pre-commit` on every seed commit (:389)
and installs `<dir>/info/exclude` into every fixture `.git`.
Observed:
- **Code execution**: the injected `pre-commit` hook ran and wrote
  `/fast/scratch/hyaku/souji-r69/S69Sentinel/hook-marker.txt` — arbitrary code, arbitrary path, outside `--work`.
- **Verdict corruption**: with `info/exclude` containing `tools/hidden.txt`, three rows flipped
  `refuse → accept` (`V1`, `E3`, `PK3`), changing the honest candidate run from
  `SUMMARY base_forgeries=3 … new_forgeries=0 class_mismatches=0 EXIT=0` to
  `SUMMARY base_forgeries=6 … new_forgeries=3 class_mismatches=3 EXIT=1`.
  The excluded path is exactly the fixture's own untracked probe file (`CASE_SPECS` `V1`/`E3` `untracked_file:
  "tools/hidden.txt"`, :179-196), i.e. the template reaches the very rows the ambient claim is about.
Impact: the C2 ambient-immunity claim is measured against a tuple that does not include `GIT_TEMPLATE_DIR`; a host
whose shell profile exports it makes the counter execute host-supplied code and report false verdicts while the
committed receipt still shows `EXIT=0`/`EXIT=1` from a run the reviewer cannot distinguish.
Smallest remediation: add `"GIT_TEMPLATE_DIR"` to the `clean_env` scrub tuple (and set `e["GIT_TEMPLATE_DIR"]` to
git's stock template dir or an empty scratch template), plus pin `GIT_DEFAULT_HASH` (F-2) and `GIT_EXEC_PATH`.

### F-2 — MEDIUM: ambient `GIT_DEFAULT_HASH` is not scrubbed — the whole matrix errors out
Same root cause (:319-340). `GIT_DEFAULT_HASH=sha256` in the ambient environment makes every fixture repo a SHA-256
repo, so the counter's 40-hex `REV_RE` checks and its rev plumbing break wholesale:
`SUMMARY matrix=47 base_forgeries=0 base_honest=0 new_forgeries=0 new_honest=0 class_mismatches=0 new_echo=0
errors=47 regress=FAIL`, `EXIT=1`. Every one of the 47 rows becomes an error row. Not a silent false-green (the run
goes red), but it makes the instrument non-reproducible on a host with that variable set, and it is one more
`GIT_*` name the scrub list misses. Smallest remediation: same one-line addition to the scrub tuple.

### F-3 — MEDIUM: the battery arm executes unverified member bytes; the receipt binds neither the member nor the manifest
`census/round-69/battery/SHA256SUMS` (28 entries) and `battery/GEN.txt` (28 lines, each with a sha256) are committed,
but **the counter never reads either** — `grep -n 'SHA256SUMS\|hashlib' census/round-69/c1-counter.py` yields only
the counter's own self-hash (:844), the matrix hash (:1322) and its own bytes (:1095). The battery arm
(:1343-1356) takes `<name>.py` straight from `--battery-dir` and runs it as the writer slot; the receipt binds the
counter (`instrument_sha256=`), the matrix (`matrix-sha256=`) and the rev (`rev=`) but records **no hash of any
battery member, of the manifest, or of the battery dir** (0 lines in `records/c1-after-battery.txt` match `^[0-9a-f]{64} `).

Exploit path (demonstrated): replacing `battery/K2.py` with an arbitrary script in a copied battery dir makes the
counter execute it (`TAMPERED MEMBER EXECUTED` marker written) and report
`MUTANT K2 outcome=over-refusal expected=forgery` — a different split — while the receipt's provenance header
remains byte-identical to a legitimate run. The receipt is therefore not evidence of *which* member bytes produced
each `MUTANT` line; the SHA256SUMS file is inert documentation.

Impact: this is the round-69 answer to round-68's routed defect D2 ("the members exist as bytes") — but the
existence of bytes is not the same as the measurement being bound to them. A falsifying wave cannot verify from the
receipt alone which members ran; it must re-derive from `battery/GEN.txt` (which the L1's own receipt does not
reference). Smallest remediation: have the battery arm emit `member_sha256=<sha>` per `MUTANT` line (or verify each
member against `battery/SHA256SUMS` before running it) and record the manifest's sha256 in the receipt header.

### F-4 — MEDIUM: `GIT_COMMON_DIR` is a *value* the base honours; the counter's W4 row measures it, but the receipt does not pin the *writer* under test
The preregistration names the base forgery set as "exactly W1, W2, W4" and my independent candidate run reproduces
`SUMMARY base_forgeries=3` with `CASE W1/W2/W4 base=accept`. Independently confirmed: `grep -c '^CASE W4 .* base=accept'
records/c1-after-battery.txt` = 26, and `grep '^CASE W4 ' probes/candidate-run-p1.txt` = `base=accept … new=refuse
new_findings=lane worktree is dirty`; the r68 before-arm is `base=refuse` (count 1 in
`census/round-68/records/c1-after/CAND.txt`). All three numbers reproduce. The security-relevant observation is that
the base writer is a *known-forging* implementation on three routes and it is the reference arm of every
battery comparison: each `MUTANT` line's `expected=` is asserted against a baseline whose own behaviour is
forgery-positive. The `forgeries=3` on the `K2`/`K5`/`K8`/`D01`/`D06`/`D08` lines shows the base forging alongside the
mutant, so a "kill" can in principle be attributed to the base's own forgery rather than to the mutant's
regression. The counter's classifier keys on the **new** slot's row fates only
(`classify_outcome`, :1000-1020), so the base's forgeries do not currently inflate the split — but nothing in the
receipt records the base's per-row forgery counts per mutant, so an auditor cannot check the attribution from the
receipt. Smallest remediation: emit per-mutant base-forgery counts alongside the `forgeries=` field.

### F-5 — LOW: `write_receipt` truncates its `--receipt` target and the path is unconfined
`write_receipt` (:1094-1103) opens the caller-supplied path with plain `open(path, "w")` — no `O_EXCL`, no
atomic temp+rename, no confinement to `--work` or the lane. Demonstrated: a pre-existing file passed as `--receipt`
was replaced in full by receipt bytes. The frozen invocations pass `--receipt records/c2-clean.txt` (a **lane-relative**
path, resolved against the process CWD), which is how the L1's receipt landed inside `census/round-69/records/`.
Not exploitable by an untrusted party here (the operator chooses the path), but a crashed or truncated receipt is
indistinguishable from a complete one. Smallest remediation: write to `<path>.tmp` and `os.replace`, and refuse a
`--receipt` path that exists without an explicit `--force`.

### F-6 — LOW: the recorded `command=` line is not replayable as written
The receipt header records the argv with `--matrix`/`--receipt` **relative** to the process CWD
(`records/c2-clean.txt:4`: `--matrix c1-matrix.tsv … --receipt records/c2-clean.txt`) while `--root` is absolute.
Replaying that line verbatim from the lane root fails (`matrix unusable: cannot read matrix:
/home/vgpnk/Projects/shokunin/souji-shokunin/c1-matrix.tsv`), and replaying from `census/round-69/` fails on the
counter path instead (`…/census/round-69/census/round-69/c1-counter.py: No such file`). The same applies to
`controls/c1-do-nothing.txt:4` and `controls/c2-do-nothing-ambient.txt:4`. The battery receipt
(`records/c1-after-battery.txt:4`) uses lane-relative `--matrix census/round-69/c1-matrix.tsv` and replays cleanly
from the lane root (verified: `MUTANT K2 outcome=forgery`, `EXIT=0`). Smallest remediation: emit absolute paths for
`--matrix`/`--receipt` in the `command=` line.

### F-7 — LOW: the `probes/` receipts name an instrument sha256 that exists nowhere in the repository
`probes/c2-clean.txt:3` and `probes/c2-ambient.txt:3` carry `instrument_sha256=127b06be31ea5b71625cccbb43595b389f7959cdd80a433ffc311eeba6241898`.
A full scan of all 14 779 blobs in the repo (sanity-checked: the frozen counter's blob `6d47e8b2…` **is** found by
the same scan) finds no blob with that sha256, and no `census/round-69/c1-counter.py` in any commit hashes to it. So
those two probe files were produced by an instrument version that is not in the repository — the pre-freeze
`P5`/ambient probes are not reproducible from committed bytes. Their *measured* content is nevertheless
identical to the frozen counter's committed receipts (diff of `^(CASE|SUMMARY|REGRESS|EXIT=)` between
`probes/c2-clean.txt` and `records/c2-clean.txt` = 0), so no claim turns on it; the provenance line is simply
unanchored. The frozen counter's own hash **is** correctly pinned everywhere it matters: `records/c2-*.txt:3`,
`controls/*.txt:3`, `records/c1-after-battery.txt:3` all carry `40757709…`, which equals the sha256 of the
committed `1412037…:census/round-69/c1-counter.py`. Smallest remediation: relabel the two `probes/c2-*.txt`
instrument lines as `instrument_sha256=UNKNOWN-DRAFT` (or commit the draft) so no receipt names an unresolvable
instrument.

## Independent re-derivation (numbers I reproduced from committed bytes, not trusted)

- Candidate run at the tip: `SUMMARY matrix=47 base_forgeries=3 base_honest=11 new_forgeries=0 new_honest=11
  class_mismatches=0 new_echo=0 errors=0 regress=PASS`, `EXIT=0` (own run, independent of the L1's).
- Full 26-mutant battery (own run, `--battery-manifest census/round-69/battery-manifest.tsv`):
  `BATTERY mutants=26 kills=18 label_only=5 over_refusal=2 echo_violation=1 survived=0 error=0`, `EXIT=0`;
  every `MUTANT` line's `outcome` equals its manifest `expected` (26/26).
- My battery `MUTANT|BATTERY|EXIT=` lines vs `records/c1-after-battery.txt`: **diff = 0 lines**; my `CASE` lines vs
  the committed receipt's: **diff = 0 lines**. The committed after-arm receipt is reproducible byte-for-byte on
  every measured line.
- Prereg counting commands on the committed receipt: `grep -c '^MUTANT .* outcome=forgery'` = 18;
  `outcome=label-only` = 5; `outcome=over-refusal` = 2; `outcome=echo-violation` = 1 — all as claimed.
- `grep -c '^CASE W4 .* base=accept' records/c1-after-battery.txt` = 26 — as claimed.
- C2 ambient diff: `diff <(grep -E '^(CASE|SUMMARY|REGRESS|EXIT=)' records/c2-clean.txt) <(… records/c2-ambient.txt)
  | grep -c '^[<>]'` = **0** — as claimed. The r68 before-arm reproduces the claimed 6 differing lines.
- C3 coverage: `awk -F'\t' 'NR>1{print $5}' records/declared-coverage.tsv | sort | uniq -c` = **12 mutant / 2 limit**;
  all 14 U-ids present (D01–D08, D10, D18, D19, D21, D29, D30); the r68 mirror carries 14 `none` in the mutant column.
- Do-nothing controls are red: `controls/c1-do-nothing.txt` and `controls/c2-do-nothing-ambient.txt` both
  `new_forgeries=3 class_mismatches=4 … EXIT=1`.
- Limits: `controls/d18-limit-battery.txt` and `controls/d29-limit-battery.txt` each show
  `MUTANT D18|D29 outcome=survived expected=survived … survived=1 error=0`, `EXIT=1`.
- Battery integrity: `sha256sum -c battery/SHA256SUMS` → all 28 OK; 28 `.py` members, 26 manifest rows + 2 limit rows,
  the two sets partitioning the members exactly (no member in neither, none in both).
- The counter's `git` never reads a host config: strace shows **no** open of `/home/vgpnk/.gitconfig` or
  `/home/vgpnk/.config/git/config`; the ambient `HOME` `.gitconfig` is likewise never opened.

## Note on the frozen chronology (not a finding against the L1)

`records/c1-after-battery.txt:1` binds `rev=893b8ef4e73b3fde45f712df3437a032b1d92d42`, but
`census/round-69/battery/` **does not exist at that revision** — it was added by the freeze commit `1412037c9fac1cd18381075d22fefbac06ae5bac`.
The receipt therefore binds the *writer* revision it measured, not the revision of the battery it executed; the
battery members are bound only by the freeze commit and by the inert `battery/SHA256SUMS` (F-3). This is consistent
with the receipt grammar's stated purpose (bind the revision the run measured) and is not a misstatement, but it is
the reason F-3 matters.

## Files I wrote

- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-69/w1/S69Sentinel.md` (this report)
- Scratch only (not part of the deliverable): `/fast/scratch/hyaku/souji-r69/S69Sentinel/{marker,marker2,marker3,
  selftest-out.txt, cand-out.txt, hash-out.txt, tmpl-out.txt, tmpl2-out.txt, fullbat-out.txt, amb-out.txt,
  fakebin-out.txt, cwdprobe-out.txt, tamper-out.txt, trace-cand.txt, trace-bat.txt, trace-exec.txt, work/, stwork/,
  strwork/, amb/, tmpl/, tmpl2/, fakebin/, home-empty/, hook-marker.txt, tamper-marker.txt}`.
  No lane tracked file was created, edited, committed, or deleted; `git -C <lane> status --porcelain` shows only
  the L1's own in-flight edits to `LOG.md`, `SCORECARD.md`, `corpus/*` — none of them mine.
