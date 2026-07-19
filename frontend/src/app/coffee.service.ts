import { Injectable, signal } from '@angular/core';
import { CoffeeShop } from './models/coffee-shop.model';

const DATA_BASE = 'data';

export interface AggregationResult {
  coordinates: [number, number];
  sample_size: number;
  aggregated_value: number | null;
  total_shops: number;
  shops_with_website: number;
  shops_with_possible_menu: number;
  disposable_income_per_person: number | null;
  overnight_stays_per_inhabitant: number | null;
}

@Injectable({ providedIn: 'root' })
export class CoffeeService {
  readonly city = signal('Bochum, Germany');
  readonly coffeeShops = signal<CoffeeShop[]>([]);
  readonly loading = signal(false);

  readonly aggregates = signal<Record<string, AggregationResult>>({});

  private loadedCity: string | null = null;
  private aggregatesLoaded = false;

  private cityToFile(city: string): string {
    return `${DATA_BASE}/${encodeURIComponent(city.replaceAll(', ', '_'))}.json`;
  }

  setCity(city: string) {
    if (city === this.city()) {
      return;
    }
    this.city.set(city);
    this.loadCoffeeShops(city);
  }

  async loadCoffeeShops(city: string = this.city()) {
    this.loading.set(true);
    try {
      const response = await fetch(this.cityToFile(city));
      if (!response.ok) {
        throw new Error(`Failed to load coffee shops (${response.status})`);
      }
      const coffeeShops: CoffeeShop[] = await response.json();
      this.coffeeShops.set(coffeeShops);
      this.loadedCity = city;
    } catch (err) {
      console.error('Error loading coffee shops', city, err);
      this.coffeeShops.set([]);
    } finally {
      this.loading.set(false);
    }
  }

  ensureLoaded() {
    if (this.loadedCity !== this.city()) {
      this.loadCoffeeShops(this.city());
    }
  }

  async loadAggregates(): Promise<Record<string, AggregationResult>> {
    try {
      const response = await fetch(`${DATA_BASE}/aggregates.json`);
      if (!response.ok) {
        throw new Error(`Failed to load aggregates (${response.status})`);
      }
      const aggregates: Record<string, AggregationResult> = await response.json();
      this.aggregates.set(aggregates);
      return aggregates;
    } catch (err) {
      console.error('Error loading aggregates', err);
      return {};
    }
  }

  ensureAggregatesLoaded() {
    if (!this.aggregatesLoaded) {
      this.aggregatesLoaded = true;
      this.loadAggregates();
    }
  }
}
