# S65ConnectorOverlap — considerthese/ check

Command (read-only, lane root, run 2026-11-05):

    ls -d /home/vgpnk/Projects/shokunin/souji-shokunin/considerthese

Result: `ls: cannot access '.../souji-shokunin/considerthese': No such file or directory`, `ls` exit code **2**. A follow-up `test -e` returned exit **1**.

Report line: `considerthese/ does not exist in the souji lane (ls exit 2).`

For contrast, the fleet's kumitate lane does have a `considerthese/` directory; it was not read and is not part of this check.
