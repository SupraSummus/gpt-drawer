<script>
  import axios from 'axios'
	import { createEventDispatcher } from 'svelte'

  let id
  let dispatch = createEventDispatcher()

  $: note_data_promise = axios.get(`/api/notes/${id}/`).then(response => response.data)

  export { id }
</script>

<article>
  <header>
    <a href aria-label="Close" class="close"
      on:click|preventDefault={() => dispatch('close', id)}
    >Close</a>
    <h2 class="title">{#await note_data_promise then data} {data.title} {/await}</h2>
  </header>
  <p class="content">
    {#await note_data_promise then data} {data.content} {/await}
  </p>
</article>

<style>
  header {
    margin-bottom: 0;
  }

  .close {
    float: right;
  }

  .title {
    margin: 0;
  }

  .content {
    margin: 0;
  }
</style>
