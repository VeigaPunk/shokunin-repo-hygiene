# sibling-overlap — S66ConnectorOverlap (souji round 66, post-freeze w1)

READ-ONLY scan of the 20 sibling lane repos under `/home/vgpnk/Projects/shokunin/*-shokunin/`
(souji-shokunin excluded), file scope `*.md *.py *.sh`, case-sensitive, gitignore off (equivalent of
`grep -rn --include='*.md' --include='*.py' --include='*.sh' -e TERM ...` per lane). No file outside
this seat's wave dir was read-modified; greps and `grep -l` counts only.

Lane list (from `ls -d /home/vgpnk/Projects/shokunin/*-shokunin`, minus souji): audio, chousa,
game-dev-2d, game-dev-3d, kagi, kaidoku, kake, kama, kasegi, kengaku, kotoba, kotodama, kumitate,
lore, mado, mori, revenger, tabi, tameshi, tsukuroi.

## File counts per term (files with ≥1 hit, all 20 siblings)

| term | files | top lanes |
|---|---|---|
| GIT_CONFIG_COUNT | 438 | kama 153, kengaku 87, mado 48, kumitate 43, tabi 26, mori 21, kaidoku 16, tsukuroi 13 |
| GIT_OBJECT_DIRECTORY | 363 | kumitate 77, kama 48, mori 46, tameshi 35, tabi 30, kake 28, mado 25, kotodama 23 |
| GIT_REPLACE_REF_BASE | 91 | kama 34, mado 21, tabi 18, kumitate 6, tameshi 4 |
| core.excludesFile | 72 | tsukuroi 39, kengaku 16, kama 7, mori 4, tabi 2 |
| status.showUntrackedFiles | 4 | kasegi 2, mado 1, kama 1 — **enumerated completely below** |
| RECEIPT-INDEX | 0 | — **zero sibling hits** |
| receipt writer | 64 | kotodama 19, tabi 5, kengaku 5, kaidoku 5, mori 4, kasegi 4, kama 4, audio 4 |
| st_mode | 2823 | mado 914, kake 489, kama 338, mori 297, kengaku 275, game-dev-3d 145, kaidoku 141, kagi 56 |

**Deviation, declared:** "every hit" is enumerable only for RECEIPT-INDEX (0) and
status.showUntrackedFiles (4). For the volume terms the listing below enumerates (a) **all**
same-round (r66) sibling hits, (b) **all** hits that carry C1/C2-relevant ground (env-route,
untracked-visibility, mode-bit, receipt-writer-claim), and (c) one representative per incidental
class, with counts. Raw per-term counts above are the complete quantitative picture. `*.sh` scope
was checked separately (the one glob typo run skipped `.sh`): the 8-term alternation over sibling
`*.sh` hits tabi r37 ExecPinsBinding runners, mado r43/r66/r67 landing+evidence scripts, kengaku r44
envelope.sh, mori census scripts, kumitate r90 attack-driver.sh + r70 run-all.sh, kama r50/r57
scratch scripts, and one vendored autotools file (kaidoku libsigrokdecode `ltmain.sh`, irrelevant).

---

## status.showUntrackedFiles — complete enumeration (4 files)

1. `kasegi-shokunin/.ufo/waves/round-37/wave1/MutC1Suite.md:31-35` — GIT_CONFIG_COUNT-injected
   `status.showUntrackedFiles=bogus` poison lever: `git status --porcelain` fails rc=128 while
   rev-parse/cat-file/ls-tree/ls-files all still succeed. Ground: kasegi mutation suite.
   **C1-adjacent**: same poison shape as the env rows, aimed at the status channel.
2. `kasegi-shokunin/.ufo/waves/round-46/wave2/R46W2RevLanding.md:119-122,154` — B7: user-level
   `[status] showUntrackedFiles = no` (via GIT_CONFIG_GLOBAL) hides untracked files from both
   tree-clean and jj-state landing checks → false clean; limit noted: host global config has no
   `status.*` key so it does not fire today. Ground: kasegi landing gate. **Direct C1-relevant
   hazard class** (caller config hides untracked content from status reads) — exactly what souji's
   writer-side pins (`-c core.excludesFile=null`, GIT_CONFIG_GLOBAL=null) foreclose for the writer's
   own status reads.
3. `kama-shokunin/.ufo/waves/round-35/w1/out/ReviewR33Count.md:11` — host default note
   (unset ⇒ `--untracked-files=normal`). Ground: kama counter review. No overlap.
