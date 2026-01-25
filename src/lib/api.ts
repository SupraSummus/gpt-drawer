const API_BASE = '/api';

export interface User {
	username: string;
}

export interface AuthState {
	user: User | null;
	token: string | null;
}

function getStoredAuth(): AuthState {
	if (typeof localStorage === 'undefined') {
		return { user: null, token: null };
	}
	const token = localStorage.getItem('authToken');
	const userJson = localStorage.getItem('authUser');
	const user = userJson ? JSON.parse(userJson) : null;
	return { user, token };
}

function setStoredAuth(user: User | null, token: string | null) {
	if (typeof localStorage === 'undefined') return;
	if (token && user) {
		localStorage.setItem('authToken', token);
		localStorage.setItem('authUser', JSON.stringify(user));
	} else {
		localStorage.removeItem('authToken');
		localStorage.removeItem('authUser');
	}
}

export function getAuthHeaders(): Record<string, string> {
	const { token } = getStoredAuth();
	return token ? { Authorization: `Token ${token}` } : {};
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
	const user: User = { username };
	const token = data.token;
	setStoredAuth(user, token);
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
	setStoredAuth(null, null);
}

export { getStoredAuth };
