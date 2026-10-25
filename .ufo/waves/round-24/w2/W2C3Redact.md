# W2C3Redact — attack on per-element `cmd=` redaction (C3, `tools/souji-receipt-run.py run`)

## Status
STATUS: FAIL — falsified. The tip's per-element pass leaks bearer tokens that the base runner redacted (4 hand-built argv, 256/200k and 227/200k in fuzz). Three of the four leaking tip receipts pass tip `verify`. HIGH.

## Evidence
Revisions: base runner `a65fac98:tools/souji-receipt-run.py` (sha256 e13d0c83…); tip runner `778747eb:tools/souji-receipt-run.py` (sha256 9df0738c…), byte-identical to the runner at `master` = c3ca7ad3 (`cmp` clean). `REDACTIONS` blocks are identical at base and tip (`diff` clean), so the only difference under test is the `cmd=` expression.

- Base, line 224: `f"cmd={redact(shlex.join(args.command))}",`
- Tip, `tools/souji-receipt-run.py:242`: `f"cmd={redact(shlex.join([redact(a) for a in args.command]))}",`
- The only pattern that spans whitespace, `tools/souji-receipt-run.py:78`: `(re.compile(r"(?i)(authorization:\s*bearer\s+)\S+"), r"\1[REDACTED]"),`
- Contract clause, `.ufo/waves/round-24/preregistration-amendment-1.txt:41`: `as RECEIPT-MALFORMED; cmd= redacts per argv element before joining.`

Harness (scratch `/var/tmp/souji-r24-W2C3Redact/`, removed): `git init` repo with one commit holding `t.sh` (`echo cases=1 pass=1`), rev c486c74a…. Each runner ran for real:
`python3 -B {base,tip}-run.py run --root <scratch>/repo --rev <rev> --tool t.sh --out <scratch>/out/<side>-<case>.txt -- sh t.sh <argv…>`. All secrets are fake (`FAKE…`).

```
== A1 --token sep ["--token", "FAKEtok0001"]
  base: cmd=sh t.sh --token FAKEtok0001   leaked=['FAKEtok']
  tip: cmd=sh t.sh --token FAKEtok0001   leaked=['FAKEtok']
== A2 -H one elem ["-H", "Authorization: Bearer FAKEbear0002"]
  base: cmd=sh t.sh -H 'Authorization: Bearer [REDACTED]   leaked=[]
  tip: cmd=sh t.sh -H 'Authorization: Bearer [REDACTED]   leaked=[]
== A3 -H three elems ["-H", "Authorization:", "Bearer", "FAKEbear0003"]
  base: cmd=sh t.sh -H Authorization: Bearer [REDACTED]   leaked=[]
  tip: cmd=sh t.sh -H Authorization: Bearer [REDACTED]   leaked=[]
== A4 password = x ["password", "=", "FAKEpw0004"]
  base: cmd=sh t.sh password = FAKEpw0004   leaked=['FAKEpw']
  tip: cmd=sh t.sh password = FAKEpw0004   leaked=['FAKEpw']
== A5 password= x ["password=", "FAKEpw0005"]
  base: cmd=sh t.sh password= FAKEpw0005   leaked=['FAKEpw']
  tip: cmd=sh t.sh password= FAKEpw0005   leaked=['FAKEpw']
== A6 --token= x ["--token=", "FAKEtok0006"]
  base: cmd=sh t.sh --token= FAKEtok0006   leaked=['FAKEtok']
  tip: cmd=sh t.sh --token= FAKEtok0006   leaked=['FAKEtok']
== A7 'Authorization: Bearer' x ["Authorization: Bearer", "FAKEbear0007"]
  base: cmd=sh t.sh 'Authorization: Bearer' FAKEbear0007   leaked=['FAKEbear']
  tip: cmd=sh t.sh 'Authorization: Bearer' FAKEbear0007   leaked=['FAKEbear']
== A8 Authorization:Bearer x (ctl) ["-H", "Authorization:Bearer", "FAKEbear0008"]
  base: cmd=sh t.sh -H Authorization:Bearer [REDACTED]   leaked=[]
  tip: cmd=sh t.sh -H Authorization:Bearer [REDACTED]   leaked=[]
== R1 password=..,Authorization: ["password=FAKEpw0009,Authorization:", "Bearer", "FAKEbear0009"]
  base: cmd=sh t.sh password=[REDACTED] Bearer [REDACTED]   leaked=[]
  tip: cmd=sh t.sh 'password=[REDACTED] Bearer FAKEbear0009   leaked=['FAKEbear']
== R2 ghp_../Authorization:Bearer ["ghp_FAKEgh0010/Authorization:Bearer", "FAKEbear0010"]
  base: cmd=sh t.sh [REDACTED]/Authorization:Bearer [REDACTED]   leaked=[]
  tip: cmd=sh t.sh '[REDACTED]/Authorization:Bearer' FAKEbear0010   leaked=['FAKEbear']
== R3 url-cred../Authorization: ["https://u:FAKEurl0011@h/Authorization:", "Bearer", "FAKEbear0011"]
  base: cmd=sh t.sh https://[REDACTED]@h/Authorization: Bearer [REDACTED]   leaked=[]
  tip: cmd=sh t.sh 'https://[REDACTED]@h/Authorization:' Bearer FAKEbear0011   leaked=['FAKEbear']
== R4 sk-..;Authorization: ["sk-FAKEsk0012;Authorization:", "Bearer", "FAKEbear0012"]
  base: cmd=sh t.sh '[REDACTED];Authorization:' Bearer FAKEbear0012   leaked=['FAKEbear']
  tip: cmd=sh t.sh '[REDACTED];Authorization:' Bearer FAKEbear0012   leaked=['FAKEbear']
== R5 AKIA..,Authorization:Bearer ["AKIAFAKEFAKEFAKE0013,Authorization:Bearer", "FAKEbear0013"]
  base: cmd=sh t.sh [REDACTED],Authorization:Bearer [REDACTED]   leaked=[]
  tip: cmd=sh t.sh '[REDACTED],Authorization:Bearer' FAKEbear0013   leaked=['FAKEbear']
```

