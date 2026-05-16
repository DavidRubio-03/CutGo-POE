from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from pydantic import BaseModel

from backend.database import get_db

router = APIRouter(
    prefix="/api/estadisticas",
    tags=["Estadisticas"]
)

class ResumenEstadistica(BaseModel):
    total_usuarios: int
    total_rutas_activas: int
    total_registros_horario: int
    incidentes_este_mes: int
    puntualidad_percent: Optional[int] = None

class RutaIncidenteEstadistica(BaseModel):
    nombre_ruta: str
    total: int

class IncidenteEstadistica(BaseModel):
    nombre_parada: str
    total_incidentes: int

class FrecuenciaEstadistica(BaseModel):
    id_parada: int
    nombre_parada: str
    frecuencia_min: Optional[float] = None

class CalificacionEstadistica(BaseModel):
    nombre_ruta: str
    promedio_seguridad: Optional[float] = None

@router.get("/resumen", response_model=ResumenEstadistica)
def obtener_resumen_estadisticas(db: Session = Depends(get_db)):
    total_usuarios = db.execute(text("SELECT COUNT(*) FROM USUARIOS")).scalar() or 0
    total_rutas_activas = db.execute(text("SELECT COUNT(*) FROM RUTAS WHERE activa = 1")).scalar() or 0
    total_registros_horario = db.execute(text("SELECT COUNT(*) FROM REGISTROS_HORARIO")).scalar() or 0
    incidentes_este_mes = db.execute(text("SELECT COUNT(*) FROM INCIDENTES WHERE fecha_reporte >= DATE_SUB(NOW(), INTERVAL 1 MONTH)")).scalar() or 0
    puntualidad_raw = db.execute(text("""
        SELECT ROUND(AVG(puntuacion) / 5 * 100)
        FROM CALIFICACIONES
        WHERE categoria = 'puntualidad'
    """)).scalar()
    puntualidad_percent = int(puntualidad_raw) if puntualidad_raw is not None else None

    return {
        "total_usuarios": total_usuarios,
        "total_rutas_activas": total_rutas_activas,
        "total_registros_horario": total_registros_horario,
        "incidentes_este_mes": incidentes_este_mes,
        "puntualidad_percent": puntualidad_percent,
    }

@router.get("/incidentes-por-ruta", response_model=List[RutaIncidenteEstadistica])
def obtener_incidentes_por_ruta(db: Session = Depends(get_db)):
    query = text("""
        SELECT r.nombre_ruta, COUNT(*) as total
        FROM INCIDENTES i 
        JOIN PARADAS p ON i.id_parada = p.id_parada
        JOIN RUTAS r ON p.id_ruta = r.id_ruta
        GROUP BY r.nombre_ruta ORDER BY total DESC
    """)
    result = db.execute(query).fetchall()
    return [dict(row._mapping) for row in result]

@router.get("/incidentes", response_model=List[IncidenteEstadistica])
def obtener_estadisticas_incidentes(db: Session = Depends(get_db)):
    query = text("""
        SELECT P.nombre_parada, COUNT(I.id_incidente) AS total_incidentes
        FROM PARADAS P
        JOIN INCIDENTES I ON P.id_parada = I.id_parada
        GROUP BY P.id_parada, P.nombre_parada
        ORDER BY total_incidentes DESC
        LIMIT 5
    """)
    result = db.execute(query).fetchall()
    return [dict(row._mapping) for row in result]

@router.get("/frecuencia", response_model=List[FrecuenciaEstadistica])
def obtener_estadisticas_frecuencia(db: Session = Depends(get_db)):
    query = text("""
        SELECT id_parada, nombre_parada,
            ROUND(AVG(diff_minutes), 1) AS frecuencia_min
        FROM (
            SELECT
                rh.id_parada,
                p.nombre_parada,
                TIMESTAMPDIFF(MINUTE, rh.timestamp_real,
                    LEAD(rh.timestamp_real) OVER (
                        PARTITION BY rh.id_parada, DATE(rh.timestamp_real)
                        ORDER BY rh.timestamp_real
                    )
                ) AS diff_minutes
            FROM REGISTROS_HORARIO rh
            JOIN PARADAS p ON rh.id_parada = p.id_parada
        ) sub
        WHERE diff_minutes IS NOT NULL
          AND diff_minutes > 0
          AND diff_minutes < 120
        GROUP BY id_parada, nombre_parada
        ORDER BY frecuencia_min ASC
        LIMIT 7
    """)
    result = db.execute(query).fetchall()
    return [dict(row._mapping) for row in result]

@router.get("/calificaciones", response_model=List[CalificacionEstadistica])
def obtener_estadisticas_calificaciones(db: Session = Depends(get_db)):
    query = text("""
        SELECT R.nombre_ruta, AVG(C.puntuacion) AS promedio_seguridad
        FROM RUTAS R
        JOIN CALIFICACIONES C ON R.id_ruta = C.id_ruta
        WHERE C.categoria = 'seguridad'
        GROUP BY R.id_ruta, R.nombre_ruta
    """)
    result = db.execute(query).fetchall()
    return [dict(row._mapping) for row in result]
