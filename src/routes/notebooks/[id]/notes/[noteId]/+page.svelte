<script lang="ts">
	import { goto } from '$app/navigation';
	import { resolve } from '$app/paths';
	import { page } from '$app/state';
	import { auth } from '$lib/auth.svelte';
	import {
		fetchNote,
		fetchNotes,
		updateNote,
		createAlias,
		deleteAlias,
		createReference,
		deleteReference,
		type Note,
	} from '$lib/notes';

	let note = $state<Note | null>(null);
	let loading = $state(true);
	let saving = $state(false);
	let error = $state('');

	// Edit state
	let title = $state('');
	let content = $state('');
	let dirty = $state(false);

	// Alias form
	let newAlias = $state('');
	let addingAlias = $state(false);

	// Reference form
	let searchQuery = $state('');
	let searchResults = $state<Note[]>([]);
	let searching = $state(false);
	let addingReference = $state(false);

	const notebookId = $derived(page.params.id);
	const noteId = $derived(page.params.noteId);

	$effect(() => {
		if (!auth.isAuthenticated && auth.isInitialized) {
			goto(resolve('/login'));
		}
	});

	$effect(() => {
		if (auth.isAuthenticated && noteId) {
			loadNote();
		}
	});

	async function loadNote() {
		if (!noteId) return;
		loading = true;
		error = '';
		try {
			note = await fetchNote(noteId);
			title = note.title ?? '';
			content = note.content ?? '';
			dirty = false;
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to load note';
		} finally {
			loading = false;
		}
	}

	function handleTitleChange(e: Event) {
		title = (e.target as HTMLInputElement).value;
		dirty = true;
	}

	function handleContentChange(e: Event) {
		content = (e.target as HTMLTextAreaElement).value;
		dirty = true;
	}

	async function handleSave() {
		if (!dirty || !note) return;

		saving = true;
		try {
			note = await updateNote(note.id, { title, content });
			dirty = false;
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to save note';
		} finally {
			saving = false;
		}
	}

	async function handleAddAlias(e: SubmitEvent) {
		e.preventDefault();
		if (!newAlias.trim() || !note) return;

		addingAlias = true;
		try {
			const alias = await createAlias(note.id, newAlias.trim());
			note = { ...note, aliases: [...note.aliases, alias] };
			newAlias = '';
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to add alias';
		} finally {
			addingAlias = false;
		}
	}

	async function handleRemoveAlias(aliasId: string) {
		if (!note) return;

		try {
			await deleteAlias(note.id, aliasId);
			note = { ...note, aliases: note.aliases.filter((a) => a.id !== aliasId) };
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to remove alias';
		}
	}

	async function handleSearchNotes() {
		if (!searchQuery.trim() || !notebookId) {
			searchResults = [];
			return;
		}

		searching = true;
		try {
			const results = await fetchNotes(notebookId, searchQuery);
			// Filter out current note and already referenced notes
			const referencedIds = new Set(note?.references.map((r) => r.target_note.id) ?? []);
			searchResults = results.filter((n) => n.id !== noteId && !referencedIds.has(n.id));
		} catch (e) {
			error = e instanceof Error ? e.message : 'Search failed';
		} finally {
			searching = false;
		}
	}

	async function handleAddReference(targetNoteId: string) {
		if (!note) return;

		addingReference = true;
		try {
			const ref = await createReference(note.id, targetNoteId);
			note = { ...note, references: [...note.references, ref] };
			searchResults = searchResults.filter((n) => n.id !== targetNoteId);
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to add reference';
		} finally {
			addingReference = false;
		}
	}

	async function handleRemoveReference(referenceId: string) {
		if (!note) return;

		try {
			await deleteReference(note.id, referenceId);
			note = { ...note, references: note.references.filter((r) => r.id !== referenceId) };
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to remove reference';
		}
	}
</script>

