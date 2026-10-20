STATUS: DONE — scoped operability harm review complete; 600 s is a defensible provisional ceiling for the observable repositories, but full-roster safety is unproven.

# Scope and axis

Axis reviewed: **operability**. This is a metadata-only harm review of C1's proposed per-repository timeout. No census or other protected tool was run against the fleet. No files other than this requested report were written.

# Findings (highest severity first)

## Low — 600 s is conservative for the seven observed manifest repositories, but not calibrated fleet-wide

**Verdict: PARTIAL.** No evidence in the allowed metadata indicates that any of the seven locally present manifest repositories would need 600 seconds for census work: their `.scratch` paths are absent, their Git object stores are small, and their direct root listings show ordinary repository files/directories. This makes 600 seconds a defensible, generous provisional timeout for those seven. It is not evidence that 600 seconds cannot time out a legitimate slow repository: six other manifest names have no matching direct checkout here, and the documented historical large-workload example is not a manifest entry.

The implementation's relevant work is traversal-sensitive, not simply proportional to bytes: `status` invokes `git status` (`tools/souji-census.sh:1122-1129`), `scratch_bytes` runs `du -sb -P` (`:1137-1149`), and `newest_mtime` walks regular files across the work tree with `find` (`:1152-1168`). The script explicitly says `git status` may read/hash tracked content (`:9-13`); `du`/`find` need to visit metadata, so a 40.4 GB apparent `.scratch` alone does not establish runtime. Conversely, file count and filesystem latency matter: the `find` comment identifies kotodama's `.scratch` as hundreds of thousands of files (`:1152-1155`), and SKILL documents its historical `.scratch` growth to 40.4 GB across rounds 1–6 (`SKILL.md:181-183`).

The seven direct manifest checkouts observed had no `.scratch`; `kotodama-shokunin` is not among the 13 `MANIFEST.json` roster repo values (`:5-110`), so I did not inspect it as a fleet-lane checkout. The other six manifest values without a matching direct checkout were `shokunin-game-audio`, `shokunin-godot-2d`, `shokunin-3d-engines`, `shokunin-world-bible`, `shokunin-binary-forensics`, and `shokunin-reverse-engineering`. Their worktree sizes and runtimes are unknown.

**Operability consequence:** 600 seconds means one slow or blocked repo can postpone all output for as much as 10 minutes (plus the specified 2-second TERM-to-KILL grace). The current emitter serially accumulates rows before printing them (`tools/souji-census.sh:1401-1415`). As a theoretical upper bound, if all seven observed repos reached the timeout, the per-repo waits plus two-second grace could total 4,214 seconds (70m14s); for all 13 manifest names if present and eligible, 7,826 seconds (2h10m26s). These are arithmetic bounds, not observed runtimes. The timeout is per-repo, not a fleet-wide deadline.

**Smallest fix/recommendation:** Keep 600 seconds as a provisional default rather than lowering it based only on the visible subset; do not claim that it is empirically safe for the whole fleet until a representative largest-worktree runtime is measured. The allowed metadata does not support selecting a better numeric threshold. If the intended operability SLO is materially less than 10 minutes before healthy-neighbour rows can be emitted, 600 seconds does not meet that SLO; that is a separate policy decision from whether a legitimate large scan needs 600 seconds.

## No implementation-level C1 verdict yet

At review time, the current script still has the pre-timeout serial loop at `tools/souji-census.sh:1394-1416`. The read-only command `git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff b5763415cc67ecff1e8fe56c58c39a6fb106d7a3 -- tools/souji-census.sh` returned `(no output)`. Thus this report reviews timeout sizing and observable baseline behavior only; it does not attest to an unlanded watchdog/process-group implementation.

# Metadata evidence

`MANIFEST.json` query `.roster[].repo` returned exactly these 13 values, in order: `kasegi-shokunin`, `kengaku-shokunin`, `kake-shokunin`, `kumitate-shokunin`, `kotoba-shokunin`, `kagi-shokunin`, `kama-shokunin`, `shokunin-game-audio`, `shokunin-godot-2d`, `shokunin-3d-engines`, `shokunin-world-bible`, `shokunin-binary-forensics`, `shokunin-reverse-engineering`.

The metadata command used for each of those names was exactly:

```sh
r=/home/vgpnk/Projects/shokunin/<repo>; printf 'repo=%s\n' "$r"; stat -c '%n type=%F size=%s blocks=%b' "$r" "$r/.scratch" "$r/.git" 2>&1; git -C "$r" count-objects -v 2>&1
```

