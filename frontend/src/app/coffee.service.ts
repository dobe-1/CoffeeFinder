import { Injectable, signal } from '@angular/core';
import { CoffeeShop } from './models/coffee-shop.model';

const API_BASE = 'http://localhost:8080';

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
  // Shared selected city + loaded coffee shops, consumed by both the map and table view.
  readonly city = signal('Bochum, Germany');
  readonly coffeeShops = signal<CoffeeShop[]>([]);
  readonly loading = signal(false);
  // website urls of shops whose menu extraction is currently running
  readonly extracting = signal<Set<string>>(new Set());

  readonly aggregates = signal<Record<string, AggregationResult>>({});

  private loadedCity: string | null = null;
  private aggregatesLoaded = false;

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
      const response = await fetch(`${API_BASE}/coffe_shops?city=${encodeURIComponent(city)}`);
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

  // Load once if we haven't loaded the current city yet (used when a view mounts).
  ensureLoaded() {
    if (this.loadedCity !== this.city()) {
      this.loadCoffeeShops(this.city());
    }
  }

  isExtracting(websiteUrl: string | null): boolean {
    return websiteUrl !== null && this.extracting().has(websiteUrl);
  }

  // Trigger menu-url extraction for a single shop (identified by its website url)
  // and replace it in the loaded list once the backend responds.
  async extractMenu(shop: CoffeeShop) {
    const websiteUrl = shop.website.url;
    if (!websiteUrl || this.isExtracting(websiteUrl)) {
      return;
    }

    this.extracting.update((set) => new Set(set).add(websiteUrl));
    try {
      const params = new URLSearchParams({
        city: this.city(),
        website_url: websiteUrl,
      });
      const response = await fetch(`${API_BASE}/coffe_shops/extract_menu?${params}`, {
        method: 'POST',
      });
      if (!response.ok) {
        throw new Error(`Extraction failed (${response.status})`);
      }
      const updated: CoffeeShop = await response.json();
      this.coffeeShops.update((shops) =>
        shops.map((s) => (s.website.url === websiteUrl ? updated : s)),
      );
    } catch (err) {
      console.error('Error extracting menu', websiteUrl, err);
    } finally {
      this.extracting.update((set) => {
        const next = new Set(set);
        next.delete(websiteUrl);
        return next;
      });
    }
  }

  async loadAggregates(): Promise<Record<string, AggregationResult>> {
    try {
      const response = await fetch(`${API_BASE}/aggregates`);
      const aggregates: Record<string, AggregationResult> = await response.json();
      this.aggregates.set(aggregates);
      return aggregates;
    } catch (err) {
      console.error('Error loading aggregates', err);
      return {};
    }
  }

  // Load aggregates once (used when a view that visualises them mounts).
  ensureAggregatesLoaded() {
    if (!this.aggregatesLoaded) {
      this.aggregatesLoaded = true;
      this.loadAggregates();
    }
  }
}
