#!/usr/bin/env python3
import sys
import re

# 1. Compile the Smart Regex
# Group 1: Matches http:// or https:// followed by valid URL characters (Protects URLs)
# Group 2: Matches the extension we want to change (.jpg, .jpeg, etc)
pattern = re.compile(r'(https?://[^\s"\'\)]+)|(\.(jpg|jpeg|JPG|JPEG))')


def replace_callback(match):
    """
    If the regex finds a URL (Group 1), return it unchanged.
    If it finds just an extension (Group 2), return '.webp'.
    """
    if match.group(1):
        return match.group(1)  # Return the protected URL exactly as it was
    return ".webp"  # Return the new extension


files_changed = False

# 2. Loop through files
for filepath in sys.argv[1:]:
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # 3. Apply the smart replacement
        new_content = pattern.sub(replace_callback, content)

        # 4. Save if changes were made
        if content != new_content:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"📝 Updated extensions in {filepath} (ignoring external URLs)")
            files_changed = True

    except Exception as e:
        print(f"Error processing {filepath}: {e}")

# 5. Exit 1 to stop commit so you can review changes
if files_changed:
    sys.exit(1)
