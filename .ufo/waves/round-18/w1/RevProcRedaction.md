STATUS: PARTIAL — policy checked and host argv counts captured; the C3 implementation is absent from this checkout, so its sanitizer cannot be audited.

Axes: calibration (credential boundary), operability (bounded readable output), coverage (all requested argv shapes).

## Finding — P2, verification gap: C3 redaction is unverified

`/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-proc-census.sh` is not present: `read` returned “not found,” `glob` found no `tools/souji-proc-census*`, and `git ls-files --stage -- tools/souji-proc-census.sh` returned no output. The scoped diff (`git diff b5763415cc67ecff1e8fe56c58c39a6fb106d7a3 -- tools/souji-proc-census.sh SKILL.md`) was empty. This is not evidence of an observed leak; it means no implementation or redaction order can be verified here.

**Policy evidence:** `SKILL.md:63-68` says under “Never”: “Credentials, tokens, `op://` refs, `.env` content — kagi's province; souji cites paths and modes only.” A process census that emits argv must therefore redact credential material; truncating raw argv alone would violate this boundary.

**Smallest fix:** make the C3 source available for review and ensure it redacts each complete argument/value before rendering or truncating the command. Test each shape below with synthetic values and assert the exact synthetic value is absent from output.

## Minimal redaction coverage

Use NUL-delimited `/proc/<pid>/cmdline` argv elements (rather than an already-flattened display string) so the `-H` option and its header value remain associated. For each `argv` element, apply these targeted patterns; preserve the indicated key/prefix and replace the full matched credential with `[REDACTED]`:

| Shape | Minimal pattern / handling |
|---|---|
| `--token=...` | `(?i)(--token=)[^\s]+` → `$1[REDACTED]` (also redact the next argv element for the separate `--token VALUE` form). |
| `-H 'Authorization: …'` | When an argv element follows `-H`/`--header` and begins with this header, `(?i)^(Authorization:\s*).+$` → `$1[REDACTED]`. Redact the entire header value, including any spaces; do not only replace a single “Bearer” word. |
| URL userinfo | `(?i)([a-z][a-z0-9+.-]*://)[^/\s@]+@` → `$1[REDACTED]@` (removes the whole `user[:password]` part). |
| `ghp_...` | `\bghp_[A-Za-z0-9_]+` → `[REDACTED]`. |
| `sk-...` | `\bsk-[A-Za-z0-9_-]+` → `[REDACTED]`. |
| `xoxb-...` | `\bxoxb-[A-Za-z0-9._-]+` → `[REDACTED]`. |
| `AKIA...` | `\bAKIA[0-9A-Z]{16}\b` → `[REDACTED]`. |
| `password=...` | `(?i)(\bpassword=)[^&;\s]+` → `$1[REDACTED]`. |

These targeted recognizers cover the requested shapes; they are not a general secret detector. In particular, apply the Authorization pattern to the `-H`/`--header` value argument, where the whole header is available.

## Safe truncation

1. Redact full values from the complete argv first; never clip raw argv before scanning, since that can leave a secret prefix or make a recognizer miss a value split at the limit.
2. Escape control characters in the sanitized argv, then join for display. Do not emit raw argv in diagnostics or exception paths.
3. Apply the display cap only to the sanitized, encoded text. Cut on a UTF-8 code-point boundary (or operate on Unicode code points) and reserve room for a fixed truncation marker such as `…[truncated]`. A clipped placeholder is harmless; a clipped raw credential is not.

## Host snapshot (counts only)

Command run; the scanner excludes its own PID and immediate wrapper PID and prints only per-process-row counts, never argv values:

```sh
ps -eo pid=,args= | python3 -c 'import os,re,sys
pats=[("--token=",r"(?i)(?:^|\s)--token="),("-H Authorization",r"(?i)(?:^|\s)-H\s+[\x27\x22]?authorization\s*:\s*\S+"),("URL userinfo",r"(?i)\b[a-z][a-z0-9+.-]*://[^\s/@]+(?::[^\s/@]*)?@"),("ghp_",r"\bghp_"),("sk-",r"\bsk-"),("xoxb-",r"\bxoxb-"),("AKIA",r"\bAKIA[0-9A-Z]{16}\b"),("password=",r"(?i)\bpassword=")]
compiled=[(n,re.compile(p)) for n,p in pats]; counts={n:0 for n,_ in pats}; own={os.getpid(),os.getppid()}
for raw in sys.stdin:
 try: pid_s,args=raw.rstrip("\n").split(None,1); pid=int(pid_s)
 except (ValueError,TypeError): continue
 if pid in own: continue
 for name,rx in compiled:
  if rx.search(args): counts[name]+=1
for name,_ in pats: print(f"{name}: {counts[name]}")'
```

Output:

```text
--token=: 0
-H Authorization: 0
URL userinfo: 0
ghp_: 0
sk-: 0
xoxb-: 0
AKIA: 0
password=: 0
```

The zeroes describe this one host snapshot only; they do not validate a sanitizer or show that a future census cannot encounter these shapes.

## Verification gaps / residual risk

- No C3 source or test was available, so there is no code-level finding that the required redaction currently occurs, and no synthetic positive-control test was run.
- `xd://lsp` is not mounted (`read` returned “No such tool”); the SKILL check used literal text grep/read output, not semantic LSP evidence.
- No secret values were read or reported. The read-only process scan emitted only the counts above.