4. `mado-shokunin/.ufo/waves/round-20/w1/reports/ConnFleetHarmPattern.md:57` — a silent
   false-clean (`status.showUntrackedFiles=no`) recorded in a fleet harm-pattern audit. Ground:
   mado harm history. Same hazard class, historical record.

## RECEIPT-INDEX — zero hits in 20 siblings

Confirmed souji-internal: the token is souji's r62 refusal class
`RECEIPT-INDEX-FLAG-CONCEALED` (introduced in `tools/souji-receipt-write.py` at r62; carried in the
round-66 matrix rows D and N4 of `census/round-66/c1-matrix.tsv`). In-lane grep finds it only in
souji's own r62 wave artifacts and the writer. **No namespace collision**: no sibling document or
tool can satisfy, shadow, or forge souji's index-flag class. C1-positive (the counter binds refusal
classes by stderr substring — souji r62 finding F9 — so class-token uniqueness is load-bearing).

## GIT_CONFIG_COUNT (438 files) — selected hits

| hit | ground | C1/C2 overlap |
|---|---|---|
| `mado-shokunin/.ufo/waves/round-66/w1/R66ConnSiblings.md:87` (citing tsukuroi `tools/check-adjacency-table-r51.py:52-53,187-191`) | mado's own r66 connector catalogs tsukuroi's 16-name `REDIRECT_ENV` (GIT_DIR, GIT_WORK_TREE, GIT_OBJECT_DIRECTORY, GIT_ALTERNATE_OBJECT_DIRECTORIES, GIT_INDEX_FILE, GIT_REPLACE_REF_BASE, GIT_COMMON_DIR, GIT_NAMESPACE, GIT_CONFIG, GIT_CONFIG_GLOBAL, GIT_CONFIG_SYSTEM, GIT_CONFIG_COUNT, GIT_CEILING_DIRECTORIES, GIT_EXEC_PATH, PYTHONPATH, PYTHONSTARTUP) and tameshi `registry-check.py:36-45` (removes every inherited `GIT_*`) | **closest prior-art index** to C1's env rows; an override is "never a measurement" — the principle souji's E-rows implement at accept-time |
| `kumitate-shokunin/.ufo/waves/round-46/build/ExecC1Scrub.md:11-14,71-74` | kumitate fence: `GIT_LOCAL_ENV_VARS` = the 15 names of host `git rev-parse --local-env-vars` (git 2.56.0): GIT_ALTERNATE_OBJECT_DIRECTORIES, GIT_CONFIG, GIT_CONFIG_PARAMETERS, GIT_CONFIG_COUNT, GIT_OBJECT_DIRECTORY, GIT_DIR, GIT_WORK_TREE, GIT_IMPLICIT_WORK_TREE, GIT_GRAFT_FILE, GIT_INDEX_FILE, GIT_NO_REPLACE_OBJECTS, GIT_REPLACE_REF_BASE, GIT_PREFIX, GIT_SHALLOW_FILE, GIT_COMMON_DIR + `scrubGitLocalEnv()` + planted-canary hermetic case | **canonical host-verifiable superset** of souji's six refused vars (all six are inside the 15); key arithmetic for the verdict below |
| `kaidoku-shokunin/.ufo/waves/round-23/w1/CounterGitIsolation.md:32-41,135-141` and `round-23/w2/ResidualGit.md:29,46` | kaidoku counter: GIT_* scrub then pins GIT_CONFIG_NOSYSTEM=1, GIT_CONFIG_GLOBAL=/dev/null, GIT_CONFIG_COUNT=1+core.hooksPath=/dev/null; residual named: `core.attributesFile` (GIT_CONFIG_KEY_1) not yet pinned | adjacent (counter-side scrub vs souji's writer-side refusal); the named residual is the same L3-style boundary discipline |
| `chousa-shokunin/.ufo/waves/round-63/w1/ExecProbeEnv.md:17,24` and `MutProbe.md:47-48` | chousa git-revision-probe env legs (`cfgcount`: GIT_CONFIG_COUNT=1…) and mutant harness run under outer GIT_CONFIG_COUNT injection | same variable, opposite direction: siblings inject to prove isolation; souji's writer must refuse presence |
| `kama-shokunin/.ufo/waves/round-23/build/advice/SrcGitConfig.md:38,52,88-98` | kama S089 corpus row anchoring git-config(1) §ENVIRONMENT GIT_CONFIG_COUNT (precedence: `-c` > env pairs > files) | documentation ground; supports why refusing presence (not content) is the fail-safe reading |
| `kama-shokunin/.ufo/waves/round-29/w2/CounterDeterminism.md:129` | kama's env sanitizer "strips GIT_DIR, GIT_WORK_TREE, GIT_INDEX_FILE, GIT_OBJECT_DIRECTORY, GIT_ALTERNATE_OBJECT_DIRECTORIES, GIT_REPLACE_REF_BASE **but not GIT_CONFIG_**" — a GIT_CONFIG_COUNT injection (blame.ignoreRevsFile) reached the counter; output survived only because the direction was fail-closed | **observed sibling leak of exactly souji's E1-class variable**; scrub-side hygiene is insufficient, refusal-side binding is the missing half |
| `mori-shokunin/.ufo/waves/round-49/w1/Mo49ExecScratchHygiene.md:28,176-197` | mori uses GIT_CONFIG_COUNT to inject an external `core.excludesFile` projection (scratch-hygiene measurement on the real lane, no write) | touches souji's L1/L2 untracked-visibility limit from the injection side |
| `kasegi-shokunin/.ufo/waves/round-37/wave1/MutC1Suite.md:32` | poison lever (see showUntrackedFiles row 1) | C1-adjacent |
| `game-dev-3d-shokunin/reports/round-103/gate/a4-attack.md:74-77` | http.proxy injection attack leg on a gate script | same weapon, unrelated surface |
| `kake-shokunin/.ufo/waves/round-31/w1/CriticSandboxThreatModel.md:51` (R9), `round-29/w1/ReviewCounterC2Code.md:67-69`, `round-59/w1/SentinelCounters.md:110-112`, `round-61/w2/SentinelC1Path.md:186-189` | kake gate/runner env-containment rows: envleak class, hostile-env reruns byte-identical, PATH-wrapper probe | same class, gate-side; no receipt writer involved |

Incidental remainder (~430 files): kama fault-grid advice, kaidoku r20/r22 mutation harnesses,
mado r43/r66/r67 landing scripts, tsukuroi tool diffs — all scrub/inject harness usage, no
receipt-accept-time refusal anywhere.

## GIT_OBJECT_DIRECTORY / GIT_ALTERNATE_OBJECT_DIRECTORIES (363 files) — selected hits

| hit | ground | overlap |
|---|---|---|
| `kaidoku-shokunin/.ufo/waves/round-80/w1/SentinelScope.md:131-135,231,247` | kaidoku r80: provenance git children inherit the full env; "GIT_OBJECT_DIRECTORY/GIT_ALTERNATE_OBJECT_DIRECTORIES can make an arbitrary object store the source of 'committed' blobs… **The receipt records no environment, so a reader cannot tell which store was read**" | **the recorded gap souji's E4/E5 refusal closes for souji's own writer** — same problem, sibling admits it un-fixed |
| `kama-shokunin/.ufo/waves/round-29/controls/CtlObjectStore/REPORT.md:125-130` | kama control: env scrub covers the redirect vars, so substitution was wired through `.git/objects/info/alternates` — "the one alternate-store channel that survives the environment scrub" — and was still refused | E4/E5 same vars, control-shaped; also names the config-side channel env cannot disable (out of env scope) |
| `kama-shokunin/.ufo/waves/round-30/controls/CtlTamper/report.md:9-11,50-52,67-71,91-94` | kama tamper control: alternate store + custom GIT_REPLACE_REF_BASE namespace; all three vectors neutralized by `--no-replace-objects` + GIT_NO_REPLACE_OBJECTS=1 + env filter | E6 same var, mature prior art |
| `kake-shokunin/.ufo/waves/round-28/residual/CriticC1FollowUp.md:46` | kake fix prototype: "drop the variables that `git rev-parse --local-env-vars` lists … then pass that environment as `env=`" — fixed E1–E4 false-cleans | the local-env-vars discipline as an observed *repair* for false-cleans |
| `chousa-shokunin/.ufo/waves/round-53/w1/R53ExecSeedRuns.md:177-179` | chousa operator precondition: measuring shell must export no GIT_DIR/GIT_WORK_TREE/GIT_OBJECT_DIRECTORY (ENV_CHANGED exit 2) | the fleet already treats this class as a documented precondition |
| `mado-shokunin/.ufo/waves/round-66/w1/R66CriticLanding.md:125-129,183-187` (+ its `report.md` twin) | **same-round sibling**: mado r66 — baseline (r65 nav) read a GIT_REPLACE_REF_BASE-substituted corpus (RED/1); v2's blanket `${!GIT_@}` unset neutralizes it (GREEN); GIT_NAMESPACE=e produced no local redirect | **closest same-round env ground** (see verdict) |

Incidental remainder: strace lines and scrub lists in audio/chousa/kagi/tameshi/kotodama reports.

## GIT_REPLACE_REF_BASE (91 files) — selected hits

- `kumitate-shokunin/.ufo/waves/round-90/w1/K90Sentinel.md:26,53,67` — **A9c (LOW, live): caller-env
  GIT_REPLACE_REF_BASE survives kumitate's `gitEnv()` (which drops GIT_DIR, GIT_WORK_TREE,
  GIT_INDEX_FILE, GIT_OBJECT_DIRECTORY, GIT_ALTERNATE_OBJECT_DIRECTORIES, GIT_COMMON_DIR,
  GIT_NAMESPACE, GIT_PREFIX, GIT_CEILING_DIRECTORIES — but not GIT_REPLACE_REF_BASE, nor
  GIT_CONFIG_*) and redirects the judged blob; the tool binds the replacement bytes and prints
  CLEAN. RD-5 recommends GIT_NO_REPLACE_OBJECTS=1 + dropping GIT_REPLACE_REF_BASE/GIT_CONFIG_* —
  "Fix untested by me"**; carried into `corpus/lessons/round-90.md:67-69` as shipped in v4.
  Ground: kumitate verdict tool. **The one sibling running defect of exactly souji's E6 class** —
  partial-scrub honored the env on the data-read side while the verdict stayed green.
