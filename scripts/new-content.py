#!/usr/bin/env python3
import argparse
import datetime as dt
import os
import re
import unicodedata


CATEGORIES_ROOT = os.path.join("content", "categories")


def slugify(value):
    normalized = unicodedata.normalize("NFKD", value)
    ascii_value = "".join(char for char in normalized if not unicodedata.combining(char))
    lowered = ascii_value.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", lowered).strip("-")
    return slug or "nuevo-contenido"


def category_path(category):
    return os.path.join(CATEGORIES_ROOT, category, "_index.md")


def existing_categories():
    if not os.path.isdir(CATEGORIES_ROOT):
        return []

    return sorted(
        entry
        for entry in os.listdir(CATEGORIES_ROOT)
        if os.path.isfile(category_path(entry))
    )


def infer_section(category):
    path = category_path(category)
    if not os.path.isfile(path):
        categories = ", ".join(existing_categories()) or "none"
        raise SystemExit(f"Unknown category '{category}'. Existing categories: {categories}")

    if os.path.isdir(os.path.join("content", category)):
        return category

    raise SystemExit(f"Category '{category}' exists, but no matching content section was found")


def parse_list_value(raw):
    raw = raw.strip()
    if not raw:
        return []

    if raw.startswith("[") and raw.endswith("]"):
        inner = raw[1:-1].strip()
        if not inner:
            return []
        return [part.strip().strip("\"'") for part in inner.split(",") if part.strip()]

    return [raw.strip("\"'")]


def quote_yaml_string(value):
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def render_list_block(key, values):
    if not values:
        return f"{key}: []\n"

    rendered_values = "".join(f"  - {quote_yaml_string(value)}\n" for value in values)
    return f"{key}:\n{rendered_values}"


def render_frontmatter(title, today, author, draft, category=None):
    draft_value = "true" if draft else "false"
    author_block = render_list_block("author", parse_list_value(author))
    categories_block = render_list_block("categories", [category]) if category else ""
    return f"""---
title: "{title}"
date: "{today}T00:00:00Z"
{author_block}{categories_block}tags: []
draft: {draft_value}
---

Resumen breve.

<!--more-->

Contenido.
"""


def main():
    parser = argparse.ArgumentParser(description="Create a dated Hugo Markdown content file.")
    parser.add_argument("section", help="Content section, for example reviews or cronicas.")
    parser.add_argument("title", nargs="+", help="Title for the new content.")
    parser.add_argument("--category", action="store_true", help="Treat section as a category and validate it.")
    parser.add_argument("--author", default="REPLACE_ME", help="Front matter author value.")
    parser.add_argument("--date", default=dt.date.today().isoformat(), help="Date in YYYY-MM-DD format.")
    parser.add_argument("--draft", action="store_true", help="Mark the new content as draft.")
    args = parser.parse_args()

    title = " ".join(args.title).strip()
    slug = slugify(title)
    category = args.section.strip("/") if args.category else None
    section = infer_section(category) if category else args.section.strip("/")
    path = os.path.join("content", section, f"{args.date}-{slug}.md")

    if os.path.exists(path):
        raise SystemExit(f"Refusing to overwrite existing file: {path}")

    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(render_frontmatter(title, args.date, args.author, args.draft, category))

    print(path)


if __name__ == "__main__":
    main()
