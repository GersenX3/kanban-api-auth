FROM python:3.11-slim

# Crear directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema (para psycopg2, bcrypt y postgresql-client)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalarlos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY . .

# Copiar y configurar entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Convertir line endings de Windows a Unix (por si acaso)
RUN sed -i 's/\r$//' /entrypoint.sh

# Exponer puerto
EXPOSE 5000

# Ejecutar entrypoint
ENTRYPOINT ["/entrypoint.sh"]