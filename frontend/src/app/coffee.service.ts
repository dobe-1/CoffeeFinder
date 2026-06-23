import { Injectable, signal } from '@angular/core';
import { CoffeeShop } from './models/coffee-shop.model';

const API_BASE = 'http://localhost:8080';

@Injectable({ providedIn: 'root' })
export class CoffeeService {
  // Shared selected city + loaded coffee shops, consumed by both the map and table view.
  readonly city = signal('Bochum, Germany');
  readonly coffeeShops = signal<CoffeeShop[]>([]);
  readonly loading = signal(false);

  private loadedCity: string | null = null;

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
      console.error('Fehler beim Laden der Cafés', city, err);
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
}
