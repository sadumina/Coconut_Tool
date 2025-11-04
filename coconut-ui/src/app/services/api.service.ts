import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ApiService {

  private BASE_URL = "http://localhost:8000";

  constructor(private http: HttpClient) {}

  getProducts(): Observable<any> {
    return this.http.get(`${this.BASE_URL}/products`);
  }

  getMarkets(product: string): Observable<any> {
    return this.http.get(`${this.BASE_URL}/markets-by-product?product=${product}`);
  }

  getPrices(product: string, market: string): Observable<any> {
    return this.http.get(`${this.BASE_URL}/prices-filtered?product=${product}&market=${market}`);
  }

  getAnalytics(product: string, market: string): Observable<any> {
    return this.http.get(`${this.BASE_URL}/analytics?product=${product}&market=${market}`);
  }

  uploadPDF(file: FormData): Observable<any> {
    return this.http.post(`${this.BASE_URL}/upload-pdf`, file);
  }
}
