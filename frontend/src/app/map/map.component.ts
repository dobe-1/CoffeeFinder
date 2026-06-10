import { AfterViewInit, Component } from '@angular/core';
import * as L from 'leaflet';

@Component({
  selector: 'app-map',
  standalone: true,
  imports: [],
  templateUrl: './map.component.html',
  styleUrl: './map.component.css'
})
export class MapComponent implements AfterViewInit {
  map:any;

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

  async getCoffeeShops() {
    const response = await fetch('http://localhost:8080/coffe_shops?city=Bochum%2C%20Germany');
    var coffeeShops = await response.json();
    for (const shop of coffeeShops) {
      const marker = L.marker(shop.coordinates).addTo(this.map);
      marker.bindPopup(`<b>${shop.name}</b><br><a href="${shop.website.url}" target="_blank">${shop.website.url}</a>`)
    }
  }
}
