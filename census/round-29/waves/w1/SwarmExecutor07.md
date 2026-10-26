# SwarmExecutor07 — C2 symlink / special-entry surface (round 29, w1)

## Status

STATUS: PASS — all 14 committed `120000` paths (round 26 only; rounds 27 and 28 hold none) enumerated with target, relative/absolute kind, waves-dir escape and dangling status; the 14-vs-15 difference resolved to exactly one path (`manifest.sha256`); source-tree `cp -a` verbatim preservation verified 14/14; ledger dispositions probed against the frozen counter. One receipt defect (5 absolute host-path targets committed) and two counter-gaming vectors are reported below without changing any predicate.

## Evidence

Revision under test: `691dd29211c53d0ef94fa072394cb9c8a69fe92e` (lane base; prereg commit `b8cb4b31` is a descendant and `census/round-26..28` are byte-identical between them: `git diff --stat 691dd29 b8cb4b3 -- census` shows only `round-29` files). All lane access was read-only git; lane Python ran with `python3 -B`.

1. Frozen counter at base:

```
python3 -B census/round-29/c2-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev 691dd29211c53d0ef94fa072394cb9c8a69fe92e
r26 records=1382 failed=152 uncovered=14 floor_violation=0
r27 records=124 failed=0 uncovered=0 floor_violation=0
r28 records=75 failed=0 uncovered=0 floor_violation=0
SUMMARY manifests=3 failed=152 uncovered=14 floor_violations=0 rev=691dd29211c53d0ef94fa072394cb9c8a69fe92e
rc=1
```

2. Mode surface (`git ls-tree -r 691dd29211c53d0ef94fa072394cb9c8a69fe92e -- census/round-26/waves census/round-27/waves census/round-28/waves | awk '{print $1}' | sort | uniq -c`): `1187 100644`, `245 100755`, `14 120000`. Per round: r26 `993 100644 / 238 100755 / 14 120000`; r27 `118 / 7 / 0`; r28 `76 / 0 / 0`. No `160000` (gitlink) anywhere in the repository (`awk '$1=="160000"' | wc -l` → `0`); no FIFO/socket/device/block entry exists in the source trees (`find .ufo/waves/round-26 .ufo/waves/round-27 .ufo/waves/round-28 \( -type p -o -type s -o -type b -o -type c \) -print` → empty). Name surface: exactly 2 of the 1446 committed paths under these dirs carry a real newline byte in the name (`.../vadv54-run/r/nl/'first\nsecond.md'`, `.../vadv54-run/r/scratch/.scratch/'old\nname.log'`), both regular files, both recorded as GNU backslash escapes at `census/round-26/waves/manifest.sha256:1064-1065` and both present and hash-matching at rev (`1009b12c…`, `ae599d14…`); no committed name contains a tab or a backslash. The special-entry surface is therefore empty — symlinks are the whole non-regular surface.

3. The uncovered set at base, reproduced with the counter's own clauses (scratch replica of `census/round-29/c2-counter.py:73-90`): exactly the 14 `120000` paths below, each `not-listed` because `census/round-26/waves/symlinks.tsv` is absent at rev (`git cat-file -e 691dd29:census/round-26/waves/symlinks.tsv` → ABSENT). r27/r28 contribute zero. Full classification in `deliver-c2-symlinks.tsv`; the 14: `mock-cli/obsidian-cli`, `mock-cli/obsidian-cli-inspector`, `vadv-51/fixture/vault/x2-note.txt`, `vadv54-run/p/alias-dotdot-target.md`, `vadv54-run/p/alias-link.md`, `vadv54-run/q/led-chain.tsv`, `vadv54-run/q/led-dangling.tsv`, `vadv54-run/q/led-devnull.tsv`, `vadv54-run/q/led-link.tsv`, `vadv54-run/q/led-outside.tsv`, `vadv54-run/q/led-swap.tsv`, `tools/impl-21.sh`, `tools/impl-39.sh`, `tools/souji-census.impl-40.sh` (all under `census/round-26/waves/assimilation/validate/`). 12 distinct link blobs (two pairs share one blob each).

4. 14 vs 15 arithmetic over committed bytes: paths under `census/round-26/waves` = `993+238+14` = **1245**; manifest records = **1382**; records absent from the committed tree = **152**; present records = **1230**; hash mismatches = **0**. The two backslash-escaped records (`manifest.sha256:1064-1065`) are present and hash-matching, so they sit in the 1230, not in the 152 — the 152 are absent names only (a zero-hash-mismatch split is what the replica reports). Of the 1231 regular committed paths, 1230 are records; the one that is not is `manifest.sha256` itself. Paths with no verifying record = `14 symlinks + 1 manifest` = **15**; the frozen counter skips the manifest at `census/round-29/c2-counter.py:82` (`if not p.startswith(d) or p == m: continue`), so it reports **14**. The r28 closure's figure is the sentence `Also cover symlinks (15 uncovered tracked paths).` at `corpus/lessons/round-28-verifier-spotcheck.md:115`; it does not name its enumeration, and no committed r28 record contains a 15 (the r28 `c2-before.tsv`/`c2-after.tsv` are a different counter: `grounded_f4`, `SOURCES_rows`). The set of 15 is fixed by arithmetic; attributing the closure's 15 to the include-`manifest.sha256` variant is `[INFERENCE]`, and it is the only set of committed paths consistent with that number.

