STATUS: DONE — C1/C2/C3 can be separated by code, but four claim sentences go further than the evidence, and C1's "no harm" claim fails on one concrete regression: an empty metadata file, which a closure can reject.

Seat: CriticRoundAdmission-2 (round 17, wave 2, critic). Targets: ddb7347 and d7e648d. Advisory only. Read-only probes are listed at the end. I ran no census/verify/vault/quarantine tool and did no git write.
Line numbers are at ddb7347. The worktree bytes match ddb7347 for every cited file (sha256 prefixes: census 688ff8ad, seat-audit 8268212d, verify 92743004, vault bbca35a1, quarantine 24c7cf05, gate c7e8eea5, r17-jj-receipts 6792df99, r17-census-hygiene 136b0e49).

## Axes that could be harmed

| axis | harmed? | by |
|---|---|---|
| operability | **yes, C1 regression (F1)**; C3 refuses more in live jj repos (F7) and has a portability floor (F8) | census stat-%F classifier; jj rules |
| calibration | tradeoffs to disclose (F9, F10); one fail-open asymmetry (F6) | jj root/novelty policy; seat-audit severities |
| coverage | gaps next to the new edge class (F12) | fixtures authored in the same round |
| safety (fail-closed) | none found. C3 is one-directional: it only removes roots or adds refusals. C1 D2 turns a hardlinked or non-regular `info/attributes` from "exit 2 for the whole run" into an `error` row for that repo; no git call reads the file afterwards | — |
| depth | shallow real-jj depth: one J9 scenario | r17-jj-receipts.sh |
| freshness | pinned to jj 0.45.1 and git ≥ 2.42; jj ≥ 0.46 not checked yet (scout pending) | C3 comments, knowledge entry |
| adjacency | jj secondary workspaces (no `.git`) are ungoverned; `status` calls in the receipt tools have no explicit `-u` | C3 / D1 scope |
| provenance / honesty | C1 matrix not recorded; one false claim sentence; one attribution overreach | F2, F4, F5 |

## Findings

**F1 — C1 harm, fixable defect, closure-rejectable.** `tools/souji-census.sh:549-574` (guard_git_files) classifies with `stat -L -c '%F %h'` and accepts only the literal `'regular file'` (:554). For a zero-byte regular file, GNU and uutils stat print `regular empty file`.
- Observed here: `stat -L -c '%F %h' /proc/version` printed `regular empty file 1`, and `/etc/hostname` printed `regular file 1`. Host stat is uutils `stat 0.8.0`.
- So an empty `config`, `HEAD`, `index`, `packed-refs`, `commondir`, `info/exclude` or `objects/info/alternates` falls into `*)` and reaches `protected_fail git-metadata-nonregular` (:573), which ends the whole fleet run with exit 2.
- An empty `info/attributes` gets a degraded `error` row (:568-571).
- 5fa6017 accepted all of these: `[ -f ]` was true and nlink was 1.
- This is the same class r16 repaired: a whole-run refusal of benign repository state.
- No fixture covers it. r17-census-hygiene.py has no empty-file case (grep `empty|truncate|touch` found only oracle text). r14 and r15 pass on both arms, so neither has one either.
- Live exposure today is nil: across the fleet's gitdirs, all 98 existing metadata files of the 8 guarded names are `regular file` with nonzero size (stat over the exact names).
- Latent locale risk [INFERENCE]: GNU `%F` strings go through gettext. The host has only the C and en_US locales, so it is not exposed.
- Smallest fix: `'regular file'|'regular empty file')` at :554, plus `LC_ALL=C` on the stat call. Add hygiene cases: an empty `info/exclude`, `objects/info/alternates` and `info/attributes` must each give a normal row with exit 0.

**F2 — C1 evidence not recorded.** `census/round-17/c1-matrix.json` does not exist (`stat`: No such file). The numbers given (hygiene 26/0 and the rest) come from L1's WORKTREE run before landing, and that run left no retained record. The bytes are now equal to ddb7347, but nothing proves the run used these bytes. Until the landed-rev record exists, C1's counts are unverified claims.