<div class="mx-auto max-w-4xl p-6">
	<nav class="mb-4">
		<a href={resolve(`/notebooks/${notebookId}`)} class="text-blue-600 hover:underline">
			← Back to Notes
		</a>
	</nav>

	{#if error}
		<div class="mb-4 rounded bg-red-100 p-4 text-red-700">{error}</div>
	{/if}

	{#if loading}
		<p class="text-gray-500">Loading...</p>
	{:else if note}
		<div class="space-y-6">
			<!-- Title & Content -->
			<section class="space-y-4">
				<input
					type="text"
					value={title}
					oninput={handleTitleChange}
					placeholder="Note title..."
					class="w-full border-b border-gray-300 pb-2 text-2xl font-bold focus:border-blue-500 focus:outline-none"
				/>

				<textarea
					value={content}
					oninput={handleContentChange}
					placeholder="Write your note content here..."
					rows="12"
					class="w-full resize-y rounded border p-3 focus:border-blue-500 focus:outline-none"
				></textarea>

				<div class="flex items-center gap-4">
					<button
						onclick={handleSave}
						disabled={!dirty || saving}
						class="rounded bg-blue-600 px-6 py-2 text-white hover:bg-blue-700 disabled:opacity-50"
					>
						{saving ? 'Saving...' : 'Save'}
					</button>
					{#if dirty}
						<span class="text-sm text-orange-600">Unsaved changes</span>
					{/if}
				</div>
			</section>

			<!-- Aliases -->
			<section class="border-t pt-6">
				<h2 class="mb-4 text-xl font-semibold">Aliases</h2>

				{#if note.aliases.length > 0}
					<div class="mb-4 flex flex-wrap gap-2">
						{#each note.aliases as alias (alias.id)}
							<span class="flex items-center gap-1 rounded bg-gray-100 px-3 py-1">
								{alias.title}
								<button
									onclick={() => handleRemoveAlias(alias.id)}
									class="ml-1 text-red-500 hover:text-red-700"
								>
									×
								</button>
							</span>
						{/each}
					</div>
				{:else}
					<p class="mb-4 text-gray-500">No aliases yet.</p>
				{/if}

				<form onsubmit={handleAddAlias} class="flex gap-2">
					<input
						type="text"
						bind:value={newAlias}
						placeholder="Add alias..."
						class="flex-1 rounded border px-3 py-2"
						disabled={addingAlias}
					/>
					<button
						type="submit"
						disabled={addingAlias || !newAlias.trim()}
						class="rounded bg-gray-200 px-4 py-2 hover:bg-gray-300 disabled:opacity-50"
					>
						{addingAlias ? 'Adding...' : 'Add'}
					</button>
				</form>
			</section>

			<!-- References -->
			<section class="border-t pt-6">
				<h2 class="mb-4 text-xl font-semibold">References</h2>

				{#if note.references.length > 0}
					<ul class="mb-4 space-y-2">
						{#each note.references as ref (ref.id)}
							<li class="flex items-center justify-between rounded bg-gray-50 p-3">
								<a
									href={resolve(`/notebooks/${notebookId}/notes/${ref.target_note.id}`)}
									class="text-blue-600 hover:underline"
								>
									{ref.target_note.title || '(Untitled)'}
								</a>
								<button
									onclick={() => handleRemoveReference(ref.id)}
									class="text-sm text-red-600 hover:text-red-800"
								>
									Remove
								</button>
							</li>
						{/each}
					</ul>
				{:else}
					<p class="mb-4 text-gray-500">No references yet.</p>
				{/if}

				<div class="space-y-2">
					<form
						onsubmit={(e) => {
							e.preventDefault();
							handleSearchNotes();
						}}
						class="flex gap-2"
					>
						<input
							type="text"
							bind:value={searchQuery}
							placeholder="Search notes to reference..."
							class="flex-1 rounded border px-3 py-2"
						/>
						<button
							type="submit"
							disabled={searching}
							class="rounded bg-gray-200 px-4 py-2 hover:bg-gray-300"
						>
							{searching ? 'Searching...' : 'Search'}
						</button>
					</form>

					{#if searchResults.length > 0}
						<ul class="divide-y rounded border">
							{#each searchResults as result (result.id)}
								<li class="flex items-center justify-between p-3">
									<span>{result.title || '(Untitled)'}</span>
									<button
										onclick={() => handleAddReference(result.id)}
										disabled={addingReference}
										class="text-sm text-blue-600 hover:text-blue-800"
									>
										+ Add
									</button>
								</li>
							{/each}
						</ul>
					{/if}
				</div>
			</section>
		</div>
	{/if}
</div>
