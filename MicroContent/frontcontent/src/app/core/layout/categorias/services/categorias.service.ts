import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class CategoriaService {
  private apiUrl = 'http://localhost:8083/categorias';

  constructor(private http: HttpClient) {}

  getCategorias(): Observable<string[]> {
    return this.http.get<string[]>(this.apiUrl);
  }
}
