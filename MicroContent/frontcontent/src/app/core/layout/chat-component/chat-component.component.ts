import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

@Component({
  selector: 'app-chat',
  templateUrl: './chat-component.component.html',
  styleUrls: ['./chat-component.component.css'],
  imports: [CommonModule, FormsModule],
  standalone: true, 
})
export class ChatComponent {
  messages: Message[] = [];
  userInput: string = '';
  isOpen = true;

  constructor(private http: HttpClient) {}

  toggleChat() {
    this.isOpen = !this.isOpen;
  }

  sendMessage() {
    if (!this.userInput.trim()) return;

    const question = this.userInput.trim();
    this.messages.push({ role: 'user', content: question });
    this.userInput = '';

    this.http.post<any>('http://localhost:8083/api/v1/questions', { question })
      .subscribe({
        next: () => this.loadHistory(),
        error: (err) => {
          this.messages.push({ role: 'assistant', content: 'Error al contactar con el asistente.' });
        }
      });
  }

  loadHistory() {
    this.http.get<{ history: Message[] }>('http://localhost:8083/api/v1/memory')
      .subscribe({
        next: (res) => this.messages = [...res.history],
        error: () => this.messages.push({ role: 'assistant', content: 'No se pudo recuperar el historial.' })
      });
  }

  ngOnInit(): void {
    this.loadHistory();
    setInterval(() => this.loadHistory(), 3000); // ⏱ cada 3 segundos
  }
  
} 