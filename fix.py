import os
import re

# CONFIGURATION
CONTENT_DIR = "content"

# Regex to find shortcode parameters with double double-quotes
# Matches: key=""value""  ->  Captures: 1=key, 2=value
# Example: alt=""Hello""  ->  alt="Hello"
DOUBLE_QUOTE_PATTERN = re.compile(r'([a-zA-Z0-9_]+)=""([^"]+)""')


def fix_quotes(match):
    key = match.group(1)
    value = match.group(2)
    # Return corrected format: key="value"
    return f'{key}="{value}"'


def process_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # We only run this regex inside shortcodes {{< ... >}} to avoid breaking other code
    # This function uses a callback to replace the bad quotes found inside the shortcodes
    def replace_in_shortcode(m):
        shortcode_content = m.group(0)
        return DOUBLE_QUOTE_PATTERN.sub(fix_quotes, shortcode_content)

    # Find shortcodes and apply the fix inside them
    # Pattern looks for {{< ... >}}
    SHORTCODE_BLOCK = re.compile(r"{{<.*?>}}", re.DOTALL)

    new_content, count = SHORTCODE_BLOCK.subn(replace_in_shortcode, content)

    # Note: subn counts the number of SHORTCODES processed, not the number of quotes fixed.
    # So we check if the content actually changed.
    if new_content != content:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"Fixed quotes in: {filepath}")


def main():
    print('Scanning for double double-quotes (e.g. alt=""Text"")...')
    for root, dirs, files in os.walk(CONTENT_DIR):
        for file in files:
            if file.endswith(".md"):
                process_file(os.path.join(root, file))
    print("Done!")


if __name__ == "__main__":
    main()
