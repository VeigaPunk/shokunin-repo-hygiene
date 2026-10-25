# ScoutRegistry — souji r24 w1: SOURCES.md registry baseline at lane tip

## Status
STATUS: PASS — every requested measurement was run at lane tip f9db2181647d91470a724a12d626bd6106805076. The census validator exits 0 with 30 W04 warnings and 0 errors. The registry has 119 rows, S001–S119, with no gaps and no duplicate ids. For the target URLs, git-worktree and gitrepository-layout are already registered, count-objects has one docs row (S115), and path.c and builtin/count-objects.c have no rows.

## Evidence
Revision: lane HEAD `f9db2181647d91470a724a12d626bd6106805076`. `git rev-parse HEAD:corpus/SOURCES.md` and `git hash-object corpus/SOURCES.md` both return `c82f11138bffaba30386fec161ad5b4f658a8ef9`, so the working tree equals the committed bytes. Fleet `scripts/sources-census.sh` and `CORPUS.md` were last changed at fleet `6a1dd8ce`. git 2.56.0.

E1 — validator (run from fleet root):
```
$ /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji ; echo exit=$?
exit=0          (31 output lines: 30 W04, 1 ok, 0 E-codes)
souji	W04	S098 duplicate url www.gnu.org/software/coreutils/manual/html_node/timeout-invocation.html across scopes
souji	W04	S099 duplicate url git-scm.com/docs/git-rev-parse across scopes
souji	W04	S106 duplicate url docs.python.org/3/library/json.html across scopes
souji	W04	S108 duplicate url docs.python.org/3/builtins/exceptions.html across scopes
souji	ok	/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md
```
Among the 30 W04 warnings, the only one on a target URL is `souji	W04	S058 duplicate url git-scm.com/docs/git-worktree across scopes`.

E2 — row count, max id, gaps, duplicates:
```
$ grep -cE '^ {0,3}\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md
119
max id: S119   (grep -oE ... | sort -V | tail -1)
duplicate ids: (none)     id gaps S001..S119: (none)
rows indented by 1-3 spaces: 0     column count per row: 119 x 11 (NF=13)
```

E3 — histograms. The frozen CORPUS.md census awk run from the lane root agrees with `sources-census.sh census`:
```
malformed=0
tier:   A=113 B=5 C=1
status: mined=96 queued=15 rejected=8
census: souji rows 119 / tier.A 113 / tier.B 5 / tier.C 1 / status.mined 96 / status.queued 15 / status.rejected 8 (exit 0)
kind:   docs 104, code 6, community 4, own-work 3, book 1, spec 1
recheck: on-release 97, 180d 8, 365d 7, 90d 5, on-change 1, on-correction 1
```

E4 — rows whose URL matches a target (`grep -nE 'git-scm\.com/docs/git-worktree|gitrepository-layout|path\.c|count-objects'`, then filtered to the source column):

| id | source URL (normalized as by `url_of`) | scope (verbatim, truncated) | status | used-by |
|---|---|---|---|---|
| S003 | git-scm.com/docs/git-worktree | git 2.55.0 worktree lock, prune and porcelain list | mined | corpus/knowledge/git-auto-maintenance-prunes-worktrees.md |
| S058 | git-scm.com/docs/git-worktree | `extensions.worktreeConfig` read order only | mined | corpus/lessons/round-17.md |
| S033 | git-scm.com/docs/gitrepository-layout | git 2.55.0 worktrees/<id> admin files | queued | — |
| S115 | git-scm.com/docs/git-count-objects | the -v field set at git 2.56.0, including the garbage and size-garbage file counts and alternate paths; … | mined | corpus/knowledge/repo-size-census-readonly.md |

S118 (Qiita) and S119 (CSDN) also match `count-objects`, but only in scope or teaches text. Their URLs are qiita.com and bbs.csdn.net, and both are used by corpus/knowledge/count-objects-garbage-readings-r25.md. No row's source URL contains `path.c` or `builtin/count-objects.c`. The only git/git source rows are S009 (`github.com/git/git/blob/v2.55.0/builtin/gc.c`; worktree.c appears in its title only), plus v2.55.0 builtin/repo.c, v2.56.0 attr.c, and the master RelNotes tree.

E5 — cross-lane sharing (information only; W04 and E04 are within-lane checks):
```
$ scripts/sources-census.sh shared --root /home/vgpnk/Projects/shokunin | grep -E 'git-worktree|gitrepository-layout|path\.c|count-objects'
git-scm.com/docs/git-worktree	shared	kumitate,souji
git-scm.com/docs/gitrepository-layout	shared	kumitate,kama,souji
```

E6 — CORPUS.md § SOURCES.md (contract v1, frozen):
- CORPUS.md:86, the exact 11-column header (this is the grep line output, not a prose quote):
```
| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |
```
  The lane header is byte-identical at corpus/SOURCES.md:19, and the validator emits the same string at scripts/sources-census.sh:304.
