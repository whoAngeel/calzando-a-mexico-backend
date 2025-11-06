"""
Servicio de Chat
Implementa el router de intenciones y orquesta las respuestas del chatbot
"""

from typing import Dict, Any
from app.services.db_service import query_tienda_datos, query_todas_tiendas
from app.services.watsonx_service import generate_chat_response
from app.utils.intent_parser import extraer_entidades, requiere_datos_bd
from app.config import DEFAULT_YEAR, DEFAULT_MONTH, MES_MAP_INV
import logging

logger = logging.getLogger(__name__)

async def process_chat_message(message: str, session_id: str = None) -> Dict[str, Any]:
    """
    Procesar mensaje del chat y generar respuesta
    
    Implementa el router de intenciones:
    - INTENT 1: Consulta de tienda específica
    - INTENT 2: Consulta agregada (todas las tiendas)
    - INTENT 3: Pregunta general (sin BD)
    
    Args:
        message: Mensaje del usuario
        session_id: ID de sesión (para futuras funcionalidades)
        
    Returns:
        Dict con response, intent y data_used
    """
    
    logger.info(f"Procesando mensaje: {message[:100]}...")
    
    # Extraer entidades del mensaje
    tienda, anio, mes = extraer_entidades(message)
    necesita_bd = requiere_datos_bd(message)
    
    # Aplicar defaults si necesita BD
    if necesita_bd:
        if not anio:
            anio = DEFAULT_YEAR
        if not mes:
            mes = DEFAULT_MONTH
    
    mes_nombre = MES_MAP_INV.get(mes, f"Mes {mes}") if mes else "Mayo"
    
    logger.info(f"Entidades: tienda={tienda}, año={anio}, mes={mes}, necesita_bd={necesita_bd}")
    
    # === ROUTER DE INTENCIONES ===
    
    # INTENT 1: Tienda Específica
    if tienda:
        return await _handle_tienda_especifica(message, tienda, anio, mes, mes_nombre)
    
    # INTENT 2: Consulta que requiere BD
    elif necesita_bd or anio or mes:
        return await _handle_resumen_tiendas(message, anio, mes, mes_nombre)
    
    # INTENT 3: Pregunta General
    else:
        return await _handle_pregunta_general(message)

async def _handle_tienda_especifica(
    message: str, 
    tienda: str, 
    anio: int, 
    mes: int, 
    mes_nombre: str
) -> Dict[str, Any]:
    """
    Manejar consulta de tienda específica (INTENT 1)
    """
    logger.info(f"INTENT 1: Consulta de {tienda}")
    
    try:
        # Consultar datos de la tienda
        datos = await query_tienda_datos(tienda, anio, mes)
        
        # Construir contexto
        contexto = f"""
Datos de la base de datos:
- Tienda: {tienda}
- Periodo: {mes_nombre} {anio}
- Inventario Total: {datos['total_inventario']:,} piezas
- Ventas Totales: {datos['total_ventas']:,} piezas
- Cobertura: {datos['total_cobertura_dias']:.1f} días

Detalle por Unidad de Negocio:
"""
        for u in datos['detalle_unidades']:
            cob = f"{u['cobertura_dias']:.1f}" if u['cobertura_dias'] != float('inf') else "Sin ventas"
            contexto += f"  • {u['unidad']}: {u['inventario']:,} inv, {u['ventas']:,} vta, {cob} días\n"
        
        contexto += "\nBenchmark retail: 28-90 días es óptimo."
        
        # Generar respuesta con IA
        response_text = await generate_chat_response(
            user_message=message,
            context=contexto
        )
        
        return {
            "response": response_text,
            "intent": "tienda_especifica",
            "data_used": {
                "tienda": tienda,
                "year": anio,
                "month": mes,
                "inventario": datos['total_inventario'],
                "ventas": datos['total_ventas'],
                "cobertura": datos['total_cobertura_dias']
            }
        }
    
    except ValueError as e:
        # No hay datos para esa tienda/periodo
        logger.warning(f"Datos no encontrados: {e}")
        
        response_text = f"No encontré datos para {tienda} en {mes_nombre} {anio}. Los datos disponibles van de Enero 2023 a Mayo 2025. Por favor verifica el nombre de la tienda y el periodo."
        
        return {
            "response": response_text,
            "intent": "tienda_especifica",
            "data_used": None
        }

