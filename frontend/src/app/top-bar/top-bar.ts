import { Component, OnInit, inject } from '@angular/core';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { RouterLink, RouterLinkActive } from '@angular/router';
import { CoffeeService } from '../coffee.service';

@Component({
  selector: 'app-top-bar',
  imports: [
    MatToolbarModule,
    MatFormFieldModule,
    MatSelectModule,
    MatButtonModule,
    RouterLink,
    RouterLinkActive,
  ],
  templateUrl: './top-bar.html',
  styleUrl: './top-bar.css',
})
export class TopBar implements OnInit {
  private readonly coffeeService = inject(CoffeeService);

  cities: string[] = [];
  selectedCity = this.coffeeService.city();

  ngOnInit() {
    this.loadCities();
  }

  async loadCities() {
    try {
      const response = await fetch('http://localhost:8080/cities');
      const cities: string[] = await response.json();
      this.cities = cities;
      if (cities.length && !cities.includes(this.selectedCity)) {
        this.onCityChange(cities[0]);
      }
    } catch (err) {
      console.error('Fehler beim Laden der Städte', err);
    }
  }

  onCityChange(city: string) {
    this.selectedCity = city;
    this.coffeeService.setCity(city);
  }
}
