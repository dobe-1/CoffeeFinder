from datetime import datetime

from pydantic import BaseModel


class MenuItem(BaseModel):
    name: str
    price: float


class Menu(BaseModel):
    menu_url: str | None = None
    menu_url_last_checked: datetime | None = None
    menu_url_accessible: bool | None = None
    currency: str | None = None
    extracted_at: datetime | None = None
    items: list[MenuItem] = []
