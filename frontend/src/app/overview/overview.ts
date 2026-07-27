import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { AggregationResult, CoffeeService } from '../coffee.service';
import { SankeyChart } from '../diagrams/sankey-chart/sankey-chart';
import { buildPriceFunnel } from '../diagrams/sankey-chart/price-funnel';
import { Scatterplot, ScatterPoint } from '../diagrams/scatterplot/scatterplot';
import { Geomap, GeoScatterPoint } from '../diagrams/geomap/geomap';

const GERMANY_MAP_NAME = 'germany';
const GERMANY_GEOJSON_URL = 'germany.geo.json';

// Minimum sample size relative to a city's shop count for its price to be
// considered reliable (derived from Berlin).
const RELIABLE_SAMPLE_RATIO = 88 / 2546;

const RELIABLE_COLOR = '#6f4e37';
const DIMMED_COLOR = '#c9c2b6';

@Component({
  selector: 'app-overview',
  standalone: true,
  imports: [SankeyChart, Scatterplot, Geomap],
  templateUrl: './overview.html',
  styleUrl: './overview.css',
})
export class Overview implements OnInit {
  private readonly coffeeService = inject(CoffeeService);

  private readonly totals = computed(() => {
    const aggregates = Object.values(this.coffeeService.aggregates());
    return aggregates.reduce(
      (acc, agg) => ({
        totalShops: acc.totalShops + agg.total_shops,
        shopsWithWebsite: acc.shopsWithWebsite + agg.shops_with_website,
        shopsWithPrices: acc.shopsWithPrices + agg.sample_size,
      }),
      { totalShops: 0, shopsWithWebsite: 0, shopsWithPrices: 0 },
    );
  });

  private readonly funnel = computed(() => buildPriceFunnel(this.totals()));

  readonly sankeyNodes = computed(() => this.funnel().nodes);
  readonly sankeyLinks = computed(() => this.funnel().links);
  readonly hasData = computed(() => this.totals().totalShops > 0);

  readonly incomePoints = computed(() =>
    this.scatterPoints((agg) => agg.disposable_income_per_person),
  );

  readonly overnightPoints = computed(() =>
    this.scatterPoints((agg) => agg.overnight_stays_per_inhabitant),
  );

  readonly germanyMapName = GERMANY_MAP_NAME;
  readonly germanyGeoJson = signal<object | null>(null);


  // Deviation of the measured price from the price predicted by a linear fit,
  // mirroring eval/heatmap.py. Only reliable cities enter the fit.
  readonly incomeDeviationPoints = computed(() =>
    this.deviationPoints((agg) => agg.disposable_income_per_person),
  );

  readonly overnightDeviationPoints = computed(() =>
    this.deviationPoints((agg) => agg.overnight_stays_per_inhabitant),
  );

  readonly incomeGeoPoints = computed(() =>
    this.geoValuePoints((agg) => agg.disposable_income_per_person),
  );

  readonly overnightGeoPoints = computed(() =>
    this.geoValuePoints((agg) => agg.overnight_stays_per_inhabitant),
  );

  readonly affordabilityPoints = computed<GeoScatterPoint[]>(() =>
    Object.entries(this.coffeeService.aggregates()).flatMap(([city, agg]) => {
      const income = agg.disposable_income_per_person;
      const price = agg.aggregated_value;
      if (income == null || price == null || price === 0) {
        return [];
      }
      const [lat, lon] = agg.coordinates;
      return [
        {
          name: city,
          lon,
          lat,
          value: income / price,
          dimmed: !this.isReliable(agg),
        },
      ];
    }),
  );

  readonly geoPoints = computed<GeoScatterPoint[]>(() =>
    Object.entries(this.coffeeService.aggregates()).flatMap(([city, agg]) => {
      if (agg.aggregated_value == null) {
        return [];
      }
      const [lat, lon] = agg.coordinates;
      return [
        {
          name: city,
          lon,
          lat,
          value: agg.aggregated_value,
          dimmed: !this.isReliable(agg),
        },
      ];
    }),
  );

  // Whether a city's extracted price is reliable enough
  // Unreliable cities are still plotted, just dimmed.
  private isReliable(agg: AggregationResult): boolean {
    return agg.total_shops > 0 && agg.sample_size > 3 && agg.sample_size >= RELIABLE_SAMPLE_RATIO * agg.total_shops * 0.7;
  }

  private geoValuePoints(
    getValue: (agg: AggregationResult) => number | null,
  ): GeoScatterPoint[] {
    return Object.entries(this.coffeeService.aggregates()).flatMap(([city, agg]) => {
      const value = getValue(agg);
      if (value == null) {
        return [];
      }
      const [lat, lon] = agg.coordinates;
      return [{ name: city, lon, lat, value }];
    });
  }

  private deviationPoints(
    getX: (agg: AggregationResult) => number | null,
  ): GeoScatterPoint[] {
    const cities = Object.entries(this.coffeeService.aggregates()).flatMap(([city, agg]) => {
      const x = getX(agg);
      const y = agg.aggregated_value;
      if (x == null || y == null || !this.isReliable(agg)) {
        return [];
      }
      const [lat, lon] = agg.coordinates;
      return [{ city, x, y, lat, lon }];
    });

    if (cities.length < 2) {
      return [];
    }

    const meanX = cities.reduce((sum, c) => sum + c.x, 0) / cities.length;
    const meanY = cities.reduce((sum, c) => sum + c.y, 0) / cities.length;
    const covariance = cities.reduce((sum, c) => sum + (c.x - meanX) * (c.y - meanY), 0);
    const variance = cities.reduce((sum, c) => sum + (c.x - meanX) ** 2, 0);
    const slope = variance === 0 ? 0 : covariance / variance;
    const intercept = meanY - slope * meanX;

    return cities.map((c) => ({
      name: c.city,
      lon: c.lon,
      lat: c.lat,
      value: c.y - (slope * c.x + intercept),
    }));
  }

  private scatterPoints(getX: (agg: AggregationResult) => number | null): ScatterPoint[] {
    return Object.entries(this.coffeeService.aggregates()).flatMap(([city, agg]) => {
      const x = getX(agg);
      const y = agg.aggregated_value;
      if (x == null || y == null) {
        return [];
      }
      return [
        {
          x,
          y,
          name: city,
          itemStyle: { color: this.isReliable(agg) ? RELIABLE_COLOR : DIMMED_COLOR },
        },
      ];
    });
  }

  ngOnInit() {
    this.coffeeService.ensureAggregatesLoaded();
    this.loadGermanyGeoJson();
  }

  private async loadGermanyGeoJson() {
    try {
      const response = await fetch(GERMANY_GEOJSON_URL);
      this.germanyGeoJson.set(await response.json());
    } catch (err) {
      console.error('Error loading Germany GeoJSON', err);
    }
  }
}
