import os
import shutil

# CONFIGURATION
SOURCE_DIR = os.path.join("static", "assets")
DEST_DIR = os.path.join("static", "images")

# List of extensions to consider as images
IMAGE_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".svg",
    ".avif",
    ".ico",
    ".bmp",
    ".tiff",
}


def move_images():
    # 1. Check if source exists
    if not os.path.exists(SOURCE_DIR):
        print(f"Error: Source directory '{SOURCE_DIR}' does not exist.")
        return

    # 2. Create destination if it doesn't exist
    if not os.path.exists(DEST_DIR):
        os.makedirs(DEST_DIR)
        print(f"Created directory: {DEST_DIR}")

    print(f"Scanning '{SOURCE_DIR}' for images...")

    moved_count = 0

    # 3. Iterate through files in the source directory
    # We use os.listdir() to just get the files in that specific folder (not recursive)
    for filename in os.listdir(SOURCE_DIR):
        src_path = os.path.join(SOURCE_DIR, filename)

        # Skip directories, process files only
        if os.path.isfile(src_path):
            # Get file extension (lowercase)
            ext = os.path.splitext(filename)[1].lower()

            if ext in IMAGE_EXTENSIONS:
                dest_path = os.path.join(DEST_DIR, filename)

                # Check for collision
                if os.path.exists(dest_path):
                    print(f"  [SKIP] '{filename}' already exists in destination.")
                else:
                    try:
                        shutil.move(src_path, dest_path)
                        print(f"  [MOVE] {filename}")
                        moved_count += 1
                    except Exception as e:
                        print(f"  [ERROR] Could not move {filename}: {e}")

    print("---")
    print(f"Done! Moved {moved_count} image(s) to '{DEST_DIR}'.")


if __name__ == "__main__":
    move_images()
