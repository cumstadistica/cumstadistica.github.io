#!/usr/bin/env python3
import sys
import re
import os

# Regex to find YYYY-MM-DD in the filename (e.g., /path/to/2025-10-15-my-post.md)
# It captures the date in group 1
filename_regex = re.compile(r".*[/\\](\d{4}-\d{2}-\d{2})-[^/]*\.md$")

# Regex to find the date field in YAML frontmatter
# It handles date: "2025..." or date: 2025...
# It captures the date in group 1
metadata_regex = re.compile(r"^date:\s*[\"']?(\d{4}-\d{2}-\d{2})")

files_changed = False

for filepath in sys.argv[1:]:
    # 1. Extract date from filename
    match_file = filename_regex.match(filepath)

    # If file doesn't start with a date, skip it
    if not match_file:
        continue

    filename_date = match_file.group(1)

    # 2. Read the file content
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except UnicodeDecodeError:
        continue  # Skip binary files

    new_lines = []
    file_modified = False

    for line in lines:
        # Check if current line is the 'date:' metadata
        match_meta = metadata_regex.match(line)

        if match_meta:
            meta_date = match_meta.group(1)

            # 3. Compare Dates
            if meta_date != filename_date:
                print(f"⚠️  Mismatch in {filepath}")
                print(f"   Filename: {filename_date} | Metadata: {meta_date}")
                print(f"   ACTION: Deleting 'date' line from metadata.")
                file_modified = True
                files_changed = True
                continue  # Skip adding this line (effectively deleting it)

        # Add line to buffer if it wasn't deleted
        new_lines.append(line)

    # 4. Write changes back to file if needed
    if file_modified:
        with open(filepath, "w", encoding="utf-8") as f:
            f.writelines(new_lines)

# Exit with error code 1 if we changed files, so pre-commit stops the commit
# and lets the user review the deletion.
if files_changed:
    sys.exit(1)
