---
layout: page
title: "Test de Personalidad Cumstatística"
---

# Test de Personalidad Cumstatística  

Responde con sinceridad para descubrir tu perfil en **las dos dimensiones Cumstatísticas**.

<form id="cumstatTest">
  <p><b>1. Alguien te dice que el póker es solo cuestión de azar. ¿Cómo reaccionas?</b></p>
  <input type="radio" name="q1" value="A:1,K:-0.5,C:0"> a) Explicas que es un juego de estrategia. (+10% Estrategia, -5% Comercial)<br>
  <input type="radio" name="q1" value="A:0,K:0.7,C:0.3"> b) Te ríes y dices que todo es comercial. (+70% Caos, +30% Autenticidad)<br>
  <input type="radio" name="q1" value="A:0.5,K:0,C:0.5"> c) "Pues eso era, buenas noches". (+50% Estrategia, +50% Autenticidad)<br>
  <input type="radio" name="q1" value="A:0,K:1,C:-0.5"> d) Apuestas para demostrar tu punto. (+100% Caos, -50% Autenticidad)<br>

  <p><b>2. ¿Cuál es tu elección de comida cuando vas a un sitio nuevo?</b></p>
  <input type="radio" name="q2" value="E:0.3,C:0.2,A:0">Pizza prosciutto; en su defecto un filete empanao o el menu para niños<br>
  <input type="radio" name="q2" value="E:0,C:0.2,A:0.8">Una ensalada de semillas de chía con edamames y aguacate<br>
  <input type="radio" name="q2" value="E:0.6,C:0,A:0.4"> c) Algo gourmet para fardar<br>
  <input type="radio" name="q2" value="E:0,C:0.7,A:-0.3"><br>

  <!-- Más preguntas aquí siguiendo el mismo formato -->

  <br>
  <button type="button" onclick="calcularResultado()">Ver resultado</button>
</form>

<h2 id="resultado"></h2>

<script>
function calcularResultado() {
    let dimensiones = { Estrategia: 0, Caos: 0, Comercial: 0, Autenticidad: 0 };
    let preguntas = document.querySelectorAll('input[type="radio"]:checked');

    preguntas.forEach(p => {
        let valores = p.value.split(",");
        valores.forEach(v => {
            let [clave, valor] = v.split(":");
            dimensiones[clave] += parseFloat(valor);
        });
    });

    let resultadoTexto = `
      🔵 **Estrategia: ${(dimensiones.Estrategia * 100).toFixed(1)}%** vs. **Caos: ${(dimensiones.Caos * 100).toFixed(1)}%**<br>
      🟢 **Comercial: ${(dimensiones.Comercial * 100).toFixed(1)}%** vs. **Autenticidad: ${(dimensiones.Autenticidad * 100).toFixed(1)}%**
    `;

    document.getElementById("resultado").innerHTML = resultadoTexto;
}
</script>

