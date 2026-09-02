import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-articulo-detalle',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './articulo-detalle.component.html',
  styleUrls: ['./articulo-detalle.component.css']
})
export class ArticuloDetalleComponent implements OnInit {
  articulo: any = null;

  constructor(private route: ActivatedRoute, private http: HttpClient) {}

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id');
    this.http.get<any>(`http://localhost:8083/articulos/${id}`).subscribe({
      next: data => {
        this.articulo = {
          ...data,
          author: JSON.parse(data.author),
          multimedias: data.multimedias
            .map((m: string) => {
              try {
                return JSON.parse(m);
              } catch {
                return null;
              }
            })
            .filter((m: any) => m?.type === 'IMAGE' && m.url?.startsWith('http'))
        };
      },
      error: err => console.error('Error al cargar el artículo:', err)
    });
  }
  
}
