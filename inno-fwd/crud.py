import datetime

from sqlalchemy.orm import Session

from . import models, schemas, auth


def get_admin(db: Session, user_id: int):
    return db.query(models.Admin).filter(models.Admin.id == user_id).first()


def get_admin_by_email(db: Session, email: str):
    return db.query(models.Admin).filter(models.Admin.email == email).first()


def get_item_by_date(db: Session, date: datetime.date):
    return db.query(models.Item).filter(models.Item.created == date).first()


def get_admins(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Admin).offset(skip).limit(limit).all()


def create_admin_by_mail_and_password(db: Session, email: str, password: str) -> models.Admin:
    hashed_password = auth.get_password_hash(password)
    db_user = models.Admin(email=email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Item).offset(skip).limit(limit).all()


def create_item_by_values(db: Session, date: datetime.date, title: str | None = None, desc: str | None = None, original : bool = False):
    db_item = models.Item(title=title, description=desc, created=date, original=original)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def delete_item_by_date(db: Session, date: datetime.date):
    db.delete(db.query(models.Item).filter(models.Item.created == date).first())
    db.commit()
