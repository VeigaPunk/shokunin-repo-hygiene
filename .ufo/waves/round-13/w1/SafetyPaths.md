# SafetyPaths — r13 w1 (sentinel, read-only)

Seat: `SoujiR13.SafetyPaths`. Scope: the evidence-gate path contract and the quarantine baseline, checked for symlink escape, FIFO hangs and credential reads. I edited no lane file; my only write is this report. I am not an independent non-author. Certification stays OFF.

Axes: **calibration** (claims match the code), **operability** (bounded, fail-closed, with diagnostics), **coverage** (special-file and path classes each have a check).

## Pins (what I read)

| artifact | sha256 | state |
|---|---|---|
| `tools/souji-quarantine.sh` | `141c0fdc4eaf9d0a3d628b381cc5386f6d4be71565ddfb98aa10f6eb3c9573c9` | baseline: `git show 31984f4:` equals installed |
| `tools/souji-verify.sh` | `9adb17645a5f452ae2cc28673642ad256f9aee92109939531f3c34a0972812cd` | tracked |
| `tools/cand-merge-verify.sh` | `9adb17645a5f…` (same bytes as above) | tracked |
| `tools/souji-cert-evidence.py` | `5c86764da23108282bfa048ddb48aec84cad9843a385a53a841b57b3f991d49d` | **draft in flight** (seat EvidenceGate). It changed three times while I read it (`f2729f19…` → `10ebfcb4…` → `5c86764d…`). Gate line numbers below are from `5c86764d`. L1 must re-check them against the final bytes. |

Host: GNU coreutils 9.11 (`pacman -Qo /usr/bin/{mv,timeout,sha256sum}`), Python 3.14.7. The repo is on btrfs `@home` (st_dev 57); `/var/tmp` is on btrfs `@` (st_dev 31).

## Findings — quarantine baseline (`souji-quarantine.sh` @ 141c0fdc)

