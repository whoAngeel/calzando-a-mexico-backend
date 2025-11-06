"""
Utilidades para cálculo de métricas de negocio
"""

from typing import Dict, List, Tuple
from app.config import BENCHMARK_MIN_DIAS, BENCHMARK_MAX_DIAS
import logging

logger = logging.getLogger(__name__)

def calcular_cobertura_dias(inventario: int, ventas: int, dias_mes: int = 30) -> float:
    """
    Calcular días de cobertura de inventario
    
    Formula: (Inventario / Ventas) * Días del mes
    
    Args:
        inventario: Piezas en inventario
        ventas: Piezas vendidas
        dias_mes: Días del periodo (default 30)
        
    Returns:
        Días de cobertura (float('inf') si no hay ventas)
    """
    if ventas is None or ventas == 0:
        return float('inf')
    if inventario is None or inventario == 0:
        return 0.0
    
    cobertura = (inventario / ventas) * dias_mes
    return round(cobertura, 2)

def calcular_rotacion_inventario(ventas_periodo: int, inventario_promedio: int) -> float:
    """
    Calcular rotación de inventario
    
    Formula: Ventas del periodo / Inventario promedio
    
    Args:
        ventas_periodo: Ventas totales del periodo
        inventario_promedio: Inventario promedio del periodo
        
    Returns:
        Índice de rotación
    """
    if inventario_promedio == 0:
        return 0.0
    
    rotacion = ventas_periodo / inventario_promedio
    return round(rotacion, 2)

def determinar_status_cobertura(cobertura_dias: float) -> str:
    """
    Determinar status según días de cobertura
    
    Args:
        cobertura_dias: Días de cobertura
        
    Returns:
        Status: "CRÍTICO", "ÓPTIMO", "SOBREINVENTARIO", "SIN VENTAS"
    """
    if cobertura_dias == float('inf'):
        return "SIN VENTAS"
    elif cobertura_dias < BENCHMARK_MIN_DIAS:
        return "CRÍTICO"
    elif cobertura_dias <= BENCHMARK_MAX_DIAS:
        return "ÓPTIMO"
    else:
        return "SOBREINVENTARIO"

def calcular_sell_through(ventas: int, inventario_inicial: int) -> float:
    """
    Calcular Sell-Through Rate (porcentaje de inventario vendido)
    
    Formula: (Ventas / Inventario Inicial) * 100
    
    Args:
        ventas: Unidades vendidas
        inventario_inicial: Inventario al inicio del periodo
        
    Returns:
        Porcentaje de sell-through
    """
    if inventario_inicial == 0:
        return 0.0
    
    sell_through = (ventas / inventario_inicial) * 100
    return round(sell_through, 2)

def calcular_stock_out_risk(cobertura_dias: float) -> str:
    """
    Calcular riesgo de desabasto
    
    Args:
        cobertura_dias: Días de cobertura
        
    Returns:
        Nivel de riesgo: "ALTO", "MEDIO", "BAJO"
    """
    if cobertura_dias < 14:
        return "ALTO"
    elif cobertura_dias < BENCHMARK_MIN_DIAS:
        return "MEDIO"
    else:
        return "BAJO"

def clasificar_tiendas_por_performance(
    tiendas: List[Dict]
) -> Dict[str, List[str]]:
    """
    Clasificar tiendas según su performance
    
    Args:
        tiendas: Lista de dicts con datos de tiendas
                 Cada dict debe tener: tienda, cobertura_dias, status
        
    Returns:
        Dict con listas de tiendas por categoría
    """
    clasificacion = {
        "criticas": [],
        "alerta": [],
        "optimas": [],
        "excelentes": []
    }
    
    for tienda in tiendas:
        nombre = tienda.get('tienda')
        cobertura = tienda.get('cobertura_dias', 0)
        status = tienda.get('status', '')
        
        if status == "CRÍTICO":
            clasificacion["criticas"].append(nombre)
        elif status in ["SOBREINVENTARIO", "SIN VENTAS"]:
            clasificacion["alerta"].append(nombre)
        elif status == "ÓPTIMO":
            # Considerar "excelentes" las que están más cerca del punto medio (59 días)
            if 40 <= cobertura <= 70:
                clasificacion["excelentes"].append(nombre)
            else:
                clasificacion["optimas"].append(nombre)
    
    return clasificacion

