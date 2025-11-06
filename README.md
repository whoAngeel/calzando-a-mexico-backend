# 🏪 Backend Calzando a México - RAG API

Backend FastAPI para el sistema de análisis gerencial con RAG (SQL-Augmented Generation) e IBM watsonx.ai

## 📋 Requisitos

- Python 3.9+
- IBM Db2 on Cloud (con datos cargados)
- IBM watsonx.ai API Key

## 🚀 Instalación Local

### 1. Crear entorno virtual

```bash
python -m venv venv

# Activar (Mac/Linux)
source venv/bin/activate

# Activar (Windows)
venv\Scripts\activate
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar variables de entorno

```bash
# Copiar template
cp .env.example .env

# Editar .env con tus credenciales
nano .env  # o tu editor favorito
```

### 4. Ejecutar servidor

```bash
# Desde el directorio backend/
uvicorn app.main:app --reload --port 8000
```

El servidor estará disponible en: http://localhost:8000

## 📚 Documentación de la API

Una vez iniciado el servidor, accede a:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔌 Endpoints Principales

### Chat RAG

```bash
POST /api/chat
Content-Type: application/json

{
  "message": "¿Cuál es el inventario de diciembre 2023?"
}
```

### Dashboard

```bash
# Resumen general
GET /api/dashboard/summary?year=2025&month=5

# Lista de tiendas
GET /api/dashboard/tiendas?year=2025&month=5

# Detalle de tienda
GET /api/dashboard/tiendas/Tienda%201?year=2025&month=5

# Histórico
GET /api/dashboard/historico?year=2024&tienda=Tienda%201
```

### Health Check

```bash
GET /health
```

## 🧪 Probar la API

### Con cURL:

```bash
# Health check
curl http://localhost:8000/health

# Chat
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "dame un resumen de todas las tiendas"}'

# Dashboard summary
curl "http://localhost:8000/api/dashboard/summary?year=2025&month=5"
```

### Con HTTPie:

```bash
# Chat
http POST localhost:8000/api/chat message="¿cómo está tienda 1?"

# Dashboard
http localhost:8000/api/dashboard/tiendas year==2025 month==5
```

### Con Python:

```python
import requests

# Chat
response = requests.post(
    "http://localhost:8000/api/chat",
    json={"message": "dame un resumen"}
)
print(response.json())

# Dashboard
response = requests.get(
    "http://localhost:8000/api/dashboard/summary",
    params={"year": 2025, "month": 5}
)
print(response.json())
```

## 📁 Estructura del Proyecto

```
backend/
├── app/
│   ├── api/              # Endpoints (routers)
│   │   ├── chat.py      # POST /chat
│   │   ├── dashboard.py # GET /dashboard/*
│   │   └── health.py    # GET /health
│   │
│   ├── models/          # Schemas Pydantic
│   │   ├── chat.py
│   │   └── dashboard.py
│   │
│   ├── services/        # Lógica de negocio
│   │   ├── chat_service.py    # (pendiente)
│   │   ├── db_service.py      # (pendiente)
│   │   └── watsonx_service.py # (pendiente)
│   │
│   ├── utils/           # Utilidades
│   │   ├── intent_parser.py  # (pendiente)
│   │   └── metrics.py         # (pendiente)
│   │
│   ├── config.py        # Configuración
│   └── main.py          # Entry point
│
├── requirements.txt     # Dependencias
├── .env                 # Variables de entorno (NO commitear)
└── README.md           # Este archivo
```

## 🔧 Configuración

Variables de entorno necesarias (ver `.env.example`):

```bash
# IBM Db2
DB2_DATABASE=
DB2_HOSTNAME=
DB2_PORT=
DB2_UID=
DB2_PWD=
DB2_SCHEMA=PTJ13762

# IBM watsonx.ai
WATSONX_API_KEY=
WATSONX_PROJECT_ID=
WATSONX_AI_URL=https://us-south.ml.cloud.ibm.com

# App
APP_ENV=development
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

## 🐛 Troubleshooting

### Error: "Module not found"
```bash
# Asegúrate de estar en el directorio correcto
cd backend/
python -c "import app; print('OK')"
```

### Error de conexión a Db2
```bash
# Verificar credenciales
curl http://localhost:8000/health/db
```

### Error de conexión a watsonx
```bash
# Verificar API key
curl http://localhost:8000/health/watsonx
```

## 📊 Datos Disponibles

- **Periodos**: Enero 2023 - Mayo 2025
- **Tiendas**: 17 tiendas (Tienda 1 - Tienda 17)
- **Métricas**: Inventario, Ventas, Cobertura

## 🚀 Próximos Pasos

1. ✅ Arquitectura definida
2. ⏭️ Implementar services (db_service, chat_service, watsonx_service)
3. ⏭️ Implementar utils (intent_parser, metrics)
4. ⏭️ Testing local completo
5. ⏭️ Deploy a IBM Cloud

## 🤝 Contribuir

Este es un proyecto de hackathon. Para agregar funcionalidades:

1. Crear nueva rama
2. Implementar cambios
3. Testear localmente
4. Merge a main

## 📝 Licencia

Proyecto académico para la Semana Interdisciplinaria UPIICSA 2025