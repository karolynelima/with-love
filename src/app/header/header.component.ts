import { Component, Inject, LOCALE_ID } from '@angular/core';
import { DOCUMENT } from '@angular/common';


@Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.scss']
})
export class HeaderComponent {
  constructor(
    @Inject(LOCALE_ID) public localeId: string,
    @Inject(DOCUMENT) private document: Document
  ) {}

  changeLanguage(lang: string) {
    // Previne o recarregamento se o idioma selecionado já estiver ativo
    if (lang === this.localeId) {
      return;
    }

    // Pega o caminho da URL atual (ex: /pt-BR/search)
    const currentPath = this.document.location.pathname;

    // Substitui o prefixo do idioma atual pelo novo
    const newPath = currentPath.replace(`/${this.localeId}/`, `/${lang}/`);

    // Redireciona o navegador para a nova URL
    this.document.location.href = newPath;
  }
}

