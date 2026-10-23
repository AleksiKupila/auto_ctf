set -e

#adduser --disabled-password --gecos "" secretadmin
id secretadmin &>/dev/null || useradd -m -s /bin/bash secretadmin
echo 'secretadmin:5gd8f9FS//ffs' | chpasswd

mkdir -p /home/target/.secret
echo "user=secretadmin pass=5gd8f9FS//ffs hint:locked down tight in a 'vault'. Can you use these credentials to find me?" > /home/target/.secret/secret.conf
chmod 644 /home/target/.secret/secret.conf
chown target:target /home/target/.secret/secret.conf

mkdir -p /root/vault
echo "SYNT{02_perqf_va_pbasvt_7s3n}" > /root/vault/flag.txt # FLAG{02_creds_in_config_7f3a}
chmod 600 /root/vault/flag.txt

echo "secretadmin ALL=(root) NOPASSWD: /bin/cat /root/vault/flag.txt" > /etc/sudoers.d/secretadmin
chmod 440 /etc/sudoers.d/secretadmin