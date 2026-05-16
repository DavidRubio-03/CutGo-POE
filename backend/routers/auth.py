from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import bcrypt
from ..database import get_db
from ..models import Usuario
from ..schemas import UserCreate, UserLogin, UserResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])

def get_password_hash(password: str) -> str:
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

@router.post("/register", response_model=UserResponse)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    existing_user = db.query(Usuario).filter(Usuario.nombre == user_in.nombre).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="El usuario ya existe")
    
    try:
        hashed_password = get_password_hash(user_in.contrasena)
        new_user = Usuario(
            nombre=user_in.nombre,
            correo=user_in.correo,
            carrera=user_in.carrera,
            semestre=user_in.semestre,
            municipio_origen=user_in.municipio_origen,
            contrasena_hash=hashed_password,
            rol='estudiante'
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error al registrar usuario")

@router.post("/login", response_model=UserResponse)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(Usuario).filter(Usuario.nombre == credentials.nombre).first()
    if not user:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    
    if not verify_password(credentials.contrasena, user.contrasena_hash):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    
    return user

@router.get("/me", response_model=UserResponse)
def get_me(id_usuario: int, db: Session = Depends(get_db)):
    user = db.query(Usuario).filter(Usuario.id_usuario == id_usuario).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user
