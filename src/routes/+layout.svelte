<script lang="ts">
	import './layout.css';
	import favicon from '$lib/assets/favicon.svg';
	import { auth } from '$lib/auth.svelte';
	import { goto } from '$app/navigation';

	let { children } = $props();

	async function handleLogout() {
		await auth.logout();
		goto('/login');
	}
</script>

<svelte:head><link rel="icon" href={favicon} /></svelte:head>

<header>
	<nav>
		<a href="/">Home</a>
		{#if auth.isAuthenticated}
			<span>Welcome, {auth.user?.username}</span>
			<button onclick={handleLogout}>Logout</button>
		{:else}
			<a href="/login">Login</a>
		{/if}
	</nav>
</header>

<main>
	{@render children()}
</main>

<style>
	header {
		padding: 1rem;
		border-bottom: 1px solid #eee;
	}

	nav {
		display: flex;
		gap: 1rem;
		align-items: center;
		max-width: 1200px;
		margin: 0 auto;
	}

	nav a {
		text-decoration: none;
		color: #007bff;
	}

	nav button {
		background: none;
		border: none;
		color: #007bff;
		cursor: pointer;
		padding: 0;
		font-size: inherit;
	}

	nav span {
		margin-left: auto;
	}

	main {
		max-width: 1200px;
		margin: 0 auto;
		padding: 1rem;
	}
</style>
