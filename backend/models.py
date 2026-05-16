from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, Enum, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class Usuario(Base):
    __tablename__ = "USUARIOS"

    id_usuario = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    correo = Column(String(100), unique=True)
    carrera = Column(String(80))
    semestre = Column(Integer)
    municipio_origen = Column(String(80))
    contrasena_hash = Column(String(255), nullable=False)
    rol = Column(Enum('estudiante', 'admin'), default='estudiante')
    fecha_registro = Column(DateTime, server_default=func.now())

    registros = relationship("RegistroHorario", back_populates="usuario")
    incidentes = relationship("Incidente", back_populates="usuario")
    calificaciones = relationship("Calificacion", back_populates="usuario")

class Ruta(Base):
    __tablename__ = "RUTAS"

    id_ruta = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre_ruta = Column(String(100), nullable=False)
    numero_camion = Column(String(20), nullable=False)
    municipio_origen = Column(String(80))
    activa = Column(Boolean, default=True)
    descripcion = Column(Text)

    paradas = relationship("Parada", back_populates="ruta", cascade="all, delete-orphan")
    calificaciones = relationship("Calificacion", back_populates="ruta")

class Parada(Base):
    __tablename__ = "PARADAS"

    id_parada = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_ruta = Column(Integer, ForeignKey("RUTAS.id_ruta", ondelete="CASCADE"), nullable=False)
    nombre_parada = Column(String(120), nullable=False)
    latitud = Column(Numeric(10, 7), nullable=False)
    longitud = Column(Numeric(10, 7), nullable=False)
    orden_en_ruta = Column(Integer, nullable=False)
    es_terminal = Column(Boolean, default=False)

    ruta = relationship("Ruta", back_populates="paradas")
    registros = relationship("RegistroHorario", back_populates="parada")
    incidentes = relationship("Incidente", back_populates="parada")

class RegistroHorario(Base):
    __tablename__ = "REGISTROS_HORARIO"

    id_registro = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_parada = Column(Integer, ForeignKey("PARADAS.id_parada"), nullable=False)
    id_usuario = Column(Integer, ForeignKey("USUARIOS.id_usuario"), nullable=False)
    timestamp_real = Column(DateTime, nullable=False)
    validaciones_pos = Column(Integer, default=0)
    validaciones_neg = Column(Integer, default=0)

    parada = relationship("Parada", back_populates="registros")
    usuario = relationship("Usuario", back_populates="registros")

class Incidente(Base):
    __tablename__ = "INCIDENTES"

    id_incidente = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_parada = Column(Integer, ForeignKey("PARADAS.id_parada"), nullable=False)
    id_usuario = Column(Integer, ForeignKey("USUARIOS.id_usuario"), nullable=False)
    tipo_incidente = Column(Enum('robo', 'acoso', 'accidente', 'camion_lleno', 'retraso', 'otro'), nullable=False)
    descripcion = Column(Text)
    estado = Column(Enum('activo', 'resuelto'), default='activo')
    fecha_reporte = Column(DateTime, server_default=func.now())

    parada = relationship("Parada", back_populates="incidentes")
    usuario = relationship("Usuario", back_populates="incidentes")

class Calificacion(Base):
    __tablename__ = "CALIFICACIONES"

    id_calif = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_ruta = Column(Integer, ForeignKey("RUTAS.id_ruta"), nullable=False)
    id_usuario = Column(Integer, ForeignKey("USUARIOS.id_usuario"), nullable=False)
    puntuacion = Column(Numeric(2, 1), nullable=False)
    categoria = Column(Enum('seguridad', 'puntualidad', 'comodidad', 'limpieza'), nullable=False)
    timestamp = Column(DateTime, server_default=func.now())

    ruta = relationship("Ruta", back_populates="calificaciones")
    usuario = relationship("Usuario", back_populates="calificaciones")
