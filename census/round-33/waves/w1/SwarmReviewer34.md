# SwarmReviewer34 — C2/O1 Q74 refusal baseline (tools/souji-evidence-cache.py)

## Status

STATUS: PASS — refusal baseline for every craftable guard of tools/souji-evidence-cache.py built and executed at 2d9bca55a9f042a2c9ed60a797a8069e74c41f46 (50 cases, two byte-identical runs), Q74 flip inputs recorded, delivery written for the L1.

## Evidence

- Revision: scratch clone of the lane at `2d9bca55a9f042a2c9ed60a797a8069e74c41f46`; `git -C <clone> rev-parse --show-toplevel` printed the clone; `git -C <clone> status --porcelain | wc -l` = 0; `git cat-file -p 2d9bca55…:tools/souji-evidence-cache.py | cmp -` against the working copy → `IDENTICAL`.
- Runner: per-case fixtures under `/fast/scratch/hyaku/souji-r33/RefusalBaselineO1/`, tool invoked as `python3 -B tools/souji-evidence-cache.py <argv>` (subprocess, `LC_ALL=C`, `PYTHONDONTWRITEBYTECODE=1`, `TMPDIR=<scratch>/tmp`; fleet rows `TMPDIR=<scratch>/fleet`).
- Count: 50 cases → rc distribution 44×2, 4×0, 2×1 (command: the driver's results JSON, 50 entries, 0 errors). Second full run into fresh fixtures: identical rc/status/finding lines for all 50 (`identical: True cases: 50`).
- Fidelity cross-check: every refusal case reproduces the rc and finding id the tool's own `--selftest` asserts for the same shape (selftest cases at tools/souji-evidence-cache.py:1259-1770 at 2d9bca55), e.g. symlink-leaf → rc 2 `path-symlink`, hardlink → rc 2 `path-hardlink`, frozen-tampered → rc 2 `snapshot_tampered`.
- Q74 flip inputs (base accepts, candidate must refuse): `TMPDIR=<scratch>/fleet` (a `git init` work tree, `rev-parse --is-inside-work-tree` = true) with `--root <scratch>/fleet/target` → rc 0 `reusable`; `--root <scratch>/fleet` itself → rc 0 `reusable`.
- Q74 source rule: corpus/QUALITY.md:179 — "a `TMPDIR` or target inside a git work tree is refused, the root itself is refused as a target" (verbatim, ≤25 words, no pipe).
- Tooling installs: none performed (no pacman/uv/npm usage; nothing to record).

## Findings

1. Guard enumeration — 46 refusal guards carry a craftable base input; all 46 were executed at the frozen rev with rc and verbatim finding line recorded (delivery table). Guard families: root boundary (`root-protected` ×5 shapes incl. `/var/tmp/token-audit` basename rule, `root-symlink` ×2, `root-not-directory`), record boundary (`record-protected` ×2, `record-unreadable`), dependency path (`path-protected` ×3, `path-symlink` ×2, `path-escape`, `path-absolute`, `path-invalid`, `path-not-directory`, `path-hardlink`, `dependency-not-regular`, `dependency-too-large`, `dependency-digest-invalid`, `key-noncanonical`, `key-invalid-encoding`), record shape (`dependencies-legacy/-empty/-invalid`, `matched-false-type`, `measured_commit-invalid`, `record-malformed`, `verdict-false-pass` ×2, `verdict-false-fail`), require (`dependency-undeclared`, `require-invalid`), frozen (`frozen-unreadable/-malformed/-schema/-incomplete`, `snapshot_tampered`, `snapshot-verdict-mismatch`), argparse usage error, plus level-1 `matched-false` and `dependency-digest-mismatch`. Location: tools/souji-evidence-cache.py at 2d9bca55 (guards: PROTECTED_* tables :287-311, `_protected_components` :341, `_resolve_root` :787, `_record_payload` :840, `evaluate` :1040, `evaluate_frozen` :1099).
2. Base accepts git-work-tree targets — the two Q74 flip rows return rc 0 `reusable` at base. The candidate repair must refuse both without moving any of the 44 refusal rows. Location: delivery rows `fleet-target-inside-worktree`, `fleet-root-is-worktree`.
3. `.config` protection is HOME-anchored — a `.config` directory outside a protected home is NOT protected. Observed: the alias fixture first returned rc 0 (`reusable`) when the symlink targeted a scratch-rooted `.config`; it returned rc 2 `record-protected` only after re-pointing the alias at a synthetic `$HOME/.config` (selftest's own construction). Location: tools/souji-evidence-cache.py:142-144 at 2d9bca55 — "Name patterns apply to every dependency key component but only" / "to the basename of an absolute root/record path" (verbatim, two lines); PROTECTED_ABSOLUTE :287-296. Consequence for the L1: keep the synthetic-HOME construction when re-running that row; a scratch-rooted `.config` silently stops testing the guard.
4. `--selftest` is not usable as the baseline runner under the scratch bound — it hardcodes its fixture root at tools/souji-evidence-cache.py:1295: `tempfile.mkdtemp(prefix="souji-r14-cache-selftest.", dir="/var/tmp")` (verbatim). It was NOT executed (would write /var/tmp, outside this seat's scratch bound); that hardcoded `/var/tmp` is the O1 defect itself. The per-case table replaces it as the refusal baseline.
5. Three guards have no craftable base input in this environment (delivery "Guards with no craftable base input here"): `key-alias` (unreachable by design per docstring :98-99), `dependency-device-escape` (needs a second filesystem inside the scratch root; scratch and /fast share st_dev 66309, /dev/shm st_dev 33 is outside the scratch bound), `internal-error` (no deterministic CLI input). These are baseline gaps, not lost refusals; the candidate re-run inherits the same gap list.

## Attack log

- No attack on a frozen predicate, target, counter, item or leg: this item is a measurement baseline, not a falsifier of a frozen claim.
- The Q74 write-scope probe (git-work-tree TMPDIR/target) was reproduced ONLY against a fake fleet root `git init`-ed inside `/fast/scratch/hyaku/souji-r33/RefusalBaselineO1/fleet`, per Q74's own rule (corpus/QUALITY.md:179: "A write-scope attack is reproduced only against a fake fleet root initialised inside scratch"). The real fleet root was never touched; `/etc`, `/`, `/var/tmp/token-audit` were passed as strings and refused lexically before any open.

## Deliveries

- /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-33/w1/deliver-c2-o1-refusal-baseline.md — 50-row baseline table (input recipe, base rc, base message, candidate expectation) + fixture recipes + gap list, for the L1 to re-run at the O1 candidate.
