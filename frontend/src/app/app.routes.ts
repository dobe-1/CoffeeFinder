import { Routes } from '@angular/router';
import { Home } from './home/home';
import { MapComponent } from './map/map.component';
import { Overview } from './overview/overview';

export const routes: Routes = [
  { path: 'home', component: Home },
  { path: 'map', component: MapComponent },
  { path: 'germany-overview', component: Overview },
  { path: '', redirectTo: 'home', pathMatch: 'full' },
];
