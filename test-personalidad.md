---

layout: page
title: "Test de Personalidad Cumstatística"
---

## Test de Personalidad Cumstatística

**1. Alguien te dice que el póker es solo cuestión de azar. ¿Cómo reaccionas?**

- <input type="radio" name="q1" value="Estrategia:0.1,Comercial:-0.05"> a) Explicas que es un juego de estrategia.
- <input type="radio" name="q1" value="Caos:0.7,Autenticidad:0.3"> b) Te ríes y dices que todo es comercial.
- <input type="radio" name="q1" value="Estrategia:0.5,Autenticidad:0.5"> c) "Pues eso era, buenas noches".
- <input type="radio" name="q1" value="Caos:1,Autenticidad:-0.5"> d) Apuestas para demostrar tu punto.

**2. ¿Cuál es tu elección de comida cuando vas a un sitio nuevo?**

- <input type="radio" name="q2" value="Estrategia:0.3,Comercial:0.2"> a) Pizza prosciutto; en su defecto un filete empanao o menú infantil.
- <input type="radio" name="q2" value="Autenticidad:0.8,Comercial:0.2"> b) Una ensalada de semillas de chía con edamames y aguacate.
- <input type="radio" name="q2" value="Estrategia:0.6,Autenticidad:0.4"> c) Algo gourmet para fardar.
- <input type="radio" name="q2" value="Caos:0.7,Autenticidad:-0.3"> d) Lo más barato, preferiblemente grasiento.

<br>
<button type="button" onclick="calcularResultado()">Ver resultado</button>

## <span id="resultado"></span>

<script>
const cumstadisticos = [
  {nombre: "C", Estrategia: 0.9, Caos: 0.1, Comercial: 0.2, Autenticidad: 0.8},
  {nombre: "U", Estrategia: 0.2, Caos: 0.8, Comercial: 0.1, Autenticidad: 0.9},
  {nombre: "J", Estrategia: 0.5, Caos: 0.5, Comercial: 0.8, Autenticidad: 0.2}
];

function calcularResultado() {
  const dimensiones = { Estrategia: 0, Caos: 0, Comercial: 0, Autenticidad: 0 };
  const preguntas = document.querySelectorAll('input[type="radio"]:checked');

  preguntas.forEach(p => {
    const valores = p.value.split(",");
    valores.forEach(v => {
      const [clave, valor] = v.split(":");
      dimensiones[clave] += parseFloat(valor);
    });
  });

  const resultadoTexto = `
    🔵 <b>Estrategia: ${(dimensiones.Estrategia * 100).toFixed(1)}%</b> vs. <b>Caos: ${(dimensiones.Caos * 100).toFixed(1)}%</b><br>
    🟢 <b>Comercial: ${(dimensiones.Comercial * 100).toFixed(1)}%</b> vs. <b>Autenticidad: ${(dimensiones.Autenticidad * 100).toFixed(1)}%</b><br>
  `;

  let masCercano = cumstadisticos[0];
  let distanciaMin = Infinity;

  cumstadisticos.forEach(c => {
    const distancia = Math.sqrt(
      Math.pow(c.Estrategia - dimensiones.Estrategia, 2) +
      Math.pow(c.Caos - dimensiones.Caos, 2) +
      Math.pow(c.Comercial - dimensiones.Comercial, 2) +
      Math.pow(c.Autenticidad - dimensiones.Autenticidad, 2)
    );
    if (distancia < distanciaMin) {
      distanciaMin = distancia;
      masCercano = c;
    }
  });

  document.getElementById("resultado").innerHTML = resultadoTexto + `<br><b>Tu Cumstadístico más parecido es: ${masCercano.nombre}</b>`;
}
</script>