| id | sev | exploit / failure path | evidence (code lines) | impact | smallest remediation |
|---|---|---|---|---|---|
| SP-Q1 | medium (operability) | A file in quarantine is type-swapped during the 450 s hold (to a FIFO or a symlink). Alternatively, the engine returns SAFE(stale) for a nonregular `.scratch` file and the stage-1 pin fails. | `set -euo pipefail` at L121. Plain assignments `pin_sha=$(content_digest "$ct")` at L498 and `now_sha=$(content_digest "$QPATH")` at L284. `file_sha` returns 1 for a non-`-f` path (L723). `dir_digest` returns 2 (L729). **Fact (bash probe, not a tool run):** under `set -e`, `x=$(f)` with `f` returning 1 or 2 makes the script exit with that rc and print nothing. So the `pin=FAIL symlink-present-in-quarantine` branch at L290–291 is dead code. | The run aborts silently with rc 1, or rc 2. rc 2 is the documented *usage* code (L88–92). There is no RESULT/SUMMARY line and later targets are skipped. After stage 2 the copy stays in `.ufo-quarantine` with a staged `git mv`. No deletion happens, so the abort is fail-closed for data, but it gives no diagnostic (Q8 requires one). | `now_sha=$(content_digest "$QPATH") \|\| dig_rc=$?`, and the same `\|\| rc=$?` capture at L498 → `block_one`/ABORTED. Add one fixture hook: `rm -- "$1"; mkfifo -- "$1"`. |
| SP-Q2 | medium (Q8) | A stalled filesystem (FUSE/NFS/hung device) under a target, or a check-then-open race (`[ -f ]` L723 → `sha256sum` L724; `s18_scope_ok` L705–718 → `find\|xargs sha256sum` L731–732). | None of the per-target operations has a timeout: `git mv` L529, `mv` L536, `sha256sum` L724/L732, the engine child L1067–1068, `git cat-file\|sha256sum` L328. `grep -cE 'timeout [0-9]+[smh]? .*(mv\|sha256sum)'` → **0** (I ran it). | The stall is unbounded and only the driver kills it. Note that a direct FIFO hang is **already closed** in the baseline: `[ -f ]` at L723, a scope refusal at L714, and `find -type f` at L731 skips FIFOs (probe). A FIFO now hits SP-Q1 instead of hanging. | `timeout -k 5s 60s mv --no-copy -T -- "$ct" "$qpath"`. Wrap `git -C … mv` in `timeout -k 5s 60s`. Use `timeout -k 5s 120s sha256sum -- "$1"`. Treat rc 124/137 as ABORTED and never delete after it. |
| SP-Q3 | medium (calibration) | Q8's lesson pointer LOG.md:373 ("staged 3 files then hung (hit its 20-min driver timeout)"). | Hold default `HOLD=450` (L141). The hold runs **per target**, inside the flow (L553–557), and `--list` rows run serially (L640–656). 3 × 450 s = 1350 s, which is more than the 1200 s driver timeout. LOG.md:376–378: "94 copies byte-equal … 2 missing post-timeout". 93 manual + 1 tool-staged = 94, and 2 deleted by the tool after a PASS = 96 rows. | **[INFERENCE]** The r11 "hang" fits serial hold windows, not a stalled `mv` or digest. The hold value used then is not recorded (to-verify). A Q8 timeout fixes the LOG:403 FIFO class (another tool) but **would not have prevented LOG:373**. C2 must not claim that it would. | Report only (outside BoundQuarantine's assignment): print `planned-wall=N×hold` before stage 2, or stage all targets, hold once, then check all. |
| SP-Q4 | low | Partial-move residue. An untracked directory target sits on a nested btrfs subvolume or bind mount inside the repo, so `mv` gets EXDEV and falls back to copy+unlink. A timeout kill mid-copy leaves a partial copy in quarantine. | `mv -- "$ct" "$qpath"` at L536. GNU 9.11 `mv --help` lists `--no-copy  do not copy if renaming fails` and `-T`. | A partial copy plus the original, or a partial original if killed during the unlink phase. | `--no-copy -T`: rename(2) only, atomic, fails fast on EXDEV. `-T` also closes the qpath-collision race after the L477 check. |
| SP-Q5 | low (credentials) | A target directory holds a **hardlink** with a harmless name to a credential file. The repo and `~` are on the same `@home` subvolume, dev 57. | The secret refusal checks names only: `is_secret_shaped` L169–182 via `s18_path_ok` L690. `find -type f` includes hardlinks (probe: `hl.txt` listed). Then `sha256sum` reads the bytes (L732). The header claim at L105–106 ("no secret-shaped file is read") holds by name only. | The key bytes are hashed, and a 12-hex digest prefix can reach the evidence string (L293). Deletion removes only the link. | Refuse `stat -c %h` ≠ 1 for files inside `file_sha` and `s18_scope_ok`. |
| SP-Q6 | low (calibration, Q6 class) | The engine actually invoked is not the installed engine that certifiers hash. | L134–138: when `tools/cand-merge-verify.sh` exists, it **overrides** the default engine. The header (L109–110) says the default is `souji-verify.sh`. Today the two are byte-identical (`9adb1764…`), so behavior is unchanged. | If they diverge, a fragment pinning `souji-verify.sh` measures bytes that are not the ones that ran. The gate's `artifact-candidate` rule (cert-evidence L591) would *reject* an honest fragment that pins `cand-merge-verify.sh`. | Default to `$REPO_ROOT/tools/souji-verify.sh` only, or print `QENGINE <path> <sha256>` once per run. |
| SP-Q7 | low (Q4 text) | An inherited `TMPDIR=/tmp`. | `${TMPDIR:-/tmp}` at L1247, L1486, L1519. `grep -c 'TMPDIR:-/tmp'` → **3** (I ran it). L685 exports `TMPDIR=${TMPDIR:-/var/tmp}` first, so the effective default is `/var/tmp`. | Fails Q4's grep test as written. The new r13 fixture should hard-code `/var/tmp`. | `mktemp -d /var/tmp/…` |

## Findings — evidence-gate path contract (`souji-cert-evidence.py` draft @ 5c86764d)

Already sound (verified by reading the code, not by running the tool):
- **FIFOs, devices, directories:** rejected by `lstat` before any open (`_check_claim` L439, fragment path L517/L526–527).
- **Races at the final component:** opens use `O_NOFOLLOW|O_NONBLOCK` plus `fstat` S_ISREG (L276/L289, L311/L323). Probe: an `O_NONBLOCK` open of a FIFO returns immediately, so a race to a FIFO cannot hang.
- **Path shape:** `..` rejected (L220), absolute paths rejected (L215), NUL rejected (L213), symlink components below root refused (`_resolve_under`).
- **Aliasing:** inode aliasing across claims is detected (`fragment-shared` / `claim-shared`, by st_dev/st_ino).
- **Selftest:** uses `mkdtemp(dir="/var/tmp")` (L1099), `rmtree` in `finally` (L1334), and a subprocess `timeout=120` (L953). It includes `evidence-fifo` (L1244–1250).

