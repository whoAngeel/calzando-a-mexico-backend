"""
Parser de Intenciones
Extrae entidades (tienda, año, mes) de los mensajes del usuario
"""

import re
from typing import Tuple, Optional
from app.config import MES_MAP
import logging

logger = logging.getLogger(__name__)

def extraer_entidades(texto: str) -> Tuple[Optional[str], Optional[int], Optional[int]]:
    """
    Extraer entidades del mensaje del usuario
    
    Args:
        texto: Mensaje del usuario
        
    Returns:
        Tupla (tienda, año, mes)
        - tienda: "Tienda X" o None
        - año: 2023-2025 o None
        - mes: 1-12 o None
    """
    texto_low = texto.lower()
    tienda = None
    mes = None
    anio = None
    
    # === EXTRACCIÓN DE TIENDA ===
    # Patrones: "tienda 1", "tienda1", "la tienda 5", etc.
    tienda_patterns = [
        r'tienda\s*(\d+)',
        r'la\s+tienda\s*(\d+)',
        r'en\s+tienda\s*(\d+)'
    ]
    
    for pattern in tienda_patterns:
        match = re.search(pattern, texto_low)
        if match:
            num = match.group(1)
            tienda = f"Tienda {num}"
            logger.debug(f"Tienda detectada: {tienda}")
            break
    
    # === EXTRACCIÓN DE MES ===
    # Buscar nombres de meses en español
    for nombre_mes, num_mes in MES_MAP.items():
        if nombre_mes in texto_low:
            mes = num_mes
            logger.debug(f"Mes detectado: {nombre_mes} ({mes})")
            break
    
    # También buscar números de mes (ej: "mes 5", "05/2024")
    if not mes:
        mes_num_match = re.search(r'mes\s+(\d{1,2})', texto_low)
        if mes_num_match:
            mes = int(mes_num_match.group(1))
            if 1 <= mes <= 12:
                logger.debug(f"Mes detectado (número): {mes}")
            else:
                mes = None
    
    # Formato fecha: "12/2023", "05/2024"
    if not mes:
        fecha_match = re.search(r'(\d{1,2})/(\d{4})', texto)
        if fecha_match:
            mes = int(fecha_match.group(1))
            anio = int(fecha_match.group(2))
            logger.debug(f"Fecha detectada: {mes}/{anio}")
    
    # === EXTRACCIÓN DE AÑO ===
    if not anio:
        # Buscar años 2023-2025
        anio_match = re.search(r'(202[3-5])', texto)
        if anio_match:
            anio = int(anio_match.group(1))
            logger.debug(f"Año detectado: {anio}")
    
    logger.info(f"Entidades extraídas: tienda={tienda}, año={anio}, mes={mes}")
    
    return tienda, anio, mes

