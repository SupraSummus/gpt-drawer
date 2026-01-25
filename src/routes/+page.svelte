<script lang="ts">
	import { resolve } from '$app/paths';
	import { auth } from '$lib/auth.svelte';
</script>

<div class="mx-auto max-w-4xl p-6">
	<h1 class="mb-6 text-3xl font-bold">Welcome to GPT Drawer</h1>

	{#if auth.isAuthenticated}
		<p class="mb-4">You're logged in as <strong>{auth.user?.username}</strong>.</p>
		<a
			href={resolve('/notebooks')}
			class="inline-block rounded bg-blue-600 px-6 py-3 text-white hover:bg-blue-700"
		>
			Go to Notebooks
		</a>
	{:else}
		<p class="mb-4">Please log in to access your notebooks and notes.</p>
		<a
			href={resolve('/login')}
			class="inline-block rounded bg-blue-600 px-6 py-3 text-white hover:bg-blue-700"
		>
			Login
		</a>
	{/if}
</div>