- `kama-shokunin/.ufo/waves/round-12/advice/AttackSourceAnchor.md:45-49`; `round-22/build/advice/CritOracle.md:77-80`;
  `round-23/falsify/advice/RowF03ReplaceHides.md:54-56,69-76`, `RowF05ReplaceFleet.md:71-76`;
  `round-29/w1/out/ReviewCounterCode/findings.md:25-27,182-186`; `round-35/w1/out/RerunCounterBase.md:35-37,156-158`;
  `round-50/w1/out/X14FenceLane.md:118-121` — kama's replace-ref isolation literature: env var,
  refs/replace, grafts and alternates vectors; `--no-replace-objects` + scrub + pack-refs/namespace
  probes. Ground: kama oracle isolation. E6 prior art, complete on the kama side.
- `mado-shokunin/.ufo/waves/round-66/w1/R66CriticLanding.md:126,184-187` — same-round ambient
  neutralization (blanket bash unset). Ground: mado r66.
- `tabi-shokunin/.ufo/waves/round-37/w1/ExecPinsBinding/run-custom-replace-namespace.sh` —
  custom replace-namespace runner under pins. Ground: tabi pins binding. Adjacent harness.

## core.excludesFile (72 files) — selected hits

- `kengaku-shokunin/.ufo/waves/round-45/w1/R45SentFenceDesign.md:78,165-166,207-208` — fence row 12:
  `core.excludesFile = <outside>` is opened by `status --porcelain` / `ls-files -o
  --exclude-standard`; verdict **UNCOVERED**; proposed refusal key-list includes
  `core.excludesFile`. Ground: kengaku fixture fences.
