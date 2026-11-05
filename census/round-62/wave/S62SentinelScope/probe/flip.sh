#!/bin/sh
# usage: flip.sh ROOT MODE ; mutates the lane AFTER the writer's clean-tree check, during the command
R=$1
case "$2" in
  flags) git -C "$R" update-index --skip-worktree tools/counter.py && printf 'forged\n' > "$R/tools/counter.py" ;;
  dirty) printf 'notes v3\n' >> "$R/notes.md" ;;
  instr) printf '#!/bin/sh\necho forged\n' > "$R/tools/instr.sh" ;;
esac
echo cmd-done
