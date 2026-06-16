from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from .aggregator import aggregator
from .models.city import CityName
from .models.coffee_shop import CoffeeShop

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/coffe_shops", response_model=list[CoffeeShop])
def get_coffee_shops(
    city: CityName = Query(..., description="City name and country", examples=["Bochum, Germany"]),
):
    coffee_shops = aggregator.get_coffee_shops(city)
    return coffee_shops

# added multiple api functions for debugging purposes
@app.get("/menu")
def get_menu_for_url(
    url: str = Query(..., description="Website URL to search for menu links"),
):
    return aggregator.get_menu_for_url(url)


@app.post("/test_sets")
def create_test_set(
    city: CityName = Query(..., description="City name and country", examples=["Bochum, Germany"]),
):
    path = aggregator.create_test_set(city)
    return {"city": city, "path": str(path)}


@app.get("/test_sets/evaluate")
def evaluate_test_set(
    city: CityName = Query(..., description="City name and country", examples=["Bochum, Germany"]),
):
    return aggregator.evaluate_test_set(city)

