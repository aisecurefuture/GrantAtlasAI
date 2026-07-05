# Deployment Guide

For the full Hetzner root-key-only hardening runbook, see [hetzner-hardening-root-ssh.md](./hetzner-hardening-root-ssh.md).

For the concise production deployment flow, see [production-deployment.md](./production-deployment.md).

## Hetzner Server Baseline

Recommended starter server:

- Ubuntu 24.04 LTS
- 4 vCPU / 8 GB RAM minimum for MVP
- Separate Hetzner volume for Postgres backups if production data is stored locally
- Firewall allowing only `22`, `80`, and `443`

## Server Hardening Checklist

- Keep root SSH enabled with keys only using `PermitRootLogin prohibit-password`.
- Disable SSH password and keyboard-interactive login.
- Enable unattended security upgrades.
- Install Docker Engine and Docker Compose plugin from Docker's official repository.
- Configure Hetzner Cloud Firewall for SSH, HTTP, and HTTPS only.
- Rotate `.env` secrets before first production launch.
- Set `POSTGRES_PASSWORD`, `DATABASE_URL`, `SECRET_KEY`, and `BOOTSTRAP_ADMIN_PASSWORD` to unique production values.
- Use a real hostname in `PUBLIC_HOSTNAME` and `PUBLIC_SITE_URL`.
- Point DNS `A` records for `grantatlas.ai`, `www.grantatlas.ai`, `app.grantatlas.ai`, and `api.grantatlas.ai` at the Hetzner server before starting Caddy.
- Keep database and Redis private to the Docker network. MinIO console, API, and web ports bind to `127.0.0.1` by default; only Caddy publishes public HTTP/HTTPS.
- Schedule encrypted off-server backups.
- Monitor disk usage, container restarts, and Caddy certificate renewal logs.

## Production Deploy

```bash
git clone <repo-url> GrantAtlas
cd GrantAtlas
cp .env.production.example .env
```

Edit `.env`:

- `SECRET_KEY`
- `POSTGRES_PASSWORD`
- `DATABASE_URL`
- `BOOTSTRAP_ADMIN_PASSWORD`
- `MINIO_SECRET_KEY`
- `PUBLIC_HOSTNAME`
- `APP_HOSTNAME`
- `API_HOSTNAME`
- `PUBLIC_SITE_URL`
- `WEB_BASE_URL`
- `CADDY_ACME_EMAIL`
- Stripe keys and price IDs
- Resend API key and verified sender

The production compose profile publishes only Caddy on public ports `80` and `443`. Direct API, web, and MinIO console ports are bound to localhost for operator access and reverse-proxy use.

Start production profile:

```bash
docker compose --profile prod up -d --build
docker compose exec api alembic upgrade head
docker compose exec api python -m app.db.seed
```

Caddy will request and renew Let’s Encrypt certificates automatically when:

- DNS resolves the configured hostnames to the server.
- Ports `80` and `443` are reachable from the public internet.
- `PUBLIC_HOSTNAME=grantatlas.ai`, `APP_HOSTNAME=app.grantatlas.ai`, and `API_HOSTNAME=api.grantatlas.ai`.
- `CADDY_ACME_EMAIL` is set to a monitored email address.

Useful checks:

```bash
docker compose --profile prod logs -f caddy
curl -I https://grantatlas.ai
curl -I https://app.grantatlas.ai
curl -I https://api.grantatlas.ai/health
```

## Update Process

```bash
git pull
docker compose --profile prod build
docker compose --profile prod up -d
docker compose exec api alembic upgrade head
docker compose ps
```

## Backup

Run:

```bash
bash scripts/backup_postgres.sh
```

For production, copy generated SQL backups to encrypted object storage or another server. Test restore monthly.

## Restore

```bash
docker compose stop api worker web
docker compose exec -T db psql -U grantatlas -d grantatlas < backups/grantatlas-YYYYMMDD-HHMMSS.sql
docker compose up -d
```
