import { Component, output } from '@angular/core';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';

@Component({
  selector: 'app-top-bar',
  imports: [MatToolbarModule, MatFormFieldModule, MatSelectModule],
  templateUrl: './top-bar.html',
  styleUrl: './top-bar.css',
})
export class TopBar {
  cityChange = output<string>();

  cities = ['Bochum, Germany'];
  selectedCity = this.cities[0];

  onCityChange(city: string) {
    this.selectedCity = city;
    this.cityChange.emit(city);
  }
}
