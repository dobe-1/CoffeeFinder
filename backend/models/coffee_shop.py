from pydantic import BaseModel

from .menu import Menu
from .website import Website


class CoffeeShop(BaseModel):
    name: str
    coordinates: tuple[float, float]
    category: str
    website: Website
    menu: Menu
