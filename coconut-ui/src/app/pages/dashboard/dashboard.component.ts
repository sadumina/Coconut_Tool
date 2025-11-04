import { Component } from '@angular/core';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
})
export class DashboardComponent {

  products: string[] = [];
  markets: string[] = [];
  prices: any[] = [];
  stats: any;

  selectedProduct = "";
  selectedMarket = "";

  constructor(private api: ApiService) {}

  ngOnInit() {
    this.api.getProducts().subscribe(data => {
      this.products = data;
    })
  }

  onProductChange() {
    this.api.getMarkets(this.selectedProduct).subscribe(data => {
      this.markets = data;
    });
  }

  onMarketChange() {
    this.api.getPrices(this.selectedProduct, this.selectedMarket).subscribe(data => {
      this.prices = data;
    });

    this.api.getAnalytics(this.selectedProduct, this.selectedMarket).subscribe(data => {
      this.stats = data;
    });
  }
}
