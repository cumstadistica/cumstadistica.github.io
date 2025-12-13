---
title: "Cómo funciona la web de Cumstadística?"
author: ["c"]
date: "2025-12-13T00:00:00Z"
---

Estimado lector del sitio web de Cumstadística,

me congratulo de saludarle por aquí.

Como UD puede ver, Cumstadística no es un blog al uso, sino extractos de un grupo de amigos integrado por J, U y C.

La idea de construir una web para conservar nuestro ingenio (y de paso mostrárselo a quien esté interesado) llevaba ya años rondando nuestras cabezas, pero lo cierto es que era muy tedioso el trabajo de pasar los mensajes de Telegram a posts en Markdown. Por lo arduo de la tarea, en esta primera etapa, sólo una pequeña porción del contenido fue subido a la web.

## La Solución

Yo, Cusa la mastermind detrás de la web, tenía claro que la solución pasaba por utilizar algún tipo de bot de Telegram que creara posts automáticamente a partir de mensajes.

Otros internautas ya habían desarrolado soluciones en este sentido, así que sin mucho esfuerzo pude adoptar un Bot de Telegram que convertía mensajes en posts de Jekyll. Además le añadí soporte para links, videos, etc.

Esto redujo un poco la frcción pero aún así, había que hacer limpieza manual de los posts, añadir metadatos, categorías, etc. Un rollazo, vamos.

## Automatización total

Así que me puse a programar un bot propio, que hiciera todo el proceso de generar posts automáticamente, sin intervención humana, nada más que hacía falta reenviar los mensajes al bot.

Para eso primero mudé la página de Jekyll a Hugo, ya que Hugo tiene un sistema de plantillas mucho más potente y flexible además de tener a día de hoy un desarrollo mucho más activo.

Luego programé el bot en Python, basandome en el bot original, pero añadiendo IA para generar los metadatos, categorías, títulos, etc. El bot también sube las imágenes y audios a la web automáticamente basado en la lógica del bot original.

Sin embargo, esto no es todo: utilizando la potencia de HUGO, al construir la web, se genera automáticamente una página llamada `index.json` donde se guardan los posibles autores, categorías, etiquetas, etc. Al generar un post, el bot utiliza los esquemas de esta página para generar los metadatos del post, gracias a esto, el bot puede generar posts con categorías y etiquetas coherentes con el resto de la web.

## Futuro

Escribo esto en diciembre de 2025, espero que esta prueba piloto funcione bien y la página web de Cumstadística pueda seguir creciendo.
