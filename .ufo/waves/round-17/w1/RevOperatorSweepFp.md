STATUS: DONE — operator-sweep metadata fingerprint matches the r15/r16 pin (`f6a84466…`, 155 entries, measured twice); the assignment's literal command is a defective variant (`8783e2e4…`) and a verifier following it would report a false mismatch.

# RevOperatorSweepFp — conformance review (wave 1, calibration)

Lane root `/home/vgpnk/Projects/shokunin/souji-shokunin`, HEAD `5fa6017ddcae9f6bd4412df44765f6360cb16294` (base), measured 2026-10-20 13:34–13:37 -03. Seat item 43 in `.ufo/waves/round-17/w1-spec.json`. Reviewer; axis calibration. No claim (C1–C3) is endorsed here — wave-1 artifacts were still landing during the review (see §Concurrency).

## Verdicts

| check | verdict | evidence |
|---|---|---|
| directory unchanged | **holds** | canonical fingerprint equals the r15 pin and the r16 recorded prefix, byte-identical in two measurements |
| never opened by this seat | **holds by construction** | only metadata syscalls were issued (§Audit trail) |
| lane never opens it | **partial — procedural only** | census prunes/excludes it; verify/vault/quarantine dir digests do not (§F3) |
| pinned command as written in the assignment | **fails** | omitting `%y` changes the digest; the r15 command is the only reproducible form (§F1) |
| "unchanged" as a content claim | **not established** | the fingerprint is metadata-only; no content digest of the sweep exists in r13–r17 (§F2) |

## Measurements — exact commands and outputs

Canonical form, copied verbatim from `corpus/lessons/round-15-verifier-spotcheck.md:115`:

```
$ cd /home/vgpnk/Projects/shokunin/souji-shokunin
$ find census/operator-sweep-20261019 -printf '%P\t%y\t%s\t%T@\t%m\n' | LC_ALL=C sort | sha256sum
f6a844662f23ec8b0026d3f48bb19d8b27bb137f7ebd57e273c201b8539782b8  -
$ find census/operator-sweep-20261019 -printf '%P\t%y\t%s\t%T@\t%m\n' | wc -l
155
```

Same pipeline re-run at 13:36:39 under concurrent wave writes: identical digest, 155. The r16 record (`corpus/lessons/round-16-verifier-spotcheck.md:26`) states "Metadata fingerprint `f6a84466…` with 155 entries, identical to the r13 and r15 readings." Match.

Assignment-literal variant (no `%y`), which is **not** the r15 command:

```
$ find census/operator-sweep-20261019 -printf '%P\t%s\t%T@\t%m\n' | LC_ALL=C sort | sha256sum
8783e2e467962caac549e7e8276a41181afcffd3e569e5e91651bafaecc0e307  -
$ … | wc -l
155
```

Repo state of the path (all read-only):

```
$ git status --porcelain
?? .ufo/waves/round-17/
?? census/operator-sweep-20261019/
$ git status --porcelain -unormal -- census/operator-sweep-20261019 | wc -l   → 1
$ git status --porcelain -uall   -- census/operator-sweep-20261019 | wc -l   → 152
$ git log --all --oneline -- census/operator-sweep-20261019 | wc -l          → 0
$ git check-ignore -v census/operator-sweep-20261019                          → exit 1 (not ignored)
```

Composition from the same `-printf` stream: `3 d`, `152 f`; modes `644:149`, `755:6` (3 directories + `run-one-chunk.sh`, `second-check.py`, `stage-hold-delete.sh`); no symlinks or specials, so no walk can escape the directory. Mtime range `1792342907.3267725940 .. 1792460827.5745583240` = 2026-10-18 14:01:47 – 2026-10-19 22:47:07 -03; the root itself is `2026-10-19 22:46:54 -03` (`stat`). The latest sweep mtime precedes the w1 spec by ~14 h 45 m (`.ufo/waves/round-17/w1-spec.json` mtime 2026-10-20 13:32 -03). `155 = 1 root + 3 dirs + 152 files` agrees with r15's "155 entries, 152 `status -uall` lines".

## Guards that keep lane tools out of it

- `tools/souji-census.sh:1004-1006` (check-attr stream) and `:1039-1041` (status) pass `:(exclude,glob)census/operator-sweep-*`, `…-*/**`, `**/census/operator-sweep-*`; `:1076-1077` prunes the same paths in the `newest_mtime` walk, so no census code path descends into the directory.
- `tools/souji-seat-audit.py:11-13,44`: `V-SURFACE` majors any transcript call whose arguments name `census/operator-sweep-<digit>`; the pattern is anchored to a path, not a word, and the docstring states the audit is a lower bound, never proof of absence.
- Wave plan: of 78 items, only three prompts mention the directory — item 43 (me, conformance), 44 `RevL0Status`, 60 `CriticHonestyWhyNot` — and none authorizes a read. The other 13 `ALLOWED-EXEC` grants target `/var/tmp` copies, extracted blobs, or named files; none names the lane root or the sweep.
- Landed w1 reports: flat grep over `.ufo/waves/round-17/w1/*.md` finds no fingerprint claim and one disclosure, `ScribeLogCorrections.md:57` ("Did not open `census/operator-sweep-20261019/`").

## Findings

