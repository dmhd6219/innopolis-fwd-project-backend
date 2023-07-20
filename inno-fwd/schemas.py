import datetime

from pydantic import BaseModel


class ItemBase(BaseModel):
    title: str | None = None
    description: str | None = None
    created: datetime.date


class ItemCreate(ItemBase):
    image: bytes


class ItemUpdate(ItemBase):
    created: datetime.date | None = None
    image: bytes | None = None


class Item(ItemBase):
    id: int
    image_path: str

    class Config:
        orm_mode = True


class AdminBase(BaseModel):
    email: str


class AdminCreate(AdminBase):
    password: str


class Admin(AdminBase):
    id: int

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str | None = None


class RegistrationForm(BaseModel):
    email: str
    password: str
