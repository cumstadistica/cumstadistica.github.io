#!/usr/bin/env python3
import os
import re
import sys


ROOT = "content"
AUTHOR_ROOT = os.path.join(ROOT, "author")
DATED_FILENAME_REGEX = re.compile(r"(\d{4}-\d{2}-\d{2})-[^/\\]+\.md$")
DISALLOWED_TAGS = {
    "j",
    "ma",
    "review",
    "reviewsdej",
    "diario",
    "lugar",
    "lugares",
}


def load_valid_authors():
    authors = set()
    for dirpath, _, filenames in os.walk(AUTHOR_ROOT):
        if dirpath == AUTHOR_ROOT:
            continue
        if "_index.md" in filenames:
            authors.add(os.path.basename(dirpath))
    return authors


def parse_author_value(raw):
    raw = raw.strip()
    if not raw:
        return []

    if raw.startswith("[") and raw.endswith("]"):
        inner = raw[1:-1].strip()
        if not inner:
            return []
        values = []
        for part in inner.split(","):
            value = part.strip().strip("\"'")
            if value:
                values.append(value)
        return values

    return [raw.strip("\"'")]


def parse_list_value(raw):
    raw = raw.strip()
    if not raw:
        return []

    if raw.startswith("[") and raw.endswith("]"):
        inner = raw[1:-1].strip()
        if not inner:
            return []
        values = []
        for part in inner.split(","):
            value = part.strip().strip("\"'")
            if value:
                values.append(value)
        return values

    return [raw.strip("\"'")]


def extract_frontmatter(path):
    with open(path, "r", encoding="utf-8") as handle:
        content = handle.read()

    parts = content.split("---", 2)
    if len(parts) < 3 or parts[0].strip():
        return None
    return parts[1]


def top_level_keys(frontmatter):
    keys = []
    for line in frontmatter.splitlines():
        if not line.strip() or line.startswith((" ", "\t")) or line.lstrip().startswith("- "):
            continue
        match = re.match(r"^([A-Za-z0-9_-]+):", line)
        if match:
            keys.append(match.group(1))
    return keys


def validate_file(path, valid_authors):
    relpath = os.path.relpath(path)

    if not path.endswith(".md") or os.path.basename(path) == "_index.md":
        return [], []

    if not path.startswith(ROOT):
        return [], []

    parts = path.replace("\\", "/").split("/")
    if len(parts) < 3:
        return [], []

    frontmatter = extract_frontmatter(path)
    if frontmatter is None:
        return [f"{relpath}: missing YAML front matter"], []

    errors = []
    warnings = []

    keys = top_level_keys(frontmatter)
    duplicates = sorted({key for key in keys if keys.count(key) > 1})
    if duplicates:
        errors.append(f"{relpath}: duplicate front matter keys: {', '.join(duplicates)}")

    author_match = re.search(r"^author:\s*(.+)$", frontmatter, re.MULTILINE)
    if not author_match:
        errors.append(f"{relpath}: missing author")
    else:
        authors = parse_author_value(author_match.group(1))
        if not authors:
            errors.append(f"{relpath}: empty author")
        else:
            invalid = [author for author in authors if author not in valid_authors]
            if invalid:
                joined = ", ".join(invalid)
                errors.append(f"{relpath}: invalid author(s): {joined}")

    date_match = re.search(r"^date:\s*(.+)$", frontmatter, re.MULTILINE)
    if not date_match or not date_match.group(1).strip():
        errors.append(f"{relpath}: missing date")
    else:
        filename_match = DATED_FILENAME_REGEX.search(path.replace("\\", "/"))
        if filename_match:
            expected = f'"{filename_match.group(1)}T00:00:00Z"'
            actual = date_match.group(1).strip()
            if actual != expected:
                errors.append(f"{relpath}: date must be {expected} for dated filenames")

    section = parts[1]
    categories_match = re.search(r"^categories:\s*(.+)$", frontmatter, re.MULTILINE)
    if categories_match and section not in {"author", "categories", "tags"}:
        raw_categories = categories_match.group(1).strip()
        if raw_categories.startswith("[") and raw_categories.endswith("]"):
            categories = [part.strip().strip("\"'") for part in raw_categories[1:-1].split(",") if part.strip()]
            if len(categories) == 1 and categories[0] == section:
                warnings.append(f"{relpath}: categories duplicates the section name '{section}'")

    tags_match = re.search(r"^tags:\s*(.+)$", frontmatter, re.MULTILINE)
    if tags_match:
        tags = parse_list_value(tags_match.group(1))
        disallowed = sorted({tag for tag in tags if tag.lower() in DISALLOWED_TAGS})
        if disallowed:
            errors.append(f"{relpath}: disallowed tag(s): {', '.join(disallowed)}")

    return errors, warnings


def main():
    valid_authors = load_valid_authors()
    all_errors = []
    all_warnings = []

    for path in sys.argv[1:]:
        normalized = path.replace("\\", "/")
        errors, warnings = validate_file(normalized, valid_authors)
        all_errors.extend(errors)
        all_warnings.extend(warnings)

    if all_warnings:
        print("Front matter warnings:")
        for warning in all_warnings:
            print(f"  - {warning}")
        print()

    if all_errors:
        print("Front matter validation failed:")
        for error in all_errors:
            print(f"  - {error}")
        print("\nValid authors:")
        print("  - " + ", ".join(sorted(valid_authors)))
        sys.exit(1)


if __name__ == "__main__":
    main()
