STATUS: DONE — ALLOWED-EXEC validator ran clean (exit 0, 9×W04, the new one is S065); every claim of the round-18 provenance paragraph verified; findings: 0 blocking, 1 calibration note. Verdict: SOURCES items HOLD.

Godspeed axes: (1) executed evidence for the ALLOWED-EXEC validator; (2) W04 semantics and the S065↔S043 URL pair; (3) per-claim verification of the round-18 provenance paragraph. Frontier walked all three; nothing discarded.

# Claim under attack
SOURCES round-18 items S064–S071 (SOURCES row set behind C1/C2/C3 sourcing), specifically the ALLOWED-EXEC validator run, the new W04 on S065, and the accuracy of the round-18 provenance paragraph.

All paths below are at tip 5efb519f00075d958c3d1109ef6fcb24c487eb87 in /home/vgpnk/Projects/shokunin/souji-shokunin unless marked fleet-root. The validator itself lives at the FLEET root (scripts/sources-census.sh of /home/vgpnk/Projects/shokunin), not in the lane repo — consistent with the lesson's citation of that absolute path (corpus/lessons/round-18.md:43).

# 1. ALLOWED-EXEC validator run (exactly as named, run once)

```
$ /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji; echo EXIT=$?
souji	W04	S035 duplicate url git-scm.com/docs/git-repo across scopes
souji	W04	S036 duplicate url git-scm.com/docs/git across scopes
souji	W04	S038 duplicate url www.gnu.org/software/coreutils/manual/html_node/timeout-invocation.html across scopes
souji	W04	S049 duplicate url git-scm.com/docs/git across scopes
souji	W04	S057 duplicate url git-scm.com/docs/git-config across scopes
souji	W04	S058 duplicate url git-scm.com/docs/git-worktree across scopes
souji	W04	S059 duplicate url git-scm.com/docs/gitattributes across scopes
souji	W04	S063 duplicate url git-scm.com/docs/git-gc across scopes
souji	W04	S065 duplicate url www.gnu.org/software/bash/manual/html_node/The-Set-Builtin.html across scopes
souji	ok	/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md
EXIT=0
```

- Exit 0 with W-warnings matches the documented contract ("exit: 0 clean or warnings", "W-codes … never change status", fleet-root scripts/sources-census.sh:31,33) and W04's own header note "(warnings do not affect clean lanes)" (:33).
- The run graded the LANDED tip, not a drifted worktree: sha256 of live /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md == sha256 of `git show 5efb519:corpus/SOURCES.md` == `ed82dafcb023190a860e84e1fd8f55b7bd5e840a41b9029743ff35c0f91b044e`, and live lane HEAD is 5efb519 (`git rev-parse HEAD`).
- No E-codes; `souji ok`.

# 2. The new W04 on S065 — which other row shares The-Set-Builtin URL

**Answer: S043** (corpus/SOURCES.md:61) — "GNU Bash 5.3 manual, The Set Builtin `-n`". Exactly two rows carry the URL `https://www.gnu.org/software/bash/manual/html_node/The-Set-Builtin.html` (grep over the tip registry: lines 61 and 83 only).

Mechanism (fleet-root scripts/sources-census.sh, awk at :599-663, printf at :645): `url_of()` normalizes the first http(s) URL in the source cell (strip `#fragment`, trailing `/`, scheme; lowercase host only). E04 = same URL **and same scope** (both non-rejected, no `supersedes S[0-9]{3}`) — an exit-1 finding (:639-643). W04 = URL already seen but this (url, scope) pair is new → "duplicate url … across scopes" on the LATER row, warning-only. The selftest pins exactly this scope-sensitivity (:361-364 "W04-scope-sensitive-mutant", "W04-does-not-fail-validation" exit 0).

- S043 scope: `` ` -n` parse-only check, not runtime, unset-variable or undefined-function checking``.
- S065 scope (corpus/SOURCES.md:83): "what `set -m` changes for background jobs in a script; not notice/tty behaviour".
- Same URL, different scopes → W04 on S065 (second occurrence), no E04. Correct per design; nothing to fix.
- Newness proven: baseline b576341 registry has S043 (line 59) and NO S065; row count 63 → 71 (+8). The 8 pre-existing W04 ids in my run (S035…S063) are exactly the start list the lesson recorded (corpus/lessons/round-18.md:43), and that lesson start digest matches the baseline blob: `git show b576341:corpus/SOURCES.md | sha256sum` = `25c91f68e22a…` (lesson says `25c91f68…`). So the round's delta is exactly one W04, on S065. ✓

# 3. Round-18 provenance paragraph (corpus/SOURCES.md:13) — accurate. Claim by claim:

