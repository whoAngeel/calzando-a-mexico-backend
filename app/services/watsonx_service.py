
from ibm_watson_machine_learning.foundation_models import Model
from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Cliente global del modelo (se inicializa una vez)
_model_instance = None

def get_watsonx_model():
    """
    Obtener instancia del modelo watsonx.ai (singleton)
    """
    global _model_instance
    
    if _model_instance is None:
        try:
            logger.info("Inicializando modelo watsonx.ai...")
            
            params = {
                GenParams.MAX_NEW_TOKENS: 512,
                GenParams.TEMPERATURE: 0.2,
                GenParams.REPETITION_PENALTY: 1.1
            }
            
            credentials = {
                "url": settings.WATSONX_AI_URL,
                "apikey": settings.WATSONX_API_KEY
            }
            
            _model_instance = Model(
                model_id=settings.WATSONX_MODEL_ID,
                params=params,
                credentials=credentials,
                project_id=settings.WATSONX_PROJECT_ID
            )
            
            logger.info("✅ Modelo watsonx.ai inicializado")
            
        except Exception as e:
            logger.error(f"Error inicializando watsonx.ai: {e}")
            raise ConnectionError(f"No se pudo conectar a watsonx.ai: {str(e)}")
    
    return _model_instance

def test_watsonx_connection() -> bool:
    """
    Probar conexión a watsonx.ai
    """
    try:
        model = get_watsonx_model()
        # Hacer una generación mínima de prueba
        test_prompt = "Test"
        response = model.generate(prompt=test_prompt)
        return response is not None and 'results' in response
    except:
        return False

async def generate_response(prompt: str) -> str:
    """
    Generar respuesta usando watsonx.ai
    
    Args:
        prompt: Prompt completo con contexto
        
    Returns:
        Texto generado por el modelo
    """
    try:
        model = get_watsonx_model()
        
        logger.info("Generando respuesta con watsonx.ai...")
        logger.debug(f"Prompt (primeros 200 chars): {prompt[:200]}...")
        
        response = model.generate(prompt=prompt)
        
        if response and 'results' in response and len(response['results']) > 0:
            generated_text = response['results'][0]['generated_text'].strip()
            logger.info(f"Respuesta generada ({len(generated_text)} chars)")
            return generated_text
        else:
            logger.error(f"Respuesta inválida de watsonx.ai: {response}")
            raise ValueError("Respuesta inválida del modelo")
    
    except Exception as e:
        logger.error(f"Error generando respuesta: {e}")
        raise RuntimeError(f"Error en watsonx.ai: {str(e)}")

async def generate_chat_response(
    user_message: str,
    context: str,
    system_role: str = "Eres el Asistente Gerencial de Calzando a México."
) -> str:
    """
    Generar respuesta de chat con contexto
    
    Args:
        user_message: Mensaje original del usuario
        context: Contexto recuperado de la BD u otra fuente
        system_role: Rol del asistente
        
    Returns:
        Respuesta generada
    """
    prompt = f"""{system_role}

{context}

Pregunta: "{user_message}"

Responde de forma ejecutiva y accionable:"""
    
    return await generate_response(prompt)