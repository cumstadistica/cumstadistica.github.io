---
layout: page
title: Filtrar por etiqueta
permalink: /tags/
---

<!-- Mostrar todos los tags como enlaces -->
<div>
  
  <a href="/tags">Todos</a>
  {% for category in site.categories %}
  <div class="tag-button"><a href="#{{ category[0] }}">{{ category[0] }}</a> ({{ category[1] | size }})</div>
  {% endfor %}
  {% for tag in site.tags %}
  <div class="tag-button"><a href="#{{ tags[0] }}">{{ tags[0] }}</a> ({{ tags[1] | size }})</div>
  {% endfor %}


</div>

<hr>

<!-- Mostrar posts agrupados por tag -->
{% for category in site.categories %}
  <h2 id="{{ category[0] }}"><a href= "/tags/{{ category[0] }}">{{ category[0] }}</a></h2>
  <div>
  {% for post in category[1] %}
    <div><a href="{{ post.url }}">{{ post.title }}</a> - {{ post.date | date: "%Y-%m-%d" }}</div>
  {% endfor %}
  </div>
{% endfor %}
