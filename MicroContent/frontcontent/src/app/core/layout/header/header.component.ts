
import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { CategoriasComponent } from '../categorias/categorias.component';
import { PortadaComponent } from '../../../feature/portada/portada.component';
@Component({
  selector: 'app-header',
  standalone: true, // importante si estás usando componentes standalone
  imports: [CommonModule, RouterModule, CategoriasComponent], // aquí se importa todo lo necesario
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.css']
})
export class HeaderComponent {

}
