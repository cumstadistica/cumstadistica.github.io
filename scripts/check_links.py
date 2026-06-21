import os
import sys
from bs4 import BeautifulSoup
from urllib.parse import urlparse, unquote

PUBLIC_DIR = os.path.join(os.getcwd(), "public")
SITE_HOSTS = {"cumstadistica.es", "cumstadistica.github.io"}
BROKEN_REFERENCES = []
URL_SCHEMES_TO_SKIP = ("#", "mailto:", "tel:", "data:", "blob:", "javascript:")
PATH_PREFIXES_TO_SKIP = ("/pagefind/",)


REFERENCE_ATTRIBUTES = {
    "a": ("href",),
    "audio": ("src",),
    "embed": ("src",),
    "iframe": ("src",),
    "img": ("src", "srcset"),
    "link": ("href",),
    "script": ("src",),
    "source": ("src", "srcset"),
    "track": ("src",),
    "video": ("src", "poster"),
}


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


def srcset_urls(value):
    for candidate in value.split(","):
        parts = candidate.strip().split()
        if parts:
            yield parts[0]


def attribute_urls(attribute, value):
    if attribute == "srcset":
        yield from srcset_urls(value)
        return

    yield value


def should_skip_reference(url):
    if not url or url.startswith(URL_SCHEMES_TO_SKIP):
        return True

    parsed = urlparse(url)
    return parsed.path.startswith(PATH_PREFIXES_TO_SKIP)


def process_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as handle:
            soup = BeautifulSoup(handle, "html.parser")
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return

    for tag_name, attributes in REFERENCE_ATTRIBUTES.items():
        for element in soup.find_all(tag_name):
            for attribute in attributes:
                if not element.has_attr(attribute):
                    continue

                for url in attribute_urls(attribute, element[attribute].strip()):
                    if should_skip_reference(url):
                        continue

                    target_path = resolve_path(file_path, url)
                    if target_path and not check_file_exists(target_path) and not check_file_exists(target_path + '.html'):
                        BROKEN_REFERENCES.append((file_path, tag_name, attribute, url))


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

    print(f"Found {len(html_files)} HTML files. Checking internal references...")

    for file_path in html_files:
        process_file(file_path)

    if BROKEN_REFERENCES:
        print(f"\nFound {len(BROKEN_REFERENCES)} broken internal references:")
        for source, tag_name, attribute, url in BROKEN_REFERENCES:
            rel_source = os.path.relpath(source, os.getcwd())
            print(f"  In {rel_source}: <{tag_name} {attribute}> {url}")
        sys.exit(1)
    else:
        print("\nNo broken internal references found.")


if __name__ == "__main__":
    main()
