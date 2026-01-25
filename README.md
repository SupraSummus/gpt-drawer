# stack

backend:

- poetry
- django

frontend:

- pnpm
- [sveltekit](https://svelte.dev/docs/kit/)

## Developing

Once you've installed dependencies with `pnpm install`, start a development server:

```sh
pnpm run dev

# or start the server and open the app in a new browser tab
pnpm run dev -- --open
```

## Building

To create a production version of your app:

```sh
pnpm run build
```

You can preview the production build with `pnpm run preview`.

## Api schema

```sh
./manage.py spectacular --file api-schema.yaml --lang en --fail-on-warn && pnpm run generate-api-types
```
