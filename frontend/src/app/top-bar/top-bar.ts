import { Component, OnInit, output } from '@angular/core';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';

@Component({
  selector: 'app-top-bar',
  imports: [MatToolbarModule, MatFormFieldModule, MatSelectModule],
  templateUrl: './top-bar.html',
  styleUrl: './top-bar.css',
})
export class TopBar implements OnInit {
  cityChange = output<string>();

  cities: string[] = [];
  selectedCity = 'Bochum, Germany';

  ngOnInit() {
    this.loadCities();
  }

  async loadCities() {
    try {
      const response = await fetch('http://localhost:8080/cities');
      const cities: string[] = await response.json();
      this.cities = cities;
      if (cities.length && !cities.includes(this.selectedCity)) {
        this.selectedCity = cities[0];
        this.cityChange.emit(this.selectedCity);
      }
    } catch (err) {
      console.error('Fehler beim Laden der Städte', err);
    }
  }

  onCityChange(city: string) {
    this.selectedCity = city;
    this.cityChange.emit(city);
  }
}
