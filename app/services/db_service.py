

import ibm_db
from typing import List, Dict, Any, Optional
from app.config import settings, BENCHMARK_MIN_DIAS, BENCHMARK_MAX_DIAS, MES_MAP_INV
from app.models.dashboard import (
    DashboardSummary,
    TiendaResumen,
    TiendaDetalle,
    UnidadNegocioDetalle,
    HistoricoResponse,
    DatoHistorico
)
import logging

logger = logging.getLogger(__name__)

# String de conexión global
DSN = (
    f"DATABASE={settings.DB2_DATABASE};"
    f"HOSTNAME={settings.DB2_HOSTNAME};"
    f"PORT={settings.DB2_PORT};"
    f"PROTOCOL=TCPIP;"
    f"UID={settings.DB2_UID};"
    f"PWD={settings.DB2_PWD};"
    f"SECURITY=SSL;"
)

def get_db_connection():
    """Crear conexión a Db2"""
    try:
        conn = ibm_db.connect(DSN, "", "")
        return conn
    except Exception as e:
        logger.error(f"Error conectando a Db2: {e}")
        raise ConnectionError(f"No se pudo conectar a Db2: {str(e)}")

def test_db_connection() -> bool:
    """Probar conexión a Db2"""
    try:
        conn = get_db_connection()
        ibm_db.close(conn)
        return True
    except:
        return False

def calcular_cobertura(inv_pzs: int, vta_pzs: int) -> float:
    """Calcular días de cobertura"""
    if vta_pzs is None or vta_pzs == 0:
        return float('inf')
    if inv_pzs is None:
        return 0.0
    return (inv_pzs / vta_pzs) * 30

def determinar_status(cobertura: float) -> str:
    """Determinar status según cobertura"""
    if cobertura == float('inf'):
        return "SIN VENTAS"
    elif cobertura < BENCHMARK_MIN_DIAS:
        return "CRÍTICO"
    elif cobertura <= BENCHMARK_MAX_DIAS:
        return "ÓPTIMO"
    else:
        return "SOBREINVENTARIO"

async def get_dashboard_summary(year: int, month: int) -> DashboardSummary:
    """
    Obtener resumen general del dashboard
    """
    conn = get_db_connection()
    
    try:
        sql = f"""
        SELECT 
            I.TIENDA,
            SUM(I.INV_PZS) as TOTAL_INV,
            SUM(COALESCE(V.VTA_PZS, 0)) as TOTAL_VTA
        FROM {settings.DB2_SCHEMA}.INVENTARIO I
        LEFT JOIN {settings.DB2_SCHEMA}.VENTAS V 
            ON I.TIENDA = V.TIENDA 
            AND I.ANIO = V.ANIO 
            AND I.MES = V.MES
            AND I.UNIDAD_NEGOCIO = V.UNIDAD_NEGOCIO
        WHERE I.ANIO = ? AND I.MES = ?
        GROUP BY I.TIENDA
        """
        
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.execute(stmt, (year, month))
        
        total_tiendas = 0
        criticas = 0
        alertas = 0
        optimas = 0
        total_inv = 0
        total_vta = 0
        
        row = ibm_db.fetch_tuple(stmt)
        
        if not row:
            raise ValueError(f"No hay datos para {month}/{year}")
        
        while row:
            tienda, inv, vta = row
            total_tiendas += 1
            total_inv += inv
            total_vta += vta if vta else 0
            
            cobertura = calcular_cobertura(inv, vta)
            status = determinar_status(cobertura)
            
            if status == "CRÍTICO":
                criticas += 1
            elif status in ["SOBREINVENTARIO", "SIN VENTAS"]:
                alertas += 1
            else:
                optimas += 1
            
            row = ibm_db.fetch_tuple(stmt)
        
        cobertura_prom = calcular_cobertura(total_inv, total_vta)
        mes_nombre = MES_MAP_INV.get(month, f"Mes {month}")
        
        return DashboardSummary(
            total_tiendas=total_tiendas,
            tiendas_criticas=criticas,
            tiendas_alerta=alertas,
            tiendas_optimas=optimas,
            inventario_total=total_inv,
            ventas_totales=total_vta,
            cobertura_promedio=round(cobertura_prom, 1) if cobertura_prom != float('inf') else 0,
            periodo=f"{mes_nombre} {year}"
        )
    
    finally:
        ibm_db.close(conn)

