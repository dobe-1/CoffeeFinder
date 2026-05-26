import re
from typing import Annotated

from pydantic import BeforeValidator


def validate_city_country(value: str) -> bool:
    pattern = r"^[A-Za-zÀ-ÖØ-öø-ÿ\s\-]+,\s*[A-Za-zÀ-ÖØ-öø-ÿ\s\-]+$"
    return bool(re.match(pattern, value.strip()))


CityName = Annotated[str, BeforeValidator(validate_city_country)]
