from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta

from backend.database import get_db
from backend.models import Incidente, Parada
from backend.schemas import IncidenteCreate, IncidenteResponse, IncidenteMapaResponse

router = APIRouter(
    prefix="/api/incidentes",
    tags=["Incidentes"]
)

@router.post("/", response_model=IncidenteResponse)
def crear_incidente(incidente: IncidenteCreate, db: Session = Depends(get_db)):
    nuevo_incidente = Incidente(
        id_parada=incidente.id_parada,
        id_usuario=incidente.id_usuario,
        tipo_incidente=incidente.tipo_incidente.value,
        descripcion=incidente.descripcion,
        estado='activo'
    )
    db.add(nuevo_incidente)
    db.commit()
    db.refresh(nuevo_incidente)
    return nuevo_incidente

@router.get("/activos", response_model=List[IncidenteResponse])
def obtener_incidentes_activos(id_parada: int, db: Session = Depends(get_db)):
    hace_7_dias = datetime.utcnow() - timedelta(days=7)
    incidentes = db.query(Incidente).filter(
        Incidente.id_parada == id_parada,
        Incidente.estado == 'activo',
        Incidente.fecha_reporte >= hace_7_dias
    ).all()
    return incidentes

@router.get("/mapa", response_model=List[IncidenteMapaResponse])
def obtener_incidentes_mapa(db: Session = Depends(get_db)):
    incidentes_activos = db.query(Incidente, Parada).join(
        Parada, Incidente.id_parada == Parada.id_parada
    ).filter(
        Incidente.estado == 'activo'
    ).all()

    mapa_dict = {}
    for incidente, parada in incidentes_activos:
        if parada.id_parada not in mapa_dict:
            mapa_dict[parada.id_parada] = {
                "id_parada": parada.id_parada,
                "nombre_parada": parada.nombre_parada,
                "latitud": parada.latitud,
                "longitud": parada.longitud,
                "total_incidentes": 0,
                "tipos": set()
            }
        mapa_dict[parada.id_parada]["total_incidentes"] += 1
        mapa_dict[parada.id_parada]["tipos"].add(incidente.tipo_incidente)

    response = []
    for item in mapa_dict.values():
        item["tipos"] = list(item["tipos"])
        response.append(item)
        
    return response
