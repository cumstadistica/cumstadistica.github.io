#!/bin/bash

# Exit on error
set -e

# Loop through the files passed by pre-commit
for file in "$@"; do
    # Check if file exists (in case it was deleted in a previous step)
    if [ -f "$file" ]; then
        echo "🔄 Converting $file to WebP..."

        # 1. Define new filename
        # Replaces .jpg, .jpeg, .JPG, etc. with .webp
        new_file="${file%.*}.webp"

        # 2. Convert (using cwebp)
        # -q 80 sets quality to 80%. Adjust as needed.
        cwebp -q 80 "$file" -o "$new_file" -quiet

        # 3. Git operations
        # Add the new webp to the commit
        git add "$new_file"
        
        # Remove the old jpg from the commit and filesystem
        # (Remove this block if you want to keep both files)
        git rm --quiet "$file"
    fi
done