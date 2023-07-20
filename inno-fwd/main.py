import datetime
import io
import os

from datetime import datetime, timedelta
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext

from sqlalchemy.orm import Session
from fastapi.responses import StreamingResponse

from . import crud, models, schemas
from .database import SessionLocal, engine


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def authenticate_user(db: Session, email: str, password: str):
    user = crud.get_admin_by_email(db, email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = schemas.TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = crud.get_admin_by_email(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
        current_user: Annotated[schemas.Admin, Depends(get_current_user)]
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


models.Base.metadata.create_all(bind=engine)
app = FastAPI()


@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me/", response_model=schemas.Admin)
async def read_users_me(
    current_user: Annotated[models.Admin, Depends(get_current_active_user)]
):
    return current_user

@app.on_event("startup")
def on_startup():
    pass


@app.on_event("shutdown")
def on_shutdown():
    pass


@app.get('/')
def index_page():
    return "hello!"


@app.post("/admins/", response_model=schemas.Admin)
def create_user(admin: schemas.AdminCreate, db: Session = Depends(get_db)):
    db_user = crud.get_admin_by_email(db, email=admin.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_admin(db=db, admin=admin)


@app.get("/admins/", response_model=list[schemas.Admin])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_admins(db, skip=skip, limit=limit)
    return users


@app.get("/items/", response_model=list[schemas.Item])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_items(db, skip=skip, limit=limit)
    return items


@app.post('/items/', response_model=schemas.Item)
def create_item(item: schemas.ItemCreate, db: Session = Depends(get_db)):
    db_item = crud.get_item_by_date(db, date=item.created)
    if db_item:
        raise HTTPException(status_code=400, detail="Email already registered")

    return crud.create_item(db=db, item=item)


@app.get('/create-database')
def create_database(db: Session = Depends(get_db)):
    for year in os.listdir('./photos'):
        for month in os.listdir(f'./photos/{year}'):
            for day in os.listdir(f'./photos/{year}/{month}'):
                files = os.listdir(f'./photos/{year}/{month}/{day}')
                if "image.png" in files:
                    date = datetime.date(int(year), int(month), int(day))
                    crud.create_item(db=db, item=schemas.ItemCreate(created=date))
                    print(f'created {year}:{month}:{day}')
    return "Hey!"


@app.get('/items/{date}', response_model=schemas.Item)
def get_item(date: datetime.date, db: Session = Depends(get_db)):
    return crud.get_item_by_date(db=db, date=date)


@app.get('/items/{date}/photo', response_model=bytes)
def get_item_image(date: datetime.date, db: Session = Depends(get_db)):
    item = crud.get_item_by_date(db=db, date=date)
    if item:
        photo = f'./photos/{item.created.year}/{item.created.month}/{item.created.day}/image.png'
        with open(photo, "rb") as f:
            image_bytes = f.read()
        return StreamingResponse(io.BytesIO(image_bytes), media_type="image/png")
    return ""
