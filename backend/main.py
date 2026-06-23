from fastapi import FastAPI, Query

from .aggregator import aggregator
from .models.city import CityName
from .models.coffee_shop import CoffeeShop

app = FastAPI()


@app.get("/coffe_shops", response_model=list[CoffeeShop])
def get_coffee_shops(
    city: CityName = Query(..., description="City name and country", examples=["Bochum, Germany"]),
):
    coffee_shops = aggregator.get_coffee_shops(city)
    return coffee_shops
