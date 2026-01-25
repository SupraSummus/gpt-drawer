<script lang="ts">
	import './layout.css';
	import favicon from '$lib/assets/favicon.svg';
	import { auth } from '$lib/auth.svelte';
	import { goto } from '$app/navigation';
	import { resolve } from '$app/paths';

	let { children } = $props();

	async function handleLogout() {
		await auth.logout();
		void goto(resolve('/login'));
	}
</script>

<svelte:head><link rel="icon" href={favicon} /></svelte:head>

{#if !auth.isInitialized}
	<div class="loading">Loading...</div>
{:else}
	<header>
		<nav>
			<a href={resolve('/')}>Home</a>
			{#if auth.isAuthenticated}
				<span>Welcome, {auth.user?.username}</span>
				<button onclick={handleLogout}>Logout</button>
			{:else}
				<a href={resolve('/login')}>Login</a>
			{/if}
		</nav>
	</header>

	<main>
		<!-- eslint-disable-next-line @typescript-eslint/no-unsafe-call -->
		{@render children()}
	</main>
{/if}

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

	.loading {
		display: flex;
		justify-content: center;
		align-items: center;
		height: 100vh;
		font-size: 1.2rem;
		color: #666;
	}
</style>
