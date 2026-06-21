# Cumstadistica.github.io

Static site built with Hugo.

## Requirements

- Hugo Extended
- Optional: Task, available as either `task` or `go-task`

## Tasks

Run `task --list` or `go-task --list` to see the command hub.

- `task python:install` creates `.venv` if needed and installs Python dependencies there.
- `task serve` starts the local Hugo server with drafts, future and expired content enabled.
- `task build` creates a production Hugo build in `public`.
- `task lint` runs the fast pre-commit hooks.
- `task fix` runs autofixing content hooks.
- `task check` builds the site and checks internal links.
- `task verify` runs `task lint` and `task check`.
- `task check:links:external` checks the generated site with Lychee, including external URLs.
- `task new -- <section> <title>` creates dated content in `content/<section>`.
- `task new:post -- <category> <title>` creates dated content in an existing category.
- `task new:review -- <title>` creates a dated review in `content/reviews`.
- `task redate -- <path>` normalizes front matter dates from dated filenames.
- `task format:frontmatter -- <path>` reorders Markdown front matter.
- `task update-mods` updates git submodules.
