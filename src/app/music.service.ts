import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface SearchResult {
  album: string;
  musica: string;
  estrofe: string;
  referencia_abnt: string;
}

@Injectable({
  providedIn: 'root'
})
export class MusicService {

  private apiUrl = '/api';

  constructor(private http: HttpClient) { }

  buscarMusicas(frase: string): Observable<SearchResult[]> {
    return this.http.post<SearchResult[]>(`${this.apiUrl}/buscar`, { frase });
  }
}