async def get_all_tiendas_resumen(year: int, month: int) -> List[TiendaResumen]:
    """
    Obtener resumen de todas las tiendas
    """
    conn = get_db_connection()
    
    try:
        sql = f"""
        SELECT 
            I.TIENDA,
            SUM(I.INV_PZS) as TOTAL_INV,
            SUM(COALESCE(V.VTA_PZS, 0)) as TOTAL_VTA
        FROM {settings.DB2_SCHEMA}.INVENTARIO I
        LEFT JOIN {settings.DB2_SCHEMA}.VENTAS V 
            ON I.TIENDA = V.TIENDA 
            AND I.ANIO = V.ANIO 
            AND I.MES = V.MES
            AND I.UNIDAD_NEGOCIO = V.UNIDAD_NEGOCIO
        WHERE I.ANIO = ? AND I.MES = ?
        GROUP BY I.TIENDA
        ORDER BY I.TIENDA
        """
        
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.execute(stmt, (year, month))
        
        tiendas = []
        row = ibm_db.fetch_tuple(stmt)
        
        if not row:
            raise ValueError(f"No hay datos para {month}/{year}")
        
        while row:
            tienda, inv, vta = row
            vta = vta if vta else 0
            cobertura = calcular_cobertura(inv, vta)
            status = determinar_status(cobertura)
            
            tiendas.append(TiendaResumen(
                tienda=tienda,
                inventario=inv,
                ventas=vta,
                cobertura=round(cobertura, 1) if cobertura != float('inf') else 0,
                status=status
            ))
            
            row = ibm_db.fetch_tuple(stmt)
        
        return tiendas
    
    finally:
        ibm_db.close(conn)

async def get_tienda_detalle(tienda_nombre: str, year: int, month: int) -> TiendaDetalle:
    """
    Obtener detalle de una tienda específica con datos por unidad de negocio
    """
    conn = get_db_connection()
    
    try:
        # Verificar que la tienda existe
        sql_check = f"""
        SELECT COUNT(*) FROM {settings.DB2_SCHEMA}.INVENTARIO 
        WHERE TIENDA = ? AND ANIO = ? AND MES = ?
        """
        stmt = ibm_db.prepare(conn, sql_check)
        ibm_db.execute(stmt, (tienda_nombre, year, month))
        count = ibm_db.fetch_tuple(stmt)[0]
        
        if count == 0:
            raise ValueError(f"No hay datos para {tienda_nombre} en {month}/{year}")
        
        # Obtener datos por unidad de negocio
        sql = f"""
        SELECT 
            COALESCE(I.UNIDAD_NEGOCIO, V.UNIDAD_NEGOCIO) as UNIDAD_NEGOCIO,
            COALESCE(I.INV_PZS, 0) as INV_PZS,
            COALESCE(V.VTA_PZS, 0) as VTA_PZS
        FROM {settings.DB2_SCHEMA}.INVENTARIO I
        FULL OUTER JOIN {settings.DB2_SCHEMA}.VENTAS V 
            ON I.TIENDA = V.TIENDA 
            AND I.ANIO = V.ANIO 
            AND I.MES = V.MES
            AND I.UNIDAD_NEGOCIO = V.UNIDAD_NEGOCIO
        WHERE COALESCE(I.TIENDA, V.TIENDA) = ? 
          AND COALESCE(I.ANIO, V.ANIO) = ? 
          AND COALESCE(I.MES, V.MES) = ?
        """
        
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.execute(stmt, (tienda_nombre, year, month))
        
        unidades = []
        total_inv = 0
        total_vta = 0
        
        row = ibm_db.fetch_tuple(stmt)
        while row:
            unidad, inv, vta = row
            cobertura = calcular_cobertura(inv, vta)
            
            unidades.append(UnidadNegocioDetalle(
                unidad=unidad,
                inventario=inv,
                ventas=vta,
                cobertura=round(cobertura, 1) if cobertura != float('inf') else 0
            ))
            
            total_inv += inv
            total_vta += vta
            
            row = ibm_db.fetch_tuple(stmt)
        
        total_cobertura = calcular_cobertura(total_inv, total_vta)
        mes_nombre = MES_MAP_INV.get(month, f"Mes {month}")
        
        return TiendaDetalle(
            tienda=tienda_nombre,
            periodo=f"{mes_nombre} {year}",
            total_inventario=total_inv,
            total_ventas=total_vta,
            cobertura=round(total_cobertura, 1) if total_cobertura != float('inf') else 0,
            detalle_unidades=unidades
        )
    
    finally:
        ibm_db.close(conn)