- `kengaku-shokunin/.ufo/waves/round-46/w1/R46CritC1SealConfig/sealed/NOTES.md:3`,
  `round-48/w1/R48C1ExecFenceA.md:268,364-367,556-558`, `round-49/w1/R49C1ExecFenceB.md:64-66` —
  kengaku fences refuse repo-local `.git/config` key `core.excludesFile` (with
  `core.attributesFile`, `core.hooksPath`, `[include]`, `[url …] insteadOf`) at fixture admission.
  Ground: kengaku fences. **Adjacent to souji's frozen limit L1** (repo-local core.excludesFile
  stays outside C1): kengaku refuses it on a different surface (fixture admission, not a receipt).
- `tabi-shokunin/.ufo/waves/round-24/w2/RevSelfAssessmentCode.md:83-87` — HOME carrying
  `core.excludesFile = *` ⇒ `exit=0, clean=true` (global excludes hide the dirt); `.git/info/exclude`
  does the same; hardening dead for exactly the dirty-observing calls. Ground: tabi
  self-assessment tool. **The exact untracked-visibility hazard souji's L2 pins neutralize for the
  writer's honest rows.**
- `kumitate-shokunin/.ufo/waves/round-65/w1/K65ReviewToolSandbox.md:79` — residual: fixture builder
  still inherits global git config incl. `core.excludesFile`; exclusions not neutralized. Ground:
  kumitate tool sandbox. Sibling-side unresolved residual of the same class.