**F3 — coupling between C1 and the r15 frozen record (separability caveat).** At ddb7347, `tests/fixtures/r15-preservation-frozen/expected.json` still pins census `64a60fd0…`, which is the 5fa6017 sha I computed. The ddb7347 census is `688ff8ad…`. ddb7347 alone is therefore a stale-pin intermediate, and d7e648d repairs the pin. [INFERENCE] the frozen checker is red at ddb7347 (pin mismatch is fact; I did not run the checker.) Reverting C1 alone requires regenerating the frozen record again.

**F4 — C3 attribution overreach (J3-quarantine).** `tests/fixtures/r17-jj-receipts.sh:169` exports `SOUJI_VERIFY_BIN="$VERIFY_BIN"`, so quarantine's stage-1 receipt is the tool-dir `souji-verify.sh`. The changed record shows `J3-quarantine … result=DRY-RUN-BLOCKED … evidence=stage1=NOT-SAFE(none)` (census/round-17/jj-receipts-ddb7347.txt). The flip is therefore verify's change. Quarantine's own r17 code is never reached by the fixture:
- `jj_keep_novel` at the stage-4 prong (:341)
- roots (:1155)
- selftest flow (:1341)

Only the quarantine selftest supports those (101/0, +10; JJ1–JJ7 at :1696-1734). [INFERENCE, not run] base quarantine plus changed verify would also pass J3-quarantine.

**F5 — claim sentence "dead shadowed sites untouched" is false for quarantine.** `try_pushed()` in souji-quarantine.sh (:994) has no caller at 5fa6017 or at ddb7347 (`grep -c try_pushed` = 1, the definition only). r17 still edited it (:1015-1022). It is inert. Its `kn=0` default marks an un-prefixed target as `jj-keep-novel`, and that is never executed. In verify and vault the edited `try_pushed` is the live (later) definition: verify :694 shadows :258, vault :894 shadows :450. So the sentence holds there.

**F6 — three copies of the same authority with different guards (fail-open edge).** `jj_keep_novel` is byte-identical in all three tools (body sha256 `e87a1e1f…` ×3). Only quarantine guards the case where the path is not under the repo (:1016-1017). verify (:718-719) and vault (:913-914) pass `${target#"$repo"/}` without that check. If target and repo canonicalize differently, `rel` stays absolute, so:
- `rev-parse C:/abs` fails;
- the loop hits `continue` and returns 1, meaning "not novel".

That is fail-open relative to the stated rule [INFERENCE: reachable only on a canonicalization mismatch; unexercised]. Quarantine's header comment (:5-7) also says receipt logic is "never re-implemented here", which its own copy now contradicts. Smallest fix: copy quarantine's guard into verify and vault with return code 2 (history-unverifiable), not 1.

**F7 — C3 live exposure is not nil, and the report must say so.** The context's "live exposure nil" covers only C1 (D1/D2). Read-only measurement:

| repo | `refs/jj/keep/*` | keep-only commits (`rev-list --glob=refs/jj/keep/* --not --branches --tags --remotes`) |
|---|---|---|
| kaidoku | 48 | 30 |
| kama | 22 | 10 |
| mado | 53 | 34 |
| souji | 17 | 13 |
| tabi | 13 | 10 |
| tameshi | 34 | 18 |
| tsukuroi | 20 | 9 |

