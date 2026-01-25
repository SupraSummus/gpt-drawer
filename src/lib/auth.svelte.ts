import {
	fetchCurrentUser,
	getStoredToken,
	login as apiLogin,
	logout as apiLogout,
	type AuthState
} from './api';

function createAuthStore() {
	let state = $state<AuthState>({ user: null, token: null });
	let initialized = $state(false);

	if (typeof window !== 'undefined') {
		const token = getStoredToken();
		if (token) {
			state = { user: null, token };
			fetchCurrentUser()
				.then((user) => {
					state = { user, token: state.token };
				})
				.finally(() => {
					initialized = true;
				});
		} else {
			initialized = true;
		}
	}

	return {
		get user() {
			return state.user;
		},
		get isAuthenticated() {
			return !!state.token;
		},
		get isInitialized() {
			return initialized;
		},
		async login(username: string, password: string) {
			state = await apiLogin(username, password);
			initialized = true;
		},
		async logout() {
			await apiLogout();
			state = { user: null, token: null };
		}
	};
}

export const auth = createAuthStore();
