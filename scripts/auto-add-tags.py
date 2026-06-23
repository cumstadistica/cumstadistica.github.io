#!/usr/bin/env python3
import os
import re
import sys
import unicodedata


ROOT = "content"
TOP_LEVEL_KEY_REGEX = re.compile(r"^([A-Za-z0-9_-]+):")
LIST_ITEM_REGEX = re.compile(r"^\s*-\s*(.+?)\s*$")
LINK_REGEX = re.compile(r"\[([^\]]+)\]\([^)]+\)")
SHORTCODE_REGEX = re.compile(r"{{[%<].*?[>%]}}", re.DOTALL)
URL_REGEX = re.compile(r"https?://\S+")
DISALLOWED_TAGS = {
    "j",
    "ma",
    "review",
    "reviewsdej",
    "diario",
    "lugar",
    "lugares",
}


def strip_accents(value):
    normalized = unicodedata.normalize("NFKD", value)
    return "".join(char for char in normalized if not unicodedata.combining(char))


def normalize_for_match(value):
    value = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", value)
    value = value.replace("_", " ").replace("-", " ")
    value = strip_accents(value.lower())
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


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


def parse_frontmatter_list(frontmatter_lines, key):
    prefix = f"{key}:"

    for index, line in enumerate(frontmatter_lines):
        if not line.startswith(prefix):
            continue

        raw = line.split(":", 1)[1].strip()
        if raw:
            return parse_list_value(raw)

        values = []
        for list_line in frontmatter_lines[index + 1 :]:
            if TOP_LEVEL_KEY_REGEX.match(list_line):
                break

            match = LIST_ITEM_REGEX.match(list_line)
            if match:
                values.append(match.group(1).strip("\"'"))

        return values

    return None


def extract_parts(path):
    with open(path, "r", encoding="utf-8") as handle:
        lines = handle.readlines()

    if not lines or lines[0].strip() != "---":
        return None, None, None

    try:
        end_index = next(index for index in range(1, len(lines)) if lines[index].strip() == "---")
    except StopIteration:
        return None, None, None

    return lines, lines[1:end_index], lines[end_index + 1 :]


def frontmatter_key_range(frontmatter_lines, key):
    prefix = f"{key}:"

    for start, line in enumerate(frontmatter_lines):
        if not line.startswith(prefix):
            continue

        end = start + 1
        while end < len(frontmatter_lines) and not TOP_LEVEL_KEY_REGEX.match(frontmatter_lines[end]):
            end += 1

        return start, end

    return None


def frontmatter_uses_list(frontmatter_lines, key):
    key_range = frontmatter_key_range(frontmatter_lines, key)
    if key_range is None:
        return False

    start, end = key_range
    raw = frontmatter_lines[start].split(":", 1)[1].strip()
    return raw.startswith("[") or any(LIST_ITEM_REGEX.match(line) for line in frontmatter_lines[start + 1 : end])


def is_eligible_tag(tag):
    normalized = normalize_for_match(tag)
    if not normalized:
        return False

    if normalized in DISALLOWED_TAGS:
        return False

    collapsed = normalized.replace(" ", "")
    if len(collapsed) < 3:
        return False

    return True


def collect_tag_pool(paths):
    pool = {}

    for path in paths:
        _, frontmatter_lines, _ = extract_parts(path)
        if frontmatter_lines is None:
            continue

        tags = parse_frontmatter_list(frontmatter_lines, "tags")
        if tags is None:
            continue

        for tag in tags:
            if not is_eligible_tag(tag):
                continue

            normalized = normalize_for_match(tag)
            pool.setdefault(normalized, tag)

    return sorted(pool.items(), key=lambda item: (-len(item[0].split()), -len(item[0]), item[0]))


def body_to_searchable_text(body_lines):
    text = "".join(body_lines)
    text = SHORTCODE_REGEX.sub(" ", text)
    text = LINK_REGEX.sub(r"\1", text)
    text = URL_REGEX.sub(" ", text)
    return normalize_for_match(text)


def detect_matching_tags(body_lines, pool, existing_tags):
    haystack = body_to_searchable_text(body_lines)
    if not haystack:
        return []

    existing_normalized = {normalize_for_match(tag) for tag in existing_tags}
    matched = []

    for normalized, original in pool:
        if normalized in existing_normalized:
            continue

        pattern = rf"(?<![a-z0-9]){re.escape(normalized)}(?![a-z0-9])"
        matches = re.findall(pattern, haystack)
        minimum_matches = 1 if " " in normalized else 2
        if len(matches) >= minimum_matches:
            matched.append(original)

    return matched


def quote_yaml_string(value):
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def render_list_block(key, values):
    lines = [f"{key}:\n"]
    lines.extend(f"  - {quote_yaml_string(value)}\n" for value in values)
    return lines


def merge_list(frontmatter_lines, key, values, preceding_keys):
    updated = list(frontmatter_lines)
    rendered_lines = render_list_block(key, values)
    key_range = frontmatter_key_range(updated, key)

    if key_range is not None:
        start, end = key_range
        updated[start:end] = rendered_lines
        return updated

    insert_at = len(updated)
    for index, line in enumerate(updated):
        if not TOP_LEVEL_KEY_REGEX.match(line):
            continue
        field = line.split(":", 1)[0]
        if field in preceding_keys:
            insert_at = index + 1

    updated[insert_at:insert_at] = rendered_lines
    return updated


def merge_tags(frontmatter_lines, tags):
    return merge_list(frontmatter_lines, "tags", tags, {"title", "date", "author", "categories"})


def normalize_author_list(frontmatter_lines):
    authors = parse_frontmatter_list(frontmatter_lines, "author")
    if authors is None:
        return frontmatter_lines

    return merge_list(frontmatter_lines, "author", authors, {"title", "date"})


def main():
    target_paths = [
        path
        for path in sys.argv[1:]
        if path.startswith(ROOT) and path.endswith(".md") and os.path.basename(path) != "_index.md"
    ]
    if not target_paths:
        return

    all_paths = []
    for dirpath, _, filenames in os.walk(ROOT):
        for filename in filenames:
            if filename.endswith(".md") and filename != "_index.md":
                all_paths.append(os.path.join(dirpath, filename))

    tag_pool = collect_tag_pool(all_paths)
    files_changed = False

    for path in target_paths:
        lines, frontmatter_lines, body_lines = extract_parts(path)
        if frontmatter_lines is None:
            continue

        existing_tags = parse_frontmatter_list(frontmatter_lines, "tags") or []
        matched_tags = detect_matching_tags(body_lines, tag_pool, existing_tags)
        if not matched_tags:
            continue

        merged_tags = existing_tags + [tag for tag in matched_tags if tag not in existing_tags]
        updated_frontmatter = merge_tags(frontmatter_lines, merged_tags)
        updated_frontmatter = normalize_author_list(updated_frontmatter)
        updated_lines = ["---\n", *updated_frontmatter, "---\n", *body_lines]
        if updated_lines == lines:
            continue

        with open(path, "w", encoding="utf-8") as handle:
            handle.writelines(updated_lines)

        files_changed = True
        print(f"🏷️ Added tags to {path}: {', '.join(matched_tags)}")

    if files_changed:
        sys.exit(1)


if __name__ == "__main__":
    main()