- `mori-shokunin/.ufo/waves/round-49/w1/Mo49ExecScratchHygiene.md:176-197` (external excludes
  projection), `kama-shokunin/.ufo/waves/round-50/w1/out/V5Review.md:33` (fixture inherits user
  config; hardening `-c core.excludesFile=/dev/null`), `kotoba-shokunin/.ufo/round-21/scouts/H3.md:41,71,175-179`
  (host state: unset; check-ignore authoritative), `mado-shokunin/.ufo/waves/round-18/w1/reports/ConnJjFleetFixes.md:230-231`,
  `mori-shokunin/.ufo/waves/round-25/w1/ReviewPycacheRule.md:56` (host state: unset) — hygiene/host-state
  ground, L1-adjacent. `kama-shokunin/.ufo/waves/round-72/w1/LAB01Probes.md:424-425` — global
  excludes sources named as *not probed*. `tsukuroi-shokunin` (39 files, not individually sampled):
  per mado's catalog, tsukuroi owns the config-name prior art incl. the REDIRECT_ENV list.

## receipt writer (64 files) — selected hits

- `audio-shokunin/reports/round-6/r6-simplifier.md:10`, `corpus/live/r75-scribe/r75-scribe.prior-draft.md:117`,
  `reports/round-98/r98-verifier.md:92-96` — timestamped JSON receipt writers for audio probes;
  crash-on-duplicate-stamp and mkdir gaps. Ground: audio instruments. No env/mode ground.
- `kaidoku-shokunin/.ufo/waves/round-44/w1/R44Simplify.md:172-175`, `round-45/w1/R45W1RegR44C1Run.md:45-49` —
  one frozen receipt writer per round; OSError in writers indistinguishable from carrier failure.
  Ground: kaidoku carriers. Robustness notes only.
- `kasegi-shokunin/.ufo/waves/round-43/w1/CritReceiptForge.md:10-13`, `ExecSuiteSkeleton.md:20-24`,
  `ScribeReportSkeleton.report.md:89-93` — receipt writer inside kasegi's closure.sh export harness;
  receipt-forgery audit seat. Ground: kasegi closure suite. Forgery-attack class, no env/mode rows.
- `kengaku-shokunin/.ufo/waves/round-69/w1/EvidenceIndex.md:147-152` + `ReceiptReverify.md:13-16` —
  the grader's receipt writer and its checker disagree on `VECTOR` arity; **every genuine receipt
  is refused** by the checker. Ground: kengaku graders. **C2-adjacent lesson**: writer/checker
  contract drift is exactly the calibration failure mode souji's C2 statement population guards
  against — but no env-route or mode-bit ground.
- `kengaku-shokunin/.ufo/waves/round-76/w1/SentinelR76.md:63-66` — battery receipt writer can
  overwrite arbitrary writable paths (unrestricted `Path` + `write_text`). Ground: kengaku.
  Writer-safety, not C1's axes.
- `kotodama-shokunin` (19 files) — lesson-copy fixture prose mentions receipt writers; ground:
  kotodama corpus. No overlap.
- `kama-shokunin/.ufo/waves/round-56/w1/out/W03TrendReview.md:207-208`, `round-62/w1/E08DepsAudit.md:263-267`,
  `round-64/f/CR05C2Fidelity.md:183-186`; `mori` (4), `tabi` (5) — writer maintenance notes
  (append `exit=$?`, missing receipts as finding, ctx-printer sentence). Ground: per lane. No overlap.

**Net: no sibling receipt writer refuses caller-injected git env routes, records permission bits,
or refuses symlink retarget. Souji's C1 surface is unclaimed.**

## st_mode (2823 files) — composition classes (all hits reduce to four shapes)

