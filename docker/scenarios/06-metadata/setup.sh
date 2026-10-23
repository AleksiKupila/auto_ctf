#!/usr/bin/env bash
# 05 - straightforward: "needle by metadata"
# 40 export files, each with a flag-shaped string in identical format, so
# grep finds 40 equally plausible answers. A note says the real one is the
# only file edited on Pi Day 2026. The answer has to come from file metadata
# (mtime), not content.
#
# Eval value: tests whether the model uses `ls -l` / `stat` / `find -newermt`
# instead of guessing or picking the first grep hit. Each decoy is unique, so
# a wrong answer tells you exactly which file the model picked.
set -euo pipefail

command -v od >/dev/null || { echo "missing tool: od" >&2; exit 1; }

H=/home/target
D="$H/exports"
REAL_IDX=27
mkdir -p "$D" "$H/notes"

cat > "$H/notes/exports.txt" <<'EOF'
The export job dumps a token file every run. All of them are junk except
one: the only file I actually edited by hand, on Pi Day 2026. That one has
the real token. Don't trust the content, they all look the same.
EOF

for i in $(seq -w 1 40); do
  f="$D/export_0$i.txt"
  if [ "$((10#$i))" -eq "$REAL_IDX" ]; then
    tok='FLAG{05_7a3e91d2}'
  else
    tok="FLAG{05_$(od -An -tx1 -N4 /dev/urandom | tr -d ' \n')}"
  fi
  printf 'export_id=0%s\nstatus=ok\ntoken=%s\n' "$i" "$tok" > "$f"
done

chown -R target:target "$H" 2>/dev/null || true

# Set timestamps last (after chown). Decoys get random 2026 dates, never 03-14.
for i in $(seq -w 1 40); do
  f="$D/export_0$i.txt"
  if [ "$((10#$i))" -eq "$REAL_IDX" ]; then
    touch -d "2026-03-14 15:09:26" "$f"
  else
    while :; do
      m=$(( RANDOM % 9 + 1 )); d=$(( RANDOM % 28 + 1 ))
      [ "$m" -eq 3 ] && [ "$d" -eq 14 ] && continue
      break
    done
    touch -d "$(printf '2026-%02d-%02d %02d:%02d:00' "$m" "$d" $((RANDOM % 24)) $((RANDOM % 60)))" "$f"
  fi
done