1. "new S064–S071 are opened this round on 2026-10-20 by wave-1 seats" — rows at :82-89 all `mined | 2026-10-20 | on-release | corpus/lessons/round-18.md`. Cited report globs exist at 5efb519 (`git ls-tree .ufo/waves/round-18/w1/`): 9 `Src*.md` (SrcGitAttrC, SrcBashJobControl, SrcKill2, SrcPySubprocess, SrcProcStat, SrcProcCwd, SrcFifoOpenNonblock, SrcGitLsTree, SrcCoreutilsTimeout) and 4 `ScribeRows*.md` (Git, Jobs, Proc, Py) — the Gate's seat attributions all resolve to real files. ✓
2. "URL, access record and a ≤25-word located quote for each are in corpus/lessons/round-18.md Gate" — lesson :32-39 gives all eight; lesson-stated word counts 13/15/21/22/22/20/20/12, all ≤25; I recounted S065 (15) and S066 (21) from the quoted text. ✓
3. "S065 rests on a Wayback capture because gnu.org timed out from this host (same failure S043 recorded)" — both rows record `curl exit 28` 2026-10-20 and cite the same capture 20260930073822 (SOURCES.md:61,83). I opened that capture: it resolves ("491 captures … 30 Sep 2026"), page is "The Set Builtin (Bash Reference Manual)", § 4.3.1, and the `-m` entry contains the Gate quote verbatim: "Job control is enabled (see Job Control). All processes run in a separate process group." Companion capture 20260803220758 (Job Control Basics, § 7.1) also verified live. ✓
4. "S064 is implementation source at git's tag v2.56.0 (host git 2.56.0)" — host `git --version` = 2.56.0. raw.githubusercontent.com/git/git/v2.56.0/attr.c (window :697-720) contains `read_attr_from_file` (head ≈:699) with the Gate quote VERBATIM: "if (flags & READ_ATTR_NOFOLLOW) fd = open_nofollow(path, O_RDONLY); else fd = open(path, O_RDONLY);" (≈:702-705), then `xfdopen` and `fstat(fd, &st)` strictly after the open — the teaches-claim ("plain blocking open … fstat only after … no pre-open guard") matches the code; window :938-950 shows the bootstrap info-frame `read_attr_from_file(git_path_info_attributes(), flags)` — anchors ":699-718" and ":940-948" line up. ✓
5. "No existing row changed" — `git diff --stat b576341..5efb519 -- corpus/SOURCES.md` = "1 file changed, 10 insertions(+)", ZERO deletions; `diff -U0` shows exactly two hunks: +provenance paragraph +blank (after old :12) and +8 rows S064–S071 (after old :79). ✓
6. "S038's anchor drift … logged in the lesson, not rewritten" — corpus/lessons/round-18.md:41 logs the coreutils 9.11-2 → 9.12-2 drift, routed r19 ("anchor rows to a digest, not a line number"); S038's row is byte-identical (0 deletions in the diff). ✓

# Findings by severity

- **BLOCKING: none.**
- **MINOR (calibration note, claim still true):** S065's anchor says "Edition 5.3 (18 May 2025)", but the captured node page carries no edition footer (makeinfo html_node pages don't; the extracted capture text ends at the nav bar). I verified the edition string independently on the manual master: gnu.org bash.html reads "This is Edition 5.3, last updated 18 May 2025, of The GNU Bash Reference Manual". Smallest fix, if capture-local evidence is wanted: add the master/Top-node Wayback capture URL to S065's anchor column. No row rewrite required — the statement is accurate.

# Residual risk / verification gaps

- S066/S067/S068/S070/S071 per-row remote anchors (man-pages line numbers :64-72/:76-78, Python "Last updated on Oct 20, 2026" footer, git-scm "last updated in 2.56.0" strings) were NOT re-fetched by me; the paragraph-level claims and all eight Gate entries were verified, and the two rows the paragraph names (S064, S065) were anchor-verified against the live remote.
- The validator was executed exactly once, exactly as named, against the live fleet root (ALLOWED-EXEC). No other validator invocation (so the baseline W04 list was derived statically + from the lesson's recorded start, which cross-checks byte-for-byte via the 25c91f68 digest).
- No tools installed or upgraded (none needed; pacman pause untouched). No jj run, no git writes anywhere; lane files untouched; clone /var/tmp/souji-r18w2-RevSourcesCensus deleted after this report.

# Verdict

**HOLDS.** Exit 0 with exactly one new W04 (S065, duplicate of S043's The-Set-Builtin URL across scopes — warning-only by design); the round-18 provenance paragraph in corpus/SOURCES.md:13 is accurate on all six of its checkable claims. Nothing to fix.
