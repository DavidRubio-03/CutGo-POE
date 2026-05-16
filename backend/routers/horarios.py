from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime, timedelta

from backend.database import get_db
from backend.models import RegistroHorario, Parada
from backend.schemas import HorarioCreate, HorarioResponse, ProximoResponse

router = APIRouter(prefix="/api", tags=["horarios"])

def calcular_intervalo_promedio(id_parada: int, db: Session) -> float:
    # SQL query to get the average interval from the last 10 records
    query = text("""
        SELECT TIMESTAMPDIFF(MINUTE, MIN(timestamp_real), MAX(timestamp_real)) / NULLIF(COUNT(*) - 1, 0) as avg_interval
        FROM (
            SELECT timestamp_real 
            FROM REGISTROS_HORARIO 
            WHERE id_parada = :id_parada 
            ORDER BY timestamp_real DESC 
            LIMIT 10
        ) as subquery
    """)
    result = db.execute(query, {"id_parada": id_parada}).fetchone()
    if result and result[0] is not None:
        return float(result[0])
    return 15.0  # Default estimate

@router.post("/horarios", response_model=HorarioResponse)
def registrar_horario(horario: HorarioCreate, db: Session = Depends(get_db)):
    nuevo_registro = RegistroHorario(
        id_parada=horario.id_parada,
        id_usuario=horario.id_usuario,
        timestamp_real=horario.timestamp_real
    )
    db.add(nuevo_registro)
    db.commit()
    db.refresh(nuevo_registro)
    
    intervalo_promedio = calcular_intervalo_promedio(horario.id_parada, db)
    
    return HorarioResponse(
        message="Registrado",
        proximo_estimado_min=intervalo_promedio
    )

@router.get("/paradas/{id_parada}/proximos", response_model=ProximoResponse)
def obtener_proximo(id_parada: int, db: Session = Depends(get_db)):
    parada = db.query(Parada).filter(Parada.id_parada == id_parada).first()
    if not parada:
        raise HTTPException(status_code=404, detail="Parada no encontrada")

    ultimo_registro = db.query(RegistroHorario).filter(RegistroHorario.id_parada == id_parada).order_by(RegistroHorario.timestamp_real.desc()).first()
    
    if not ultimo_registro:
        now = datetime.now()
        return ProximoResponse(
            ultimo_paso=now,
            intervalo_promedio_min=15.0,
            proximo_estimado=now + timedelta(minutes=15),
            recent_records=[]
        )
        
    intervalo_promedio = calcular_intervalo_promedio(id_parada, db)
    proximo_estimado = ultimo_registro.timestamp_real + timedelta(minutes=intervalo_promedio)
    
    # Fetch last 5 records for history
    recent_records = db.query(RegistroHorario)\
        .filter(RegistroHorario.id_parada == id_parada)\
        .order_by(RegistroHorario.timestamp_real.desc())\
        .limit(5).all()
    
    return ProximoResponse(
        ultimo_paso=ultimo_registro.timestamp_real,
        intervalo_promedio_min=intervalo_promedio,
        proximo_estimado=proximo_estimado,
        recent_records=recent_records
    )
