import { Component, signal } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { MapComponent } from './map/map.component';
import { TopBar } from "./top-bar/top-bar";

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, MapComponent, TopBar],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
  protected readonly title = signal('CoffeeFinder');
  protected readonly city = signal('Bochum, Germany');
}
