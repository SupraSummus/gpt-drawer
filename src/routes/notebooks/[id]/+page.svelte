<script lang="ts">
	import { goto } from '$app/navigation';
	import { resolve } from '$app/paths';
	import { page } from '$app/state';
	import { auth } from '$lib/auth.svelte';
	import {
		fetchNotebook,
		fetchNotes,
		createNote,
		deleteNote,
		type Notebook,
		type Note,
	} from '$lib/notes';

	let notebook = $state<Notebook | null>(null);
	let notes = $state<Note[]>([]);
	let loading = $state(true);
	let error = $state('');
	let search = $state('');
	let creating = $state(false);

	const notebookId = $derived(page.params.id);

	$effect(() => {
		if (!auth.isAuthenticated && auth.isInitialized) {
			goto(resolve('/login'));
		}
	});

	$effect(() => {
		if (auth.isAuthenticated && notebookId) {
			loadData();
		}
	});

	async function loadData() {
		if (!notebookId) return;
		loading = true;
		error = '';
		try {
			const [nb, noteList] = await Promise.all([fetchNotebook(notebookId), fetchNotes(notebookId)]);
			notebook = nb;
			notes = noteList;
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to load data';
		} finally {
			loading = false;
		}
	}

	async function handleSearch() {
		if (!notebookId) return;
		loading = true;
		try {
			notes = await fetchNotes(notebookId, search || undefined);
		} catch (e) {
			error = e instanceof Error ? e.message : 'Search failed';
		} finally {
			loading = false;
		}
	}

	async function handleCreateNote() {
		if (!notebookId) return;
		creating = true;
		try {
			const note = await createNote(notebookId);
			goto(resolve(`/notebooks/${notebookId}/notes/${note.id}`));
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to create note';
			creating = false;
		}
	}

	async function handleDeleteNote(noteId: string) {
		if (!confirm('Delete this note?')) return;

		try {
			await deleteNote(noteId);
			notes = notes.filter((n) => n.id !== noteId);
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to delete note';
		}
	}
</script>

<div class="mx-auto max-w-4xl p-6">
	<nav class="mb-4">
		<a href={resolve('/notebooks')} class="text-blue-600 hover:underline">← Back to Notebooks</a>
	</nav>

	{#if loading && !notebook}
		<p class="text-gray-500">Loading...</p>
	{:else if notebook}
		<div class="mb-6 flex items-center justify-between">
			<h1 class="text-3xl font-bold">{notebook.title}</h1>
			<button
				onclick={handleCreateNote}
				disabled={creating}
				class="rounded bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 disabled:opacity-50"
			>
				{creating ? 'Creating...' : '+ New Note'}
			</button>
		</div>

		{#if error}
			<div class="mb-4 rounded bg-red-100 p-4 text-red-700">{error}</div>
		{/if}

		<form
			onsubmit={(e) => {
				e.preventDefault();
				handleSearch();
			}}
			class="mb-6 flex gap-2"
		>
			<input
				type="text"
				bind:value={search}
				placeholder="Search notes..."
				class="flex-1 rounded border px-3 py-2"
			/>
			<button type="submit" class="rounded bg-gray-200 px-4 py-2 hover:bg-gray-300">
				Search
			</button>
		</form>

		{#if loading}
			<p class="text-gray-500">Loading notes...</p>
		{:else if notes.length === 0}
			<p class="text-gray-500">No notes yet. Create one to get started!</p>
		{:else}
			<ul class="space-y-2">
				{#each notes as note (note.id)}
					<li class="rounded border p-4 hover:bg-gray-50">
						<div class="flex items-start justify-between gap-4">
							<a href={resolve(`/notebooks/${notebookId}/notes/${note.id}`)} class="flex-1">
								<h3 class="text-lg font-medium text-blue-600 hover:underline">
									{note.title || '(Untitled)'}
								</h3>
								{#if note.content}
									<p class="mt-1 line-clamp-2 text-sm text-gray-600">
										{note.content.slice(0, 200)}
									</p>
								{/if}
								{#if note.aliases.length > 0}
									<div class="mt-2 flex flex-wrap gap-1">
										{#each note.aliases as alias (alias.id)}
											<span class="rounded bg-gray-200 px-2 py-1 text-xs">{alias.title}</span>
										{/each}
									</div>
								{/if}
							</a>
							<button
								onclick={() => handleDeleteNote(note.id)}
								class="text-sm text-red-600 hover:text-red-800"
							>
								Delete
							</button>
						</div>
					</li>
				{/each}
			</ul>
		{/if}
	{/if}
</div>
