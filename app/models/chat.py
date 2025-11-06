from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class ChatRequest(BaseModel):
    """Request del chatbot"""
    message: str = Field(..., min_length=1, max_length=1000, description="Mensaje del usuario")
    session_id: Optional[str] = Field(None, description="ID de sesión (para futuro)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "¿Cuál es el inventario de diciembre 2023?",
                "session_id": "abc123"
            }
        }

class ChatResponse(BaseModel):
    """Response del chatbot"""
    response: str = Field(..., description="Respuesta generada por la IA")
    intent: str = Field(..., description="Intención detectada")
    data_used: Optional[Dict[str, Any]] = Field(None, description="Datos usados para la respuesta")
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_schema_extra = {
            "example": {
                "response": "El inventario total en diciembre 2023 fue de 87,500 piezas...",
                "intent": "resumen_tiendas",
                "data_used": {
                    "year": 2023,
                    "month": 12,
                    "total_inventario": 87500
                },
                "timestamp": "2025-11-05T10:30:00"
            }
        }

class ChatError(BaseModel):
    """Error del chatbot"""
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)