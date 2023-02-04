<script>
	import NoteSearch from './NoteSearch.svelte'
	import Note from './Note.svelte'

	let id
	let title
	let note_ids = []

	function add_note(note_id) {
		remove_note(note_id)
		note_ids.unshift(note_id)
	}

	function remove_note(note_id) {
		note_ids = note_ids.filter(id => id !== note_id)
	}

	export {
		id,
		title,
	}
</script>

<header>
	<h1>Notebook</h1>
	<p>{ title }</p>
</header>

<NoteSearch notebook_id={id} on:selected={(e) => add_note(e.detail)} />

{#each note_ids as note_id (note_id)}
	<Note id={note_id} on:close={(e) => remove_note(e.detail)} />
{/each}

<style>
	header h1 {
		font-size: 2rem;
		margin: 0;
	}
</style>
