STATUS: DONE — at base `3ab2c81479f5004c8bc91946eea482caec45408f`, all four existing C3 evidence targets resolve; the proposed knowledge target does not yet exist.

# Findings

| C3 pointer | State at base; digest | Landing-gate citation resolution at base |
|---|---|---|
| `tools/souji-proc-census.sh` | Exists. SHA-256 `37c3316a1fd8cdda18cbefdc7692d3d3f388e5783e8fe19085f5d932a8ceba64`. | Yes as a tree target: the base SKILL row cites it at `SKILL.md:179`; the registry matcher accepts this one-level `.sh` path, and it exists in the base tree. |
| `tests/fixtures/r18-proc-census.sh` | Exists. SHA-256 `01995f8d79f128b07dfab50ca317c13069adcd1ed933fd9325295610d56758be`. | Yes as a tree target: cited at `SKILL.md:180`, accepted by the registry matcher, and present in the base tree. |
| `census/round-18/proc-agreement-counterfix.json` | Exists. SHA-256 `a162f5409ae0e4ca36fb2abc087bc652ce1cbbd5d5d850660f193c9379654d87`. | Yes: cited at `SKILL.md:179`; the round-18 census path is within the general pointer roots and exists in the base tree. |
| `census/round-18/final-verification-4800fd7.json` | Exists. SHA-256 `137369e89794f986fdb3191b20592016435cb0d7a5dd72e74f01c39c66802c9b`. | Yes: cited at `SKILL.md:180`; recognized as a `census/` pointer and present in the base tree. |
| SKILL registry row | Exists at `SKILL.md:179-180`. SHA-256 of the containing `SKILL.md` (which pins the row): `5d98425431e861b1d19b7bb6a86b0bcee3160bd56d2e410acc9492238b6a3a4e`. | The row is in the scanned `SKILL.md` source. A direct `SKILL.md:179-180` citation is not itself a dangling-pointer candidate: the pointer roots omit `SKILL.md`. The four paths embedded in the rows are checked as described above. |
| `corpus/knowledge/process-residue-observations.md` (proposed destination) | Absent at base; no content digest. The proposed name is recorded in the round-19 C3 preregistration. | No: a citation to this `corpus/` path from a scanned source at base would be unresolved and produce `LG-DANGLING-PTR`. The absent file cannot itself be scanned as a knowledge-source document at base. |

Therefore, the base already supports citations to the proc tool, fixture, and both round-18 records. It does not contain the proposed new knowledge entry. “Yes” above means the cited path resolves in the base tree, not that the entire landing gate was executed or that every other gate check passes.

# Evidence

- Base identity: `3ab2c81479f5004c8bc91946eea482caec45408f` (`git rev-parse 3ab2c81`). The relevant base registry rows are `SKILL.md:179-180`.
- C3 names the proposed destination at `.ufo/waves/round-19/preregistration.txt:53-60`.
- Base gate citation roots and candidate syntax: `tools/souji-landing-gate.py:121-134`. The registry matcher is `tools/souji-landing-gate.py:83-86`; it checks cited registry paths against the base tree at `:947-959`. Pointer sources include `SKILL.md` and present top-level `corpus/knowledge/*.md` files at `:826-843`; actual tree-path resolution and `LG-DANGLING-PTR` emission are at `:864-900`.
- Existence and SHA-256 values above were obtained from the Git blobs at the exact base, not from the integrated worktree. The missing proposed path returned absent from that same base.

# Commands run

- `git rev-parse 3ab2c81`.
- For each listed target: `git cat-file -e "3ab2c81:<path>"`; for existing blobs, `git cat-file blob "3ab2c81:<path>" | sha256sum`.
- Read-only `git show 3ab2c81:<path>` on the four evidence targets and extracted base `SKILL.md` and `tools/souji-landing-gate.py` to seat-owned `/var/tmp` scratch for line-anchored inspection.
- `git diff --quiet 3ab2c81 -- SKILL.md tools/souji-landing-gate.py` confirmed the integrated worktree differs; findings use the extracted base bytes, not the integrated versions.
- No landing-gate, test, fixture, census, or other executable check was run; no tool was installed.

# Contract compliance

Read-only base inspection; only this requested report was written in the lane. No subagents, git/jj mutations, live census, network access, or tool installation. The temporary base extracts were removed after inspection.
