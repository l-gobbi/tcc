import { Component, OnInit, signal } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms'; // 👈 Reactive Forms
import { JsonPipe, NgIf } from '@angular/common';
import { ApiService } from './services/api.service'; // 👈 Nosso serviço

// Tipagem da resposta para uso no componente
interface ComparisonResponse {
  'bert_similarity (Semântica)': number;
  'tfidf_similarity (Keywords)': number;
  'jaccard_similarity (Vocabulário)': number;
  'levenshtein_similarity (Estrutura/Typos)': number;
}

@Component({
  selector: 'app-root',
  standalone: true, // Componente Standalone
  imports: [RouterOutlet, ReactiveFormsModule, JsonPipe, NgIf], // Importa ReactiveFormsModule e comuns
  templateUrl: './app.html',
  styleUrl: './app.scss'
})
export class App implements OnInit {
  protected readonly title = signal('frontend');
  
  // 1. Definição do FormGroup para os dois campos
  comparisonForm = new FormGroup({
    text1: new FormControl('', Validators.required),
    text2: new FormControl('', Validators.required)
  });
  
  // Variáveis de estado usando signals (melhor prática para zoneless)
  loading = signal(false);
  result = signal<ComparisonResponse | null>(null);
  error = signal<string | null>(null);

  // Injeção do serviço
  constructor(private apiService: ApiService) { }

  ngOnInit(): void {
    // Aqui você pode adicionar lógica de inicialização, se necessário
  }

  // 2. Método de Envio do Formulário
  onSubmit() {
    if (this.comparisonForm.valid) {
      this.loading.set(true);
      this.error.set(null);
      this.result.set(null);

      // Pega os valores do formulário
      const payload = this.comparisonForm.value;

      // Chama o serviço para enviar os dados
      this.apiService.compareTexts(payload as any).subscribe({
        next: (response) => {
          this.result.set(response);
          this.loading.set(false);
        },
        error: (err) => {
          console.error('Erro ao chamar API:', err);
          // Mensagem de erro útil para o desenvolvedor/usuário
          this.error.set(`Erro de comunicação com o backend. Verifique o CORS (http://localhost:4200 -> http://localhost:8080) e se o servidor está rodando. Mensagem detalhada no console.`);
          this.loading.set(false);
        }
      });
    } else {
      this.error.set('Por favor, preencha ambos os campos de texto.');
    }
  }
}