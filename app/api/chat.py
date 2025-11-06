from fastapi import APIRouter, HTTPException, status
from app.models.chat import ChatRequest, ChatResponse, ChatError
from app.services.chat_service import process_chat_message
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Endpoint del chatbot RAG
    
    Procesa mensajes del usuario y genera respuestas contextualizadas
    usando datos de Db2 y watsonx.ai
    """
    try:
        logger.info(f"Procesando mensaje: {request.message[:50]}...")
        
        # Procesar mensaje con el servicio de chat
        response = await process_chat_message(request.message, request.session_id)
        
        logger.info(f"Respuesta generada con intent: {response['intent']}")
        
        return ChatResponse(**response)
    
    except ValueError as e:
        # Errores de validación o datos no encontrados
        logger.warning(f"Error de validación: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    except Exception as e:
        # Errores inesperados
        logger.error(f"Error en chat: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error procesando el mensaje. Por favor intenta de nuevo."
        )