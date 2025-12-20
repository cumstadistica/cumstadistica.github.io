import feedparser
import tweepy
import os
from datetime import datetime, timezone

# Credenciales
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

# Leer RSS
feed = feedparser.parse("public/index.xml")
if not feed.entries:
    print("RSS vacío.")
    exit(0)

last_entry = feed.entries[0]
# Opcional: Solo publicar si el post es de hace menos de 1 hora
# para evitar duplicados en cada despliegue técnico.
print(f"Procesando: {last_entry.title}")

message = f"🚀 Nuevo post: {last_entry.title}\n\n{last_entry.link}"
client.create_tweet(text=message)
