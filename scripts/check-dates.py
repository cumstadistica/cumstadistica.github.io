#!/usr/bin/env python3
import re
import sys

# 1. Configuration
# Regex to capture YYYY-MM-DD from filename
filename_regex = re.compile(r".*[/\\](\d{4}-\d{2}-\d{2})-[^/]*\.md$")
# Regex to find existing date field (captures the whole line)
date_line_regex = re.compile(r"^date:\s*.*")

files_changed = False

for filepath in sys.argv[1:]:
    # --- Step 1: Check Filename ---
    match_file = filename_regex.match(filepath)
    if not match_file:
        continue  # Skip files without a date in the name

    filename_date = match_file.group(1)
    # We format it to match your example: 2025-10-15T00:00:00Z
    new_date_line = f'date: "{filename_date}T00:00:00Z"\n'

    # --- Step 2: Read Content ---
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except Exception:
        continue

    # --- Step 3: Logic to Update or Insert ---
    new_lines = []
    has_frontmatter = False
    in_frontmatter = False
    date_found = False
    file_modified = False

    # Check if file actually has frontmatter delimiters
    if len(lines) > 0 and lines[0].strip() == "---":
        has_frontmatter = True

    for i, line in enumerate(lines):
        # Track if we are inside the YAML frontmatter
        if line.strip() == "---":
            # If this is the second "---", and we haven't found a date yet, we might need to insert it
            if in_frontmatter and not date_found:
                # INSERTION LOGIC (End of Frontmatter)
                # If we didn't find a title to place it after, we insert it at the end of FM
                new_lines.append(new_date_line)
                print(f"➕ Added missing date to {filepath}")
                file_modified = True
                in_frontmatter = False  # We are leaving frontmatter
            elif not in_frontmatter:
                in_frontmatter = True
            else:
                in_frontmatter = False

            new_lines.append(line)
            continue

        # Process lines inside frontmatter
        if in_frontmatter:
            # Check for existing date
            if date_line_regex.match(line):
                date_found = True
                # CHECK MISMATCH
                # We check if the existing line contains our target date
                if filename_date not in line:
                    print(f"🔄 Updating date in {filepath} to {filename_date}")
                    new_lines.append(new_date_line)
                    file_modified = True
                else:
                    new_lines.append(line)  # It matches, keep it

            # INSERTION LOGIC (After Title - Preferred Spot)
            elif line.startswith("title:") and not date_found:
                new_lines.append(line)
                # We peek ahead to ensure we don't insert if date is on the next line
                # (Simple heuristic: just insert now, if date exists later the regex above handles it,
                # but duplicate keys are bad YAML. For simplicity, we assume well-formed YAML).
                # To be safe: We only insert here if we haven't seen date yet.
                # If date is actually *below* title, we might have a duplicate.
                # Let's use the 'End of Frontmatter' strategy instead?
                # Actually, standardizing on "After Title" is cleaner.
                # Let's keep it simple: We append the line. If we reach the end of FM and date_found is False, we insert.

            else:
                new_lines.append(line)
        else:
            new_lines.append(line)

    # --- Step 4: Write changes ---
    if file_modified:
        files_changed = True
        with open(filepath, "w", encoding="utf-8") as f:
            f.writelines(new_lines)

# Exit 1 so pre-commit stops and lets you review the changes
if files_changed:
    sys.exit(1)