Tip `verify --root <scratch>/repo <receipt>` on the tip receipts:
```
tip-R2.txt tip:rc=0 verify=ok rev=c486c74a6f6ba44051ce716c7a436eeb72499192 tool=t.sh ...
tip-R3.txt tip:rc=0 verify=ok rev=c486c74a6f6ba44051ce716c7a436eeb72499192 tool=t.sh ...
tip-R5.txt tip:rc=0 verify=ok rev=c486c74a6f6ba44051ce716c7a436eeb72499192 tool=t.sh ...
tip-R1.txt tip:rc=2 RECEIPT-MALFORMED	cmd= does not parse as shell words: No closing quotation
tip-A2.txt tip:rc=2 RECEIPT-MALFORMED	cmd= does not parse as shell words: No closing quotation
```
(Base `verify` returns RECEIPT-COUNTS-ABSENT on every receipt here because the base `COUNTS_RE` has no `cases=` alternative. That is unrelated to redaction.)

Differential fuzz, run in-process with the tip module's `redact`. Random argv of 1–4 elements built from secret-pattern fragments plus quote, control-character and separator characters; each fuzz secret is a unique literal:
```
seed=24 N=200000 tip_leaks_base_redacted=256 base_leaks_tip_redacted=7 tip_unparsable=35299 base_unparsable=19745
seed=25 N=200000 tip_leaks_base_redacted=227 base_leaks_tip_redacted=3 tip_unparsable=35234 base_unparsable=19806
```

Candidate remediation, same fuzz: render `cmd=` as `shlex.join([redact(a) for a in argv])` with no second pass, and refuse when any `REDACTIONS` match on the space-joined argv spans more than one element:
```
seed=24 N=200000 refused=21662 fixed_leaks_base_redacted=0 fixed_unparsable=0
seed=25 N=200000 refused=21696 fixed_leaks_base_redacted=0 fixed_unparsable=0
A3 None   A8 None   R1 None   R2 None   R3 None   R5 None   (None = refused, no receipt)
A2 "sh t.sh -H 'Authorization: Bearer [REDACTED]'"
```