| id | sev | exploit path | evidence | impact | smallest remediation |
|---|---|---|---|---|---|
| SP-G1 | medium (false success in output) | A fragment sets `"artifact": "x\nsouji-cert-evidence: clean"`, or puts a newline in an `evidence` or fragment path. | `_classify_rel` rejects only NUL and outer whitespace (L213). Raw keys are printed with `%s` at L423/429/432/437/440, L511/517/524/527, L616, L647. `_emit` joins lines with `\n`. | The output gets a forged `souji-cert-evidence: clean` line or forged `finding …` lines. The exit code stays 2 and `_reported_status` takes the first match (L969), but any consumer grepping the output, and `_finding_ids` (L961–964), can be fooled. **[INFERENCE: not executed — tool in flight]** | In `_classify_rel`, reject `any(ord(c) < 0x20 or ord(c) == 0x7f for c in value)` → `path-invalid` (this mirrors the quarantine check `[[:cntrl:]]` at L689). Also reject control characters in `author`/`class`. |
| SP-G2 | low–medium (credentials / operator sweep) | A fragment claims `artifact` or `evidence` = `census/operator-sweep-20261019/<f>`, `.env`, `id_ed25519` or `x.pem` under root. | No name or prefix refusal comes before `_digest_regular` (L611 artifact, L642 evidence). The evidence content is now **read in full** to check `evidence_sha256`. | The gate reads the operator-sweep file or a secret-shaped file under root. That breaks the round rule against reading sweep or secret content. The declared-sha comparison also works as a guess oracle. | Before any `lstat`/open, refuse components matching the lane list `*.env\|.env\|.env.*\|.envrc\|*credential*\|*secret*\|id_*\|*.pem` (case-insensitive; quarantine L176), and the prefixes `.git/`, `.ufo/state/`, `.ufo/watchdog.log`, `census/operator-sweep-*/`. New level-2 id `path-protected`. |
| SP-G3 | low (containment) | `tools/x.sh` is a hardlink to a file outside root, e.g. `~/.ssh/id_*` on the same dev 57. | Containment checks names only (`_resolve_under`). The inode check only catches aliases *within* the manifest. Probe: an `nlink == 2` hardlink passes a name/lstat walk. | An out-of-root file is hashed as "installed bytes". | Require `info.st_nlink == 1` for the artifact and evidence → `path-hardlinked`. Git checkouts have nlink 1. |
| SP-G4 | low | A bind mount or nested subvolume inside root. | No `st_dev` comparison with root. | Containment escape through a mount. | Require each component's `st_dev` to equal the root's `st_dev`. |
| SP-G5 | low (acknowledged) | A parent directory is swapped during evaluation. | Header L140–142 admits it. | TOCTOU (check-then-use race). | A dir-fd walk: `os.open(part, O_RDONLY\|O_DIRECTORY\|O_NOFOLLOW, dir_fd=d)` per component, then `os.stat(..., dir_fd=d, follow_symlinks=False)`, then `os.open(..., O_NOFOLLOW\|O_NONBLOCK, dir_fd=d)` and an inode compare. I validated this pattern in a probe (FIFO, symlink, hardlink and missing all refused; regular accepted). |
| SP-G6 | low (operability) | `--manifest` outside root, or reached through a symlinked parent. | L1385 `Path(args.manifest)` goes to `_read_text_abs`, which checks only the final component. | The manifest is uncontained (it is operator input, so this is low). | Resolve it with `_resolve_under(root, rel)`. |
| SP-G7 | low (operability) | A huge or sparse artifact or evidence file. | Only JSON has a cap (`MAX_JSON_BYTES`). Digests have no size or time bound. | The hash takes a long time; there is no hang class on local disk. | L1 runs the gate under `timeout -k 5 300`. Optionally cap the size. |
| SP-G8 | calibration note | `--root` = a `/var/tmp` copy. | — | Proves the copy's digest, not the installed bytes. | The C1 claim needs `--root /home/vgpnk/Projects/shokunin/souji-shokunin`, with fragments in that seat's own write set. |

## Proposed final checks for L1 (not run by me)

Run all of these with absolute paths, `git -C`, and fixtures only in `mktemp -d /var/tmp/…` with a trap cleanup.

