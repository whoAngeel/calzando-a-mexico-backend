from pydantic import BaseModel, Field
from typing import List, Optional

class DashboardSummary(BaseModel):
    """Resumen general del dashboard"""
    total_tiendas: int
    tiendas_criticas: int
    tiendas_alerta: int
    tiendas_optimas: int
    inventario_total: int
    ventas_totales: int
    cobertura_promedio: float
    periodo: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_tiendas": 17,
                "tiendas_criticas": 3,
                "tiendas_alerta": 4,
                "tiendas_optimas": 10,
                "inventario_total": 95000,
                "ventas_totales": 78000,
                "cobertura_promedio": 36.5,
                "periodo": "Mayo 2025"
            }
        }

class TiendaResumen(BaseModel):
    """Datos resumidos de una tienda"""
    tienda: str
    inventario: int
    ventas: int
    cobertura: float
    status: str  # CRÍTICO, ALERTA, ÓPTIMO
    
    class Config:
        json_schema_extra = {
            "example": {
                "tienda": "Tienda 1",
                "inventario": 5200,
                "ventas": 4100,
                "cobertura": 38.0,
                "status": "ÓPTIMO"
            }
        }

class UnidadNegocioDetalle(BaseModel):
    """Detalle por unidad de negocio"""
    unidad: str
    inventario: int
    ventas: int
    cobertura: float

class TiendaDetalle(BaseModel):
    """Datos detallados de una tienda"""
    tienda: str
    periodo: str
    total_inventario: int
    total_ventas: int
    cobertura: float
    detalle_unidades: List[UnidadNegocioDetalle]
    
    class Config:
        json_schema_extra = {
            "example": {
                "tienda": "Tienda 1",
                "periodo": "Mayo 2025",
                "total_inventario": 5200,
                "total_ventas": 4100,
                "cobertura": 38.0,
                "detalle_unidades": [
                    {
                        "unidad": "Dama",
                        "inventario": 2000,
                        "ventas": 1500,
                        "cobertura": 40.0
                    }
                ]
            }
        }

class DatoHistorico(BaseModel):
    """Un punto en el histórico"""
    mes: int
    inventario: int
    ventas: int
    cobertura: float

class HistoricoResponse(BaseModel):
    """Datos históricos para gráficos"""
    tienda: Optional[str] = None  # None si es agregado
    year: int
    datos: List[DatoHistorico]
    
    class Config:
        json_schema_extra = {
            "example": {
                "tienda": "Tienda 1",
                "year": 2024,
                "datos": [
                    {"mes": 1, "inventario": 4800, "ventas": 3900, "cobertura": 36.9},
                    {"mes": 2, "inventario": 5100, "ventas": 4200, "cobertura": 36.4}
                ]
            }
        }