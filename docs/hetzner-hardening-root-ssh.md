# Hetzner Ubuntu Hardening With Root SSH Keys

This runbook hardens a Hetzner Ubuntu server for GrantAtlas while intentionally keeping `root` SSH login enabled with public keys only.

## Assumptions

- Ubuntu 24.04 LTS
- Domain: `grantatlas.ai`
- Production hosts:
  - `grantatlas.ai`
  - `www.grantatlas.ai`
  - `app.grantatlas.ai`
  - `api.grantatlas.ai`
- App path on server: `/opt/grantatlas`
- Caddy terminates TLS and reverse-proxies to Docker Compose services.

## DNS

Create these DNS `A` records pointing to the Hetzner server IPv4:

```text
grantatlas.ai      -> SERVER_IP
www.grantatlas.ai  -> SERVER_IP
app.grantatlas.ai  -> SERVER_IP
api.grantatlas.ai  -> SERVER_IP
```

Caddy can only obtain Let's Encrypt certificates after DNS resolves to the server and ports `80` and `443` are reachable.

## Hetzner Cloud Firewall

In Hetzner Cloud Console, attach a firewall that allows only:

```text
TCP 22   from your IP address if practical
TCP 80   from 0.0.0.0/0
TCP 443  from 0.0.0.0/0
ICMP     optional
```

Do not expose PostgreSQL, Redis, MinIO, the API port, or the Next.js port directly to the public internet.

## Initial Server Update

SSH in as root:

```bash
ssh root@SERVER_IP
```

Update the system:

```bash
apt update
apt -y full-upgrade
apt -y install curl git ufw fail2ban unattended-upgrades apt-listchanges ca-certificates gnupg lsb-release htop jq
reboot
```

Reconnect after reboot:

```bash
ssh root@SERVER_IP
```

## Root SSH: Key-Only

Create an OpenSSH drop-in:

```bash
mkdir -p /etc/ssh/sshd_config.d
nano /etc/ssh/sshd_config.d/99-grantatlas-root-key-only.conf
```

Use this configuration:

```sshconfig
PermitRootLogin prohibit-password
PasswordAuthentication no
KbdInteractiveAuthentication no
PubkeyAuthentication yes
AuthenticationMethods publickey
X11Forwarding no
AllowTcpForwarding no
ClientAliveInterval 300
ClientAliveCountMax 2
MaxAuthTries 3
```

Validate and reload SSH:

```bash
sshd -t
systemctl reload ssh
```

Open a second terminal and confirm root key login still works before closing the first session:

```bash
ssh root@SERVER_IP
```

## Local Firewall With UFW

Use UFW as a local backstop:

```bash
ufw default deny incoming
ufw default allow outgoing
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
ufw status verbose
```

Important: Docker can publish ports in ways that are not fully governed by UFW. The Hetzner Cloud Firewall should be the primary external boundary. For production, only Caddy should be publicly reachable.

## Fail2Ban

Create an SSH jail:

```bash
nano /etc/fail2ban/jail.d/sshd.local
```

```ini
[sshd]
enabled = true
port = ssh
filter = sshd
logpath = %(sshd_log)s
maxretry = 5
findtime = 10m
bantime = 1h
```

Enable and verify:

```bash
systemctl enable --now fail2ban
systemctl restart fail2ban
fail2ban-client status sshd
```

## Automatic Security Updates

Enable unattended upgrades:

```bash
dpkg-reconfigure --priority=low unattended-upgrades
systemctl status unattended-upgrades
```

## Docker Engine

Install Docker from Docker's official Ubuntu repository:

```bash
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc
```

```bash
echo \
"deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
$(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" \
> /etc/apt/sources.list.d/docker.list
```

```bash
apt update
apt -y install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
systemctl enable --now docker
docker version
docker compose version
```

## Optional Swap

For smaller Hetzner instances, add swap:

```bash
fallocate -l 4G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
echo '/swapfile none swap sw 0 0' >> /etc/fstab
```

## Log and Disk Hygiene

Limit journald disk use:

```bash
nano /etc/systemd/journald.conf
```

Set:

```ini
SystemMaxUse=1G
RuntimeMaxUse=256M
```

Restart:

```bash
systemctl restart systemd-journald
```

Check disk regularly:

```bash
df -h
docker system df
```

## Production Deployment

See [production-deployment.md](./production-deployment.md) for the GrantAtlas deployment flow.

## Operational Checks

```bash
ufw status verbose
fail2ban-client status sshd
docker compose ps
docker compose logs --tail=100 api
docker compose logs --tail=100 web
docker compose logs --tail=100 caddy
journalctl -u ssh --since "1 hour ago"
```

## References

- Docker Engine on Ubuntu: https://docs.docker.com/engine/install/ubuntu/
- Caddy Automatic HTTPS: https://caddyserver.com/docs/automatic-https
- Ubuntu OpenSSH Server: https://ubuntu.com/server/docs/how-to/security/openssh-server/
- Hetzner Cloud Firewalls: https://docs.hetzner.com/cloud/firewalls/faq/

