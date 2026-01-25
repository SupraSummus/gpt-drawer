import createClient, { type Client } from 'openapi-fetch';
import type { paths } from './api-schema';

function getStoredToken(): string | null {
	if (typeof localStorage === 'undefined') {
		return null;
	}
	return localStorage.getItem('authToken');
}

function getBaseUrl(): string {
	if (typeof window !== 'undefined') {
		return window.location.origin;
	}
	// Node.js / test environment
	return 'http://localhost';
}

export function createApiClient(customFetch?: typeof fetch): Client<paths> {
	const client = createClient<paths>({
		baseUrl: getBaseUrl(),
		fetch: customFetch
	});

	client.use({
		onRequest({ request }) {
			const token = getStoredToken();
			if (token) {
				request.headers.set('Authorization', `Token ${token}`);
			}
			return request;
		}
	});

	return client;
}

export const apiClient = createApiClient();
