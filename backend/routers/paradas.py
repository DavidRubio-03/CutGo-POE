from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Parada
from ..schemas import ParadaResponse

router = APIRouter(prefix="/api/paradas", tags=["paradas"])

@router.get("/todas", response_model=List[ParadaResponse])
def get_todas_las_paradas(db: Session = Depends(get_db)):
    """
    Returns all paradas from all routes.
    Used for client-side GPS detection.
    """
    try:
        paradas = db.query(Parada).order_by(Parada.id_ruta, Parada.orden_en_ruta).all()
        return paradas
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener paradas: {str(e)}")
