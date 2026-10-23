#!/bin/bash
set -e

mkdir -p /home/target/Documents/secrets
echo "FLAG{01_easy_flag_53a1}" > /home/target/Documents/secrets/secret.txt

#systemctl start ufw
#ufw allow OpenSSH
