import datetime
import io
import os

from datetime import timedelta

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.responses import StreamingResponse
from starlette.middleware.cors import CORSMiddleware

from . import crud, models, schemas, auth, images
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)
app = FastAPI()
app.add_middleware(CORSMiddleware,
                   allow_origins=["*"],
                   allow_credentials=True,
                   allow_methods=["*"],
                   allow_headers=["*"])


@app.get('/')
def index_page():
    return "hello!"


@app.get("/admins/me", response_model=schemas.Admin)
def get_authorized_admin_account(token: str, db: Session = Depends(get_db)):
    print("in users/me")
    return auth.get_current_user(db, token)


@app.get("/items", response_model=list[schemas.Item])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_items(db, skip=skip, limit=limit)
    return items


@app.post('/create-database')
def create_database(token: str, db: Session = Depends(get_db)):
    if not auth.get_current_user(db, token):
        raise HTTPException(status_code=400, detail="Not authenticated to do this")
    for year in os.listdir('./photos'):
        for month in os.listdir(f'./photos/{year}'):
            for day in os.listdir(f'./photos/{year}/{month}'):
                files = os.listdir(f'./photos/{year}/{month}/{day}')
                if "image.png" in files:
                    date = datetime.date(int(year), int(month), int(day))
                    crud.create_item(db=db, item=schemas.ItemCreate(created=date))
                    print(f'created {year}:{month}:{day}')
    return "DB is created!"


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


@app.post('/items/create', response_model=schemas.Item)
def create_item(token: str, item: schemas.ItemCreate, override: bool = False,
                db: Session = Depends(get_db)):
    if not auth.get_current_user(db, token):
        raise HTTPException(status_code=400, detail="Not authenticated to do this")

    old_item = crud.get_item_by_date(db=db, date=item.created)
    if old_item and override:
        # removing existing items
        os.remove(os.path.dirname(
            os.path.realpath(__file__)) + f'/{item.date.year}/{item.date.month}/{item.date.day}/image.png')
        crud.delete_item(db=db, item=old_item)

        # saving photo from bytesarray
        images.save_photo(item.image, item.created)

        return crud.create_item_by_values(db=db, title=item.title, desc=item.desc, date=item.date)

    if not old_item:
        images.save_photo(item.image, item.created)

        return crud.create_item_by_values(db=db, title=item.title, desc=item.desc, date=item.date)

    raise HTTPException(status_code=400, detail="Such Item already exists")


@app.post('/items/edit', response_model=schemas.Item)
def edit_item(token: str, item: schemas.ItemCreate, create: bool = False,
              db: Session = Depends(get_db)):
    if not auth.get_current_user(db, token):
        raise HTTPException(status_code=400, detail="Not authenticated to do this")

    old_item = crud.get_item_by_date(db=db, date=item.created)
    if not old_item and create:
        images.save_photo(item.image, item.created)

        return crud.create_item_by_values(db=db, title=item.title, desc=item.desc, date=item.date)

    if old_item:
        # removing existing items
        os.remove(os.path.dirname(
            os.path.realpath(__file__)) + f'/{item.date.year}/{item.date.month}/{item.date.day}/image.png')
        crud.delete_item(db=db, item=old_item)

        # saving photo from bytesarray
        images.save_photo(item.image, item.created)

        return crud.create_item_by_values(db=db, title=item.title, desc=item.desc, date=item.date)

    raise HTTPException(status_code=400, detail="No such Item")


@app.post("/register", response_model=schemas.Admin)
def register(email: str, password: str, db: Session = Depends(get_db)):
    if crud.get_admin_by_email(db=db, email=email):
        raise HTTPException(status_code=400, detail="You already authenticated to do this")
    return crud.create_admin_by_mail_and_password(db=db, email=email, password=password)


@app.post("/token")
async def login_for_access_token(email: str, password: str, db: Session = Depends(get_db)):
    user = auth.authenticate_user(db, email, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return access_token
