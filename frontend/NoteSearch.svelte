<script>
    let notebook_id

    let search_term = ''
	let debounce_timer
	let search_results = null
	let focus = false

	$: if (search_term !== '') {
		search_results = search(search_term)
	} else {
		search_results = null
	}

	function debounce(v) {
		clearTimeout(debounce_timer);
		debounce_timer = setTimeout(() => {
			search_term = v;
		}, 250);
	}

	async function search(term) {
		const response = await fetch(`/api/notes/?notebook_id=${notebook_id}&search=${term}`)
		const data = await response.json()
		return data.results
	}

    export { notebook_id }
</script>

<div class="search">
    <input
		on:keyup={({ target: { value } }) => debounce(value)}
		on:focus={() => focus = true}
		on:blur={() => focus = false}
		placeholder="Search"
		class="search-input"
	/>

	{#if search_results && focus}
		<div class="search-results">
			{#await search_results}
				<p aria-busy="true">Searching...</p>

			{:then result}
				{#if result.length === 0}
					<p>No results</p>
				{:else}
					<ul role="listbox">
						{#each result as note}
							<li>
								<a href="/note/{note.id}">{note.title}</a>
							</li>
						{/each}
					</ul>
				{/if}

			{:catch error}
				<p>Oops, it broke ;(</p>
			{/await}
		</div>
	{/if}
</div>

<style>
	.search {
		position: relative;
	}

	.search-input {
		width: 100%;
		margin: 0;
	}

	.search-results {
		position: absolute;
		top: 100%;
		left: 0;
		width: 100%;
		background: var(--color-background);
		border: 1px solid var(--dropdown-border-color);
		padding: 1em;
	}

	.search-results ul {
		padding: 0;
		margin: 0;
	}

	.search-results ul li {
		list-style: none;
		padding: 0;
		margin: 0;
	}
</style>
