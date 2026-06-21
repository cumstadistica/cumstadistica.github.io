import argparse
import os
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

import feedparser
import tweepy
from bs4 import BeautifulSoup


SCRIPT_DIR = Path(__file__).parent
TWEETED_FILE = SCRIPT_DIR / ".tweeted_posts.txt"
DEFAULT_RSS_PATH = Path("public/index.xml")
DEFAULT_SITE_DIR = Path("public")
MAX_TWEET_CHARS = 280
MAX_IMAGE_COUNT = 4
TCO_URL_LENGTH = 23
STATIC_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
GIF_EXTENSION = ".gif"


def load_tweeted_urls() -> set[str]:
    if not TWEETED_FILE.exists():
        return set()

    return {
        line.strip()
        for line in TWEETED_FILE.read_text(encoding="utf-8").splitlines()
        if line.strip()
    }


def save_tweeted_url(url: str) -> None:
    with TWEETED_FILE.open("a", encoding="utf-8") as f:
        f.write(url + "\n")


def normalize_space(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def truncate(value: str, max_length: int) -> str:
    if max_length <= 0:
        return ""
    if len(value) <= max_length:
        return value
    return value[: max_length - 1].rstrip() + "…"


def tweet_length(text: str) -> int:
    # X counts every URL as a t.co URL. This approximation keeps us safely under
    # the API limit without pulling in a heavier twitter-text dependency.
    url_pattern = re.compile(r"https?://\S+")
    length = len(text)
    for match in url_pattern.finditer(text):
        length += TCO_URL_LENGTH - len(match.group(0))
    return length


def build_tweet_text(title: str, excerpt: str, url: str) -> str:
    if not excerpt:
        return truncate(f"{title}\n\n{url}", MAX_TWEET_CHARS)

    text = f"{title}\n\n{excerpt}\n\n{url}"
    extra = tweet_length(text) - MAX_TWEET_CHARS
    if extra <= 0:
        return text

    shortened_excerpt = truncate(excerpt, len(excerpt) - extra)
    return f"{title}\n\n{shortened_excerpt}\n\n{url}"


def entry_html_path(entry_url: str, site_dir: Path) -> Path:
    path = urlparse(entry_url).path
    if not path or path.endswith("/"):
        return site_dir / path.lstrip("/") / "index.html"
    if Path(path).suffix:
        return site_dir / path.lstrip("/")
    return site_dir / path.lstrip("/") / "index.html"


def image_path_from_src(src: str, site_dir: Path) -> Path | None:
    parsed = urlparse(src)
    if parsed.scheme and parsed.scheme not in {"http", "https"}:
        return None
    if parsed.scheme in {"http", "https"}:
        src_path = parsed.path
    else:
        src_path = src

    path = Path(src_path.lstrip("/"))
    local_path = site_dir / path
    return local_path if local_path.exists() else None


def extract_post_payload(entry, site_dir: Path) -> tuple[str, list[Path]]:
    html_path = entry_html_path(entry.link, site_dir)
    if not html_path.exists():
        print(f"No se encuentra el HTML del post: {html_path}")
        return "", []

    soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "html.parser")
    content = soup.select_one(".nested-copy-line-height.lh-copy")
    if content is None:
        print(f"No se encuentra el contenido principal en: {html_path}")
        return "", []

    text_parts: list[str] = []
    for element in content.find_all(["p", "h2", "h3", "blockquote"]):
        if element.find_parent("figure"):
            continue
        text = normalize_space(element.get_text(" ", strip=True))
        if text:
            text_parts.append(text)

    excerpt = normalize_space(" ".join(text_parts))

    image_paths: list[Path] = []
    seen: set[Path] = set()
    for img in content.select("img[src]"):
        local_path = image_path_from_src(img["src"], site_dir)
        if local_path is None or local_path in seen:
            continue
        suffix = local_path.suffix.lower()
        if suffix not in STATIC_IMAGE_EXTENSIONS and suffix != GIF_EXTENSION:
            continue
        seen.add(local_path)
        image_paths.append(local_path)

    gif_paths = [path for path in image_paths if path.suffix.lower() == GIF_EXTENSION]
    if gif_paths:
        return excerpt, gif_paths[:1]

    return excerpt, image_paths[:MAX_IMAGE_COUNT]


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Falta la variable de entorno {name}")
    return value


