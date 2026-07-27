import { Component } from '@angular/core';
import Prism from 'prismjs';
import 'prismjs/components/prism-json';
import { COFFEE_SHOP_EXAMPLE } from './coffee-shop-example';

@Component({
  selector: 'app-home',
  imports: [],
  templateUrl: './home.html',
  styleUrl: './home.css',
})
export class Home {
  readonly coffeeShopExample = Prism.highlight(
    COFFEE_SHOP_EXAMPLE,
    Prism.languages['json'],
    'json',
  );
}
