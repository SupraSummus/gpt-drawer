import { apiClient } from './api-client';
import type { components } from './api-schema';

export type Notebook = components['schemas']['Notebook'];
export type Note = components['schemas']['Note'];
export type NoteShort = components['schemas']['NoteShort'];
export type Alias = components['schemas']['Alias'];
export type Reference = components['schemas']['Reference'];

// Notebooks

export async function fetchNotebooks(): Promise<Notebook[]> {
	const { data, response } = await apiClient.GET('/api/notebooks/');
	if (!response.ok || !data) throw new Error('Failed to fetch notebooks');
	return data.results;
}

export async function fetchNotebook(id: string): Promise<Notebook> {
	const { data, response } = await apiClient.GET('/api/notebooks/{id}/', {
		params: { path: { id } },
	});
	if (!response.ok || !data) throw new Error('Failed to fetch notebook');
	return data;
}

export async function createNotebook(title: string): Promise<Notebook> {
	const { data, response } = await apiClient.POST('/api/notebooks/', {
		body: { title } as Notebook,
	});
	if (!response.ok || !data) throw new Error('Failed to create notebook');
	return data;
}

export async function updateNotebook(id: string, title: string): Promise<Notebook> {
	const { data, response } = await apiClient.PATCH('/api/notebooks/{id}/', {
		params: { path: { id } },
		body: { title },
	});
	if (!response.ok || !data) throw new Error('Failed to update notebook');
	return data;
}

export async function deleteNotebook(id: string): Promise<void> {
	const { response } = await apiClient.DELETE('/api/notebooks/{id}/', {
		params: { path: { id } },
	});
	if (!response.ok) throw new Error('Failed to delete notebook');
}

// Notes

export async function fetchNotes(notebookId?: string, search?: string): Promise<Note[]> {
	const { data, response } = await apiClient.GET('/api/notes/', {
		params: {
			query: {
				notebook_id: notebookId,
				search,
			},
		},
	});
	if (!response.ok || !data) throw new Error('Failed to fetch notes');
	return data.results;
}

export async function fetchNote(id: string): Promise<Note> {
	const { data, response } = await apiClient.GET('/api/notes/{id}/', {
		params: { path: { id } },
	});
	if (!response.ok || !data) throw new Error('Failed to fetch note');
	return data;
}

export async function createNote(
	notebookId: string,
	title?: string,
	content?: string,
): Promise<Note> {
	const { data, response } = await apiClient.POST('/api/notes/', {
		body: { notebook_id: notebookId, title, content } as Note,
	});
	if (!response.ok || !data) throw new Error('Failed to create note');
	return data;
}

export async function updateNote(
	id: string,
	updates: { title?: string; content?: string },
): Promise<Note> {
	const { data, response } = await apiClient.PATCH('/api/notes/{id}/', {
		params: { path: { id } },
		body: updates as Note,
	});
	if (!response.ok || !data) throw new Error('Failed to update note');
	return data;
}

export async function deleteNote(id: string): Promise<void> {
	const { response } = await apiClient.DELETE('/api/notes/{id}/', {
		params: { path: { id } },
	});
	if (!response.ok) throw new Error('Failed to delete note');
}

// Aliases

export async function createAlias(noteId: string, title: string): Promise<Alias> {
	const { data, response } = await apiClient.POST('/api/notes/{note_pk}/aliases/', {
		params: { path: { note_pk: noteId } },
		body: { title } as Alias,
	});
	if (!response.ok || !data) throw new Error('Failed to create alias');
	return data;
}

export async function deleteAlias(noteId: string, aliasId: string): Promise<void> {
	const { response } = await apiClient.DELETE('/api/notes/{note_pk}/aliases/{id}/', {
		params: { path: { note_pk: noteId, id: aliasId } },
	});
	if (!response.ok) throw new Error('Failed to delete alias');
}

// References

export async function createReference(noteId: string, targetNoteId: string): Promise<Reference> {
	const { data, response } = await apiClient.POST('/api/notes/{note_pk}/references/', {
		params: { path: { note_pk: noteId } },
		body: { target_note_id: targetNoteId } as Reference,
	});
	if (!response.ok || !data) throw new Error('Failed to create reference');
	return data;
}

export async function deleteReference(noteId: string, referenceId: string): Promise<void> {
	const { response } = await apiClient.DELETE('/api/notes/{note_pk}/references/{id}/', {
		params: { path: { note_pk: noteId, id: referenceId } },
	});
	if (!response.ok) throw new Error('Failed to delete reference');
}