def requiere_datos_bd(texto: str) -> bool:
    """
    Determinar si la pregunta requiere consultar la base de datos
    
    Args:
        texto: Mensaje del usuario
        
    Returns:
        True si necesita consultar BD, False si no
    """
    texto_low = texto.lower()
    
    # Keywords que indican consulta de datos
    keywords_datos = [
        # Métricas
        'inventario', 'ventas', 'venta', 'cobertura',
        'piezas', 'stock', 'almacen', 'bodega',
        
        # Acciones de consulta
        'resumen', 'reporte', 'datos', 'información', 'info',
        'total', 'totales', 'suma', 'sumar',
        'mostrar', 'dame', 'dime', 'muestra', 'consulta',
        'ver', 'visualiza', 'lista', 'listar',
        
        # Preguntas cuantitativas
        'cuanto', 'cuánto', 'cuanta', 'cuánta', 'cuantos', 'cuántos',
        'cual', 'cuál', 'cuales', 'cuáles',
        'hay', 'tiene', 'tenemos', 'queda', 'quedan',
        
        # Comparativas y análisis
        'todas', 'todos', 'tiendas', 'comparativa', 'comparar',
        'mejor', 'peor', 'top', 'ranking', 'mayor', 'menor',
        
        # Problemas y estados
        'problemas', 'crítico', 'critico', 'alerta', 'estado',
        'situación', 'situacion', 'status', 'condición', 'condicion',
        
        # Referencias temporales
        'mes', 'año', 'periodo', 'fecha', 'trimestre',
        'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
        'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre',
        
        # Otros
        'analisis', 'análisis', 'estadistica', 'estadística',
        'kpi', 'metrica', 'métrica', 'indicador'
    ]
    
    # Si tiene alguna keyword, necesita BD
    tiene_keyword = any(keyword in texto_low for keyword in keywords_datos)
    
    if tiene_keyword:
        logger.debug(f"Mensaje requiere BD: contiene keywords de datos")
        return True
    
    # Keywords que indican pregunta general (NO necesita BD)
    keywords_general = [
        'que es', 'qué es', 'define', 'definición', 'concepto',
        'explica', 'explicar', 'como', 'cómo',
        'por que', 'por qué', 'porque', 'significa',
        'que significa', 'qué significa',
        'diferencia entre', 'tipos de', 'ejemplos de'
    ]
    
    tiene_keyword_general = any(keyword in texto_low for keyword in keywords_general)
    
    if tiene_keyword_general:
        logger.debug(f"Mensaje NO requiere BD: pregunta conceptual")
        return False
    
    logger.debug(f"Mensaje NO requiere BD: no tiene keywords claras")
    return False

def detectar_intent_explicito(texto: str) -> Optional[str]:
    """
    Detectar intención explícita del usuario
    
    Args:
        texto: Mensaje del usuario
        
    Returns:
        Nombre de la intención o None
    """
    texto_low = texto.lower()
    
    # Intenciones explícitas
    if any(word in texto_low for word in ['resumen', 'todas las tiendas', 'general']):
        return 'resumen_tiendas'
    
    if any(word in texto_low for word in ['problemas', 'críticas', 'criticas', 'alerta']):
        return 'identificar_problemas'
    
    if any(word in texto_low for word in ['mejor', 'top', 'ranking']):
        return 'ranking_tiendas'
    
    if any(word in texto_low for word in ['histórico', 'historico', 'tendencia', 'evolución', 'evolucion']):
        return 'historico'
    
    if any(word in texto_low for word in ['recomendación', 'recomendacion', 'sugerencia', 'que hacer']):
        return 'recomendacion'
    
    return None

def normalizar_nombre_tienda(tienda_input: str) -> str:
    """
    Normalizar nombre de tienda
    
    Args:
        tienda_input: Input del usuario (ej: "tienda1", "la tienda 5")
        
    Returns:
        Nombre normalizado (ej: "Tienda 1", "Tienda 5")
    """
    # Extraer número
    match = re.search(r'(\d+)', tienda_input)
    if match:
        num = match.group(1)
        return f"Tienda {num}"
    return tienda_input

def validar_periodo(anio: Optional[int], mes: Optional[int]) -> Tuple[bool, str]:
    """
    Validar si un periodo es válido según los datos disponibles
    
    Args:
        anio: Año (2023-2025)
        mes: Mes (1-12)
        
    Returns:
        Tupla (es_valido, mensaje_error)
    """
    if anio is None or mes is None:
        return True, ""  # Si no se especifica, se usarán defaults
    
    # Validar rango de año
    if anio < 2023 or anio > 2025:
        return False, f"El año {anio} está fuera del rango disponible (2023-2025)"
    
    # Validar rango de mes
    if mes < 1 or mes > 12:
        return False, f"El mes {mes} no es válido (debe estar entre 1 y 12)"
    
    # Validar que no sea futuro (después de Mayo 2025)
    if anio == 2025 and mes > 5:
        return False, f"No hay datos disponibles para {mes}/2025. Los datos llegan hasta Mayo 2025."
    
    return True, ""