async def _handle_resumen_tiendas(
    message: str,
    anio: int,
    mes: int,
    mes_nombre: str
) -> Dict[str, Any]:
    """
    Manejar consulta agregada de todas las tiendas (INTENT 2)
    """
    logger.info(f"INTENT 2: Resumen de todas las tiendas")
    
    try:
        # Consultar todas las tiendas
        tiendas = await query_todas_tiendas(anio, mes)
        
        # Construir contexto
        contexto = f"Resumen de tiendas ({mes_nombre} {anio}):\n\n"
        
        criticas = []
        alertas = []
        total_inv = 0
        total_vta = 0
        
        for t in tiendas:
            contexto += f"• {t['tienda']}: {t['inventario']:,} inv, {t['ventas']:,} vta, {t['cobertura_dias']} días → {t['status']}\n"
            
            total_inv += t['inventario']
            total_vta += t['ventas']
            
            if t['status'] == 'CRÍTICO':
                criticas.append(t['tienda'])
            elif t['status'] in ['SOBREINVENTARIO', 'SIN VENTAS']:
                alertas.append(t['tienda'])
        
        contexto += f"\n📊 TOTALES: {total_inv:,} piezas inventario, {total_vta:,} piezas vendidas"
        contexto += f"\n🚨 Tiendas críticas: {len(criticas)}"
        contexto += f"\n⚠️  Tiendas con alerta: {len(alertas)}"
        
        if criticas:
            contexto += f"\nTiendas críticas: {', '.join(criticas)}"
        if alertas:
            contexto += f"\nTiendas con alerta: {', '.join(alertas)}"
        
        # Generar respuesta con IA
        response_text = await generate_chat_response(
            user_message=message,
            context=contexto
        )
        
        return {
            "response": response_text,
            "intent": "resumen_tiendas",
            "data_used": {
                "year": anio,
                "month": mes,
                "total_tiendas": len(tiendas),
                "tiendas_criticas": len(criticas),
                "tiendas_alerta": len(alertas),
                "total_inventario": total_inv,
                "total_ventas": total_vta
            }
        }
    
    except ValueError as e:
        # No hay datos para ese periodo
        logger.warning(f"Datos no encontrados: {e}")
        
        response_text = f"No encontré datos para {mes_nombre} {anio}. Los datos disponibles van de Enero 2023 a Mayo 2025. Por favor verifica el periodo."
        
        return {
            "response": response_text,
            "intent": "resumen_tiendas",
            "data_used": None
        }

async def _handle_pregunta_general(message: str) -> Dict[str, Any]:
    """
    Manejar pregunta general sin necesidad de BD (INTENT 3)
    """
    logger.info(f"INTENT 3: Pregunta general")
    
    contexto = """
Contexto del problema de Calzando a México:

1. **Caos en el flujo de mercancía:**
   - Procesos manuales sin tecnología
   - Recibo sin programación (camiones llegan sin aviso)
   - Surtido reactivo ("apagar fuegos")
   - Separación manual que consume horas

2. **Sobreinventario y Venta Perdida:**
   - Bodegas llenas pero clientes no encuentran su talla
   - Inventario fantasma (sistema vs. realidad)
   - Más de 6,000 SKUs pero 80% de ventas viene del 20%
   - Producto dañado acumulándose

3. **Problemas organizacionales:**
   - Alta rotación de personal (60% anual)
   - Más de 40 códigos de puesto con roles superpuestos
   - Gerentes en trastienda en lugar del piso de venta

4. **Benchmark retail:**
   - Cobertura óptima: 28-90 días
   - Menos de 28 días: riesgo de desabasto
   - Más de 90 días: sobreinventario
"""
    
    # Generar respuesta con IA
    response_text = await generate_chat_response(
        user_message=message,
        context=contexto,
        system_role="Eres un consultor experto en retail y optimización de operaciones."
    )
    
    return {
        "response": response_text,
        "intent": "pregunta_general",
        "data_used": None
    }