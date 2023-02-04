import Notebook from './Notebook.svelte';
import './style.css';
import axios from 'axios';

// axios CRSF config for Django
axios.defaults.xsrfHeaderName = "X-CSRFTOKEN";
axios.defaults.xsrfCookieName = "csrftoken";

for (let element of document.querySelectorAll('.notebook')) {
	new Notebook({
		target: element,
		props: element.dataset,
	});
}
