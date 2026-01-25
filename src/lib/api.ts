import { apiClient } from './api-client';
import type { components } from './api-schema';

export type User = components['schemas']['User'];

export interface AuthState {
	user: User | null;
	token: string | null;
}

function getStoredToken(): string | null {
	if (typeof localStorage === 'undefined') {
		return null;
	}
	return localStorage.getItem('authToken');
}

function setStoredToken(token: string | null) {
	if (typeof localStorage === 'undefined') return;
	if (token) {
		localStorage.setItem('authToken', token);
	} else {
		localStorage.removeItem('authToken');
	}
}

export function getAuthHeaders(): Record<string, string> {
	const token = getStoredToken();
	return token ? { Authorization: `Token ${token}` } : {};
}

export async function fetchCurrentUser(): Promise<User | null> {
	const token = getStoredToken();
	if (!token) {
		return null;
	}

	const { data, error, response } = await apiClient.GET('/api/auth/users/me/');

	if (error || !response.ok) {
		setStoredToken(null);
		return null;
	}

	return data ?? null;
}

export async function login(username: string, password: string): Promise<AuthState> {
	const { data, error } = await apiClient.POST('/api/auth/login/', {
		headers: {
			Authorization: 'Basic ' + btoa(`${username}:${password}`),
		},
	});

	if (error || !data) {
		throw new Error('Invalid credentials');
	}

	const token = data.token;
	setStoredToken(token);

	const user = await fetchCurrentUser();
	return { user, token };
}

export async function logout(): Promise<void> {
	const token = getStoredToken();
	if (token) {
		await apiClient.POST('/api/auth/logout/');
	}
	setStoredToken(null);
}

export { getStoredToken };
