from fastapi import APIRouter, status
from datetime import datetime
from app.services.db_service import test_db_connection
from app.services.watsonx_service import test_watsonx_connection

router = APIRouter()

@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """
    Health check endpoint
    Verifica la salud de la aplicación y sus dependencias
    """
    
    # Test Db2 connection
    db_status = test_db_connection()
    
    # Test watsonx.ai connection
    watsonx_status = test_watsonx_connection()
    
    # Determinar status general
    overall_status = "healthy" if (db_status and watsonx_status) else "degraded"
    status_code = status.HTTP_200_OK if overall_status == "healthy" else status.HTTP_503_SERVICE_UNAVAILABLE
    
    return {
        "status": overall_status,
        "db_connected": db_status,
        "watsonx_connected": watsonx_status,
        "timestamp": datetime.now().isoformat()
    }

@router.get("/health/db", status_code=status.HTTP_200_OK)
async def health_check_db():
    """Check específico de la base de datos"""
    connected = test_db_connection()
    return {
        "service": "db2",
        "connected": connected,
        "timestamp": datetime.now().isoformat()
    }

@router.get("/health/watsonx", status_code=status.HTTP_200_OK)
async def health_check_watsonx():
    """Check específico de watsonx.ai"""
    connected = test_watsonx_connection()
    return {
        "service": "watsonx",
        "connected": connected,
        "timestamp": datetime.now().isoformat()
    }