import json
import random
from pathlib import Path

from backend.models.coffee_shop import CoffeeShop

store_path = Path("store")
test_set_path = Path("test_sets/test_set.json")


def get_all_cafes_with_websites():
    cafes = []
    for path in store_path.glob("*_Germany.json"):
        shops = [CoffeeShop.model_validate(shop) for shop in json.loads(path.read_text())]
        for shop in shops:
            if shop.website.url and shop.website.accessible is not False:
                cafes.append((path.stem, shop))
    return cafes


def get_cafes_via_cities():
    cafes = {}
    for path in store_path.glob("*_Germany.json"):
        city = []
        shops = [CoffeeShop.model_validate(shop) for shop in json.loads(path.read_text())]
        for shop in shops:
            if shop.website.url and shop.website.accessible is not False:
                city.append(shop)
        cafes[path.stem] = city
    return cafes


def evaluate_test_set():
    if not test_set_path.exists():
        raise FileNotFoundError("`Test set not found!")

    with test_set_path.open() as f:
        cafes = json.load(f)

    store = get_cafes_via_cities()

    n = len(cafes)
    test_menus = 0
    test_prices = 0
    menu_correct = 0
    prices_correct = 0

    for cafe in cafes:
        city = cafe["city"]

        store_cafe = None
        for sc in store[city]:
            if sc.website.url == cafe["website"]["url"]:
                store_cafe = sc
        if not store_cafe:
            print("Error Cafe not found in Store. Skipping...")
            continue

        menu = cafe.get("menu", {})

        if menu.get("menu_url") is not None:
            test_menus += 1
            if menu["menu_url"] == store_cafe.menu.menu_url:
                menu_correct += 1

        items = menu.get("items", [])
        if items and items[0].get("price") is not None:
            test_prices += 1
            if store_cafe.menu.items and items[0]["price"] == store_cafe.menu.items[0].price:
                prices_correct += 1

    # print results
    print(f"Total Cafes in Test Set {n}")
    # test set created such that menu only shown when menu WITH cappucino price exists 
    print(f"{menu_correct}  possible menus  of {test_menus} correctly extracted") 
    print(f"{prices_correct} possible cappucino prices of {test_prices} correctly extracted")


def create_test_set():
    n = 50
    random.seed()
    cafes = get_all_cafes_with_websites()

    cafes_with_city = []
    for city, coffee_shop in random.sample(cafes, n):
        cafe_dict = coffee_shop.model_dump(mode="json")
        cafe_dict["city"] = city
        cafes_with_city.append(cafe_dict)
    data = json.dumps(cafes_with_city, indent=2, ensure_ascii=False)

    test_set_path.parent.mkdir(exist_ok=True)
    with test_set_path.open("w") as f:
        f.write(data)


if __name__ == "__main__":
    if not test_set_path.exists():
        create_test_set()
        print("Created Test Set Template. Please manually check entries.")
    else:
        evaluate_test_set()
