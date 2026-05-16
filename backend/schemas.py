from pydantic import BaseModel, ConfigDict
from typing import Optional
from decimal import Decimal
from datetime import datetime

class RutaResponse(BaseModel):
    id_ruta: int
    nombre_ruta: str
    numero_camion: str
    municipio_origen: Optional[str] = None
    activa: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True)

class ParadaResponse(BaseModel):
    id_parada: int
    id_ruta: int
    nombre_parada: str
    latitud: Decimal
    longitud: Decimal
    orden_en_ruta: int

    model_config = ConfigDict(from_attributes=True)

class ParadaConRuta(ParadaResponse):
    nombre_ruta: str

class HorarioSimple(BaseModel):
    timestamp_real: datetime
    id_usuario: int

    model_config = ConfigDict(from_attributes=True)

class HorarioCreate(BaseModel):
    id_parada: int
    id_usuario: int
    timestamp_real: datetime

class HorarioResponse(BaseModel):
    message: str
    proximo_estimado_min: float

class ProximoResponse(BaseModel):
    ultimo_paso: datetime
    intervalo_promedio_min: float
    proximo_estimado: datetime
    recent_records: list[HorarioSimple]

from enum import Enum as PyEnum

class TipoIncidente(str, PyEnum):
    robo = 'robo'
    acoso = 'acoso'
    accidente = 'accidente'
    camion_lleno = 'camion_lleno'
    retraso = 'retraso'
    otro = 'otro'

class IncidenteCreate(BaseModel):
    id_parada: int
    id_usuario: int
    tipo_incidente: TipoIncidente
    descripcion: Optional[str] = None

class IncidenteResponse(BaseModel):
    id_incidente: int
    id_parada: int
    id_usuario: int
    tipo_incidente: str
    descripcion: Optional[str] = None
    estado: str
    fecha_reporte: datetime
    
    model_config = ConfigDict(from_attributes=True)

class IncidenteMapaResponse(BaseModel):
    id_parada: int
    nombre_parada: str
    latitud: Decimal
    longitud: Decimal
    total_incidentes: int
    tipos: list[str]

class UserCreate(BaseModel):
    nombre: str
    correo: str
    carrera: str
    semestre: int
    municipio_origen: str
    contrasena: str

class UserLogin(BaseModel):
    nombre: str
    contrasena: str

class UserResponse(BaseModel):
    id_usuario: int
    nombre: str
    correo: Optional[str] = None
    carrera: str
    rol: str
    municipio_origen: Optional[str] = None
    semestre: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)
