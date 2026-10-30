# S44scout58 — C3 source opening

Result: both requested primary sources opened and snapshotted; one scoped A-row candidate proposed below; preservation-authority inference rejected. No registry append or production change.

Axes: calibration / operability / coverage. This seat supplies coverage evidence only; no numerical score delta or admission claim. Admission remains outside non-author closure; certification OFF, K5 HELD.

## Observed source evidence

Access date for all quotes: **2026-10-30**. Quotes were HTML-decoded and whitespace-normalized, not paraphrased; each is <=25 words.

| Source and location | Located quote | Words |
|---|---|---:|
| [symlink(2), DESCRIPTION](https://man7.org/linux/man-pages/man2/symlink.2.html#DESCRIPTION); saved `symlink.2.html:98-99` | “symlink() creates a symbolic link named linkpath which contains the string target.” | 12 |
| [Python os.open](https://docs.python.org/3/library/os.html#os.open); saved `os.html:1620` | “Return the file descriptor for the newly opened file.” | 9 |
| [Python os.open](https://docs.python.org/3/library/os.html#os.open); saved `os.html:1622` | “For a description of the flag and mode values, see the C run-time documentation;” | 14 |

Snapshots in this directory (raw HTML, with HTTP headers alongside):

- `symlink.2.html`, 15347 bytes, SHA-256 `c929903b2dec6c985e149ca27d509243e04fc80861d8b98c1f98e2325e857178`; `symlink.headers.txt`. Source identifies Linux man-pages 6.19, page dated 2026-02-08.
- `os.html`, 790778 bytes, SHA-256 `8f012514a510509ff3243541c99de48e7817a427beba3b6dbab48ffc46fd1ece`; `os.headers.txt`. Reader title identifies Python 3.15.2 documentation. `/3/` is a moving documentation URL, not the installed-interpreter version.

## One proposed source row — artifact only

Column order follows the observed `corpus/SOURCES.md:28` header. Candidate ID is deliberately not an allocated S-number; integration owner decides allocation, deduplication and admission.

| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |
|---|---|---|---|---|---|---|---|---|---|---|
| CANDIDATE-S44scout58 | Linux symlink(2) — https://man7.org/linux/man-pages/man2/symlink.2.html ; Python os.open — https://docs.python.org/3/library/os.html#os.open | docs | A | symlink creation and Python low-level open interface only; not preservation or deletion authority | Linux man-pages 6.19 DESCRIPTION; Python 3.15.2 os.open; snapshots and located quotes in .ufo/waves/round-44/w1/S44scout58/report.md, opened 2026-10-30 | symlink creates a link containing its target string; os.open returns a descriptor and directs flag/mode semantics to C run-time documentation. Neither source decides Souji output policy or authorizes cleanup. | queued | 2026-10-30 | on-release | proposed C3 source support only; not registered |

## Inference explicitly rejected

**Unsupported:** “Because symlink semantics and os.open are documented, leaf refusal (or an O_NOFOLLOW-based open) proves preservation of all target/ancestor/hardlink state and authorizes deletion of rejected paths.”

**Rejection:** these passages describe interfaces, not an ownership/admission decision, complete race-proof preservation guarantee, or permission to delete. Python explicitly defers flag semantics to C documentation. C3 refusal is a separately decided defensive caller-output contract. Establishing implementation behavior requires the frozen counter and relevant fixture evidence; it cannot be promoted from these citations. No deletion or preservation-authority conclusion is admitted.

## Frozen context and bounded checks

Read `census/round-44/preregistration.txt` and the relevant `c3-counter.py:1-45`, plus `c3-surface.tsv:1-9`. Counter documentation calls for `JSON-TARGET-SYMLINK`, same-landing legacy cutover, rejecting clean/refuse stubs, and five prior fixtures. This seat did **not** run those suites or claim their outcome.

Exact provenance command (read-only):

```sh
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show d314fd6e85d62565344fa6c4b102f52f62297884:census/round-44/c3-counter.py | sha256sum
```

Observed output:

```text
eba3e69ffef1493f4733c5c5537b8b2e5ed0a4cdcbaf551f560e03e8bcc64d66  -
```

`sha256sum /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-44/c3-counter.py` returned the same digest, matching preregistration. Consequently the read counter bytes match the specified freeze. No counter executed or changed.

Exact fetch commands (both exited 0, run from the explicitly created seat scratch):

```sh
curl --fail --location --silent --show-error --dump-header /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-44/w1/S44scout58/symlink.headers.txt --output /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-44/w1/S44scout58/symlink.2.html --write-out 'symlink http=%{http_code} bytes=%{size_download} effective=%{url_effective}\n' https://man7.org/linux/man-pages/man2/symlink.2.html
curl --fail --location --silent --show-error --dump-header /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-44/w1/S44scout58/os.headers.txt --output /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-44/w1/S44scout58/os.html --write-out 'os.open http=%{http_code} bytes=%{size_download} effective=%{url_effective}\n' 'https://docs.python.org/3/library/os.html#os.open'
```

Observed output:

```text
symlink http=200 bytes=15347 effective=https://man7.org/linux/man-pages/man2/symlink.2.html
os.open http=200 bytes=790778 effective=https://docs.python.org/3/library/os.html#os.open
```

Additional bounded probe: Python Eval used `html.parser.HTMLParser.handle_data`, joined decoded text with whitespace normalization, and checked each quoted string for membership and `len(quote.split()) <= 25`. Observed output:

```text
symlink.2.html #DESCRIPTION: words=12 present=True <=25=True quote=symlink() creates a symbolic link named linkpath which contains the string target.
os.html #os.open: words=9 present=True <=25=True quote=Return the file descriptor for the newly opened file.
os.html #os.open: words=14 present=True <=25=True quote=For a description of the flag and mode values, see the C run-time documentation;
```

## Limitations and boundaries

High confidence in located source statements and snapshot integrity. These sources do not establish runtime race safety, ancestor handling, hardlink preservation, complete C3 behavior, or preservation/deletion authority. No exported implementation contract was modified or semantically traced; source opening does not require an LSP implementation claim. No whole-suite validation, delegation, package transaction, installation/update, PATH change, git/jj mutation, shared bookkeeping edit, or registry write was performed. Only seat-owned evidence and the explicitly requested Report trailer file were written. Scratch cleanup command and outcome are recorded in the trailer report.
