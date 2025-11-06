from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    """Configuración de la aplicación desde variables de entorno"""
    
    # App Config
    APP_NAME: str = "Calzando a México RAG API"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    
    # IBM Db2
    DB2_DATABASE: str
    DB2_HOSTNAME: str
    DB2_PORT: str
    DB2_UID: str
    DB2_PWD: str
    DB2_SCHEMA: str = "PTJ13762"
    
    # IBM watsonx.ai
    WATSONX_API_KEY: str
    WATSONX_PROJECT_ID: str
    WATSONX_AI_URL: str = "https://us-south.ml.cloud.ibm.com"
    WATSONX_MODEL_ID: str = "ibm/granite-3-2b-instruct"
    # WATSONX_MODEL_ID: str = "meta-llama/llama-3-1-8b"
    # WATSONX_MODEL_ID: str = "ibm/granite-3-2-8b-instruct"
    
    # CORS - string opcional, se parsea en main.py
    CORS_ORIGINS: str = "*"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Instancia global de configuración
settings = Settings()

# Constantes de negocio
BENCHMARK_MIN_DIAS = 28
BENCHMARK_MAX_DIAS = 90
DEFAULT_YEAR = 2025
DEFAULT_MONTH = 5  # Mayo (último mes con datos)

# Mapeo de meses
MES_MAP = {
    'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4, 
    'mayo': 5, 'junio': 6, 'julio': 7, 'agosto': 8, 
    'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
}

MES_MAP_INV = {v: k.capitalize() for k, v in MES_MAP.items()}