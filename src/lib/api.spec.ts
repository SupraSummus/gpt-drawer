import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { getAuthHeaders, getStoredAuth, login, logout } from './api';

const localStorageMock = (() => {
	let store: Record<string, string> = {};
	return {
		getItem: (key: string) => store[key] ?? null,
		setItem: (key: string, value: string) => {
			store[key] = value;
		},
		removeItem: (key: string) => {
			delete store[key];
		},
		clear: () => {
			store = {};
		}
	};
})();

vi.stubGlobal('localStorage', localStorageMock);

describe('api auth', () => {
	beforeEach(() => {
		localStorageMock.clear();
	});

	afterEach(() => {
		vi.restoreAllMocks();
	});

	describe('getStoredAuth', () => {
		it('returns null when no auth stored', () => {
			const auth = getStoredAuth();
			expect(auth.user).toBeNull();
			expect(auth.token).toBeNull();
		});

		it('returns stored auth', () => {
			localStorage.setItem('authToken', 'test-token');
			localStorage.setItem('authUser', JSON.stringify({ username: 'testuser' }));

			const auth = getStoredAuth();
			expect(auth.token).toBe('test-token');
			expect(auth.user?.username).toBe('testuser');
		});
	});

	describe('getAuthHeaders', () => {
		it('returns empty object when not authenticated', () => {
			expect(getAuthHeaders()).toEqual({});
		});

		it('returns Authorization header when authenticated', () => {
			localStorage.setItem('authToken', 'test-token');
			localStorage.setItem('authUser', JSON.stringify({ username: 'testuser' }));

			expect(getAuthHeaders()).toEqual({ Authorization: 'Token test-token' });
		});
	});

	describe('login', () => {
		it('stores token and user on success', async () => {
			vi.spyOn(globalThis, 'fetch').mockResolvedValue(
				new Response(JSON.stringify({ token: 'new-token' }), { status: 200 })
			);

			const result = await login('testuser', 'password123');

			expect(result.token).toBe('new-token');
			expect(result.user?.username).toBe('testuser');
			expect(localStorage.getItem('authToken')).toBe('new-token');
		});

		it('throws on invalid credentials', async () => {
			vi.spyOn(globalThis, 'fetch').mockResolvedValue(new Response(null, { status: 401 }));

			await expect(login('bad', 'creds')).rejects.toThrow('Invalid credentials');
		});

		it('sends Basic auth header', async () => {
			const fetchSpy = vi
				.spyOn(globalThis, 'fetch')
				.mockResolvedValue(new Response(JSON.stringify({ token: 'token' }), { status: 200 }));

			await login('user', 'pass');

			expect(fetchSpy).toHaveBeenCalledWith('/api/auth/login/', {
				method: 'POST',
				headers: { Authorization: 'Basic ' + btoa('user:pass') }
			});
		});
	});

	describe('logout', () => {
		it('clears stored auth', async () => {
			localStorage.setItem('authToken', 'test-token');
			localStorage.setItem('authUser', JSON.stringify({ username: 'testuser' }));
			vi.spyOn(globalThis, 'fetch').mockResolvedValue(new Response(null, { status: 204 }));

			await logout();

			expect(localStorage.getItem('authToken')).toBeNull();
			expect(localStorage.getItem('authUser')).toBeNull();
		});

		it('calls logout endpoint with token', async () => {
			localStorage.setItem('authToken', 'test-token');
			localStorage.setItem('authUser', JSON.stringify({ username: 'testuser' }));
			const fetchSpy = vi
				.spyOn(globalThis, 'fetch')
				.mockResolvedValue(new Response(null, { status: 204 }));

			await logout();

			expect(fetchSpy).toHaveBeenCalledWith('/api/auth/logout/', {
				method: 'POST',
				headers: { Authorization: 'Token test-token' }
			});
		});

		it('skips fetch when not authenticated', async () => {
			const fetchSpy = vi.spyOn(globalThis, 'fetch');

			await logout();

			expect(fetchSpy).not.toHaveBeenCalled();
		});
	});
});
