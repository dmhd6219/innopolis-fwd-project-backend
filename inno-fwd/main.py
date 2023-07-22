import datetime
import io
import os
from datetime import timedelta

from fastapi import Depends, FastAPI, HTTPException, status, Form, File, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi.responses import StreamingResponse
from starlette.middleware.cors import CORSMiddleware

from . import crud, models, schemas, auth, images
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)
app = FastAPI()
app.add_middleware(CORSMiddleware,
                   allow_origins=[
                       'https://innopolis-fwd-project.pages.dev',
                       "http://localhost:5173"
                   ],
                   allow_credentials=True,
                   allow_methods=["POST", "DELETE", "GET"],
                   allow_headers=['*']
                   )


@app.get('/')
def index_page():
    return "hello!"


@app.get("/admins/me")
def get_authorized_admin_account(token: str, db: Session = Depends(get_db)):
    print("in users/me")
    return auth.get_current_user(db, token)


@app.get("/items")
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_items(db, skip=skip, limit=limit)
    return items

# # TODO : remove
# @app.get('/create-database')
# def create_database(db: Session = Depends(get_db)):
#     for year in os.listdir('./photos'):
#         for month in os.listdir(f'./photos/{year}'):
#             for day in os.listdir(f'./photos/{year}/{month}'):
#                 files = os.listdir(f'./photos/{year}/{month}/{day}')
#                 if "image.png" in files:
#                     date = datetime.date(int(year), int(month), int(day))
#                     crud.create_item_by_values(db=db, date=date, original=True)
#                     print(f'created {year}:{month}:{day}')
#     return "DB is created!"


@app.get('/items/{date}/exists')
def get_item_existence(date: datetime.date, db: Session = Depends(get_db)):
    return not (crud.get_item_by_date(db=db, date=date) is None)


@app.get('/items/{date}')
def get_item(date: datetime.date, db: Session = Depends(get_db)):
    return crud.get_item_by_date(db=db, date=date)


@app.get('/items/{date}/photo')
def get_item_image(date: datetime.date, db: Session = Depends(get_db)):
    item = crud.get_item_by_date(db=db, date=date)
    if item:
        photo = '\\'.join(os.path.dirname(os.path.realpath(__file__)).split('\\')[:-1:]) + \
                f'\\photos\\{item.created.year if item.created.year > 9 else "0" + str(item.created.year)}\\' \
                f'{item.created.month}\\' \
                f'{item.created.day if item.created.day > 9 else "0" + str(item.created.day)}\\image.png'

        with open(photo, "rb") as f:
            image_bytes = f.read()
        return StreamingResponse(io.BytesIO(image_bytes), media_type="image/png")
    return ""


@app.delete('/items/{date}/delete')
async def get_item(token: str, date: datetime.date, db: Session = Depends(get_db)):
    if not await auth.get_current_user(db, token):
        raise HTTPException(status_code=400, detail="Not authenticated to do this")

    old_item = crud.get_item_by_date(db=db, date=date)
    if not old_item:
        raise HTTPException(status_code=400, detail="No such Item")

    if old_item.original:
        raise HTTPException(status_code=400, detail="You cannot delete Original Item")

    return crud.delete_item_by_date(db=db, date=date)


@app.post('/items/{item_date}/edit')
async def edit_item(token: str,
                    item_date: datetime.date,
                    title: str = Form(...),
                    file: UploadFile = File(...),
                    desc: str = Form(...),
                    db: Session = Depends(get_db)):
    if not await auth.get_current_user(db, token):
        raise HTTPException(status_code=400, detail="Not authenticated to do this")

    old_item = crud.get_item_by_date(db=db, date=item_date)
    if not old_item:
        raise HTTPException(status_code=400, detail="No such Item")

    if old_item.original:
        raise HTTPException(status_code=400, detail="You cannot edit Original Item")

    crud.delete_item_by_date(db=db, date=item_date)
    images.save_photo(await file.read(), item_date)
    return crud.create_item_by_values(db=db, title=title, desc=desc, date=item_date)


@app.post('/items/create')
async def create_item(token: str,
                      title: str = Form(...),
                      date: str = Form(...),
                      file: UploadFile = File(...),
                      desc: str = Form(...),
                      db: Session = Depends(get_db)):
    if not await auth.get_current_user(db, token):
        raise HTTPException(status_code=400, detail="Not authenticated to do this")

    date_obj = datetime.date(year=int(date.split('-')[0]), month=int(date.split('-')[1]), day=int(date.split('-')[2]))
    old_item = crud.get_item_by_date(db=db, date=date_obj)

    if old_item:
        raise HTTPException(status_code=400, detail="Such Item already exists")

    images.save_photo(await file.read(), date_obj)
    return crud.create_item_by_values(db=db, title=title, desc=desc, date=date_obj)


@app.post("/register")
def register(email: str, password: str, db: Session = Depends(get_db)):
    print(email, password)
    if crud.get_admin_by_email(db=db, email=email):
        raise HTTPException(status_code=400, detail="You already authenticated to do this")
    return crud.create_admin_by_mail_and_password(db=db, email=email, password=password)


@app.post("/token")
async def login_for_access_token(email: str, password: str, db: Session = Depends(get_db)):
    print(email, str)
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
