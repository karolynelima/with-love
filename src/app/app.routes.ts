import { MusicFinderComponent } from './music-finder/music-finder.component';
import { HomeComponent } from './home/home.component';

export const routes = [
	{ path: '', component: HomeComponent },
	{ path: 'search', component: MusicFinderComponent }
];
