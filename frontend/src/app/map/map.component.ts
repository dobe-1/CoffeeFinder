import { AfterViewInit, Component, computed, effect, inject, signal } from '@angular/core';
import {MatCardModule} from '@angular/material/card';
import * as L from 'leaflet';
import { CoffeeShop } from '../models/coffee-shop.model';
import { CoffeeService } from '../coffee.service';

@Component({
  selector: 'app-map',
  standalone: true,
  imports: [MatCardModule],
  templateUrl: './map.component.html',
  styleUrl: './map.component.css'
})
export class MapComponent implements AfterViewInit {
  private readonly coffeeService = inject(CoffeeService);

  city = this.coffeeService.city;
  coffeeShops = this.coffeeService.coffeeShops;

  map:any;
  selectedIndex = signal<number | null>(null);
  markers: L.Marker[] = [];
  private mapReady = signal(false);
  private lastCenteredCity: string | null = null;

  private readonly defaultIcon = L.icon({
    iconUrl: '/media/marker-icon.png',
    iconRetinaUrl: '/media/marker-icon-2x.png',
    shadowUrl: '/media/marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41],
  });
  private readonly grayIcon = L.icon({
    iconUrl: '/media/marker-icon.png',
    iconRetinaUrl: '/media/marker-icon-2x.png',
    shadowUrl: '/media/marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41],
    className: 'marker-gray',
  });

  shopsWithWebsite = computed(() =>
    this.coffeeShops()
      .map((shop, index) => ({ shop, index }))
      .filter(({ shop }) => !!shop.website.url),
  );
  shopsWithoutWebsite = computed(() =>
    this.coffeeShops()
      .map((shop, index) => ({ shop, index }))
      .filter(({ shop }) => !shop.website.url),
  );

  constructor() {
    // Re-center when the city changes.
    effect(() => {
      const city = this.city();
      if (this.mapReady() && city !== this.lastCenteredCity) {
        this.lastCenteredCity = city;
        this.centerOnCity(city);
      }
    });

    // Re-draw markers whenever the shared coffee shop list changes.
    effect(() => {
      const shops = this.coffeeShops();
      if (this.mapReady()) {
        this.renderMarkers(shops);
      }
    });
  }

  ngAfterViewInit() {
    this.initMap();
    this.mapReady.set(true);
    this.coffeeService.ensureLoaded();
  }

  initMap() {
    this.map = L.map('map').setView([51.4818, 7.2162], 13);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(this.map);

    setTimeout(() => this.map.invalidateSize(), 0);
  }

  async centerOnCity(city: string) {
    try {
      const coords = await this.getCoordinates(city);
      if (coords) {
        this.map.setView([coords.lat, coords.lon], 13);
      }
    } catch (err) {
      console.error('Fehler beim Zentrieren auf Stadt', city, err);
    }
  }

  async getCoordinates(city: string) {
    const response = await fetch(
      `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(city)}&format=json`
    );
    const data = await response.json();

    if (!data.length) {
      console.warn('Keine Koordinaten gefunden für', city);
      return null;
    }

    return { lat: Number(data[0].lat), lon: Number(data[0].lon) };
  }

  openUrl(url: string | null) {
    if (url) {
      window.open(url, '_blank', 'noopener');
    }
  }

  private renderMarkers(coffeeShops: CoffeeShop[]) {
    for (const marker of this.markers) {
      marker.remove();
    }
    this.markers = [];
    this.selectedIndex.set(null);

    coffeeShops.forEach((shop: CoffeeShop, index: number) => {
      const marker = L.marker(shop.coordinates, {
        icon: shop.website.url ? this.defaultIcon : this.grayIcon,
      }).addTo(this.map);
      marker.bindPopup(`<b>${shop.name}</b><br><a href="${shop.website.url}" target="_blank">${shop.website.url}</a>`);
      marker.on('popupopen', () => {
        this.selectedIndex.set(index);
        this.scrollCardIntoView(index);
      });
      marker.on('popupclose', () => {
        if (this.selectedIndex() === index) {
          this.selectedIndex.set(null);
        }
      });
      this.markers.push(marker);
    });
  }

  selectShop(index: number) {
    const marker = this.markers[index];
    if (marker) {
      this.selectedIndex.set(index);
      this.map.setView(marker.getLatLng(), 16);
      marker.openPopup();
    }
  }

  private scrollCardIntoView(index: number) {
    const card = document.getElementById(`shop-card-${index}`);
    card?.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }
}
