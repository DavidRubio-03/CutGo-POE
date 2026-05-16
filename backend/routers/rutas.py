from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_db
from backend.models import Ruta, Parada
from backend.schemas import RutaResponse, ParadaResponse

router = APIRouter(prefix="/api/rutas", tags=["rutas"])

@router.get("", response_model=List[RutaResponse])
@router.get("/", response_model=List[RutaResponse])
def get_active_routes(db: Session = Depends(get_db)):
    rutas = db.query(Ruta).filter(Ruta.activa == True).all()
    return rutas

@router.get("/{id_ruta}/paradas", response_model=List[ParadaResponse])
def get_route_stops(id_ruta: int, db: Session = Depends(get_db)):
    # Check if the route exists
    ruta = db.query(Ruta).filter(Ruta.id_ruta == id_ruta).first()
    if not ruta:
        raise HTTPException(status_code=404, detail="Ruta no encontrada")
    
    # Return stops ordered by order_en_ruta
    paradas = db.query(Parada).filter(Parada.id_ruta == id_ruta).order_by(Parada.orden_en_ruta).all()
    return paradas
