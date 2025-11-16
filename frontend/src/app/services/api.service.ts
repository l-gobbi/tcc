import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

// Interface para garantir a tipagem dos dados enviados
interface ComparisonRequest {
  text1: string;
  text2: string;
}

// Interface para tipar o JSON de resposta do seu backend
interface ComparisonResponse {
  'bert_similarity (Semântica)': number;
  'tfidf_similarity (Keywords)': number;
  'jaccard_similarity (Vocabulário)': number;
  'levenshtein_similarity (Estrutura/Typos)': number;
}

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  // A URL base do seu backend, como combinamos
  private readonly apiUrl = 'http://localhost:8080';

  constructor(private http: HttpClient) { }

  /**
   * Envia os dois textos para o endpoint /compare do FastAPI.
   * @param data Objeto contendo text1 e text2.
   */
  compareTexts(data: ComparisonRequest): Observable<ComparisonResponse> {
    const url = `${this.apiUrl}/compare`;
    // Faz a requisição POST com a tipagem da resposta
    return this.http.post<ComparisonResponse>(url, data);
  }
}