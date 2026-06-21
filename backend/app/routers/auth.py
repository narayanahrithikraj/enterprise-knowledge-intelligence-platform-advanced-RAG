from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import jwt
from pydantic import BaseModel, EmailStr

from app.db.session import get_db
from app.db.models import User
from app.core.config import settings

from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login-form")

class UserSignup(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: str = "User"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate corporate session tokens.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        email: str = payload.get("sub")
        if email is None: raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
        
    user = db.query(User).filter(User.email == email).first()
    if user is None: raise credentials_exception
    return user

@router.post("/signup", status_code=201)
def signup(payload: UserSignup, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == payload.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Identity profile record already exists within organization catalog indexes.")
    
    hashed_password = pwd_context.hash(payload.password)
    new_user = User(
        email=payload.email,
        hashed_password=hashed_password, # FIXED: Aligned property mapping with database columns
        full_name=payload.full_name,
        role=payload.role,
        is_active=True
    )
    db.add(new_user)
    db.commit()
    return {"message": "Identity profile initialized successfully."}

@router.post("/login")
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    # FIXED: Re-mapped validation query parameters to verify using database column strings
    if not user or not pwd_context.verify(payload.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Verification Blocked: Invalid Credentials.")
    
    token = create_access_token(data={"sub": user.email})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {"email": user.email, "full_name": user.full_name, "role": user.role}
    }

@router.post("/login-form")
def login_swagger(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    return login(UserLogin(email=form_data.username, password=form_data.password), db)