import { Component } from '@angular/core';
import { trigger, transition, style, animate, query, stagger } from '@angular/animations';
import { MusicService, SearchResult } from '../music.service';

@Component({
  selector: 'app-music-finder',
  templateUrl: './music-finder.component.html',
  styleUrls: ['./music-finder.component.scss'],
  animations: [
    trigger('pageAnimations', [
      transition(':enter', [
        query('.music-finder-left > *, .music-finder-right', [
          style({ opacity: 0, transform: 'translateY(20px)' }),
          stagger(100, [ // Diminuí o tempo de escalonamento
            animate('0.7s cubic-bezier(0.35, 0, 0.25, 1)', style({ opacity: 1, transform: 'none' })) // Diminuí a duração
          ]),
        ])
      ])
    ])
  ]
})
export class MusicFinderComponent {
  searchTerm: string = '';
  searchResults: SearchResult[] = [];
  isLoading: boolean = false;
  hasSearched: boolean = false;

  constructor(private musicService: MusicService) {}

  buscar(): void {
    if (!this.searchTerm.trim()) {
      return;
    }

    this.isLoading = true;
    this.hasSearched = true;
    this.searchResults = [];

    this.musicService.buscarMusicas(this.searchTerm).subscribe(data => {
      this.searchResults = data;
      this.isLoading = false;
    });
  }

  onSearchInput(): void {
    // Quando o usuário começa a digitar, a busca anterior (com ou sem resultados)
    // é invalidada. Redefinimos o estado para o inicial.
    this.hasSearched = false;
    this.searchResults = [];
  }


}