For the seven matching direct checkouts, `stat` returned `type=directory` and `blocks=0` for the repo and `.git`, reported `.scratch: No such file or directory (os error 2)`, and `git count-objects -v` returned the exact values below (`count`, `size`, `in-pack`, `packs`, `size-pack`):

| Repo | repo dir size | `.git` dir size | count | size | in-pack | packs | size-pack |
|---|---:|---:|---:|---:|---:|---:|---:|
| kasegi-shokunin | 212 | 204 | 202 | 1840 | 270 | 1 | 331 |
| kengaku-shokunin | 230 | 204 | 348 | 2872 | 336 | 1 | 1165 |
| kake-shokunin | 226 | 240 | 488 | 3796 | 241 | 1 | 228 |
| kumitate-shokunin | 216 | 204 | 0 | 0 | 755 | 3 | 1501 |
| kotoba-shokunin | 230 | 224 | 132 | 1900 | 3942 | 2 | 22226 |
| kagi-shokunin | 212 | 204 | 176 | 1896 | 306 | 1 | 452 |
| kama-shokunin | 268 | 220 | 1026 | 8780 | 594 | 2 | 1179 |

Directory `stat` sizes above are directory-inode sizes, **not** recursive worktree sizes. `git count-objects -v` `size`/`size-pack` fields are Git object-store metadata, not working-tree size. Kotoba had the largest observed object store (`size=1900`, `size-pack=22226`).

For each of the six absent direct paths, the same command returned `stat: cannot stat '<path>': No such file or directory (os error 2)` for the repo, `.scratch`, and `.git`, followed by `fatal: cannot change to '<path>': No such file or directory` from Git. No object-store or scratch estimate is available for them.

The exact direct-listing commands were `ls -la -- /home/vgpnk/Projects/shokunin/<repo>` for each of the seven present repos. They showed these top-level entries (no `.scratch` entry in any listing):

- `kasegi-shokunin`: `.git`, `.gitignore`, `.ufo`, `AGENTS.md`, `LOG.md`, `PROVINCE.md`, `README.md`, `SCORECARD.md`, `SKILL.md`, `SHONEN.md`, `considerthese`, `corpus`, `plans`.
- `kengaku-shokunin`: `.git`, `.gitignore`, `.ufo`, `AGENTS.md`, `LOG.md`, `PROVINCE.md`, `README.md`, `SCORECARD.md`, `SKILL.md`, `SHONEN.md`, `considerthese`, `corpus`, `grader.py`, `plans`.
- `kake-shokunin`: `.git`, `.gitignore`, `.ufo`, `AGENTS.md`, `LOG.md`, `PROVINCE.md`, `README.md`, `SCORECARD.md`, `SKILL.md`, `SHONEN.md`, `considerthese`, `corpus`, `plans`, `scripts`.
- `kumitate-shokunin`: `.git`, `.gitignore`, `.ufo`, `AGENTS.md`, `LOG.md`, `PROVINCE.md`, `README.md`, `SCORECARD.md`, `SKILL.md`, `SHONEN.md`, `considerthese`, `corpus`, `plans`, `scripts`.
- `kotoba-shokunin`: `.git`, `.gitignore`, `.ufo`, `AGENTS.md`, `LOG.md`, `PROVINCE.md`, `README.md`, `SCORECARD.md`, `SHONEN.md`, `considerthese`, `corpus`, `plans`, `verifiers`.
- `kagi-shokunin`: `.git`, `.gitignore`, `.ufo`, `AGENTS.md`, `LOG.md`, `PROVINCE.md`, `README.md`, `SCORECARD.md`, `SKILL.md`, `SHONEN.md`, `considerthese`, `plans`.
- `kama-shokunin`: `.git`, `.jj`, `.gitignore`, `.ufo`, `AGENTS.md`, `LOG.md`, `MINT.md`, `PROVINCE.md`, `README.md`, `SCORECARD.md`, `SHONEN.md`, `SKILL.md`, `considerthese`, `corpus`, `plans`, `registry`, `tests`, `tools`.

# Verification gaps and residual risk

- No runtime benchmark was performed; the assignment prohibited running the census on the fleet and supplied no allowed large-repo fixture. No `du` command was run.
- `lsp` was unavailable: `read xd://lsp` returned `No such tool: xd://lsp` and listed mounted devices without an LSP device. No LSP status/references/definition/diagnostics could be requested.
- No test, build, or lint command was run. No tools were installed or updated.
- The principal residual risk is unmeasured metadata traversal time on the six absent manifest checkouts and the historical kotodama-scale workload. The available evidence supports retaining 600 seconds provisionally, not declaring a fleet-wide runtime guarantee.