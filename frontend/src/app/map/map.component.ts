import { AfterViewInit, Component, effect, input, signal } from '@angular/core';
import {MatCardModule} from '@angular/material/card';
import * as L from 'leaflet';
import { CoffeeShop } from '../models/coffee-shop.model';

@Component({
  selector: 'app-map',
  standalone: true,
  imports: [MatCardModule],
  templateUrl: './map.component.html',
  styleUrl: './map.component.css'
})
export class MapComponent implements AfterViewInit {
  city = input('Bochum, Germany');

  map:any;
  coffeeShops = signal<CoffeeShop[]>([]);
  selectedIndex = signal<number | null>(null);
  markers: L.Marker[] = [];
  private mapReady = signal(false);

  constructor() {
    effect(() => {
      const city = this.city();
      if (this.mapReady()) {
        this.loadCity(city);
      }
    });
  }

  ngAfterViewInit() {
    this.initMap();
    this.mapReady.set(true);
  }

  initMap() {
    this.map = L.map('map').setView([51.4818, 7.2162], 13);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(this.map);

    setTimeout(() => this.map.invalidateSize(), 0);
  }

  async loadCity(city: string) {
    try {
      const coords = await this.getCoordinates(city);
      if (coords) {
        this.map.setView([coords.lat, coords.lon], 13);
      }
      await this.getCoffeeShops(city);
    } catch (err) {
      console.error('Fehler beim Laden der Stadt', city, err);
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

  async getCoffeeShops(city: string) {
    const response = await fetch(`http://localhost:8080/coffe_shops?city=${encodeURIComponent(city)}`);
    var coffeeShops = await response.json();
    this.coffeeShops.set(coffeeShops);

    for (const marker of this.markers) {
      marker.remove();
    }
    this.markers = [];

    this.selectedIndex.set(null);

    coffeeShops.forEach((shop: CoffeeShop, index: number) => {
      const marker = L.marker(shop.coordinates).addTo(this.map);
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
