import { AfterViewInit, Component, signal } from '@angular/core';
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
  map:any;
  coffeeShops = signal<CoffeeShop[]>([]);
  markers: L.Marker[] = [];

  ngAfterViewInit() {
    this.getCoordinates('Bochum').then(({ lat, lon }) => {
      this.initMap(lat, lon);
      this.getCoffeeShops();
    });
  }

  initMap(lat: number, lon: number) {
    this.map = L.map('map').setView([lat, lon], 13);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(this.map);

    // Leaflet muss seine Container-Größe neu vermessen, sobald das Flex-Layout steht
    setTimeout(() => this.map.invalidateSize(), 0);
  }

  async getCoordinates(city: string) {
  const response = await fetch(
    `https://nominatim.openstreetmap.org/search?city=${city}&format=json`
  );
  const data = await response.json();
  
  const lat = data[0].lat;
  const lon = data[0].lon;

  console.log(`Latitude: ${lat}, Longitude: ${lon}`);
  return { lat, lon };
}

  openUrl(url: string | null) {
    if (url) {
      window.open(url, '_blank', 'noopener');
    }
  }

  async getCoffeeShops() {
    const response = await fetch('http://localhost:8080/coffe_shops?city=Bochum%2C%20Germany');
    var coffeeShops = await response.json();
    this.coffeeShops.set(coffeeShops);
    for (const shop of coffeeShops) {
      const marker = L.marker(shop.coordinates).addTo(this.map);
      marker.bindPopup(`<b>${shop.name}</b><br><a href="${shop.website.url}" target="_blank">${shop.website.url}</a>`)
      this.markers.push(marker);
    }
  }

  selectShop(index: number) {
    const marker = this.markers[index];
    if (marker) {
      this.map.setView(marker.getLatLng(), 16);
      marker.openPopup();
    }
  }
}