def calcular_variacion_porcentual(valor_actual: float, valor_anterior: float) -> float:
    """
    Calcular variación porcentual entre dos valores
    
    Formula: ((Actual - Anterior) / Anterior) * 100
    
    Args:
        valor_actual: Valor del periodo actual
        valor_anterior: Valor del periodo anterior
        
    Returns:
        Porcentaje de variación (positivo = crecimiento, negativo = decrecimiento)
    """
    if valor_anterior == 0:
        return 0.0
    
    variacion = ((valor_actual - valor_anterior) / valor_anterior) * 100
    return round(variacion, 2)

def generar_resumen_metricas(
    inventario: int,
    ventas: int,
    cobertura: float
) -> Dict[str, any]:
    """
    Generar resumen completo de métricas
    
    Args:
        inventario: Piezas en inventario
        ventas: Piezas vendidas
        cobertura: Días de cobertura
        
    Returns:
        Dict con todas las métricas calculadas
    """
    status = determinar_status_cobertura(cobertura)
    riesgo = calcular_stock_out_risk(cobertura)
    
    # Calcular rotación mensual aproximada
    rotacion = round(30 / cobertura, 2) if cobertura > 0 and cobertura != float('inf') else 0
    
    return {
        "inventario": inventario,
        "ventas": ventas,
        "cobertura_dias": cobertura if cobertura != float('inf') else 0,
        "status": status,
        "riesgo_desabasto": riesgo,
        "rotacion_mensual": rotacion,
        "dentro_benchmark": BENCHMARK_MIN_DIAS <= cobertura <= BENCHMARK_MAX_DIAS
    }

def calcular_prioridad_resurtido(
    tiendas: List[Dict]
) -> List[Tuple[str, int]]:
    """
    Calcular prioridad de resurtido para tiendas
    
    Args:
        tiendas: Lista de dicts con datos de tiendas
        
    Returns:
        Lista de tuplas (tienda, prioridad) ordenada por prioridad (1 = más urgente)
    """
    tiendas_con_prioridad = []
    
    for tienda in tiendas:
        nombre = tienda.get('tienda')
        cobertura = tienda.get('cobertura_dias', 0)
        ventas = tienda.get('ventas', 0)
        
        # Calcular score de prioridad
        # Menos cobertura + más ventas = mayor prioridad
        if cobertura == float('inf') or cobertura == 0:
            score = 1000  # Baja prioridad
        else:
            # Invertir cobertura (menor cobertura = mayor prioridad)
            # Multiplicar por ventas (más ventas = mayor prioridad)
            score = (1 / cobertura) * ventas
        
        tiendas_con_prioridad.append((nombre, score))
    
    # Ordenar por score descendente
    tiendas_con_prioridad.sort(key=lambda x: x[1], reverse=True)
    
    # Asignar prioridades (1, 2, 3, ...)
    resultado = [(tienda, idx + 1) for idx, (tienda, score) in enumerate(tiendas_con_prioridad)]
    
    return resultado

def calcular_salud_general(tiendas: List[Dict]) -> Dict[str, any]:
    """
    Calcular indicadores de salud general del negocio
    
    Args:
        tiendas: Lista de dicts con datos de todas las tiendas
        
    Returns:
        Dict con indicadores agregados
    """
    total_tiendas = len(tiendas)
    
    if total_tiendas == 0:
        return {
            "salud_general": "SIN DATOS",
            "score": 0,
            "tiendas_saludables_pct": 0
        }
    
    # Contar tiendas por status
    criticas = sum(1 for t in tiendas if t.get('status') == 'CRÍTICO')
    optimas = sum(1 for t in tiendas if t.get('status') == 'ÓPTIMO')
    
    # Calcular porcentaje de tiendas saludables
    pct_saludables = (optimas / total_tiendas) * 100
    
    # Determinar salud general
    if pct_saludables >= 80:
        salud = "EXCELENTE"
        score = 5
    elif pct_saludables >= 60:
        salud = "BUENA"
        score = 4
    elif pct_saludables >= 40:
        salud = "REGULAR"
        score = 3
    elif pct_saludables >= 20:
        salud = "DEFICIENTE"
        score = 2
    else:
        salud = "CRÍTICA"
        score = 1
    
    return {
        "salud_general": salud,
        "score": score,
        "tiendas_saludables_pct": round(pct_saludables, 1),
        "tiendas_criticas": criticas,
        "tiendas_optimas": optimas,
        "total_tiendas": total_tiendas
    }