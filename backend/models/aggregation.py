from pydantic import BaseModel


class AggregationResult(BaseModel):
    coordinates: tuple[float, float]
    sample_size: int
    aggregated_value: float | None
    total_shops: int
    shops_with_website: int
    shops_with_possible_menu: int
    # Correlation data from Grossstädte-Korrelation.csv (only available for
    # larger cities, hence optional).
    disposable_income_per_person: float | None = None
    overnight_stays_per_inhabitant: float | None = None
