#!/usr/bin/env python3
import re
import sys


PATTERN = re.compile(r'(https?://[^\s"\'\)]+)|(\.(png|jpg|jpeg|PNG|JPG|JPEG))')


def replace_callback(match):
    if match.group(1):
        return match.group(1)
    return ".webp"


def main():
    files_changed = False

    for filepath in sys.argv[1:]:
        try:
            with open(filepath, "r", encoding="utf-8") as handle:
                content = handle.read()
        except OSError as exc:
            print(f"Error processing {filepath}: {exc}")
            continue

        new_content = PATTERN.sub(replace_callback, content)
        if new_content == content:
            continue

        with open(filepath, "w", encoding="utf-8") as handle:
            handle.write(new_content)

        files_changed = True
        print(f"📝 Updated raster image refs in {filepath}")

    if files_changed:
        sys.exit(1)


if __name__ == "__main__":
    main()
