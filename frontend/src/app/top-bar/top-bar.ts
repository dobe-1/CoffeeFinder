import { Component, OnInit, inject, signal } from '@angular/core';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { NavigationEnd, Router, RouterLink, RouterLinkActive } from '@angular/router';
import { filter } from 'rxjs/operators';
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
  private readonly router = inject(Router);

  cities: string[] = [];
  selectedCity = this.coffeeService.city();
  // Views that operate on all cities at once, so the city picker doesn't apply.
  hideCitySelect = signal(this.isCityAgnosticUrl(this.router.url));

  ngOnInit() {
    this.loadCities();
    this.router.events
      .pipe(filter((event) => event instanceof NavigationEnd))
      .subscribe((event) =>
        this.hideCitySelect.set(this.isCityAgnosticUrl(event.urlAfterRedirects)),
      );
  }

  private isCityAgnosticUrl(url: string): boolean {
    return url === '/' || url.startsWith('/home') || url.startsWith('/germany-overview');
  }

  async loadCities() {
    try {
      const response = await fetch('data/aggregates.json');
      const aggregates: Record<string, unknown> = await response.json();
      const cities = Object.keys(aggregates)
        .map((city) => `${city}, Germany`)
        .sort((a, b) => a.localeCompare(b, 'de'));
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