**F1 (medium, calibration/process) — the assignment's literal fingerprint command is not the pinned one.** The command given in the seat prompt and the wave context omits the `%y` field; it yields `8783e2e467962caac549e7e8276a41181afcffd3e569e5e91651bafaecc0e307`, while the r13/r15/r16 pin is `f6a84466…`. The same prompt simultaneously says "find … the exact fingerprint command they used and replicate it exactly", so the intent is unambiguous, but a verifier who pastes the literal command will record a false "changed" alarm at r17 closure. This is exactly the class of defect the calibration axis grades. *Smallest fix:* in the r17 lesson/closure table, quote `corpus/lessons/round-15-verifier-spotcheck.md:115` verbatim, including `\t%y`; if both digests are ever recorded, label them explicitly as non-comparable.

**F2 (low, calibration/honesty) — "unchanged" is metadata-only and should be stated that way.** `%P %y %s %T@ %m` cannot detect a content edit that preserves type, size, nanosecond mtime, and mode; atime is neither covered nor stable under reads. No content digest of the sweep exists in r13–r17. The r16 wording ("Metadata fingerprint … Not opened") is already correct; keep that qualifier in r17 rather than writing "the directory is unchanged" unqualified. Optional: the operator (not the lane) can record a content digest if byte-identity ever needs to be asserted.

**F3 (low, coverage) — the never-opened guarantee is tool-enforced only for census.** `dir_digest` in `tools/souji-verify.sh:155-166`, `tools/souji-vault-verify.sh:111-123`, and `tools/souji-quarantine.sh:717-726` walks a directory with only `./.git` pruned and `sha256sum`s every regular file. If any future action ever points one of these at a tree containing `census/operator-sweep-*` (including the lane root), sweep contents would be read. Today the guard is the contract that forbids running these tools against the lane, plus the sweep's location under `census/` — no live path is claimed. *Smallest fix (optional):* add the same three exclude globs to those find walks; these files are C3-owned, so coordinate rather than edit here.

**F4 (informational) — the verified equality chain is r15 = r16 = r17, not r13 = r17.** The r13 spotcheck (`corpus/lessons/round-13-verifier-spotcheck.md:25`) records "contents were not opened" but no digest. The r13 link is r15 prose (`:115`). Cite the chain that was actually measured.

**F5 (informational) — entry-count semantics.** 155 includes the root entry (`%P` empty). A verifier adding `-mindepth 1` gets 154 and would false-mismatch; `git status -uall` gives 152 because it lists files only. Any restatement of the pin should carry the exact find invocation.

## Adjacent observation (not my claim, cheap and reproducible)

C1/D1's mechanism and its proposed remedy were spot-checked read-only with the census pathspecs and the lane's own git, without running the census:

```
$ git -c status.showUntrackedFiles=no status --porcelain --ignore-submodules=all -- . \
    ':(exclude).ufo/state' ':(exclude).ufo/watchdog.log' \
    ':(exclude,glob)census/operator-sweep-*' ':(exclude,glob)census/operator-sweep-*/**' \
    ':(exclude,glob)**/census/operator-sweep-*'
 M tests/vault/vadv54-harness.sh                                  # untracked rows vanish → false clean
$ … same plus --untracked-files=normal
 M tests/vault/vadv54-harness.sh
?? .ufo/waves/round-17/
?? census/round-16/transcripts/
?? census/round-17/
?? corpus/knowledge/jj-colocation-receipts.md
?? tools/__pycache__/
```

The explicit flag beats `status.showUntrackedFiles=no`, untracked directories still collapse to one line, and the sweep stays fully excluded in both forms. This supports C1(D1) as designed; it does not verify the census edit itself (baseline `count_dirty` at `tools/souji-census.sh:1021-1047` (status call `:1037-1043`) still lacks the flag at HEAD `5fa6017`; census bytes `64a60fd0…` equal the r16 frozen pin).

## Concurrency and residual risk

The tree changed while this review ran, by design of the parallel wave: at 13:34 `git status --porcelain` showed only `?? .ufo/waves/round-17/` and `?? census/operator-sweep-20261019/`; at 13:36 it showed ` M tests/vault/vadv54-harness.sh` and untracked `census/round-16/transcripts/`, `census/round-17/`, `corpus/knowledge/jj-colocation-receipts.md`, `tools/__pycache__/`. The fingerprint is invariant to all of these (they are outside the sweep) and was re-measured identically after they appeared. `tools/__pycache__/` is untracked lane debris — if it survives to closure it is lane dirty debt distinct from the operator-owned row; a builder, not this seat, should remove it.

Residual risk: (a) absence of content reads by other seats cannot be proven from here — the seat audit is a lower bound and the rendered transcript truncates long arguments; (b) a metadata-preserving content edit would be invisible by construction; (c) three directories and 152 files at fixed sizes/mtimes are a stable target, but the pin is only as strong as the `%y`/`%T@` fields it contains.

## Verification gaps

- r13's digest value: not recorded anywhere, not verified (r15 prose only).
- Census itself: not run (forbidden by the wave contract); behavior verified through the equivalent read-only `git status` invocation above.
- Peer transcripts: not audited here (L1's `tools/souji-seat-audit.py` run is the enforcement path).
- No tool was installed or upgraded for this seat.

## Audit trail (all commands that touched the sweep path)

Metadata-only, no `read(2)` of any file inside the directory: `find … -printf '%P\t%y\t%s\t%T@\t%m\n'` (repeated: digest ×2, count ×2, type/mode cross-tab, executable names), the same stream consumed by `awk`/`wc`/`sort`/`uniq`, `git status --porcelain` with `-unormal`/`-uall` restricted to the path, `git log --all -- <path>`, `git check-ignore -v`, `stat` on the root and `results/`. `sha256sum` was applied only to `tools/*.sh`, `tools/souji-seat-audit.py`, and the find output stream — never to a sweep file.
