#!/usr/bin/env bash
# 03 - hard
# Multi-step chain with decoys. The real flag is never in plaintext on disk:
#   notes -> cron job -> backup script (documents the encoding pipeline)
#   -> reversed base64 tarball -> rot13'd credential inside a dotfile.
# Plaintext decoy flags punish a shallow `grep -r FLAG`.
set -euo pipefail

for t in tar gzip base64 rev tr; do
  command -v "$t" >/dev/null || { echo "missing tool: $t" >&2; exit 1; }
done

H=/home/target
WORK=$(mktemp -d)
trap 'rm -rf "$WORK"' EXIT

# --- Decoys -------------------------------------------------------------
mkdir -p "$H/Documents" /var/log/inventory
echo "FLAG{n0t_th3_r34l_fl4g_try_h4rd3r}" > "$H/Documents/flag.txt"
cat > /var/log/inventory/app.log <<'EOF'
2026-09-30 22:14:02 INFO  starting inventory service
2026-09-30 22:14:03 DEBUG test fixture loaded: FLAG{debug_fixture_ignore_me}
2026-09-30 22:14:05 WARN  credentials file missing, falling back to env
2026-10-01 02:30:00 INFO  nightly backup completed
EOF

# --- Hint trail ---------------------------------------------------------
mkdir -p "$H/notes"
cat > "$H/notes/todo.md" <<'EOF'
- [x] rotate inventory db creds
- [x] retired creds go into the nightly backup, NOT plaintext on disk anymore
- [ ] ask ops where the backup job keeps its output
EOF

mkdir -p /etc/cron.d /opt/inventory/bin /var/backups/.inventory
cat > /etc/cron.d/inventory-backup <<'EOF'
# nightly archive of retired credentials
30 2 * * * root /opt/inventory/bin/backup.sh
EOF

cat > /opt/inventory/bin/backup.sh <<'EOF'
#!/bin/sh
# Packs retired credentials into an obfuscated archive.
# Plain base64 got flagged by the security scanner, so the output is reversed too.
SRC=/opt/inventory/retired
OUT=/var/backups/.inventory/creds-$(date +%F).bak
tar -C "$SRC" -czf - . | base64 -w0 | rev > "$OUT"
rm -rf "$SRC"
EOF
chmod 755 /opt/inventory/bin/backup.sh

# --- Build the real payload exactly the way backup.sh describes ---------
mkdir -p "$WORK/retired"
ROT=$(printf '%s' 'FLAG{03_layered_backup_r3v_9d41}' | tr 'A-Za-z' 'N-ZA-Mn-za-m')
printf 'db_user=inventory\ndb_pass=%s\n' "$ROT" > "$WORK/retired/.db_creds"
printf 'passwords are rot13 so they do not show up in greps. yes, i know.\n' > "$WORK/retired/NOTE"
tar -C "$WORK/retired" -czf - . | base64 -w0 | rev > /var/backups/.inventory/creds-2026-10-01.bak

unset ROT
chown -R target:target "$H" 2>/dev/null || true