1. `grep -cE 'timeout [0-9]+[smh]? .*(mv|sha256sum)' /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-quarantine.sh`: baseline 0, must be ≥ 1 after the fix.
2. `grep -c 'TMPDIR:-/tmp' /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-quarantine.sh tests/fixtures/r13-quarantine-bounds.sh`: baseline 3 in the tool; the new fixture must give 0.
3. `sha256sum /home/vgpnk/Projects/shokunin/souji-shokunin/tools/{souji-verify,cand-merge-verify}.sh`: they must stay equal, or the composition must be removed (SP-Q6).
4. Quarantine type-swap regression (red on baseline). Fixture hook under `SOUJI_Q_SELFTEST_ACTIVE=1 SOUJI_Q_TEST_HOOK=<hook>` (the same mechanism as A1 at L1455): `rm -- "$1" && mkfifo -- "$1"`. Wrap it in `timeout -k 5 120`.
   - Baseline: expect rc 1, no `^SUMMARY` line, and the FIFO left in quarantine **[INFERENCE]**.
   - Fixed: rc 3, `RESULT … ABORTED`, a `SUMMARY` line, and no hang.
   - Repeat with a symlink hook (`ln -s <fixture-file> "$1"`). Baseline expectation: rc 2.
5. `timeout -k 5 600 python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-cert-evidence.py --selftest; echo rc=$?`, run on the final bytes. Record the sha256 alongside.
6. Gate cases to add (each built inside the mkdtemp base; never point at real credentials):
   - (a) `artifact` containing `\n` → after the fix, rc 2 and `grep -c '^souji-cert-evidence: clean$'` = 0.
   - (b) A dummy file named `id_dummy` with harmless bytes → `path-protected`.
   - (c) A hardlink from `root/installed/x.sh` to `base/outside/x.sh` → `path-hardlinked`.
   - (d) An artifact FIFO (today only an evidence FIFO is covered).

## Limitations

- I did not execute either lane tool. SP-Q1, SP-Q3 and SP-G1 are read from code plus a bash-semantics probe. Their exact rc and output need checks 4 and 6a.
- The gate draft was still changing; SP-G1–G7 are pinned to `5c86764d` only.
- I did not check git `mv`'s EXDEV behavior (to-verify). I also did not check whether the engine actually returns SAFE(stale) for a FIFO file target. `s18_evaluate_path` (souji-verify L403–434) has no explicit nonregular rejection; the directory case is refused at L836.
- My probes ran in a `mktemp -d /var/tmp/souji-r13-safetypaths.*` directory with a trap; it was removed afterwards (confirmed by `ls`). Nothing under the operator sweep or any credential file was opened.
- Coordination: I sent SP-Q1–Q4 facts to `SoujiR13.BoundQuarantine`.
- Tool installs or updates: none.

## Addendum — landed gate re-read (`souji-cert-evidence.py` @ `0a16bb37ad3d42ac63a3a923c4d96d70639dce936625d9facc6c6a4a71fdb038`)

The EvidenceGate seat reported fixes for G1–G3. I re-read the code; I did not execute it.
- **SP-G1 closed in code.** L250 rejects `ord < 0x20` or `0x7F` and maps it to `path-invalid`. Caller paths in `_check_claim` are printed with `%r` (L450–456). Selftest case `control-char-path` is at L1353–1359.
- **SP-G2 mostly closed.** `_protected_reason` (L210–224) runs before `_resolve_under` and before hashing (claims L458–461; fragments L564; manifest L501; frozen L747/L766/L836/L846). It also catches the adjacent `census/operator-sweep-*` and `.ufo/state` pairs. Selftest case `protected-path` is at L1362–1369.
  - **Residual gap:** `PROTECTED_NAME_PATTERNS` (L199–207) lacks the lane's `.env.*` pattern (quarantine L176). `.env.local` and `.env.production` match neither `*.env` nor `.envrc`, so they would still be hashed.
  - **Minor:** `.ufo/watchdog.log` (quarantine L692) is not covered.
  - **Smallest fix:** add `".env"` and `".env.*"` to the tuple.
- **SP-G3 closed in code.** `st_nlink != 1` maps to `path-hardlink` for claims (L483–490) and fragments (L594–599). Selftest case `hardlinked-artifact` is at L1341–1350.
- **Still open (low, unchanged):** SP-G4 (`st_dev` mount crossing), SP-G5 (parent swap, acknowledged), SP-G6 (manifest containment; protected-name check only), SP-G7 (digest size bound; L1 should keep the `timeout` wrapper).
- **Note for L1:** the gate's line numbers moved again. Re-pin with sha256 at final check 5.
- **SP-G2 residual closed in code** (re-read @ `325c10e3b67e3b194d6b67792afdae80357df10e36c9f36d211d6eaa89c24902`): `PROTECTED_NAME_PATTERNS` L200–210 now has `.env`, `.env.*`, `*.env`, `.envrc` and `watchdog.log`. `watchdog.log` matches as a bare name anywhere, which is stricter than the `.ufo/` pair. The `protected-env-local` selftest case is at L1376–1383. The seat reports the battery at 36/36; I have not run it, and L1 must confirm it at final check 5.
