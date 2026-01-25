# check before committing

```sh
poetry run flake8
poetry run pytest
poetry run ./manage.py check
poetry run ./manage.py makemigrations --check --dry-run
pnpm check
pnpm lint
pnpm test
```

some commands to fix issues:

```sh
poetry run isort .
poetry run ./manage.py makemigrations
pnpm format
```

# testing

Tests are super important! They need to be readable.

tests style:

- flat pytest functions (no test classes)
- place tests next to tested code using `_test.py` suffix: `notes/models.py` -> `notes/models_test.py`
- fixtures and factories go in the test module for the data's origin (e.g., User factories in `users/models_test.py`, Note factories in `notes/models_test.py`)

# api schema

we keep frontend and backend in sync by:

```sh
poetry run ./manage.py spectacular --file api-schema.yaml --lang en --fail-on-warn
pnpm generate-api-types
pnpm check
```

# architecture, design

we try to do "vertical slice" architecture

# writing or updating guidelines

dont micromanage. assume the reader of your documents is an intelligent software developer
dont explain basic concepts. dont say obvious things.

every line of ducmentation needs mainteneace so try to write as little as possible
