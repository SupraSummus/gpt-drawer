<script>
    let notebook_id

    let search_term = ''
	let debounce_timer

	const debounce = v => {
		clearTimeout(debounce_timer);
		debounce_timer = setTimeout(() => {
			search_term = v;
		}, 750);
	}

    export { notebook_id }
</script>

<div>
    <p>Search on notebook ID: {notebook_id}</p>
    <input on:keyup={({ target: { value } }) => debounce(value)} />
    <p>Current term: {search_term}</p>
</div>
