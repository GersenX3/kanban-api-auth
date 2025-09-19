#!/bin/sh
set -e

echo "Esperando a la base de datos de PostgreSQL..."
until PGPASSWORD=supersecretpassword pg_isready -h postgres-auth -p 5432 -U authuser -d authdb; do
  >&2 echo "PostgreSQL no está disponible - esperando..."
  sleep 1
done

echo "PostgreSQL está listo. Aplicando migraciones..."

# Verificar si el directorio migrations existe y tiene archivos
if [ ! -d "migrations" ] || [ ! "$(ls -A migrations/versions 2>/dev/null)" ]; then
    echo "Inicializando migrations..."
    flask --app app:create_app db init
fi

# Verificar si necesitamos crear una nueva migración
echo "Creando migración..."
flask --app app:create_app db migrate -m "create users table" || echo "No hay cambios para migrar"

echo "Aplicando migraciones..."
flask --app app:create_app db upgrade

echo "Iniciando el servidor Flask..."
exec flask --app app:create_app run --host=0.0.0.0 --port=5000