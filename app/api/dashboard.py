from fastapi import APIRouter, HTTPException, Query, status
from typing import Optional, List
from app.models.dashboard import (
    DashboardSummary, 
    TiendaResumen, 
    TiendaDetalle,
    HistoricoResponse
)
from app.services.db_service import (
    get_dashboard_summary,
    get_all_tiendas_resumen,
    get_tienda_detalle,
    get_historico,
    
    
)
from app.config import DEFAULT_YEAR, DEFAULT_MONTH
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/summary", response_model=DashboardSummary)
async def dashboard_summary(
    year: int = Query(DEFAULT_YEAR, ge=2023, le=2025, description="Año"),
    month: int = Query(DEFAULT_MONTH, ge=1, le=12, description="Mes")
):
    """
    Obtener resumen general del dashboard
    
    Retorna métricas agregadas de todas las tiendas para el periodo especificado
    """
    try:
        logger.info(f"Obteniendo resumen: {month}/{year}")
        summary = await get_dashboard_summary(year, month)
        return summary
    except ValueError as e:
        logger.warning(f"Datos no encontrados: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No hay datos disponibles para {month}/{year}"
        )
    except Exception as e:
        logger.error(f"Error en summary: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error obteniendo resumen"
        )

@router.get("/tiendas", response_model=List[TiendaResumen])
async def list_tiendas(
    year: int = Query(DEFAULT_YEAR, ge=2023, le=2025),
    month: int = Query(DEFAULT_MONTH, ge=1, le=12)
):
    """
    Listar todas las tiendas con sus métricas
    
    Retorna datos resumidos de cada tienda para el periodo especificado
    """
    try:
        logger.info(f"Listando tiendas: {month}/{year}")
        tiendas = await get_all_tiendas_resumen(year, month)
        return tiendas
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No hay datos disponibles para {month}/{year}"
        )
    except Exception as e:
        logger.error(f"Error listando tiendas: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error listando tiendas"
        )

@router.get("/tiendas/{tienda_nombre}", response_model=TiendaDetalle)
async def get_tienda(
    tienda_nombre: str,
    year: int = Query(DEFAULT_YEAR, ge=2023, le=2025),
    month: int = Query(DEFAULT_MONTH, ge=1, le=12)
):
    """
    Obtener datos detallados de una tienda específica
    
    Retorna inventario, ventas y cobertura por unidad de negocio
    """
    try:
        logger.info(f"Obteniendo detalle de {tienda_nombre}: {month}/{year}")
        detalle = await get_tienda_detalle(tienda_nombre, year, month)
        return detalle
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error obteniendo tienda: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error obteniendo datos de tienda"
        )

@router.get("/historico", response_model=HistoricoResponse)
async def get_historical_data(
    year: int = Query(2024, ge=2023, le=2025),
    tienda: Optional[str] = Query(None, description="Nombre de tienda (opcional para agregado)")
):
    """
    Obtener datos históricos para gráficos
    
    Si se especifica tienda, retorna datos de esa tienda.
    Si no, retorna datos agregados de todas las tiendas.
    """
    try:
        logger.info(f"Obteniendo histórico: tienda={tienda}, year={year}")
        historico = await get_historico(year, tienda)
        return historico
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error obteniendo histórico: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error obteniendo datos históricos"
        )