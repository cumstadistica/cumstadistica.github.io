#!/usr/bin/env python3
import os
import re
import sys


ROOT = os.path.join("content", "es")
AUTHOR_ROOT = os.path.join(ROOT, "author")
DATED_FILENAME_REGEX = re.compile(r"(\d{4}-\d{2}-\d{2})-[^/\\]+\.md$")


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


def extract_frontmatter(path):
    with open(path, "r", encoding="utf-8") as handle:
        content = handle.read()

    parts = content.split("---", 2)
    if len(parts) < 3 or parts[0].strip():
        return None
    return parts[1]


def validate_file(path, valid_authors):
    relpath = os.path.relpath(path)

    if not path.endswith(".md") or os.path.basename(path) == "_index.md":
        return []

    if not path.startswith(ROOT):
        return []

    frontmatter = extract_frontmatter(path)
    if frontmatter is None:
        return [f"{relpath}: missing YAML front matter"]

    errors = []

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

    return errors


def main():
    valid_authors = load_valid_authors()
    all_errors = []

    for path in sys.argv[1:]:
        normalized = path.replace("\\", "/")
        all_errors.extend(validate_file(normalized, valid_authors))

    if all_errors:
        print("Front matter validation failed:")
        for error in all_errors:
            print(f"  - {error}")
        print("\nValid authors:")
        print("  - " + ", ".join(sorted(valid_authors)))
        sys.exit(1)


if __name__ == "__main__":
    main()