## Findings
1. **HIGH — the tip leaks secrets the base redacted** (`tools/souji-receipt-run.py:242`).
   - **Mechanism:** the per-element pass rewrites a secret in element *k* to `[REDACTED]`. The brackets are shell-unsafe, so `shlex.join` single-quotes that element. The closing `'` then sits between `Authorization:`/`Bearer` and the next element, and the joined-line pass `authorization:\s*bearer\s+` (`:78`) no longer matches across the boundary. In R1 the per-element `password=\S+` swallows `Authorization:` entirely, so the joined pass has no context left.
   - **Exploit path:** any recorded argv where the element carrying `Authorization:` or `Authorization:Bearer` (with no internal space) also contains another secret-shaped span (ghp_, AKIA, URL credentials, password=), followed by the token as its own argv element.
   - **Impact:** the bearer token is written in plaintext into a receipt that is committed under `census/`. In R2, R3 and R5 tip `verify` accepts that receipt as `verify=ok`.
   - **Scale:** 256 and 227 tip-only leaks against 7 and 3 base-only leaks per 200k cases. Neither expression's coverage contains the other's, but the change is net-negative by about 40× on this fragment set.
2. **MEDIUM — run/verify asymmetry on ordinary bearer headers** (`:242` plus `:305`). With `-H 'Authorization: Bearer x'` (A2, the normal curl form), the joined pass's `\S+` eats the closing quote that `shlex.join` added, so `cmd=` is unparsable. Tip `run` writes the receipt and tip `verify` refuses it (`RECEIPT-MALFORMED`). The base did the same text damage, but base `verify` never parsed `cmd=`, so this refusal is new in the tip. The fuzz shows unparsable `cmd=` about 1.8× as often at the tip (35299 vs 19745). C3 frozen case `c clean` passes only because its synthetic command carries no secret-shaped argv. [INFERENCE: from the case text at preregistration.txt:107; I did not read the fixture.]
3. **MEDIUM (pre-existing, unchanged by the tip) — split-secret forms are not redacted by either runner.** A1 `--token` `x`, A4 `password` `=` `x`, A5 `password=` `x`, A6 `--token=` `x`, A7 `'Authorization: Bearer'` `x` and R4 (`;` forces quoting at base as well) all leak at both revisions. The patterns only cover the `=`-glued or whitespace-unquoted forms.
4. **LOW (pre-existing) — a newline in an argv element splits the `cmd=` header line.** `CTRL_RE` (`:87`) is `[\x00-\x08\x0b-\x1f\x7f]`, which excludes `\n` and `\t`. Argv `$'x\nrc=0'` makes both runners write `cmd=sh t.sh 'x` followed by `rc=0'`. Tip `verify` fails closed (`RECEIPT-MALFORMED header order or fences do not match receipt v1`). This is a header-injection surface, and it is fail-closed today.

**Smallest remediation (Findings 1 and 2):** drop the second, joined-line `redact` at `:242`, so `cmd=` is `shlex.join([redact(a) for a in args.command])` and always parses. Before running anything, refuse with exit 2 and no receipt (for example `CMD-SECRET-SPANS-ARGV`) when any `REDACTIONS` match on `" ".join(argv)` crosses an element boundary. Fuzz result: 0 leaks relative to base and 0 unparsable lines over 400k cases. The cost is that about 11% of fuzz argv, including A3 and A8, are refused instead of recorded. The kill rule is untouched, because this is a code fix, not a counter change.

## Attack log
- Target: the per-element `cmd=` redaction landed in 778747e (C3 symmetry clause, amendment-1:41).
- Attacks: 8 split-secret shapes (A1–A8) and 5 shapes that cross the quoting boundary (R1–R5), run through both real runners. Then 400k differential fuzz cases.
- Result: falsified (R1, R2, R3, R5). Survives only for A2, A3 and A8 (redacted equally) and for A1, A4–A7 and R4 (leaked equally, pre-existing).
- Remediation check: done by simulation in scratch only. No lane file was edited.
- Lane writes: this report only. No git or jj mutation. Scratch `/var/tmp/souji-r24-W2C3Redact/` removed at the end. No tools installed.
