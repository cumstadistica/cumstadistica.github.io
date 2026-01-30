#!/bin/bash
set -e

for file in "$@"; do
    if [ -f "$file" ]; then
        echo "🔄 Converting $file to WebP..."

        new_file="${file%.*}.webp"

        # Convert
        cwebp -q 80 "$file" -o "$new_file" -quiet

        # Add the new WebP
        git add "$new_file"
        
        # Force remove the old JPG
        git rm --force --quiet "$file"
    fi
done