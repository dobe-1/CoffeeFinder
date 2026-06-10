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
}
