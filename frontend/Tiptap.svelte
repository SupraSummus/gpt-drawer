<script>
  import { onMount, onDestroy } from 'svelte'
  import { Editor } from '@tiptap/core'
  import Document from '@tiptap/extension-document'
  import Paragraph from '@tiptap/extension-paragraph'
  import Text from '@tiptap/extension-text'
  import Link from '@tiptap/extension-link'
  import BubbleMenu from '@tiptap/extension-bubble-menu'

  let element
  let bubble_menu_element
  let editor

  onMount(() => {
    editor = new Editor({
      element: element,
      extensions: [
        Document,
        Paragraph,
        Text,

        Link.configure({
          protocols: ['ftp', 'mailto'],
        }),

        BubbleMenu.configure({
          element: bubble_menu_element,
        }),
      ],
      content: '<p>Hello World! 🌍️ </p>',
      onTransaction: () => {
        // force re-render so `editor.isActive` works as expected
        editor = editor
      },
    })
  })

  onDestroy(() => {
    if (editor) {
      editor.destroy()
    }
  })
</script>

{#if editor}
  <button
    on:click={() => editor.chain().focus().toggleHeading({ level: 1}).run()}
    class:active={editor.isActive('heading', { level: 1 })}
  >
    H1
  </button>
  <button
    on:click={() => editor.chain().focus().toggleHeading({ level: 2 }).run()}
    class:active={editor.isActive('heading', { level: 2 })}
  >
    H2
  </button>
  <button on:click={() => editor.chain().focus().setParagraph().run()} class:active={editor.isActive('paragraph')}>
    P
  </button>
{/if}

<div bind:this={element} class='editor'>
  <div bind:this={bubble_menu_element}>
    <p>eee</p>
  </div>
</div>

{#if editor}
  <div class='output'>
    <pre>{editor.getText()}</pre>
  </div>
  <div class='output'>
    <pre>{editor.getHTML()}</pre>
  </div>
  <div class='output'>
    <pre>{JSON.stringify(editor.getJSON(), null, 2)}</pre>
  </div>
{/if}

<style>
  button.active {
    background: black;
    color: white;
  }

  .editor {
    margin-top: 1em;
    border: 1px solid #ccc;
    min-height: 200px;
  }

  .output {
    margin-top: 1em;
    border: 1px solid #ccc;
  }
</style>