- CORPUS.md:105-106 gives the allowed `recheck` forms: "`recheck` — ISO date or cadence (`90d`, `180d`, `on-release`)."
- The maintained validator is broader than that example list. scripts/sources-census.sh:28 reads "E09 invalid recheck (ISO date, NNd, or symbolic cadence)", and :582 reads `function symbolic(s) { return s ~ /^[A-Za-z][A-Za-z0-9 _-]*$/ }`. An ISO-shaped date must also parse to a real day (:663-664).
- CORPUS.md:116, append-only rule: "Only `status`, `recheck` and `used-by` change in place". The correction form is at :117-118: "A correction is a new row whose `teaches` opens `supersedes S0NN —`."

## Findings
1. **Next id: S120.** Max id is S119, there are 119 rows, and S001–S119 has no gaps (E2). CORPUS.md:89 says "`id` — `S` + 3 or more digits, the next unused; never reused." This conflicts with the preregistration's staged ids S134/S141/S147/S153 and the quarantine slice S114/S118/S123/…/S138 (preregistration.txt:128-131). S114, S118 and S119 are already used in this lane registry, so staged shokuknow ids MUST be renumbered from S120. The 11 collisions recorded at preregistration.txt:130 are consistent with this. Confidence: high.
2. **What triggers W04 versus E04** (scripts/sources-census.sh:600-605 and :643-653). The URL is the first `https?://` match in the source cell, with the fragment, trailing `/` and scheme stripped and the host lowercased. **E04** fires only when the same normalized URL appears with the identical trimmed scope string, the new row is not `rejected`, a prior non-rejected row has that URL and scope, and teaches does not contain `supersedes S\d{3}`. **W04** fires when the URL is already registered under a different scope. W04 does not change the exit code (E1 exits 0, and the header comment at :33 says "warnings do not affect clean lanes"). Confidence: high (read from source and observed).
3. **git-worktree DETAILS row (for C1 sourcing).** `git-scm.com/docs/git-worktree` already appears twice: S003 cites § DETAILS at 2.55.0, and S058 cites § DETAILS at 2.56.0, scoped to worktreeConfig. A third row with `#_details` or any fragment normalizes to the same URL, so it adds one more W04 (31 total). It hits E04 only if its scope repeats S003's or S058's scope verbatim. The other route is `used-by` on S003 or S058, which is an in-place change allowed by CORPUS.md:116 if logged old→new in the round lesson. However, S003's scope (lock/prune/porcelain at 2.55.0) and S058's scope (worktreeConfig) do not cover per-worktree `refs` under `worktrees/<id>` at 2.56.0. [INFERENCE] Citing either row for the garbage false positive would stretch its scope, so a new row with a distinct scope (W04, not E04) is the honest form.
4. **gitrepository-layout (S033) is `queued`, scope "git 2.55.0 worktrees/<id> admin files", used-by `—`.** If the C1 entry cites it for `worktrees/<id>/refs`, the allowed in-place changes are status→mined and used-by→path. Scope text cannot change (append-only), and S033's anchor lists only gitdir and locked at 2.55.0. [INFERENCE] A 2.56.0 refs claim therefore needs a new row with a distinct scope (W04) or a supersedes row.
5. **No `path.c` or `builtin/count-objects.c` row exists.** A new `github.com/git/git/blob/v2.56.0/path.c` or `.../builtin/count-objects.c` row has no within-lane or cross-lane duplicate (E4, E5), so it produces neither W04 nor E04. S009 shows the existing pattern for multi-file rows: one URL, extra files named in the title. `url_of` keys only the first URL, so a combined path.c and count-objects.c row keys on whichever URL comes first.
6. **count-objects: S115 is the only authoritative row** (docs, A, mined, at 2.56.0, scope includes garbage and size-garbage). Its anchor says "no write side effect documented". A new row for the same `git-scm.com/docs/git-count-objects` URL with a different scope gives W04. Repeating S115's scope gives E04 unless the teaches field begins `supersedes S115 —`.
7. **Some recheck values fall outside the contract's example list.** S039 `on-change`, S041 `on-correction`, and S017/S022/S027/S028/S029/S030/S048 `365d` are outside the `90d`/`180d`/`on-release` examples at CORPUS.md:106. The maintained validator accepts them (`NNd` and the symbolic regex), so validate stays clean. This bears on calibration but not on any r24 counter. Whether v1 meant those three as examples or as a closed set is unresolved.
8. **The baseline matches recorded counts.** The lane's committed SOURCES.md bytes equal the working tree (E-header). There are 119 rows, consistent with "reg-ids 119" in preregistration.txt:130.

## Unknowns
- W04 count after landing depends on how many rows C1 adds against already-registered URLs. Each new row on git-worktree, gitrepository-layout or git-count-objects with a distinct scope adds exactly one W04.
- Whether CORPUS.md v1's recheck list is closed (Finding 7) is not settled by the text.

Tooling: none installed or updated. Scratch was the single file `/var/tmp/souji-r24-ScoutRegistry.out` (the validate output), removed before finishing.
