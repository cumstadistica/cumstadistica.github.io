import os
import sys
from bs4 import BeautifulSoup
from urllib.parse import urlparse, unquote

PUBLIC_DIR = os.path.join(os.getcwd(), "public")
SITE_HOSTS = {"cumstadistica.es", "cumstadistica.github.io"}
BROKEN_LINKS = []


def resolve_path(source_file, link):
    link = unquote(link)
    parsed = urlparse(link)
    if parsed.scheme in {"http", "https"} and parsed.netloc.lower() not in SITE_HOSTS:
        return None

    path = parsed.path

    if not path:
        return None

    if path.startswith('/'):
        target = os.path.join(PUBLIC_DIR, path.lstrip('/'))
    else:
        source_dir = os.path.dirname(source_file)
        target = os.path.join(source_dir, path)

    return os.path.normpath(target)


def check_file_exists(path):
    if os.path.isfile(path):
        return True
    if os.path.isdir(path) and os.path.isfile(os.path.join(path, 'index.html')):
        return True
    return False


def process_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as handle:
            soup = BeautifulSoup(handle, "html.parser")
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return

    for a in soup.find_all('a', href=True):
        href = a['href']
        href = href.strip()
        
        if not href or href.startswith('#') or href.startswith('mailto:') or href.startswith('tel:'):
            continue

        target_path = resolve_path(file_path, href)
        if target_path and not check_file_exists(target_path) and not check_file_exists(target_path + '.html'):
            BROKEN_LINKS.append((file_path, href))


def main():
    if not os.path.isdir(PUBLIC_DIR):
        print(f"Generated site directory not found: {PUBLIC_DIR}")
        print("Run `task build` before checking links.")
        sys.exit(1)

    print(f"Scanning directory: {PUBLIC_DIR}")
    html_files = []
    for root, dirs, files in os.walk(PUBLIC_DIR):
        for file in files:
            if file.endswith('.html'):
                html_files.append(os.path.join(root, file))

    print(f"Found {len(html_files)} HTML files. Checking internal links...")

    for file_path in html_files:
        process_file(file_path)

    if BROKEN_LINKS:
        print(f"\nFound {len(BROKEN_LINKS)} broken internal links:")
        for source, link in BROKEN_LINKS:
            rel_source = os.path.relpath(source, os.getcwd())
            print(f"  In {rel_source}: {link}")
        sys.exit(1)
    else:
        print("\nNo broken internal links found.")


if __name__ == "__main__":
    main()
