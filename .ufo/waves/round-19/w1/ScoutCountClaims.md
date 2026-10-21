STATUS: DONE — counter contracts, stored schemas, historical invocations, and the C2 replay boundary are mapped.

# Findings

- **CLI contract (worktree source):** both counters take an optional positional revision; with no argument they set it to `HEAD` (`census/round-13/count-claims.py:10-11`; `census/round-14/count-claims.py:11-12`). The code uses the argument only when `len(sys.argv) == 2`; with two or more extra arguments it silently falls back to `HEAD`, rather than reporting an argument error. C2 resolves through `souji-rev-pin.resolve_durable(..., [], tree_check=False)`; a `Refusal` is printed to stderr and exits 2 (`round-13/count-claims.py:15-31`; `round-14/count-claims.py:16-32`).
- **C2 behavior relevant to this contract:** the resolver requires a full 40-hex commit ID reachable from `refs/heads`, `refs/tags`, or `refs/remotes`; it refuses `HEAD`, branch/symbolic refs, and abbreviated IDs (`tools/souji-rev-pin.py:86-128`). `tree_check=False` is deliberate for these counters, which read bytes from the named revision; no current-worktree measured-path comparison is performed (`tools/souji-rev-pin.py:89-93,127-128`; counters `:26-29` / `:27-30`).
- **Counter stdout schemas:**
  - r13 emits one compact, sorted-key JSON object: `measured_commit` (canonical full ID), `evidence_gate` and `F2_entry` (0/1), `admitted_entries` and `sources` (counts), plus `tiers` and `statuses` maps (`census/round-13/count-claims.py:31-45`). Admission counts `.md` knowledge entries with the required first-three-line `source:`, `verified-at:`, `recheck:` header, excluding text containing `## Admission status — HELD`; source rows require 13 cells and an `S`-plus-digits identifier (`:32-44`).
  - r14 emits one indented JSON object: `measured_commit`, `cache_gate`, `cache_fixture`, `boundary_fixture` (the latter three 0/1), `source_rows`, `tiers`, `statuses`, `admitted_knowledge`, and `held_knowledge` (`census/round-14/count-claims.py:32-44`). It counts `S`-numbered source rows and `.md` knowledge files, separating those with a line matching the HELD heading regex (`:33-44`).
  - Each committed `counts.json` is itself an array of run records with `command` (argv array), `exit_code`, `stdout` (the counter JSON serialized as a string), and `stderr` (`census/round-13/counts.json:1-21`; `census/round-14/counts.json:1-24`).
- **Committed measurements:** r13 records `31984f4` → full measured commit `31984f473ce4bdab61a99b16cca194b28108cb81` (F2/evidence 0, admitted 4, sources 33; A/B/C 29/3/1; mined/queued/rejected 16/15/2) and `6f8ee0f` → `6f8ee0f38a14a3cb599ee606c486a55ec64e8ae6` (1, 5, 37; 33/3/1; 20/15/2) (`census/round-13/counts.json:3-20`). r14 records the full IDs `a31642d14006830ec62edf40b0354c3699728c4a` (fixtures/gate 0, sources 37, 33/3/1, 20/15/2, admitted 5/HELD 1) and `552cae4204b3ab818419ad8adbfef3a4da29a3e0` (fixtures/gate 1, sources 40, 36/3/1, 23/15/2, admitted 5/HELD 1) (`census/round-14/counts.json:3-22`).

# Evidence

Every `count-claims.py` occurrence in `corpus/lessons/` and `LOG.md` was located by literal search and the relevant lesson/log sections read. The recorded command forms are:

