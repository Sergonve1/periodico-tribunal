import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, NavigationEnd, RouterModule } from '@angular/router';
import { filter } from 'rxjs/operators';

@Component({
  selector: 'app-portada',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './portada.component.html',
  styleUrls: ['./portada.component.css']
})
export class PortadaComponent implements OnInit {
  articulos: any[] = [];
  categoria: string | null = null;

  constructor(
    private http: HttpClient,
    private route: ActivatedRoute,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.router.events
      .pipe(filter(event => event instanceof NavigationEnd))
      .subscribe(() => {
        this.categoria = this.route.snapshot.paramMap.get('nombre');
        this.cargarArticulos();
      });

    this.categoria = this.route.snapshot.paramMap.get('nombre');
    this.cargarArticulos();
  }

  cargarArticulos(): void {
    const url = this.categoria
      ? `http://localhost:8083/articulos/categoria/${this.categoria}`
      : 'http://localhost:8083/articulos/ultimos';

    this.http.get<any[]>(url).subscribe({
      next: data => {
        this.articulos = data
          .sort((a, b) => new Date(b.publication).getTime() - new Date(a.publication).getTime())
          .slice(0, 30);
      },
      error: err => console.error('Error al cargar artículos:', err)
    });
  }
}
