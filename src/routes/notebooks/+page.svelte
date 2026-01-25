<script lang="ts">
	import { goto } from '$app/navigation';
	import { resolve } from '$app/paths';
	import { auth } from '$lib/auth.svelte';
	import { fetchNotebooks, createNotebook, deleteNotebook, type Notebook } from '$lib/notes';

	let notebooks = $state<Notebook[]>([]);
	let loading = $state(true);
	let error = $state('');
	let newTitle = $state('');
	let creating = $state(false);

	$effect(() => {
		if (!auth.isAuthenticated && auth.isInitialized) {
			void goto(resolve('/login'));
		}
	});

	$effect(() => {
		if (auth.isAuthenticated) {
			void loadNotebooks();
		}
	});

	async function loadNotebooks() {
		loading = true;
		error = '';
		try {
			notebooks = await fetchNotebooks();
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to load notebooks';
		} finally {
			loading = false;
		}
	}

	async function handleCreate(e: SubmitEvent) {
		e.preventDefault();
		if (!newTitle.trim()) return;

		creating = true;
		try {
			const notebook = await createNotebook(newTitle.trim());
			notebooks = [...notebooks, notebook];
			newTitle = '';
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to create notebook';
		} finally {
			creating = false;
		}
	}

	async function handleDelete(id: string) {
		if (!confirm('Delete this notebook and all its notes?')) return;

		try {
			await deleteNotebook(id);
			notebooks = notebooks.filter((n) => n.id !== id);
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to delete notebook';
		}
	}
</script>

<div class="mx-auto max-w-4xl p-6">
	<h1 class="mb-6 text-3xl font-bold">Notebooks</h1>

	{#if error}
		<div class="mb-4 rounded bg-red-100 p-4 text-red-700">{error}</div>
	{/if}

	<form onsubmit={handleCreate} class="mb-6 flex gap-2">
		<input
			type="text"
			bind:value={newTitle}
			placeholder="New notebook title..."
			class="flex-1 rounded border px-3 py-2"
			disabled={creating}
		/>
		<button
			type="submit"
			disabled={creating || !newTitle.trim()}
			class="rounded bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 disabled:opacity-50"
		>
			{creating ? 'Creating...' : 'Create'}
		</button>
	</form>

	{#if loading}
		<p class="text-gray-500">Loading notebooks...</p>
	{:else if notebooks.length === 0}
		<p class="text-gray-500">No notebooks yet. Create one to get started!</p>
	{:else}
		<ul class="space-y-2">
			{#each notebooks as notebook (notebook.id)}
				<li class="flex items-center gap-2 rounded border p-4 hover:bg-gray-50">
					<a
						href={resolve(`/notebooks/${notebook.id}`)}
						class="flex-1 text-lg font-medium text-blue-600 hover:underline"
					>
						{notebook.title}
					</a>
					<button
						onclick={() => handleDelete(notebook.id)}
						class="px-2 text-red-600 hover:text-red-800"
					>
						Delete
					</button>
				</li>
			{/each}
		</ul>
	{/if}
</div>
