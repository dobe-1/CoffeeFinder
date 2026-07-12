from pydantic import BaseModel


class AggregationResult(BaseModel):
    coordinates: tuple[float, float]
    sample_size: int
    aggregated_value: float | None
    total_shops: int
    shops_with_website: int
    shops_with_possible_menu: int
