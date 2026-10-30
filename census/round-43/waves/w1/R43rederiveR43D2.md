# R43rederiveR43D2 — independent calibration review

Axes: derivation accuracy, pinned-byte provenance, stale-receipt fidelity, scope isolation.

## Verdict

No actionable defect found in the R43-D2 register row. Independently derived **W04=48** at `0242085909fb6a4ee041c5443d76316ac6d59d4b`; **match=yes** with the frozen register. The receipt actually prints **W04=47** at line 4; **stale-value check=yes**. This attacks C1's R43-D2 calibration value, not the scoring implementation. No counter code was read or executed.

## Exact evidence commands and observed output

All commands exited 0. No scratch directory or fixture was created, no git mutation occurred, and no tools were installed.

### Frozen register

```sh
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show f8c805dbfa7f45814cf9a7270fa8bbffb41a8373:census/round-43/c1-required.tsv
```

Relevant observed row (other rows omitted here):

```text
R43-D2	census/round-39/records/census-after.txt	W04	47	W04=48	0242085909fb6a4ee041c5443d76316ac6d59d4b	census-w04
```

### Pinned source and independent count

First inspected the source with:

```sh
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 0242085909fb6a4ee041c5443d76316ac6d59d4b:corpus/SOURCES.md
```

Observed Markdown Registry columns `id | source | kind | tier | scope | ...`; the subsequent aggregation consumes the complete git output, not the display-truncated preview.

Counting method: scan S-numbered registry rows in document order. Extract the first HTTP(S) URL from the source cell; strip fragment, trailing slash and scheme; lowercase the host only. Trim the scope cell. Warn once for a later row when its normalized URL has occurred before but its `(URL, scope)` pair has not. Record both URL and scope pair after processing each row. Rejected rows are included. This counts warning-emitting rows, not URL groups or all pairwise collisions.

```sh
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 0242085909fb6a4ee041c5443d76316ac6d59d4b:corpus/SOURCES.md | gawk -F'|' 'function trim(s){sub(/^[[:space:]]+/,"",s);sub(/[[:space:]]+$/,"",s);return s} /^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|/ {id=trim($2);s=trim($3);scope=trim($6);if(!match(s,/https?:\/\/[^[:space:]|]+/))next;u=substr(s,RSTART,RLENGTH);sub(/#[^ ]*$/,"",u);sub(/\/$/,"",u);sub(/^[A-Za-z]+:\/\//,"",u);n=index(u,"/");u=n?tolower(substr(u,1,n-1)) substr(u,n):tolower(u);k=u SUBSEP scope;if((u in seen)&&!(k in scopes)){count++;print id "\t" u}seen[u]=1;scopes[k]=1} END{print "W04=" count}'
```

Observed warning rows, in emitted order (the command also printed their normalized URLs):

```text
S035 S036 S038 S049 S057 S058 S059 S063
S065 S072 S073 S075 S076 S077 S086 S087
S088 S089 S090 S091 S092 S093 S094 S095
S096 S097 S098 S099 S106 S108 S123 S124
S125 S126 S210 S216 S225 S232 S236 S237
S238 S240 S241 S242 S244 S245 S246 S250
W04=48
```

### Stale receipt

```sh
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 0242085909fb6a4ee041c5443d76316ac6d59d4b:census/round-39/records/census-after.txt
```

Observed complete output:

```text
# SOURCES census after — command: sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji
census_rc=0
rows=173
W04=47
E11=0
souji	ok	/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md
```

## Residual risk and verification gaps

The LSP device lookup returned `No such tool: xd://lsp`; semantic status/references/definition/diagnostics were unavailable. Text inspection is not presented as semantic proof. The supplied validator warning rule was cross-checked by text inspection; evidence for the actual numeric conclusion is the independent aggregation over the committed source bytes above. No full validator, counter, candidate scorer, runtime continuity or unrelated D1/D3 check was run or claimed. No candidate behavior changed.

Self-evaluation: accuracy 4/5 (independent deterministic count, not a second validator execution); completeness 5/5 (derived value, frozen comparison and stale line evidenced); clarity 4/5 (long shell command is reproducible but dense); actionability 5/5 (explicit match and provenance); conciseness 4/5 (full command retained for audit). Overall 4.4/5. Improvement: a second implementation would add corroboration but is not necessary for this scoped recommendation. The evidence supports the stated recommendation without an admission claim.
