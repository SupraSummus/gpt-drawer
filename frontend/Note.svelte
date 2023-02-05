<script>
  import axios from 'axios'
	import { createEventDispatcher, onMount } from 'svelte'

  let id = null
  let title = ''
  let content = ''

  let dispatch = createEventDispatcher()
  let state = 'fetching'

  function load_from_response(response) {
    const data = response.data
    console.assert(data.id === id)
    title = data.title
    content = data.content
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
        <a href on:click|preventDefault={() => save_note()}>
          Save
        </a>
        <a href on:click|preventDefault={() => fetch_note()}>
          Cancel
        </a>
      {:else if state === 'view'}
        <a href on:click|preventDefault={() => {state = 'edit'}}>
          Edit
        </a>
      {/if}
      
      <a href class="close"
        on:click|preventDefault={() => dispatch('close', id)}
      >
        Close
      </a>
    </div>

    {#if state === 'edit'}
      <h2 class="title" contenteditable bind:textContent={title}></h2>
    {:else}
      <h2 class="title">{title}</h2>
    {/if}
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
  }

  .title {
    margin: 0;
  }

  .content {
    margin: 0;
  }

  [contenteditable] {
    outline: none;
    border: 1px solid red;
  }
</style>
