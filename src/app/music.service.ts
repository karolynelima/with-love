import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface SearchResult {
  album: string;
  musica: string;
  estrofe: string;
}

@Injectable({
  providedIn: 'root'
})
export class MusicService {
  private apiUrl = 'http://127.0.0.1:8000'; // URL da sua API Python

  constructor(private http: HttpClient) { }

  buscarMusicas(frase: string): Observable<SearchResult[]> {
    return this.http.post<SearchResult[]>(`${this.apiUrl}/buscar`, { frase });
  }
}
