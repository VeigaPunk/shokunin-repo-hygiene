source: S256 Python `codecs` error handlers — https://docs.python.org/3/library/codecs.html#error-handlers (snapshot census/round-40/sources/codecs.html sha256 023ec448648e7089efe4b4c25a167e491fa7f93d1cbf116662c6596e71158a4c; opened 2026-10-28)
verified-at: 2026-10-28 — the `replace` handler entry was read from the live Python documentation page and its pinned snapshot
recheck: 365d — reopen the `replace` row and compare the exact decoding clause: `grep -n -A5 "'replace'" census/round-40/sources/codecs.html`
ground: F1 — the drift record's UTF-8 decoding behavior (correction to the source quote used by the r40 entry)

# S256 corrects the codec quote without changing the record-decoder observation

S256 **supersedes S253's spliced quotation**. The S253 quote omitted the encoding sentence and
punctuation around the decoding sentence, so it was not verbatim at the cited location. The exact
text of the decoding clause at `census/round-40/sources/codecs.html:595-596` is:

> “On decoding, use � (U+FFFD, the official REPLACEMENT CHARACTER).”

This source supports the behavior of Python's `replace` error handler. It does not by itself establish
how `tools/souji-worktree-drift.py` handles a decoded name; that is established by the tool's schema
and `tests/fixtures/r40-drift-record-branches.py` (`invalid-utf8-in-repo-name` / `invalid-utf8-in-comment`).

The older knowledge entry `drift-record-invalid-utf8-r40.md` remains as filed; this correction narrows
the source claim to the exact documented decoding behavior. The earlier `replace` quote's substantive
meaning was right but its source wording was not exact.
