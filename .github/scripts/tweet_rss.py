import feedparser
import tweepy
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# 1. Configuración de credenciales
api_key = os.getenv("X_API_KEY")
api_secret = os.getenv("X_API_SECRET")
access_token = os.getenv("X_ACCESS_TOKEN")
access_token_secret = os.getenv("X_ACCESS_TOKEN_SECRET")

# Autenticación
client = tweepy.Client(
    consumer_key=api_key,
    consumer_secret=api_secret,
    access_token=access_token,
    access_token_secret=access_token_secret,
)

# Archivo para registrar posts ya tuiteados
TWEETED_FILE = Path(__file__).parent / ".tweeted_posts.txt"


def load_tweeted_urls() -> set[str]:
    """Carga las URLs de posts ya tuiteados desde el archivo local."""
    if not TWEETED_FILE.exists():
        return set()

    with open(TWEETED_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip())


def save_tweeted_url(url: str) -> None:
    """Guarda una URL como ya tuiteada."""
    with open(TWEETED_FILE, "a", encoding="utf-8") as f:
        f.write(url + "\n")


def check_and_post():
    # 2. Parsear el RSS de Hugo
    # Asegúrate de que la ruta sea correcta tras el build (ej. public/index.xml)
    rss_path = "public/index.xml"
    if not os.path.exists(rss_path):
        print(f"Error: No se encuentra el archivo {rss_path}")
        return

    feed = feedparser.parse(rss_path)
    if not feed.entries:
        print("RSS vacío.")
        return

    last_entry = feed.entries[0]
    new_post_title = last_entry.title
    new_post_url = last_entry.link

    print(f"Procesando: {new_post_title}")

    # 3. Verificar si ya fue tuiteado usando archivo local
    tweeted_urls = load_tweeted_urls()
    if new_post_url in tweeted_urls:
        print(f"El post '{new_post_title}' ya fue publicado anteriormente. Saltando...")
        return

    # 4. Publicar el tweet
    message = f"¡Nuevo Facto! 🚀\n\n{new_post_title}\n\nLéelo aquí: {new_post_url}"

    try:
        response = client.create_tweet(text=message)
        print(f"✓ ¡Tweet publicado con éxito! Tweet ID: {response.data['id']}")

        # Guardar la URL como tuiteada
        save_tweeted_url(new_post_url)
        print(f"✓ URL registrada en {TWEETED_FILE}")

    except tweepy.errors.Forbidden as e:
        print(
            f"Error 403: Revisa que tus tokens tengan permiso de 'Read and Write'.\n{e}"
        )
    except Exception as e:
        print(f"Error al publicar: {e}")


if __name__ == "__main__":
    check_and_post()
