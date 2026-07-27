import { AfterViewInit, Component, computed, effect, inject, signal } from '@angular/core';
import {MatCardModule} from '@angular/material/card';
import * as L from 'leaflet';
import { CoffeeShop } from '../models/coffee-shop.model';
import { CoffeeService } from '../coffee.service';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import {
  SankeyChart,
  SankeyLink,
  SankeyNode,
} from '../diagrams/sankey-chart/sankey-chart';
import { buildPriceFunnel } from '../diagrams/sankey-chart/price-funnel';

@Component({
  selector: 'app-map',
  standalone: true,
  imports: [MatCardModule, MatExpansionModule, MatSlideToggleModule, SankeyChart],
  templateUrl: './map.component.html',
  styleUrl: './map.component.css'
})
export class MapComponent implements AfterViewInit {
  private readonly coffeeService = inject(CoffeeService);

  city = this.coffeeService.city;
  coffeeShops = this.coffeeService.coffeeShops;

  map:any;
  selectedIndex = signal<number | null>(null);
  markers: L.Marker[] = [];
  private mapReady = signal(false);

  readonly showWithoutPrices = signal(true);

  private readonly defaultIcon = L.icon({
    iconUrl: 'media/marker-icon.png',
    iconRetinaUrl: 'media/marker-icon-2x.png',
    shadowUrl: 'media/marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41],
  });
  private readonly grayIcon = L.icon({
    iconUrl: 'media/marker-icon.png',
    iconRetinaUrl: 'media/marker-icon-2x.png',
    shadowUrl: 'media/marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41],
    className: 'marker-gray',
  });

  shopsWithMenu = computed(() =>
    this.coffeeShops()
      .map((shop, index) => ({ shop, index }))
      .filter(({ shop }) => !!shop.menu.items?.length),
  );
  shopsWithoutMenu = computed(() =>
    this.coffeeShops()
      .map((shop, index) => ({ shop, index }))
      .filter(({ shop }) => !shop.menu.items?.length),
  );

  readonly cheapestIndex = computed(() => {
    let best: { index: number; price: number } | null = null;
    for (const { shop, index } of this.shopsWithMenu()) {
      const price = this.cappuccinoPrice(shop);
      if (price !== null && (best === null || price < best.price)) {
        best = { index, price };
      }
    }
    return best?.index ?? null;
  });

  private readonly cityAggregate = computed(() => {
    const key = this.city().split(',')[0].trim();
    return this.coffeeService.aggregates()[key] ?? null;
  });

  private readonly funnel = computed(() => {
    const agg = this.cityAggregate();
    if (!agg) {
      return { nodes: [], links: [] };
    }
    return buildPriceFunnel({
      totalShops: agg.total_shops,
      shopsWithWebsite: agg.shops_with_website,
      shopsWithPrices: agg.sample_size,
    });
  });

  readonly sankeyNodes = computed<SankeyNode[]>(() => this.funnel().nodes);
  readonly sankeyLinks = computed<SankeyLink[]>(() => this.funnel().links);

  readonly hasAggregate = computed(() => this.cityAggregate() !== null);

  constructor() {
    effect(() => {
      const shops = this.coffeeShops();
      if (this.mapReady()) {
        this.renderMarkers(shops);
      }
    });
  }

  ngAfterViewInit() {
    this.initMap();
    this.mapReady.set(true);
    this.coffeeService.ensureLoaded();
    this.coffeeService.ensureAggregatesLoaded();
  }

  initMap() {
    this.map = L.map('map').setView([51.4818, 7.2162], 13);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(this.map);

    setTimeout(() => this.map.invalidateSize(), 0);
  }

  openUrl(url: string | null) {
    if (url) {
      window.open(url, '_blank', 'noopener');
    }
  }

  private renderMarkers(coffeeShops: CoffeeShop[]) {
    for (const marker of this.markers) {
      marker?.remove();
    }
    this.markers = [];
    this.selectedIndex.set(null);

    const showWithoutPrices = this.showWithoutPrices();

    coffeeShops.forEach((shop: CoffeeShop, index: number) => {
      const hasMenu = !!shop.menu.items?.length;
      if (!hasMenu && !showWithoutPrices) {
        return; // leave a hole at this index so markers stay index-aligned
      }
      const marker = L.marker(shop.coordinates, {
        icon: hasMenu ? this.defaultIcon : this.grayIcon,
      }).addTo(this.map);
      marker.bindPopup(`<b>${shop.name}</b><br>${this.buildPopupContent(shop)}`);
      marker.on('popupopen', () => {
        this.selectedIndex.set(index);
        this.scrollCardIntoView(index);
      });
      marker.on('popupclose', () => {
        if (this.selectedIndex() === index) {
          this.selectedIndex.set(null);
        }
      });
      this.markers[index] = marker;
    });

    if (coffeeShops.length) {
      this.map.fitBounds(L.latLngBounds(coffeeShops.map((shop) => shop.coordinates)), {
        padding: [30, 30],
      });
    }
  }

  selectShop(index: number) {
    const marker = this.markers[index];
    if (marker) {
      this.selectedIndex.set(index);
      this.map.setView(marker.getLatLng(), 16);
      marker.openPopup();
    }
  }

  cappuccinoPrice(shop: CoffeeShop): number | null {
    const prices = (shop.menu.items ?? [])
      .filter((item) => item.name.toLowerCase().includes('cappuccino'))
      .map((item) => item.price);
    if (!prices.length) {
      return null;
    }
    return prices.reduce((sum, price) => sum + price, 0) / prices.length;
  }

  private buildPopupContent(shop: CoffeeShop): string {
    const items = shop.menu.items ?? [];

    if (items.length) {
      const price = this.cappuccinoPrice(shop);

      const parts: string[] = [];
      if (price !== null) {
        parts.push(`Extracted Cappuccino Price: ${price.toFixed(2)} €`);
      }
      if (shop.menu.menu_url) {
        parts.push(`<a href="${shop.menu.menu_url}" target="_blank">See Menu</a>`);
      }
      return parts.join('<br>');
    }

    if (shop.website.accessible && shop.website.url) {
      return `Price extraction not possible, check <a href="${shop.website.url}" target="_blank">website</a>`;
    }

    return 'Price extraction not possible, no website found';
  }

  private scrollCardIntoView(index: number) {
    const card = document.getElementById(`shop-card-${index}`);
    card?.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }
}
