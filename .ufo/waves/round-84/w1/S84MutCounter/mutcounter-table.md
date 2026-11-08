| mutant | clause | killed r83 | killed r84 | row(s) that kill it |
|---|---|---|---|---|
| `x11-owntree-short-guard` | the own-tree suffix binding requires at least two path components on each side (len(want) < 2 or len(got) < 2) | no | no | — (survives both) |
| `x12-owntree-no-capture-fallback` | the own-tree binding keeps the r82 capture fallback (_capture_ok) before the wave-directory branch | yes | yes | TF4 |
| `x13-basename-blind` | a MOVED target's last component must equal the token's | no | no | — (survives both) |
| `x14-location-unbound` | a MOVED target's round-<N> directory is the token's own or the lane's census/ capture root | yes | yes | NF10, NF12b |
| `x15-unknown-class-free` | a ledger class outside MOVED/LOCAL-POLICY/QUARANTINED/FLEET/TOKEN/ABSENT is refused | no | no | — (survives both) |
| `x16-quarantine-undeclared` | a QUARANTINED leaf must be declared by a committed authority line naming the token and the quarantine path | yes | yes | NF4, NF6b, NF6c, NF6d, NF6e |
| `x17-localpolicy-disk-blind` | a LOCAL-POLICY row needs the lane disk to still hold the token path's frozen bytes | no | no | — (survives both) |
| `x18-no-round-free` | a MOVED token that names no round-<N> cannot bind a moved location | yes | yes | NF3 |
| `x19-token-on-line-free` | the population item's token must occur on its recorded base line (R0 integrity) | no | no | — (survives both) |
| `x20-duplicate-ledger-free` | a duplicate ledger id makes the row REFUSED (the ledger dictionary keeps the first row) | no | no | — (survives both) |