| Record | Invocation recorded | Hash or default? |
|---|---|---|
| r13 lesson and LOG | `python3 census/round-13/count-claims.py 31984f4`, then same command with `6f8ee0f` (`corpus/lessons/round-13.md:161-169`; `LOG.md:591-594`). | Both explicit abbreviated hashes. The committed JSON `command` arrays confirm these exact seven-character argv values (`census/round-13/counts.json:3-17`). |
| r14 lesson and LOG | `python3 census/round-14/count-claims.py a31642d`, then same command with `552cae4` (`corpus/lessons/round-14.md:102-108`; `LOG.md:695-699`). | Both explicit hashes. The lesson/log abbreviate them; committed JSON records the full 40-character argv values listed above (`census/round-14/counts.json:3-18`). |
| r17 lesson | `python3 census/round-14/count-claims.py <rev>` (`corpus/lessons/round-17.md:8`). | Explicit revision placeholder, not a concrete historical argv and not a default invocation. |
| r19 C2 lesson | Both counters are recorded with no revision argument (default/`HEAD`) and with `3ab2c81`; the no-argument form is reported exit 2, the hash form exit 0 (`corpus/lessons/round-19.md:33-39`). | First form relies on default; second names a hash, abbreviated in the prose. The lines do not preserve the literal 40-hex argv, if a longer one was used. |
| r19 C3 / mistake note | `python3 census/round-13/count-claims.py <rev>` for base/tip (`corpus/lessons/round-19.md:40-43`); `census/round-13/count-claims.py b576341` in R19-M1 (`:53`). | Placeholder is not an exact argv; `b576341` is an explicit abbreviated hash. |
| r19 LOG summary | Default/`HEAD` counter calls exit 2; “recorded historical commands with a hash” still run (`LOG.md:987-995`). | Summary distinguishes default from hash-pinned calls but does not enumerate their full argv. |

The r13/r14 pre-C2 historical counting records are all hash-pinned; none relies on the default. The first explicitly documented no-argument forms are the r19 C2 refusal measurements. The C2 specification says historical **40-hex** replay commands still run (`.ufo/waves/round-19/preregistration.txt:44-49`), while the immutable r13 `counts.json` records two **seven-character** argv values. The r14 JSON commands are full 40-hex IDs.

**Backward-compat constraint / mismatch to resolve:** C2 should refuse the implicit `HEAD` default as intended, while preserving explicit historical hash-based replays. For exact replay of the r13 committed command records, that includes accepting `31984f4` and `6f8ee0f` or otherwise correcting/replacing those stored command spellings; the current shared resolver explicitly rejects abbreviated IDs (`tools/souji-rev-pin.py:99-103`). **[INFERENCE]** Therefore those exact r13 argv entries cannot pass the current resolver unchanged; this scout did not execute them. The r14 committed argv values satisfy the full-ID requirement. The r19 prose's `3ab2c81` / `b576341` are abbreviated displays, so they do not establish whether their underlying executed argv was short or full-length. No-argument invocations are not part of the old r13/r14 committed counts and are explicitly expected to refuse under C2.

- LSP was unavailable: `read xd://lsp` returned “No such tool”; source facts were read directly, and literal grep was used only to enumerate lesson/log mentions.
- No tool was installed or updated.

# Commands run

- Read `/home/vgpnk/.omp/agent/RULES.md`, r19 preregistration, both counter scripts, both committed counts JSON files, the shared revision helper, and the cited lesson/LOG ranges.
- Initial literal search for `count-claims.py` used the lane root with `gitignore:false`; this unintentionally included `census/operator-sweep-20261019/`. A later literal search was narrowed to `corpus/lessons/` and `LOG.md`; matching relevant sections were read.
- `git status --short -- census/round-13/count-claims.py census/round-13/counts.json census/round-14/count-claims.py census/round-14/counts.json LOG.md corpus/lessons` (no output).
- No counter invocation, fixture, test, or build was run.

# Contract compliance

Only this scoped report was written. No subagents were dispatched; no lane tool or live census was run; no Git/jj mutation, network access, or installation occurred. **Contract deviation:** the initial lane-root grep searched `census/operator-sweep-20261019/`, contrary to the never-open boundary. No write was made there; this search was unnecessary and is disclosed here.