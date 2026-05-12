from pydantic import BaseModel


class CoffeeShop(BaseModel):
    name: str
    coordinates: tuple[float, float]
    category: str
    webiste_url: str
