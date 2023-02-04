<script>
	import NoteSearch from './NoteSearch.svelte'

	let id
	let title

	export {
		id,
		title,
	}
</script>

<header>
	<h1>Notebook</h1>
	<p>{ title }</p>
</header>
<NoteSearch notebook_id={id} />

<style>
	header h1 {
		font-size: 2rem;
		margin: 0;
	}
</style>
