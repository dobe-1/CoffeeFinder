import csv
import json
import math
import os
from importlib.util import find_spec
from pathlib import Path

os.environ.setdefault(
    "MPLCONFIGDIR",
    str(Path(__file__).with_name(".matplotlib-cache")),
)

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.colors import TwoSlopeNorm
from matplotlib.lines import Line2D
from shapely.geometry import Polygon
from sklearn.linear_model import LinearRegression

BASE_DIR = Path(__file__).resolve().parents[1]
CORRELATION_DATA_PATH = BASE_DIR / "Grossstädte-Korrelation.csv"
AGGREGATES_PATH = Path("store") / "aggregates.json"
OUTPUT_PATH = Path(__file__).with_name("heatmap.png")
INCOME_COLUMN = "Verfügbares Einkommen pro Person in Euro"
MARKER_SIZE = 180


def parse_number(value: str) -> float | None:
    cleaned = value.strip().replace(" ", "").replace(",", ".")
    if not cleaned:
        return None
    return float(cleaned)


def normalize_city_name(city: str) -> str:
    return city.split(" (", 1)[0]


def load_income_data() -> dict[str, float]:
    with CORRELATION_DATA_PATH.open(encoding="utf-8", newline="") as file:
        rows = csv.DictReader(file)
        return {
            normalize_city_name(row["Stadt"]): income
            for row in rows
            if (income := parse_number(row[INCOME_COLUMN])) is not None
        }


def load_cappuccino_aggregates() -> dict[str, dict[str, object]]:
    if not AGGREGATES_PATH.exists():
        raise FileNotFoundError(
            f"{AGGREGATES_PATH} is missing. Run `python eval/aggregate_cappuccino_prices.py` first."
        )
    return json.loads(AGGREGATES_PATH.read_text(encoding="utf-8"))


def load_germany_map() -> gpd.GeoDataFrame:
    pyogrio_spec = find_spec("pyogrio")
    if pyogrio_spec is not None:
        shapefile_path = (
            Path(pyogrio_spec.origin).parent
            / "tests"
            / "fixtures"
            / "naturalearth_lowres"
            / "naturalearth_lowres.shp"
        )
        if shapefile_path.exists():
            world = gpd.read_file(shapefile_path)
            germany = world[world["name"] == "Germany"]
            if not germany.empty:
                return germany.to_crs("EPSG:4326")

    # Coarse fallback used only when the local Natural Earth fixture is absent.
    outline = Polygon(
        [
            (5.87, 47.27),
            (7.59, 47.55),
            (9.53, 47.27),
            (10.45, 47.56),
            (12.16, 47.67),
            (13.83, 48.77),
            (13.40, 50.10),
            (15.04, 51.04),
            (14.69, 53.30),
            (13.03, 54.43),
            (11.06, 54.42),
            (8.67, 54.90),
            (6.75, 53.60),
            (6.07, 51.91),
            (5.95, 50.13),
            (6.18, 49.46),
            (5.87, 47.27),
        ]
    )
    return gpd.GeoDataFrame({"name": ["Germany"]}, geometry=[outline], crs="EPSG:4326")


def add_correlation_metrics(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    priced = df.dropna(subset=["cappuccino_price", "income"]).copy()

    df["expected_cappuccino_price"] = pd.NA
    df["price_deviation"] = pd.NA
    df["affordability_ratio"] = pd.NA

    if priced.empty:
        return df

    if len(priced) < 2:
        df.update(priced[["affordability_ratio"]])
        return df

    model = LinearRegression()
    model.fit(priced[["income"]], priced["cappuccino_price"])

    priced["expected_cappuccino_price"] = model.predict(priced[["income"]])
    priced["price_deviation"] = priced["cappuccino_price"] - priced["expected_cappuccino_price"]
    priced["affordability_ratio"] = priced["cappuccino_price"] / priced["income"] * 1000

    df.update(
        priced[
            [
                "expected_cappuccino_price",
                "price_deviation",
                "affordability_ratio",
            ]
        ]
    )
    return df


def build_city_points() -> tuple[gpd.GeoDataFrame, list[str]]:
    rows = []
    missing = []
    aggregates = load_cappuccino_aggregates()
    income_data = load_income_data()

    # Filter out cafes low on sample size
    required_sample_size_rel = 88 / 2546  # This is the ratio extracted from Berlin
    skipped = 0

    for city, aggregate in aggregates.items():
        if aggregate.get("total_shops", 0) == 0:
            continue
        if aggregate.get("sample_size", 0) < required_sample_size_rel * aggregate.get(
            "total_shops", 0
        ):
            print(
                f"Skipping {city} due to insufficient sample size: {aggregate.get('sample_size', 0)} < {required_sample_size_rel * aggregate.get('total_shops', 0)}"
            )
            skipped += 1
            continue

        coordinates = aggregate.get("coordinates")
        lat = None
        lon = None
        if isinstance(coordinates, list | tuple) and len(coordinates) >= 2:
            lat = coordinates[0]
            lon = coordinates[1]

        if lat is None or lon is None:
            missing.append(city)
            continue

        income = income_data.get(city)
        cappuccino_price = aggregate.get("aggregated_value")
        sample_size = aggregate.get("sample_size", 0)
        price_source = "extracted" if cappuccino_price is not None else "missing"

        rows.append(
            {
                "city": city,
                "lat": lat,
                "lon": lon,
                "income": income,
                "cappuccino_price": cappuccino_price,
                "sample_size": sample_size,
                "price_source": price_source,
            }
        )

    print(
        f"Skipped {skipped} cities due to insufficient sample size. ({skipped / len(aggregates) * 100:.2f}%)"
    )

    df = add_correlation_metrics(pd.DataFrame(rows))
    gdf = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df["lon"], df["lat"]),
        crs="EPSG:4326",
    )
    return gdf, missing


