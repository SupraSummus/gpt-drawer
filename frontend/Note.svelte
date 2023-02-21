<script>
  import axios from 'axios'
	import { createEventDispatcher, onMount } from 'svelte'
  import Alias from './Alias.svelte'

  let id = null
  let title = ''
  let content = ''
  let aliases = []

  let dispatch = createEventDispatcher()
  let state = 'fetching'

  function load_from_response(response) {
    const data = response.data
    console.assert(data.id === id)
    title = data.title
    content = data.content
    aliases = data.aliases
    state = 'view'
  }

  async function save_note() {
    state = 'saving'
    const response = await axios.patch(`/api/notes/${id}/`, {
      title,
      content,
    })
    load_from_response(response)
  }

  async function fetch_note() {
    state = 'fetching'
    const response = await axios.get(`/api/notes/${id}/`)
    load_from_response(response)
  }

  function add_alias() {
    aliases.push({
      id: null,
      title: '',
    })
    aliases = aliases
  }

  function delete_alias(alias_id) {
    aliases = aliases.filter(alias => alias.id !== alias_id)
  }

  onMount(() => {
    fetch_note()
  })

  export { id }
</script>

<article on:dblclick={() => {
  if (state === 'view') state = 'edit'
}} aria-busy="{state === 'saving' || state === 'fetching'}">
  <header>
    
    <div class="actions">
      {#if state === 'edit'}
        <button on:click|preventDefault={() => save_note()} class='action-button outline'>
          Save
        </button>
        <button on:click|preventDefault={() => fetch_note()} class='action-button outline'>
          Cancel
        </button>
      {:else if state === 'view'}
        <button on:click|preventDefault={() => {state = 'edit'}} class='action-button outline'>
          Edit
        </button>
      {/if}
      
      <button class='action-button outline'
        on:click|preventDefault={() => dispatch('close', id)}
      >
        Close
      </button>
    </div>

    {#if state === 'edit'}
      <h2 class="title" contenteditable bind:textContent={title}></h2>
    {:else}
      <h2 class="title">{title}</h2>
    {/if}

    <details>
      <summary>Aliases</summary>
      <ul>
        {#each aliases as alias (alias.id || '')}
          <li>
            {#if alias.id === null}
              <Alias
                note_id={id}
                bind:title={alias.title}
                bind:id={alias.id}
                state='edit'
                on:alias-deleted={() => delete_alias(alias.id)}
              />
            {:else}
              <Alias
                note_id={id}
                bind:title={alias.title}
                bind:id={alias.id}
                on:alias-deleted={() => delete_alias(alias.id)}
              />
            {/if}
          </li>
        {/each}
        {#if !aliases.some(alias => alias.id === null)}
          <li>
            <button on:click|preventDefault={() => add_alias()} class='outline'>
              Add alias
            </button>
          </li>
        {/if}
      </ul>
    </details>

  </header>

  {#if state === 'edit'}
    <p class="content" contenteditable bind:textContent={content}></p>
  {:else}
    <p class="content">{content}</p>
  {/if}

</article>

<style>
  header {
    margin-bottom: 0;
  }

  .actions {
    float: right;
    display: flex;
  }

  .title {
    margin: 0;
  }

  .action-button {
    display: inline-block;
    margin-left: 0.5em;
  }

  .content {
    margin: 0;
  }

  [contenteditable] {
    outline: none;
    border: 1px solid red;
  }
</style>
