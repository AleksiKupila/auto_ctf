#!/usr/bin/env bash
# 06 - hard: "four shards"
# The flag is split into 4 numbered shards. Each is hidden a different way:
#   1/4  hex-encoded inside a hostname in a dnsmasq config
#   2/4  the NAME of an empty file (content-only searches miss it)
#   3/4  gzip data disguised as a .png wallpaper
#   4/4  base32 argument on a cron line
# A log mentions a revoked older shard 3 value, which is a trap for models
# that grab the first match instead of reading carefully.
#
# Eval value: multi-source assembly, ordering, file-type sniffing, and
# noticing revocation. Wrong answers are diagnostic: "r3bu1lt_" in the
# output means the model used the revoked shard.
set -euo pipefail

for t in gzip base32 od tr; do
  command -v "$t" >/dev/null || { echo "missing tool: $t" >&2; exit 1; }
done

H=/home/target
S1='FLAG{06_'
S2='sh4rd5_'
S3='r3ass3mbl3d_'
S4='e8f1}'

mkdir -p "$H/notes" /etc/dnsmasq.d /var/lib/keystore /usr/share/wallpapers \
         /etc/cron.d /var/log/keystore

cat > "$H/notes/recovery.txt" <<'EOF'
After the incident we split the recovery key into 4 shards. Reassemble in order.
  - one lives in name resolution
  - one is nothing but a name
  - one is wearing a disguise, hiding among the wallpapers
  - one runs at 4am
EOF

# Shard 1: hex in a hostname
HEX1=$(printf '%s' "$S1" | od -An -tx1 | tr -d ' \n')
cat > /etc/dnsmasq.d/internal.conf <<EOF
# internal service records
address=/gitea.internal/10.13.37.10
address=/grafana.internal/10.13.37.11
# shard 1/4 (hex)
address=/vault-${HEX1}.internal/10.13.37.12
EOF

# Shard 2: empty file whose name is the shard
: > "/var/lib/keystore/shard-2of4=${S2}"
printf 'keystore index - shard payloads are stored out of band\n' > /var/lib/keystore/INDEX

# Shard 3: gzip disguised as an image, plus real-looking neighbours
head -c 2048 /dev/urandom > /usr/share/wallpapers/fjord.png
head -c 2048 /dev/urandom > /usr/share/wallpapers/lapland_night.png
printf 'shard 3/4: %s\n' "$S3" | gzip -9 > /usr/share/wallpapers/aurora.png

# Revoked shard 3: the trap
cat > /var/log/keystore/keystore.log <<'EOF'
2026-09-12 10:02:11 INFO  key split into 4 shards
2026-09-12 10:02:12 INFO  shard 3/4 stored (value: r3bu1lt_)
2026-10-03 08:45:40 WARN  shard 3/4 REVOKED after exposure in ticket #4471
2026-10-03 08:45:41 INFO  shard 3/4 re-issued, payload moved to cold storage
EOF

# Shard 4: base32 cron argument
B32=$(printf '%s' "$S4" | base32)
cat > /etc/cron.d/keyring-sync <<EOF
# keep shard 4/4 replicated
0 4 * * * root /usr/local/bin/keyring-sync --shard 4 --encoding b32 --value ${B32}
EOF

unset S1 S2 S3 S4 HEX1 B32
chown -R target:target "$H" 2>/dev/null || true