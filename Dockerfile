FROM python:3.11-slim

WORKDIR /app

# Copiar requirements primero (para cache de layers)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY . .

# Exponer puerto
EXPOSE 8080

# Variables de entorno por defecto
ENV PORT=8080
ENV PYTHONUNBUFFERED=1

# Comando para ejecutar (Code Engine usa PORT variable)
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
