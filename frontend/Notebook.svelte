<script>
	import Note from './Note.svelte'
	import NoteSearch from './NoteSearch.svelte'

	let id
	let title

	export {
		id,
		title,
	}
</script>

<h1>Notebook</h1>
<p>{ title }</p>
<NoteSearch notebook_id={id} />
<Note />

<style>
</style>