5. Source tree vs receipt (`find .ufo/waves/round-26 -type l | wc -l` → **17**; tracked at rev → **14**; `readlink` comparison for all 14 → identical, `source_verbatim=yes`): `cp -a` preserved every tracked link verbatim, never dereferenced. The excess 3 are `vadv-49/fixture/a{1,2}/source/link.txt` and `vadv-49/fixture/a4/vault/copy.txt`, ignored by `census/round-26/waves/assimilation/validate/tests/vault/vadv-49/.gitignore:1` (`fixture/`) and never committed. Absolute targets by host prefix: **4** under `/home/vgpnk/Projects/shokunin/souji-shokunin/tests/vault/...` (lane), **1** `/dev/null`, **0** under `/var/tmp`, **0** at the fleet root `/home/vgpnk/Projects/shokunin` itself. The 4 lane-absolute targets all exist at rev (`git cat-file -e <rev>:tests/vault/...` → exists), i.e. they resolve only while the repository sits at the recorded host path, outside the receipt.

6. Frozen-counter probe on a throwaway clone (`git clone -q --no-local <lane> /var/tmp/souji-r29-SwarmExecutor07.Omgkla/c`, identity via `git -C` inside that clone only; `rev-parse --show-toplevel` printed the clone before the first commit). Ledger = the 14 verbatim pairs. `failed` stays 152 throughout (unrelated to the uncovered axis):

```
A ledger committed, NOT in manifest          -> r26 records=1382 uncovered=1   (the ledger file itself)
B ledger + its sha256 record in manifest     -> r26 records=1383 uncovered=0
C led-outside.tsv retargeted RELATIVE, ledger col2 + manifest updated -> uncovered=0
D led-dangling.tsv link deleted, ledger row KEPT                      -> uncovered=0
E link deleted AND row deleted                                        -> uncovered=0
F led-link target in ledger altered, link untouched (positive control)-> uncovered=1
```

## Findings

1. **The entire committed symlink surface is 14 entries, all in round 26; rounds 27 and 28 are clean and there are no special/gitlink entries.** Location: `git ls-tree -r 691dd29211c53d0ef94fa072394cb9c8a69fe92e -- census/round-2{6,7,8}/waves`, mode histogram above; `deliver-c2-symlinks.tsv` columns `round`/`kind`.

2. **5 of the 14 carry absolute targets, so host paths are already in committed bytes.** 4 point into `/home/vgpnk/Projects/shokunin/souji-shokunin/tests/vault/...` and 1 at `/dev/null`. Location: `census/round-26/waves/assimilation/validate/tests/vault/vadv54-run/q/led-outside.tsv` (target `/home/vgpnk/Projects/shokunin/souji-shokunin/tests/vault/vadv54-run/elsewhere/led-outside.tsv`), `.../vadv54-run/p/alias-link.md`, `.../vadv54-run/p/alias-dotdot-target.md`, `.../vadv-51/fixture/vault/x2-note.txt`, `.../vadv54-run/q/led-devnull.tsv`.

3. **One link is dangling by design and must not be treated as a refusal signal.** `census/round-26/waves/assimilation/validate/tests/vault/vadv54-run/q/led-dangling.tsv` targets `missing.tsv` (absent from the tree at rev); it is the under-test "dangling symlink" fixture. Location: `deliver-c2-symlinks.tsv` row `dangling_at_rev=yes`.

4. **The 14 uncovered paths are exactly the 14 symlinks; nothing else in the three receipts is unaccounted.** Location: counter output (Evidence 1) and the replica enumeration (Evidence 3); `symlinks.tsv` is absent at rev.

5. **14 vs 15 is a one-path counting difference, not a missing or extra symlink.** The differing path is `census/round-26/waves/manifest.sha256`: the r28 closure's 15 includes the manifest that cannot record itself; the frozen counter excludes it at `census/round-29/c2-counter.py:82`. The 14 symlinks are identical in both counts. Location: `corpus/lessons/round-28-verifier-spotcheck.md:115` vs counter `:82`; arithmetic in Evidence 4.

6. **`cp -a` preserved the tracked links verbatim; the capture tool's refusal scan lets absolute targets through.** `tools/souji-wave-evidence-capture.sh:69` refuses only a symlinked source root, and the scan at `:84` accepts entries where `-L` holds, copying them "verbatim (never dereferenced)" (`:74-76`) and excluding them from the manifest (`find -type f` at `:157`). That is the mechanism by which Finding 2's host paths reached committed bytes. Location: `tools/souji-wave-evidence-capture.sh:69,74-90,154-161`.

