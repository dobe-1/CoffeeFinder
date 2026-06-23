import { Routes } from '@angular/router';
import { MapComponent } from './map/map.component';
import { TableComponent } from './table/table.component';

export const routes: Routes = [
  { path: 'map', component: MapComponent },
  { path: 'table', component: TableComponent },
  { path: '', redirectTo: 'map', pathMatch: 'full' },
];
