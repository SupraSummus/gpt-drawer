import Notebook from './Notebook.svelte';

for (let element of document.querySelectorAll('.notebook')) {
	new Notebook({
		target: element,
		props: element.dataset,
	});
}
