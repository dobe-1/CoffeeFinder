import { Component, OnInit, computed, inject } from '@angular/core';
import { MatTableModule } from '@angular/material/table';
import { MatButtonModule } from '@angular/material/button';
import { CoffeeService } from '../coffee.service';
import { CoffeeShop } from '../models/coffee-shop.model';

@Component({
  selector: 'app-table',
  standalone: true,
  imports: [MatTableModule, MatButtonModule],
  templateUrl: './table.component.html',
  styleUrl: './table.component.css',
})
export class TableComponent implements OnInit {
  private readonly coffeeService = inject(CoffeeService);

  coffeeShops = this.coffeeService.coffeeShops;
  loading = this.coffeeService.loading;

  // Rank: website + menu first, then website only, then the rest (no website).
  private rank(shop: CoffeeShop): number {
    if (shop.website.url && shop.menu.menu_url) {
      return 0;
    }
    if (shop.website.url) {
      return 1;
    }
    return 2;
  }

  sortedShops = computed(() =>
    [...this.coffeeShops()].sort((a, b) => this.rank(a) - this.rank(b)),
  );

  displayedColumns = ['name', 'website', 'menu'];

  isInaccessible(shop: CoffeeShop): boolean {
    return shop.website.accessible === false;
  }

  ngOnInit() {
    this.coffeeService.ensureLoaded();
  }

  openUrl(url: string | null) {
    if (url) {
      window.open(url, '_blank', 'noopener');
    }
  }
}
