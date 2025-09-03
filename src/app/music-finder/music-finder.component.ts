import { Component } from '@angular/core';
import { MusicService, SearchResult } from '../music.service';

@Component({
  selector: 'app-music-finder',
  templateUrl: './music-finder.component.html',
  styleUrls: ['./music-finder.component.scss']
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