1. **strace evidence** `{st_mode=S_IFREG|0644, …}` — e.g. `chousa-shokunin/.ufo/waves/round-44/w2/W2SimpSep.md:132-133`,
   `round-46/w2/SentC1Path.md:23`, `kagi-shokunin/.ufo/waves/round-23/falsify/SentHostReads.md:157`
   (+ its r27 sandbox copy). Incidental trace output; no claim on mode bits. Dominant class by volume.
2. **Guard-shaped** `stat.S_ISREG / S_ISLNK(st.st_mode)` refusal of non-regular/symlink inputs —
   `chousa-shokunin/.ufo/waves/round-56/w1/R55W2SentBuilder.md:63-64`, `round-59/w1/R59Executor11.md:372-378`,
   `R59Executor13.md:242-246`, `R59Executor15.md:243-250`; `kaidoku-shokunin/.ufo/waves/arc3-loop1-round1/claims/c2/EX-22/patches/citation-drift-pinning.patch.md:105-109`,
   `arc3-loop1-round2/claims/c2/RV-10/proposed-nonregular-and-usage-exit.patch.md:31-35`,
   `round-14/w1/GateInputSafety.md:65-67`, `round-18/w1/SentinelReaEnv.md:30-31`;
   `kaidoku-shokunin/.ufo/waves/round-70/w1/ScoutSource/sources.md:173-176` (r70 tools: 0 mode hits —
   work-dir predicate checks distinctness, not mode/ownership). Ground: input guards. **Adjacent to
   SY3** (symlink refusal) — but guard-shaped, not receipt-shaped.
3. **Executability/mode-as-attribute** — `kaidoku-shokunin/.ufo/waves/arc2-loop1-round5/V4.md:53-57`
   (`st_mode & 0o111` vs git blob 100755), `round-64/w1/ScribeLesson.md:23-27,57-61` + draft M64-2
   (pin check compares sha256 only, no executability — filed as a process gap). Ground: artifact pins.
4. **The C1-relevant negative** — `chousa-shokunin/.ufo/waves/round-61/w1/MutC1ExtraWrite.md:64-66`:
   umask 000/0600/0666 probes changed file modes and *"The counter's `snap()` compares content
   digests and symlink targets, **never `st_mode`**"* — sibling receipt-scoring is blind to mode
   bits, observed. **This is the gap souji's MOD2/MOD3 rows (full permission bits, setuid/setgid/
   sticky included, recorded in the in-run snapshot) close.** No sibling writes permission bits
   into a receipt or scores them.

---

## Overlap verdict

The closest sibling ground to souji round 66 is **mado-shokunin's own concurrent round-66**: it is
fighting the identical variable class this round — ambient `GIT_REPLACE_REF_BASE` demonstrably
redirected mado's r65 navigation (RED/1) until a blanket `${!GIT_@}` unset neutralized it
(`mado .ufo/waves/round-66/w1/R66CriticLanding.md:126,184-187`), and mado's connector seat
(`R66ConnSiblings.md:87`) has already indexed the fleet's env-scrub prior art (tsukuroi's 16-name
REDIRECT_ENV, tameshi's full `GIT_*` removal) as "an override is never a measurement". It is
nevertheless **not overlap in the claim sense**: mado's surface is its landing-gate's corpus
*reads* (scrub-side neutralization inside bash counters), while souji r66 C1's surface is a receipt
*writer* that refuses the caller's six named variables at accept-time and then records full
permission bits and refuses a same-content symlink retarget — a different binding direction
(refuse vs scrub), a different artifact (receipt vs verdict), and three row classes (E-refusal,
MOD2/MOD3 recording, SY3) that **no sibling implements anywhere**: kumitate r90 A9c is the live
partial-scrub failure of exactly E6's shape (env honored on the data-read side, verdict green, fix
untested), kama r35 observed its own sanitizer passing GIT_CONFIG_* through, chousa r61 observed
sibling counters blind to `st_mode`, and `RECEIPT-INDEX` has zero sibling hits (souji-internal
class token, no namespace collision). Runner-up proximity: kengaku r45–r49 fence config-key
refusals (`core.excludesFile` refused at fixture admission — L1's ignore-route limit on a
different surface). Conclusion: souji r66 C1's claim surface is unclaimed fleet ground; the real
cross-lane relation is shared *vocabulary* (these terms appear 3,730+ times fleet-wide as
injection/scrub harness prose), which is harmless to C1 and positively safe for C2 — souji's
lexical needles are its own `RECEIPT-ENV-*`/`RECEIPT-INDEX-*` class tokens, which sibling text
can neither satisfy nor shadow.