async def get_historico(year: int, tienda: Optional[str] = None) -> HistoricoResponse:
    """
    Obtener datos históricos para gráficos
    """
    conn = get_db_connection()
    
    try:
        if tienda:
            # Datos de una tienda específica
            sql = f"""
            SELECT 
                I.MES,
                SUM(I.INV_PZS) as TOTAL_INV,
                SUM(COALESCE(V.VTA_PZS, 0)) as TOTAL_VTA
            FROM {settings.DB2_SCHEMA}.INVENTARIO I
            LEFT JOIN {settings.DB2_SCHEMA}.VENTAS V 
                ON I.TIENDA = V.TIENDA 
                AND I.ANIO = V.ANIO 
                AND I.MES = V.MES
                AND I.UNIDAD_NEGOCIO = V.UNIDAD_NEGOCIO
            WHERE I.TIENDA = ? AND I.ANIO = ?
            GROUP BY I.MES
            ORDER BY I.MES
            """
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.execute(stmt, (tienda, year))
        else:
            # Datos agregados de todas las tiendas
            sql = f"""
            SELECT 
                I.MES,
                SUM(I.INV_PZS) as TOTAL_INV,
                SUM(COALESCE(V.VTA_PZS, 0)) as TOTAL_VTA
            FROM {settings.DB2_SCHEMA}.INVENTARIO I
            LEFT JOIN {settings.DB2_SCHEMA}.VENTAS V 
                ON I.TIENDA = V.TIENDA 
                AND I.ANIO = V.ANIO 
                AND I.MES = V.MES
                AND I.UNIDAD_NEGOCIO = V.UNIDAD_NEGOCIO
            WHERE I.ANIO = ?
            GROUP BY I.MES
            ORDER BY I.MES
            """
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.execute(stmt, (year,))
        
        datos = []
        row = ibm_db.fetch_tuple(stmt)
        
        if not row:
            raise ValueError(f"No hay datos históricos para {year}" + (f" - {tienda}" if tienda else ""))
        
        while row:
            mes, inv, vta = row
            cobertura = calcular_cobertura(inv, vta)
            
            datos.append(DatoHistorico(
                mes=mes,
                inventario=inv,
                ventas=vta,
                cobertura=round(cobertura, 1) if cobertura != float('inf') else 0
            ))
            
            row = ibm_db.fetch_tuple(stmt)
        
        return HistoricoResponse(
            tienda=tienda,
            year=year,
            datos=datos
        )
    
    finally:
        ibm_db.close(conn)

async def query_tienda_datos(tienda: str, year: int, month: int) -> Dict[str, Any]:
    """
    Query auxiliar para el chat service
    Retorna datos de una tienda en formato dict
    """
    detalle = await get_tienda_detalle(tienda, year, month)
    
    return {
        "total_inventario": detalle.total_inventario,
        "total_ventas": detalle.total_ventas,
        "total_cobertura_dias": detalle.cobertura,
        "detalle_unidades": [
            {
                "unidad": u.unidad,
                "inventario": u.inventario,
                "ventas": u.ventas,
                "cobertura_dias": u.cobertura
            }
            for u in detalle.detalle_unidades
        ]
    }

async def query_todas_tiendas(year: int, month: int) -> List[Dict[str, Any]]:
    """
    Query auxiliar para el chat service
    Retorna datos de todas las tiendas en formato dict
    """
    tiendas = await get_all_tiendas_resumen(year, month)
    
    return [
        {
            "tienda": t.tienda,
            "inventario": t.inventario,
            "ventas": t.ventas,
            "cobertura_dias": t.cobertura,
            "status": t.status
        }
        for t in tiendas
    ]