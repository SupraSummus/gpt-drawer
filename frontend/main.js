import Notebook from './Notebook.svelte';
import './style.css';

for (let element of document.querySelectorAll('.notebook')) {
	new Notebook({
		target: element,
		props: element.dataset,
	});
}
