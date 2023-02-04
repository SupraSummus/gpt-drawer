<script>
	import axios from 'axios'
	import { createEventDispatcher } from 'svelte'

	let notebook_id
	let search_term = ''
	let debounce_timer = null
	let search_results = null
	let search_id = notebook_id

	const dispatch = createEventDispatcher()

	// This is a mechanism to discard successive focusout-focusin events.
	// Such events happen when focus within the element is moved.
	let focus = false
	let focus_timer = null
	function set_focus(focus_value) {
		clearTimeout(focus_timer)
		if (focus_value) {
			focus = true
		} else {
			focus_timer = setTimeout(() => {
				focus = false
				focus_timer = null
			})
		}
	}

	$: if (search_term !== '') {
		search_results = search(search_term)
	} else {
		search_results = null
	}

	function debounced_search(v) {
		clearTimeout(debounce_timer);
		debounce_timer = setTimeout(() => {
			search_term = v;
		}, 250);
	}

	async function search(term) {
		const response = await axios.get('/api/notes/', {
			params: {
				notebook_id,
				search: term,
			}
		})
		const data = response.data
		return data.results
	}

	function select_note(note) {
		set_focus(false)
		dispatch('selected', note.id)
	}

	async function create_note() {
		const response = await axios.post('/api/notes/', {
			notebook_id,
			title: search_term,
			content: '',
		})
		const data = response.data
		select_note(data)
	}

	export { notebook_id }
</script>

<div
	class="search"
	tabindex="-1"
	on:focusin={() => set_focus(true)}
	on:focusout={() => set_focus(false)}
>
	<input
		on:keyup={({ target: { value } }) => debounced_search(value)}
		placeholder="Search"
		class="search-input"
		role="combobox"
		aria-controls="search-results-{search_id}"
		aria-expanded="{focus && search_results}"
	/>

	{#if focus && search_results}
		<div class="search-results" id="search-results-{search_id}">
			{#await search_results}
				<p aria-busy="true">Searching...</p>

			{:then result}
				{#if result.length === 0}
					<p>No results</p>
				{:else}
					<ul role="listbox">
						{#each result as note (note.id)}
							<li>
								<a href on:click|preventDefault={() => select_note(note)}>
									{note.title}
								</a>
							</li>
						{/each}
					</ul>
				{/if}

				<button
					class="outline"
					on:click={create_note}
				>
					Create note "{search_term}"
				</button>

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
		background: var(--background-color);
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
