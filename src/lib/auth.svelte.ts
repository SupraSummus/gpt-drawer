import { getStoredAuth, login as apiLogin, logout as apiLogout, type AuthState } from './api';

function createAuthStore() {
	let state = $state<AuthState>({ user: null, token: null });

	if (typeof window !== 'undefined') {
		state = getStoredAuth();
	}

	return {
		get user() {
			return state.user;
		},
		get isAuthenticated() {
			return !!state.token;
		},
		async login(username: string, password: string) {
			state = await apiLogin(username, password);
		},
		async logout() {
			await apiLogout();
			state = { user: null, token: null };
		}
	};
}

export const auth = createAuthStore();
