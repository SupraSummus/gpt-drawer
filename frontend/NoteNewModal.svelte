<script>
    import axios from 'axios'
    import { createEventDispatcher } from 'svelte';

	const dispatch = createEventDispatcher();

    let notebook_id
    let title = ''
    let content = ''
    let form_disabled = false

    async function create_note() {
        form_disabled = true
        const response = await axios.post('/api/notes/', {
            notebook_id,
            title,
            content,
        })
        const data = response.data
        dispatch('created', data)
    }

    export { notebook_id, title, content }
</script>

<modal>
    <article>
        <header>
            <a
                href
                aria-label="Close" class="close"
                on:click={() => dispatch('cancel')}
            >Close</a>
            New note
        </header>
        <form on:submit|preventDefault={create_note} disabled={form_disabled}>
            <label for="title">Title</label>
            <input
                id="title"
                bind:value={title}
                placeholder="Title"
                required
            />
            <label for="content">Content</label>
            <textarea
                id="content"
                bind:value={content}
                placeholder="Content"
                required
            />
            <div class="grid">
                <button type="submit">Create</button>
                <button type="button"
                    on:click={() => dispatch('cancel')}
                    class='outline'
                >Cancel</button>
            </div>
        </form>
    </article>
</modal>
