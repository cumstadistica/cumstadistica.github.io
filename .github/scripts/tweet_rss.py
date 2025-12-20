import feedparser
import tweepy
import os
import sys

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

    # 3. Obtener tu propio ID de usuario y el último tweet
    try:
        me = client.get_me()
        user_id = me.data.id

        # Obtenemos el último tweet que publicaste
        last_tweets = client.get_users_tweets(id=user_id, max_results=5)

        if last_tweets.data:
            for tweet in last_tweets.data:
                # Si el link del post ya aparece en alguno de tus últimos 5 tweets, abortamos
                if new_post_url in tweet.text:
                    print(
                        f"El post '{new_post_title}' ya fue publicado anteriormente. Saltando..."
                    )
                    return

    except Exception as e:
        print(f"Error al verificar el historial de X: {e}")
        # En caso de error de lectura, podemos decidir si seguir o no.
        # Aquí seguimos por si es la primera vez que publicas.

    # 4. Publicar si es nuevo
    message = f"¡Nuevo Facto! 🚀\n\n{new_post_title}\n\nLéelo aquí: {new_post_url}"

    try:
        client.create_tweet(text=message)
        print("¡Tweet publicado con éxito!")
    except tweepy.errors.Forbidden as e:
        print(
            f"Error 403: Revisa que tus tokens tengan permiso de 'Read and Write'.\n{e}"
        )
    except Exception as e:
        print(f"Error al publicar: {e}")


if __name__ == "__main__":
    check_and_post()
