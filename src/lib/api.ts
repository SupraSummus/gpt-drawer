const API_BASE = '/api';

export interface User {
	id: string;
	username: string;
	email: string;
}

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

	const response = await fetch(`${API_BASE}/auth/users/me/`, {
		headers: getAuthHeaders()
	});

	if (!response.ok) {
		setStoredToken(null);
		return null;
	}

	return await response.json();
}

export async function login(username: string, password: string): Promise<AuthState> {
	const response = await fetch(`${API_BASE}/auth/login/`, {
		method: 'POST',
		headers: {
			Authorization: 'Basic ' + btoa(`${username}:${password}`)
		}
	});

	if (!response.ok) {
		throw new Error('Invalid credentials');
	}

	const data = await response.json();
	const token = data.token;
	setStoredToken(token);

	const user = await fetchCurrentUser();
	return { user, token };
}

export async function logout(): Promise<void> {
	const headers = getAuthHeaders();
	if (headers.Authorization) {
		await fetch(`${API_BASE}/auth/logout/`, {
			method: 'POST',
			headers
		});
	}
	setStoredToken(null);
}

export { getStoredToken };
