<script lang="ts">
	import { goto } from '$app/navigation';
	import { auth } from '$lib/auth.svelte';

	let username = $state('');
	let password = $state('');
	let error = $state('');
	let loading = $state(false);

	async function handleSubmit(e: SubmitEvent) {
		e.preventDefault();
		error = '';
		loading = true;

		try {
			await auth.login(username, password);
			goto('/');
		} catch (err) {
			error = err instanceof Error ? err.message : 'Login failed';
		} finally {
			loading = false;
		}
	}
</script>

<div class="login-container">
	<h1>Login</h1>
	<form onsubmit={handleSubmit}>
		<div class="field">
			<label for="username">Username</label>
			<input id="username" type="text" bind:value={username} required autocomplete="username" />
		</div>
		<div class="field">
			<label for="password">Password</label>
			<input
				id="password"
				type="password"
				bind:value={password}
				required
				autocomplete="current-password"
			/>
		</div>
		{#if error}
			<p class="error">{error}</p>
		{/if}
		<button type="submit" disabled={loading}>
			{loading ? 'Logging in...' : 'Login'}
		</button>
	</form>
</div>

<style>
	.login-container {
		max-width: 400px;
		margin: 2rem auto;
		padding: 2rem;
	}

	.field {
		margin-bottom: 1rem;
	}

	label {
		display: block;
		margin-bottom: 0.25rem;
	}

	input {
		width: 100%;
		padding: 0.5rem;
		border: 1px solid #ccc;
		border-radius: 4px;
	}

	button {
		width: 100%;
		padding: 0.75rem;
		background: #007bff;
		color: white;
		border: none;
		border-radius: 4px;
		cursor: pointer;
	}

	button:disabled {
		opacity: 0.6;
		cursor: not-allowed;
	}

	.error {
		color: #dc3545;
		margin-bottom: 1rem;
	}
</style>
