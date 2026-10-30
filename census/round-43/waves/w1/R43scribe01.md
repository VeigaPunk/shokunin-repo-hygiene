# R43scribe01 — SOURCES draft report

## Behavior and verdict
PASS for the requested local-snapshot drafting deliverables, with a grounding limitation on S260 (not a pass for its full application claim). Axes: provenance, quote fidelity, locator precision, registry shape, scope calibration. No candidate scoring or product execution was performed.

## Commands and observed output
All paths below are lane-relative unless the command spells an absolute path. No network sources were opened.

Executed:
```sh
sha256sum /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-43/sources/man2-symlink.html /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-43/sources/python-3-library-subprocess.html
```
Observed output:
```text
c929903b2dec6c985e149ca27d509243e04fc80861d8b98c1f98e2325e857178  /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-43/sources/man2-symlink.html
5935a4afd34ad560cc5b66f0ed6e90d4d63ba9047ad8f367d5081474650078b5  /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-43/sources/python-3-library-subprocess.html
```
Executed separately:
```sh
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show f8c805dbfa7f45814cf9a7270fa8bbffb41a8373:census/round-43/sources/man2-symlink.html | sha256sum
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show f8c805dbfa7f45814cf9a7270fa8bbffb41a8373:census/round-43/sources/python-3-library-subprocess.html | sha256sum
```
Observed respectively:
```text
c929903b2dec6c985e149ca27d509243e04fc80861d8b98c1f98e2325e857178  -
5935a4afd34ad560cc5b66f0ed6e90d4d63ba9047ad8f367d5081474650078b5  -
```
Both working snapshots and committed snapshots therefore match the two assigned hashes.

Executed this read-only Python evaluation to count committed registry ids (the only child command is the shown `git show`):
```python
import re, subprocess
lane = '/home/vgpnk/Projects/shokunin/souji-shokunin'
cmd = ['git', '-C', lane, 'show', 'f8c805dbfa7f45814cf9a7270fa8bbffb41a8373:corpus/SOURCES.md']
r = subprocess.run(cmd, capture_output=True, text=True, check=True)
ids = [int(x) for x in re.findall(r'^\| S(\d+) \|', r.stdout, re.M)]
print('command:', ' '.join(cmd))
print('registry_rows=', len(ids), 'unique_ids=',len(set(ids)), 'max_id=',max(ids), 'S260_count=',ids.count(260), 'S261_count=',ids.count(261), 'next_ids=', [max(ids)+1,max(ids)+2])
print('missing_below_max=', sorted(set(range(1,max(ids)+1))-set(ids)))
```
Observed count line:
```text
registry_rows= 183 unique_ids= 183 max_id= 259 S260_count= 0 S261_count= 0 next_ids= [260, 261]
```
The final output line listed historical gaps S133-S151, S153-S209. Thus there are 183 rows, not 259; S260/S261 are the next append ids after maximum S259.

Tool reads (not shell commands): `read` opened `corpus/SOURCES.md:1-38`, `:-20`, and `:209-222:raw`; header line 28 establishes the eleven-column order and final rows include S258/S259. `grep` searched both assigned snapshots for `ELOOP|man-pages|Last updated|re-raised|killed and waited`, case-insensitive. `read` then opened symlink snapshot `:138-165,222-239` and subprocess snapshot `:258-295,2030-2040`. Skill reads: `skill://godspeed`, `skill://agent-self-evaluation`. No installations or upgrades.

## Located quotes and gates
- **S260, 9 words:** “Too many symbolic links were encountered in resolving linkpath.” HTML `ERRORS` heading line 143; ELOOP quote lines 163-164 of `census/round-43/sources/man2-symlink.html`. Marker: `Linux man-pages 6.19` at line 239; `COLOPHON` line 229 names `man-pages-6.19.tar.gz`.
- **S261, 25 words:** “If the timeout expires, the child process will be killed and waited for. The TimeoutExpired exception will be re-raised after the child process has terminated.” HTML `Using the subprocess Module` (lines 264-265), `subprocess.run` entry line 270, quote lines 289-291 of `census/round-43/sources/python-3-library-subprocess.html`. Footer line 2037: `Last updated on Oct 30, 2026 (04:20 UTC).`
Quotes remove HTML tags and normalize physical whitespace, without rewriting words. Expanded locators, hashes and boundaries: `.ufo/waves/round-43/w1/R43scribe01/gate.md`.

## Draft rows and touched surfaces
Two headerless TSV records are in `.ufo/waves/round-43/w1/R43scribe01/rows.tsv`. Exact registry column order: id, source, kind, tier, scope, anchor, teaches, status, opened, recheck, used-by. S260/S261: docs, A, mined, locally opened 2026-10-30, recheck on-release/365d respectively, used-by corpus/lessons/round-43.md. No cell contains a pipe character or an escaped pipe. The rows retain the requested application scopes but explicitly distinguish documented behavior from application inference.
Only the two seat artifacts and this seat report were written. The gate's quote word-count correction briefly replaced its section locator; a second surgical edit restored that locator and left one 9-word quote. Product, registry and frozen instruments remained read-only. No scratch directory or clone was created, so none remains to delete.

## Findings and known limits
1. **Attacks S260 requested source grounding, not an instrument:** requested wording verbatim: “a leaf symlink named by --json is refused, ELOOP is what an O_NOFOLLOW walk raises on a link”. The assigned symlink(2) ERRORS sentence concerns linkpath resolution; it does not establish O_NOFOLLOW behavior or the Souji refusal policy. Draft labels those as requested application scope requiring separate evidence rather than upgrading them to a source-backed claim.
2. **Bounds S261 inference:** the page documents child kill/wait and TimeoutExpired re-raise. “load-robust kill” is the fixture's application inference, not a documented performance result. Lines 291-294 explicitly qualify initial process-creation timeout delivery; descendant cleanup is not established.
3. Local reopening is not a live URL recheck, original fetch-date verification, fixture execution, or registry admission. No builds, tests, counters, scoring, commits, pushes, deployment or other agent runtime were run. Frozen-source facts only; no scoring outcome is claimed.

## Self-evaluation
Accuracy 4/5: source hashes and locators observed; full S260 application grounding remains unsupported by the assigned source. Completeness 5/5: both rows, both quotes, both hashes, version markers and id count delivered. Clarity 4/5: necessary command evidence makes this report longer than the summary. Actionability 4/5: draft rows ready, but S260's explicit source limitation must remain visible on integration. Conciseness 4/5: hashes repeat to make committed/working equivalence auditable. Overall 4.2/5. Highest-impact improvement is retaining the S260 limitation during integration, not silently broadening its evidence. Would the user agree? The deliverable is complete as a calibrated draft, not proof of every requested application claim.
