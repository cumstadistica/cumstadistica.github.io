#!/usr/bin/env python3
import os
import re
import sys


FILENAME_DATE_REGEX = re.compile(r"(\d{4}-\d{2}-\d{2})-[^/\\]+\.md$")
DATE_LINE_REGEX = re.compile(r"^date:\s*.*$")


def canonical_date_line(filepath):
    match = FILENAME_DATE_REGEX.search(filepath)
    if not match:
        return None
    return f'date: "{match.group(1)}T00:00:00Z"\n'


def replace_or_insert_date(lines, date_line):
    if not lines or lines[0].strip() != "---":
        return lines, False

    try:
        end_index = next(index for index in range(1, len(lines)) if lines[index].strip() == "---")
    except StopIteration:
        return lines, False

    frontmatter = lines[1:end_index]
    body = lines[end_index:]

    updated_frontmatter = []
    date_written = False
    changed = False

    for line in frontmatter:
        if DATE_LINE_REGEX.match(line):
            if not date_written:
                updated_frontmatter.append(date_line)
                date_written = True
                if line != date_line:
                    changed = True
            else:
                changed = True
            continue

        updated_frontmatter.append(line)

        if line.startswith("title:") and not date_written:
            updated_frontmatter.append(date_line)
            date_written = True
            changed = True

    if not date_written:
        updated_frontmatter.append(date_line)
        changed = True

    updated_lines = [lines[0], *updated_frontmatter, *body]
    return updated_lines, changed


def main():
    files_changed = False

    for filepath in sys.argv[1:]:
        normalized = filepath.replace("\\", "/")
        date_line = canonical_date_line(normalized)
        if date_line is None or not os.path.isfile(filepath):
            continue

        with open(filepath, "r", encoding="utf-8") as handle:
            lines = handle.readlines()

        updated_lines, changed = replace_or_insert_date(lines, date_line)
        if not changed or updated_lines == lines:
            continue

        with open(filepath, "w", encoding="utf-8") as handle:
            handle.writelines(updated_lines)

        files_changed = True
        print(f"🔄 Normalized date in {filepath}")

    if files_changed:
        sys.exit(1)


if __name__ == "__main__":
    main()
