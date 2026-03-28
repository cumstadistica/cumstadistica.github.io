#!/bin/bash
set -e

for file in "$@"; do
    if [ -f "$file" ]; then
        echo "🔄 Converting $file to WebP..."

        new_file="${file%.*}.webp"

        cwebp -q 80 "$file" -o "$new_file" -quiet

        git add "$new_file"
        git rm --force --quiet "$file"
    fi
done
