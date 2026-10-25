# case-F10 — secrets-refusal fixture

Payload for spec case **F10** (`tools/souji-verify.spec.md`, safety rails):
a tree with two secret-shaped files and one normal control file.

## Contents

| file | role |
| --- | --- |
| `app.env` | secret-shaped payload, matched by `*.env` |
| `creds.pem` | secret-shaped payload, matched by `*.pem` |
| `notes.txt` | normal control payload (no secret-shaped basename) |
| `expected.json` | harness metadata: expected verdicts, canaries, assertions |
| `README.md` | harness metadata: this note |

`payload_files` is the tree a selftest may copy into its `mktemp -d`
fixture repo; `expected.json` and `README.md` are metadata and must not be
copied into the repo under test.

## The rail this fixture guards

**The tool must never `cat`, read, hash, `git add`, or otherwise open
`app.env` or `creds.pem`.** They are synthetic, non-functional placeholders
(no real credential material), shipped with mode `600` only so a harness can
copy the tree; the expected verdicts come from the basename rules alone and
need no file access at all:

- `app.env` → `NOT-SAFE<TAB>app.env<TAB>NOT-SAFE<TAB>secrets-refusal`
- `creds.pem` → `NOT-SAFE<TAB>creds.pem<TAB>NOT-SAFE<TAB>secrets-refusal`
- `notes.txt` → ordinary receipt chain, never `secrets-refusal`
  (plain copy with no receipt ⇒ `NOT-SAFE(none)`; committed on the default
  branch ⇒ `SAFE(pushed)`)

Run exit code for this case is `0`: refusal is a verdict, not an evaluation
error.

## How a selftest can prove non-reading

1. **Leak canary.** Each secret-shaped payload carries a unique token; the
   tokens are declared in `expected.json.leak_canaries`. Assert the tool's
   stdout+stderr contains neither. (Do not leak-scan the fixture directory
   itself — `expected.json` legitimately holds the canary strings.)
2. **Unreadable-copy probe (optional).** In a throwaway `mktemp -d` copy,
   `chmod 000` both secret-shaped files and re-run the case. A tool that
   honors the rail still returns `secrets-refusal`; a tool that tries to
   open them fails. Remove the temp dir afterwards.
3. **No indirect reads.** The harness must not `git add -A` the payload
   tree, and the tool must not stage it either: `git add` reads file
   contents and would violate the rail transitively. Stage only
   `notes.txt`, or evaluate the secret-shaped targets by path/name alone.

## Determinism

All payload content is fixed literals; no timestamps, hostnames, or random
data. Re-running any staging step reproduces byte-identical files.