def plot_map(germany: gpd.GeoDataFrame, cities: gpd.GeoDataFrame) -> None:
    fig, ax = plt.subplots(figsize=(11, 13))
    priced_cities = cities.dropna(subset=["cappuccino_price", "price_deviation"])

    germany.plot(
        ax=ax,
        color="#f6f1e7",
        edgecolor="#34495e",
        linewidth=1.2,
    )

    if not priced_cities.empty:
        max_abs_deviation = priced_cities["price_deviation"].abs().max()
        if max_abs_deviation == 0:
            max_abs_deviation = 1
        norm = TwoSlopeNorm(
            vmin=-max_abs_deviation,
            vcenter=0,
            vmax=max_abs_deviation,
        )
        scatter = ax.scatter(
            priced_cities.geometry.x,
            priced_cities.geometry.y,
            s=MARKER_SIZE,
            c=priced_cities["price_deviation"],
            cmap="coolwarm",
            edgecolors="white",
            linewidths=0.9,
            norm=norm,
            alpha=0.9,
            zorder=3,
        )
        colorbar = fig.colorbar(scatter, ax=ax, fraction=0.035, pad=0.02)
        colorbar.set_label("EUR above or below predicted cappuccino price")

    for index, row in cities.reset_index(drop=True).iterrows():
        x_offset = 0.08 if index % 2 == 0 else -0.08
        y_offset = 0.045 if index % 3 == 0 else -0.045
        ha = "left" if x_offset > 0 else "right"
        ax.text(
            row.geometry.x + x_offset,
            row.geometry.y + y_offset,
            row["city"],
            fontsize=9,
            color="#25313d",
            ha=ha,
            va="center",
        )

    legend_handles = [
        Line2D(
            [0],
            [0],
            marker="o",
            color="none",
            label="Below income trend",
            markerfacecolor="#3b4cc0",
            markeredgecolor="white",
            markersize=8,
        ),
        Line2D(
            [0],
            [0],
            marker="o",
            color="none",
            label="Above income trend",
            markerfacecolor="#b40426",
            markeredgecolor="white",
            markersize=8,
        ),
    ]
    ax.legend(handles=legend_handles, loc="lower left", frameon=True)
    ax.set_title(
        "Cappuccino price deviation from the income trend",
        fontsize=16,
        pad=12,
    )
    # ax.set_xlim(5.3, 15.6)
    # ax.set_ylim(47.0, 55.3)
    # ax.set_xticks(range(6, 16, 2))
    # ax.set_yticks(range(48, 56, 2))
    # ax.set_xlabel("Longitude")
    # ax.set_ylabel("Latitude")
    # ax.grid(color="#d8dee4", linestyle="--", linewidth=0.45, alpha=0.75)
    ax.set_xticks([])
    ax.set_yticks([])
    mean_latitude = sum(ax.get_ylim()) / 2
    ax.set_aspect(1 / math.cos(math.radians(mean_latitude)))
    fig.tight_layout()
    fig.savefig(OUTPUT_PATH, dpi=300, bbox_inches="tight", pad_inches=0.1)
    plt.close(fig)


def main() -> None:
    germany = load_germany_map()
    city_points, missing = build_city_points()
    plot_map(germany, city_points)

    priced_count = city_points["cappuccino_price"].notna().sum()
    extracted_price_count = (city_points["price_source"] == "extracted").sum()
    sample_count = city_points["sample_size"].sum()
    print(f"Plotted {len(city_points)} cities on Germany map.")
    print(f"Used extracted cappuccino prices for {priced_count} cities.")
    print(f"  extracted price averages: {extracted_price_count}")
    print(f"  coffee-shop samples used: {sample_count}")
    if missing:
        print(f"Missing coordinates for: {', '.join(missing)}")
    print(f"Saved heatmap to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
