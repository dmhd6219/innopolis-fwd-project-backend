import datetime
import io
import os

from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from fastapi.responses import StreamingResponse

from . import crud, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)
app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


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
