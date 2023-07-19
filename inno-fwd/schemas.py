import datetime

from pydantic import BaseModel


class ItemBase(BaseModel):
    title: str | None = None
    description: str | None = None
    created: datetime.date
    is_private: bool = False


class ItemCreate(ItemBase):
    pass


class Item(ItemBase):
    id: int

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
