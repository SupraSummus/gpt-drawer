<script>
    import axios from 'axios';
    import { createEventDispatcher } from 'svelte'

    export let note_id;
    export let id = null;
    export let title = '';
    export let state = 'view';
    let dispatch = createEventDispatcher();

    async function save() {
        state = 'saving';
        let response
        if (id === null) {
            response = await axios.post(`/api/notes/${note_id}/aliases/`, {
                title,
            });
        } else {
            response = await axios.patch(`/api/notes/${note_id}/aliases/${id}/`, {
                title,
            });
        }
        state = 'view';
        id = response.data.id;
        title = response.data.title;
    }

    async function delete_alias() {
        state = 'saving';
        if (id !== null) {
            await axios.delete(`/api/notes/${note_id}/aliases/${id}/`);
        }
        state = 'deleted';
        dispatch('alias-deleted');
    }
</script>

<div class='alias-row'>
    {#if state === 'view'}
        <span>{title}</span>
        <button on:click={() => state = 'edit'} class="action-button outline row-end">Edit</button>
        <button on:click={() => delete_alias()} class="action-button outline">Delete</button>
    {:else if state === 'edit'}
        <input bind:value={title} />
        <button on:click={() => save()} class="action-button outline row-end">Save</button>
        <button on:click={() => delete_alias()} class="action-button outline">Delete</button>
    {:else if state === 'saving'}
        <span>{title}</span>
        <span aria-busy="true" class="row-end">Saving...</span>
    {:else if state === 'deleted'}
        <span class="deleted">{title}</span>
    {/if}
</div>

<style>
    .alias-row {
        display: flex;
        flex-direction: row;
        align-items: center;
    }

    .action-button, input {
        display: inline-block;
        width: auto;
        margin-bottom: auto;
        margin-top: auto;
    }

    .action-button {
        margin-left: 0.5em;
    }

    .row-end {
        margin-left: auto;
    }

    .deleted {
        text-decoration: line-through;
    }
</style>
