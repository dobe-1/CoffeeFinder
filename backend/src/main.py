from fastapi import FastAPI
from model import CoffeeShop

app = FastAPI()


@app.get("/", response_model=CoffeeShop)
def read_root():
    return CoffeeShop(
        name="Example Coffee Shop",
        coordinates=(40.7128, -74.0060),
        category="Cafe",
        webiste_url="https://example.com",
    )