- These 7 of the 21 gitdirs are jj-colocated.
- Lower bound on (b') refusals: blobs that only keep-only commits reach (`rev-list --objects … --not --branches --tags --remotes` | `cat-file --batch-check` type blob). That gives 2 paths in kaidoku (`SKILL.md`, `.ufo/waves/round-18/w2/SiblingOverlap2.md`) and 0 in the other six.
- Not measured: the live (a') worktree delta, the live verdict delta, and the runtime of the per-target `rev-list --objects --remotes -- <rel>`. jj repos always have keep refs, so this query runs for every target in them, and verify and vault have no timeout around it.

**F8 — portability and freshness.** `for-each-ref --exclude` arrived in git 2.42 (GitHub blog, "Highlights from Git 2.42: Exclude references by pattern in for-each-ref", https://github.blog/open-source/git/highlights-from-git-2-42). The host has git 2.56.0. On older git every absent-worktree evaluation degrades to `durable-refs-unverifiable` NOT-SAFE: conservative, but an operability cliff. Both fixture records were taken only on git 2.56.0 and jj 0.45.1. SOURCES or QUALITY should record the git ≥ 2.42 floor.

**F9 — calibration tradeoff for the closure to rule on, not a defect.**
- A head held only by `refs/stash` stays a root: SAFE(metadata-prune), pinned by quarantine selftest JJ6 at :1724-1728.
- A head held only by `refs/jj/keep` is NOT-SAFE.
- Both refs are local-only and deletable by the user.
- Likewise, git amend predecessors that only the reflog holds never refuse SAFE(pushed), while jj predecessors that only keep refs hold refuse it when their blob is novel.

The direction is conservative. The knowledge entry must state the asymmetry and justify it from S054 and S063, not leave it implicit.

**F10 — C2 counts verified; the adjudication sentence needs scope.** Replay records:

| record | auditor sha | manifest | w1 major/minor | w2 major/minor |
|---|---|---|---|---|
| base | `c9ff355c…` (= 5fa6017) | "check OK: 144 files verified" | 1/19 | 3/42 |
| after | `8268212d…` (= ddb7347) | "check OK: 144 files verified" | 1/20 | 1/52 |

- In the after record, the only w2 major is ConnReadmeIndex:180 `V-WRITE-RELATIVE`. Both RerunGateReplayR14 base majors carried edit-body text as `args`.
- Transcript file line 180 is `179:→ edit(.ufo/waves/round-16/w2/ConnReadmeIndex.md) ⇒ error · 1 line — File not found`.
- Honest wording: "an attempted relative-path edit that resolves under the fleet root. It failed and created nothing. It was intended for the seat's own report, so D4's reason described intent, not effect."
- Severity policy to disclose: a known out-of-scope or relative target is major whatever the status, while an unparsed target is graded by status. That is defensible.
- The manifest proves only that the bundle is internally consistent. It does not prove the bundle matches the live sessions.

**F11 — the gate judges the round that changed it.** `tools/souji-landing-gate.py` and `gate-replays-expected.json` land in the same commit as the work they will admit. `gate-replays-ddb7347.json` binds the gate to sha `c7e8eea5…` at ddb7347 and gives `match: true`, but has `selftest: null`, so 28/28 is not in this record. No replay of round 17 itself appears under either gate. Admission should show the round-17 report set under both the 5fa6017 gate and the ddb7347 gate, and disclose any divergence.

**F12 — coverage gaps; fixtures were written alongside the fix.** The hygiene and jj fixtures are new in ddb7347, so the base-arm failures show detection by construction. The no-harm evidence is the non-repair cases, plus the unchanged r14 and r15 fixtures, which do count independently. Missing negative cases:
- empty metadata (F1);
- a jj draft that is a working-copy snapshot superseded by a pushed final (F9);
- an un-prefixed or absolute target in verify and vault (F6);
- jj secondary workspaces (`.jj` without `.git`) — an adjacent class nobody measured.

Also, the receipt tools' `status --porcelain` calls (verify :361, :405, :865; vault :539, :583, :1072) have no `--untracked-files`. That affects only the reason field (`dirty` vs `none`), never the verdict, because present worktrees and repo roots are always NOT-SAFE (verify :363, :409-413).

## Can each claim be checked with the other two reverted?

- **Code: yes.** The files don't overlap.
  - The census sources no other souji tool (grep of non-comment `souji-*.sh|py` references: none).
  - seat-audit imports only the standard library.
  - run-matrix.py takes only `tools/souji-census.sh` at the given rev (:193-203).
  - seat-audit-replay.py takes `--auditor`.
  - r17-jj-receipts.sh binds `--tool-dir`.
- **Commit: no.** Everything is in one commit, so isolating a claim needs a path-limited revert.
- Caveats:
  - F3: C1 is coupled to the r15 frozen pin.
  - F4: inside C3, quarantine's measured flip comes from verify.
  - D6 is separate code, but it is the admission instrument (F11).
  - The vadv54 harness/stub change is not tied to any C1–C3 count.
- I ran none of the revert arms (no ALLOWED-EXEC for this seat).

## Claims a closure could reject

1. C1 "no harm" / operability: F1 is a strict regression from 5fa6017 on benign state.
2. C1 matrix numbers presented as measured at landing: F2, no record yet.
3. C3 "dead shadowed sites untouched": F5.
4. J3-quarantine counted as evidence for the quarantine change: F4.
5. "Live exposure nil" if it is read as round-wide: F7.

## What an honest report must say

- C1: "D1/D2 hold on the fixtures. D2 deliberately relaxes one exit-2 path to a per-repo error row. ddb7347 refuses empty regular metadata files that 5fa6017 accepted (F1); fix pending. The matrix record is pending; the numbers come from a pre-landing WORKTREE run whose bytes now equal ddb7347."
- C2: the counts as in F10, and the ConnReadmeIndex correction worded as failed, no effect, resolves under the fleet root.
- C3:
  - "The change is one-directional: only refusals are added.
  - It is live in 7 of 21 repos, with at least 2 novel-blob paths in kaidoku. The live verdict delta and runtime were not measured.
  - It needs git ≥ 2.42.
  - J3-quarantine measures souji-verify. Quarantine's own additions are supported only by its selftest.
  - The quarantine edit to a dead function is inert.
  - The keep-vs-stash/reflog asymmetry is a declared policy."
- Gate: report admission under both gates.

## Smallest corrections (advisory, L1 integrates)

1. census.sh:554 → `'regular file'|'regular empty file')`, and `LC_ALL=C stat`. Add three empty-file hygiene cases.
2. Land `census/round-17/c1-matrix.json` from `--changed d7e648d` (or ddb7347). Commit `jj-receipts-*.txt`, `seat-audit-r16-replay-*.json` and `gate-replays-ddb7347.json` with the integration.
3. Add quarantine's un-prefixed `rel` guard to verify :718 and vault :913, returning 2. Optionally delete the dead quarantine `try_pushed`, or drop the "untouched" sentence.
4. Rewrite the claim sentences for F4, F5 and F7 as above, and add the git ≥ 2.42 floor to SOURCES or QUALITY.

## Commands run (read-only; outputs summarized above)

- `git -C <lane> show --stat ddb7347 d7e648d`; `log --oneline 5fa6017..d7e648d` → 2 commits.
- `git ls-tree -r --name-only d7e648d census/round-17` → 5 files. `git ls-files -o --exclude-standard census/round-17 corpus/knowledge tests/fixtures tools` → 5 untracked evidence files plus the knowledge draft.
- `git show ddb7347:<f> | sha256sum` against the worktree `sha256sum` for 8 files → all equal. `stat census/round-17/c1-matrix.json` → No such file.
- `git diff 5fa6017 ddb7347 -- tools/souji-census.sh`; `git show 5fa6017:tools/souji-census.sh | sha256sum` → `64a60fd0…`. `git diff ddb7347 d7e648d -- …/expected.json`.
- `git show <rev>:tools/souji-quarantine.sh | grep -n try_pushed…` (base and ddb7347). The jj_keep_novel body sha ×3 → identical.
- `stat -L -c '%F|%s|%n'` over the 8 guarded metadata names in each fleet entry → 98 `regular file`, none empty. `stat -L -c '%F %h' /proc/version /etc/hostname`; `locale -a`; `stat --version` → uutils 0.8.0.
- Per jj repo:
  - `git -C <repo> for-each-ref --format=x refs/jj/keep/ | wc -l`;
  - `rev-list --glob='refs/jj/keep/*' --not --branches --tags --remotes | wc -l`;
  - `show --name-only` (upper bound on paths touched: 126–914; a noisy metric, not used for claims);
  - `rev-list --objects … | cat-file --batch-check` (the lower bound in F7).
- `grep -ci showuntrackedfiles` on ~/.config/git/config → 0. ~/.gitconfig and /etc/gitconfig are absent. The census exports `GIT_CONFIG_GLOBAL=/dev/null` (:171).
- python3, read-only JSON summaries of the two seat-audit replay records and gate-replays-ddb7347.json. Disclosure: python3 is not in the probe-rule list; nothing was written.
- Web: one search confirming `for-each-ref --exclude` in git 2.42.
- Probe disclosure for the L1 audit: one `ls -d <fleet>/*/.git | wc -l`, plus fixed-depth `<fleet>/*/.git/...` globs, which list fleet-root entries one level deep (not recursive). No find, strace, realpath or readlink. No files were written except this report. No tools were installed.
