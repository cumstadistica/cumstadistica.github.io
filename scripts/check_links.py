import os
import sys
from bs4 import BeautifulSoup
from urllib.parse import urlparse, unquote
import concurrent.futures
import requests

PUBLIC_DIR = os.path.join(os.getcwd(), 'public')
BROKEN_LINKS = []
EXTERNAL_LINKS = set()

def resolve_path(source_file, link):
    """
    Resolves a link found in source_file to an absolute filesystem path.
    """
    link = unquote(link)
    parsed = urlparse(link)
    path = parsed.path
    
    if not path:
        return None # Anchor only or empty

    # Absolute path (relative to site root)
    if path.startswith('/'):
        # Remove leading slash and join with PUBLIC_DIR
        target = os.path.join(PUBLIC_DIR, path.lstrip('/'))
    else:
        # Relative path
        source_dir = os.path.dirname(source_file)
        target = os.path.join(source_dir, path)
    
    # Normalize path
    target = os.path.normpath(target)
    
    return target

def check_file_exists(path):
    if os.path.isfile(path):
        return True
    # Check if it is a directory with index.html
    if os.path.isdir(path) and os.path.isfile(os.path.join(path, 'index.html')):
        return True
    return False

def process_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return

    for a in soup.find_all('a', href=True):
        href = a['href']
        href = href.strip()
        
        if not href or href.startswith('#') or href.startswith('mailto:') or href.startswith('tel:'):
            continue
            
        if href.startswith('http://') or href.startswith('https://'):
            EXTERNAL_LINKS.add(href)
            continue

        target_path = resolve_path(file_path, href)
        if target_path:
            if not check_file_exists(target_path):
                # Try appending .html? (Hugo sometimes links to /page which is /page.html or /page/index.html)
                # check_file_exists handles directory/index.html.
                # Let's check if appending .html works (for non-pretty URLs)
                if not check_file_exists(target_path + '.html'):
                     BROKEN_LINKS.append((file_path, href))

def main():
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
    else:
        print("\nNo broken internal links found.")

    # Optional: External links
    # print(f"\nFound {len(EXTERNAL_LINKS)} external links. (Not checked)")

if __name__ == "__main__":
    main()
