#!/usr/bin/env python3
import os
import re
import sys


CANONICAL_ORDER = [
    "title",
    "date",
    "author",
    "categories",
    "tags",
    "nota",
    "description",
    "layout",
    "permalink",
    "weight",
    "outputs",
    "draft",
    "headless",
    "cascade",
]

TOP_LEVEL_KEY_REGEX = re.compile(r"^([A-Za-z0-9_-]+):")


def order_index(key):
    try:
        return CANONICAL_ORDER.index(key)
    except ValueError:
        return len(CANONICAL_ORDER)


def split_frontmatter_blocks(lines):
    blocks = []
    current_key = None
    current_lines = []

    for line in lines:
        key_match = TOP_LEVEL_KEY_REGEX.match(line)
        is_top_level = key_match and not line.startswith((" ", "\t"))

        if is_top_level:
            if current_lines:
                blocks.append((current_key, current_lines))
            current_key = key_match.group(1)
            current_lines = [line]
            continue

        if current_lines:
            current_lines.append(line)
        else:
            blocks.append((None, [line]))

    if current_lines:
        blocks.append((current_key, current_lines))

    return blocks


def reorder_frontmatter(lines):
    if not lines or lines[0].strip() != "---":
        return lines, False

    try:
        end_index = next(index for index in range(1, len(lines)) if lines[index].strip() == "---")
    except StopIteration:
        return lines, False

    frontmatter_lines = lines[1:end_index]
    body_lines = lines[end_index:]
    blocks = split_frontmatter_blocks(frontmatter_lines)

    preamble = [block for block in blocks if block[0] is None]
    keyed_blocks = [(key, block_lines, position) for position, (key, block_lines) in enumerate(blocks) if key is not None]

    keyed_blocks.sort(key=lambda item: (order_index(item[0]), item[2]))

    reordered_frontmatter = []
    for _, block_lines in preamble:
        reordered_frontmatter.extend(block_lines)
    for _, block_lines, _ in keyed_blocks:
        reordered_frontmatter.extend(block_lines)

    updated_lines = [lines[0], *reordered_frontmatter, *body_lines]
    return updated_lines, updated_lines != lines


def main():
    files_changed = False

    for filepath in sys.argv[1:]:
        if not filepath.endswith(".md") or not os.path.isfile(filepath):
            continue

        with open(filepath, "r", encoding="utf-8") as handle:
            lines = handle.readlines()

        updated_lines, changed = reorder_frontmatter(lines)
        if not changed:
            continue

        with open(filepath, "w", encoding="utf-8") as handle:
            handle.writelines(updated_lines)

        files_changed = True
        print(f"🔀 Reordered front matter in {filepath}")

    if files_changed:
        sys.exit(1)


if __name__ == "__main__":
    main()
