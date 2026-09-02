import { Routes } from '@angular/router';
import { LayoutComponent } from './core/layout/layout.component';
import { PortadaComponent } from './feature/portada/portada.component';
import { ArticuloDetalleComponent } from './feature/articulo-detalle/articulo-detalle.component'; // 👈 nuevo import

export const routes: Routes = [
  {
    path: '',
    component: LayoutComponent,
    children: [
      {
        path: '',
        component: PortadaComponent
      },
      {
        path: 'categoria/:nombre',
        component: PortadaComponent
      },
      {
        path: 'articulo/:id',
        component: ArticuloDetalleComponent // 👈 nueva ruta para detalle
      }
    ]
  }
];
