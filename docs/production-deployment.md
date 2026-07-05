# GrantAtlas Production Deployment

Use this after hardening the server with [hetzner-hardening-root-ssh.md](./hetzner-hardening-root-ssh.md).

## Clone The Repository

```bash
mkdir -p /opt
cd /opt
git clone REPO_URL grantatlas
cd /opt/grantatlas
```

## Configure Environment

```bash
cp .env.production.example .env
nano .env
```

Replace at minimum:

```env
SECRET_KEY=long-random-production-secret
DATABASE_URL=postgresql+psycopg://grantatlas:strong-db-password@db:5432/grantatlas
MINIO_SECRET_KEY=strong-minio-secret
BOOTSTRAP_ADMIN_PASSWORD=strong-bootstrap-password
CADDY_ACME_EMAIL=admin@grantatlas.ai
```

Set provider credentials when ready:

```env
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=
STRIPE_STARTER_PRICE_ID=
STRIPE_PROFESSIONAL_PRICE_ID=
STRIPE_GROWTH_PRICE_ID=
STRIPE_ENTERPRISE_PRICE_ID=
RESEND_API_KEY=
SAM_GOV_API_KEY=
```

Confirm production hostnames:

```env
PUBLIC_HOSTNAME=grantatlas.ai
APP_HOSTNAME=app.grantatlas.ai
API_HOSTNAME=api.grantatlas.ai
PUBLIC_SITE_URL=https://grantatlas.ai
WEB_BASE_URL=https://app.grantatlas.ai
API_BASE_URL=https://api.grantatlas.ai
NEXT_PUBLIC_APP_URL=https://app.grantatlas.ai
CORS_ORIGINS=https://grantatlas.ai,https://app.grantatlas.ai
COOKIE_SECURE=true
```

## Deploy

```bash
docker compose --profile prod up -d --build
docker compose exec api alembic upgrade head
docker compose exec api python -m app.db.seed
```

Watch Caddy request certificates:

```bash
docker compose --profile prod logs -f caddy
```

Caddy will request and renew Let's Encrypt certificates automatically when:

- DNS resolves the configured hostnames to the server.
- Ports `80` and `443` are reachable.
- `CADDY_ACME_EMAIL` is set.

## Verify

```bash
docker compose --profile prod ps
curl -I https://grantatlas.ai
curl -I https://app.grantatlas.ai
curl -s https://api.grantatlas.ai/health
```

Expected API health response:

```json
{"status":"ok","service":"grantatlas-api"}
```

## Update

```bash
cd /opt/grantatlas
git pull
docker compose --profile prod build
docker compose --profile prod up -d
docker compose exec api alembic upgrade head
docker compose ps
```

## Backup

```bash
cd /opt/grantatlas
bash scripts/backup_postgres.sh
```

Copy backups off-server to encrypted storage. Test restore monthly.

## Restore

```bash
cd /opt/grantatlas
docker compose stop api worker web
docker compose exec -T db psql -U grantatlas -d grantatlas < backups/grantatlas-YYYYMMDD-HHMMSS.sql
docker compose up -d
```

## Useful Logs

```bash
docker compose logs --tail=100 api
docker compose logs --tail=100 web
docker compose logs --tail=100 worker
docker compose logs --tail=100 caddy
```