7. **Adding `symlinks.tsv` naively breaks the capture tool's own identity check.** The source-vs-receipt comparison excludes only `manifest.sha256` and `summary.tsv` from the receipt side (`tools/souji-wave-evidence-capture.sh:189`), so a new `symlinks.tsv` makes the two hash sets differ and the tool exits 4 (`error: source and receipt file sets differ`). The ledger must be written before the manifest block (so it is hashed as a record — probe A/B) and excluded in that `find` prune. Location: `tools/souji-wave-evidence-capture.sh:157,189`; Evidence 6 A/B.

8. **Name surface carries two real newline bytes, both covered; a path-keyed ledger must escape if a symlink name ever does.** `census/round-26/waves/assimilation/validate/tests/vault/vadv54-run/r/nl/<first,newline>second.md` and `.../r/scratch/.scratch/<old,newline>name.log` are regular files, recorded at `census/round-26/waves/manifest.sha256:1064-1065` with a leading `\` and a `\n` escape, and both hash-match at rev (`1009b12c…`, `ae599d14…`); the counter's decoder resolves them (`unparsed_lines=0`). No symlink carries such a name today, so `symlinks.tsv` col1 is unambiguous for the 14 rows; a future capture writing a tab- or newline-bearing symlink path would need the same GNU escaping in col1, which the frozen counter's `split('\t')` does not decode.

9. **Ledger format that the frozen counter accepts:** tab-separated, col1 = path relative to the waves dir, col2 = raw `readlink` target, `#`-prefixed lines skipped, extra columns ignored (`census/round-29/c2-counter.py:75-79`), committed link blob must equal col2 byte-exactly (`:87`). A header row that does not start with `#` would be parsed as a row — `deliver-c2-symlinks.tsv` prefixes its column header with `#` for that reason.

## Attack log

- **ATTACK-1 (uncovered is satisfiable by rewriting an absolute link; verbatim preservation is unproven by the counter).** Probe C: retarget `led-outside.tsv` from the absolute host path to `../elsewhere/led-outside.tsv`, update ledger col2 and the ledger's own manifest record — `SUMMARY ... uncovered=0`, nothing fires. The counter compares only the committed blob to the ledger (`census/round-29/c2-counter.py:87`); it never compares a committed link to the source tree, so `uncovered=0` is self-consistency, not preservation. No predicate change proposed; the stricter guard is comparing `find -type l -printf '%P\t%l\n'` on source and receipt inside the capture tool.
- **ATTACK-2 (unaccounted deletion is invisible).** Probes D and E: deleting a committed link, with or without its ledger row, leaves `uncovered=0`, because the scan iterates committed paths only (`census/round-29/c2-counter.py:82-90`); a ledger row for an uncommitted path is never consulted. So "drop every problematic symlink" scores the C2 target identically to "account for every symlink". The tool-side guard must make an unaccounted exclusion fail rather than producing a clean ledger.
- **Positive control.** Probe F shows the equality clause is not vacuous: altering a ledger target while the link stays verbatim yields `uncovered=1`.
- No predicate, target, counter or case set is proposed for change; both vectors are priced into the recommendation as tool-side (stricter-only) guards.

## Recommendation (symlinks.tsv handling)

Record every symlink verbatim in `symlinks.tsv` — written by the capture tool from `readlink` as col1 = waves-relative path, col2 = raw target, optional col3 disposition — and hash the ledger into `manifest.sha256` (write it before the manifest block and add `! -name symlinks.tsv` to the source-vs-receipt prune at `tools/souji-wave-evidence-capture.sh:189`), because otherwise the frozen counter counts the ledger itself as uncovered (probe A: `uncovered=1`; probe B: `uncovered=0`); rewrite nothing, since retargeting falsifies evidence and is undetectable by the counter (probe C), and the links under test (`led-outside`, `x2-note`, `alias-*`) exist precisely to exercise absolute-target semantics; and **refuse absolute targets rather than commit them** — the capture tool must exit nonzero on a link whose target starts with `/`, unless it also writes an accounting row (path, raw target, `reason=absolute-target`) so the loss is visible in committed bytes, and any exclusion without such a row must fail the capture; relative targets (`obsidian`, `led-link.tsv`, `led-real.tsv`, `missing.tsv`, the two `impl-*` shims) are recorded byte-exactly and remain covered, which keeps the C2 target (`uncovered=0` over committed bytes) reachable while no `/home/...`, `/var/tmp/...` or fleet-root path is ever committed again.

## Deliveries

- `.ufo/waves/round-29/w1/deliver-c2-symlinks.tsv` — 14 committed `120000` rows at `691dd29` with target, kind, escape flags, dangling, resolved path, blob, source-verbatim check and disposition; first two columns are the frozen ledger's (path, target) pair.
- `.ufo/waves/round-29/w1/SwarmExecutor07.md` — this report.

No tool installed or upgraded this run. Scratch `/var/tmp/souji-r29-SwarmExecutor07/` and clone `/var/tmp/souji-r29-SwarmExecutor07.Omgkla/` are removed after this report; no lane file outside this wave directory was modified, and no git/jj mutation ran against the lane.