def build_tweepy_clients() -> tuple[tweepy.Client, tweepy.API]:
    api_key = require_env("X_API_KEY")
    api_secret = require_env("X_API_SECRET")
    access_token = require_env("X_ACCESS_TOKEN")
    access_token_secret = require_env("X_ACCESS_TOKEN_SECRET")

    client = tweepy.Client(
        consumer_key=api_key,
        consumer_secret=api_secret,
        access_token=access_token,
        access_token_secret=access_token_secret,
    )

    auth = tweepy.OAuth1UserHandler(
        consumer_key=api_key,
        consumer_secret=api_secret,
        access_token=access_token,
        access_token_secret=access_token_secret,
    )
    return client, tweepy.API(auth)


def upload_media(api: tweepy.API, image_paths: list[Path]) -> list[str]:
    media_ids: list[str] = []
    for image_path in image_paths:
        is_gif = image_path.suffix.lower() == GIF_EXTENSION
        response = api.media_upload(
            str(image_path),
            chunked=is_gif,
            media_category="tweet_gif" if is_gif else "tweet_image",
        )
        media_ids.append(response.media_id_string)
        print(f"Imagen subida: {image_path}")
    return media_ids


def latest_entry_from_rss(rss_path: Path):
    if not rss_path.exists():
        raise FileNotFoundError(f"No se encuentra el archivo {rss_path}")

    feed = feedparser.parse(str(rss_path))
    if not feed.entries:
        raise RuntimeError("RSS vacío.")
    return feed.entries[0]


def check_and_post(args: argparse.Namespace) -> int:
    entry = latest_entry_from_rss(args.rss)
    title = entry.title
    url = entry.link

    print(f"Procesando: {title}")
    print(f"URL: {url}")

    tweeted_urls = load_tweeted_urls()
    if url in tweeted_urls:
        print(f"El post '{title}' ya fue publicado anteriormente. Saltando...")
        return 0

    excerpt, image_paths = extract_post_payload(entry, args.site)
    tweet_text = build_tweet_text(title, excerpt, url)

    print("\nTweet preparado:")
    print(tweet_text)
    print(f"\nLongitud estimada: {tweet_length(tweet_text)}/{MAX_TWEET_CHARS}")
    if image_paths:
        print("\nImágenes:")
        for image_path in image_paths:
            print(f"- {image_path}")
    else:
        print("\nSin imágenes adjuntas.")

    if args.dry_run:
        print("\nDry-run activo: no se publica ni se marca como tuiteado.")
        return 0

    try:
        client, api = build_tweepy_clients()
        media_ids = upload_media(api, image_paths)
        response = client.create_tweet(
            text=tweet_text,
            media_ids=media_ids or None,
            user_auth=True,
        )
        print(f"Tweet publicado con éxito. Tweet ID: {response.data['id']}")

        save_tweeted_url(url)
        print(f"URL registrada en {TWEETED_FILE}")
        return 0
    except tweepy.errors.Forbidden as e:
        print(
            "Error 403: revisa que tus tokens tengan permisos de Read and Write.\n"
            f"{e}"
        )
    except Exception as e:
        print(f"Error al publicar: {e}")

    return 1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Publica en X el último post del RSS con texto e imágenes."
    )
    parser.add_argument("--rss", type=Path, default=DEFAULT_RSS_PATH)
    parser.add_argument("--site", type=Path, default=DEFAULT_SITE_DIR)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Prepara el tweet sin llamar a la API ni registrar el post.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    sys.exit(check_and_post(parse_args()))
