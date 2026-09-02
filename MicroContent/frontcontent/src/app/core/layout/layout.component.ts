import { Component } from '@angular/core';
import { CommonModule } from '@angular/common'; // <-- IMPORTANTE
import { FooterComponent } from "./footer/footer.component";
import { HeaderComponent } from './header/header.component';
import { CategoriasComponent } from './categorias/categorias.component';
import { RouterOutlet } from '@angular/router';
import { ChatComponent } from './chat-component/chat-component.component'; 

@Component({
  selector: 'app-layout',
  standalone: true,
  imports: [CommonModule, FooterComponent, HeaderComponent,RouterOutlet, ChatComponent],
  templateUrl: './layout.component.html',
  styleUrls: ['./layout.component.css'] // <-- corregido (antes decía styleUrl)
})
export class LayoutComponent { }
