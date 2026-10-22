#!/usr/bin/env bash
# Respaldo de PostgreSQL y adjuntos privados (macOS / Linux).
# Uso desde la raíz del proyecto:  bash scripts/respaldo.sh
# Los respaldos contienen DATOS PERSONALES: guárdalos cifrados y fuera del repositorio.
set -euo pipefail
RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
ENV="$RAIZ/backend/.env"
[ -f "$ENV" ] || { echo "No existe $ENV"; exit 1; }

leer() { grep -E "^$1=" "$ENV" | head -n1 | cut -d= -f2-; }
DB_NAME="$(leer DB_NAME)"; DB_USER="$(leer DB_USER)"; DB_PASSWORD="$(leer DB_PASSWORD)"
DB_HOST="$(leer DB_HOST)"; DB_PORT="$(leer DB_PORT)"
: "${DB_NAME:?Falta DB_NAME}"; : "${DB_USER:?Falta DB_USER}"; : "${DB_PASSWORD:?Falta DB_PASSWORD}"

DESTINO="$RAIZ/backups/$(date +%Y%m%d-%H%M)"
mkdir -p "$DESTINO"
PGPASSWORD="$DB_PASSWORD" pg_dump -h "${DB_HOST:-localhost}" -p "${DB_PORT:-5432}" -U "$DB_USER" -d "$DB_NAME" -F c -f "$DESTINO/base_datos.dump"
[ -d "$RAIZ/backend/storage_privado" ] && cp -r "$RAIZ/backend/storage_privado" "$DESTINO/adjuntos"
echo "Respaldo creado en: $DESTINO"
echo "Recuerda: contiene datos personales. Guárdalo cifrado y fuera del repositorio."
