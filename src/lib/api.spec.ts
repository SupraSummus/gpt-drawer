import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

// Hoist mock function so it can be used in vi.mock
const mockFetchFn = vi.hoisted(() => vi.fn());

// Mock api-client to use our mocked fetch
vi.mock('./api-client', async () => {
	const { createApiClient } = await vi.importActual<typeof import('./api-client')>('./api-client');
	return {
		apiClient: createApiClient(mockFetchFn),
		createApiClient
	};
});

import { getAuthHeaders, getStoredToken, login, logout, fetchCurrentUser } from './api';

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

function mockFetch(response: Response) {
	mockFetchFn.mockResolvedValue(response);
	return mockFetchFn;
}

function mockFetchSequence(...responses: Response[]) {
	let callIndex = 0;
	mockFetchFn.mockImplementation(async () => {
		return responses[callIndex++];
	});
	return mockFetchFn;
}

describe('api auth', () => {
	beforeEach(() => {
		localStorageMock.clear();
		mockFetchFn.mockReset();
	});

	afterEach(() => {
		vi.restoreAllMocks();
	});

	describe('getStoredToken', () => {
		it('returns null when no token stored', () => {
			const token = getStoredToken();
			expect(token).toBeNull();
		});

		it('returns stored token', () => {
			localStorage.setItem('authToken', 'test-token');

			const token = getStoredToken();
			expect(token).toBe('test-token');
		});
	});

	describe('getAuthHeaders', () => {
		it('returns empty object when not authenticated', () => {
			expect(getAuthHeaders()).toEqual({});
		});

		it('returns Authorization header when authenticated', () => {
			localStorage.setItem('authToken', 'test-token');

			expect(getAuthHeaders()).toEqual({ Authorization: 'Token test-token' });
		});
	});

	describe('fetchCurrentUser', () => {
		it('returns null when no token', async () => {
			const user = await fetchCurrentUser();
			expect(user).toBeNull();
		});

		it('fetches user from /users/me/', async () => {
			localStorage.setItem('authToken', 'test-token');
			const mockUser = { id: '123', username: 'testuser', email: 'test@test.com' };
			const fetchSpy = mockFetch(new Response(JSON.stringify(mockUser), { status: 200 }));

			const user = await fetchCurrentUser();

			expect(user).toEqual(mockUser);
			const request = fetchSpy.mock.calls[0][0] as Request;
			expect(request.url).toBe('http://localhost/api/auth/users/me/');
		});

		it('clears token and returns null on error', async () => {
			localStorage.setItem('authToken', 'invalid-token');
			mockFetch(new Response(null, { status: 401 }));

			const user = await fetchCurrentUser();

			expect(user).toBeNull();
			expect(localStorage.getItem('authToken')).toBeNull();
		});
	});

	describe('login', () => {
		it('stores token and fetches user on success', async () => {
			const mockUser = { id: '123', username: 'testuser', email: 'test@test.com' };
			const fetchSpy = mockFetchSequence(
				new Response(JSON.stringify({ token: 'new-token' }), { status: 200 }),
				new Response(JSON.stringify(mockUser), { status: 200 })
			);

			const result = await login('testuser', 'password123');

			expect(result.token).toBe('new-token');
			expect(result.user).toEqual(mockUser);
			expect(localStorage.getItem('authToken')).toBe('new-token');
			expect(fetchSpy).toHaveBeenCalledTimes(2);
		});

		it('throws on invalid credentials', async () => {
			mockFetch(new Response(null, { status: 401 }));

			await expect(login('bad', 'creds')).rejects.toThrow('Invalid credentials');
		});

		it('sends Basic auth header', async () => {
			const mockUser = { id: '123', username: 'user', email: 'user@test.com' };
			const fetchSpy = mockFetchSequence(
				new Response(JSON.stringify({ token: 'token' }), { status: 200 }),
				new Response(JSON.stringify(mockUser), { status: 200 })
			);

			await login('user', 'pass');

			const request = fetchSpy.mock.calls[0][0] as Request;
			expect(request.url).toBe('http://localhost/api/auth/login/');
			expect(request.method).toBe('POST');
			expect(request.headers.get('Authorization')).toBe('Basic ' + btoa('user:pass'));
		});
	});

	describe('logout', () => {
		it('clears stored token', async () => {
			localStorage.setItem('authToken', 'test-token');
			mockFetch(new Response(null, { status: 204 }));

			await logout();

			expect(localStorage.getItem('authToken')).toBeNull();
		});

		it('calls logout endpoint with token', async () => {
			localStorage.setItem('authToken', 'test-token');
			const fetchSpy = mockFetch(new Response(null, { status: 204 }));

			await logout();

			const request = fetchSpy.mock.calls[0][0] as Request;
			expect(request.url).toBe('http://localhost/api/auth/logout/');
			expect(request.method).toBe('POST');
			expect(request.headers.get('Authorization')).toBe('Token test-token');
		});

		it('skips fetch when not authenticated', async () => {
			const fetchSpy = vi.spyOn(globalThis, 'fetch');

			await logout();

			expect(fetchSpy).not.toHaveBeenCalled();
		});
	});
});
