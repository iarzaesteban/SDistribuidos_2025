
# Hit 1

## Tipos de Shaders

Existen tres tipos principales de shaders: píxel, vértice y geometrícos, aunque últimamente aparecieron algunos nuevos. Antes, las placas gráficas más viejas tenían unidades específicas para cada tipo de shader. Ahora, las más modernas usan shaders unificados que ejecutan cualquier tipo, aprovechando mejor el poder de procesamiento.

## Shaders en 2D

Los shaders en 2D laburan directamente sobre imágenes digitales, también conocidas como texturas en gráficos por computadora. Básicamente, modifican atributos de los píxeles. Hoy en día, el único shader 2D es el pixel shader.

## Pixel Shaders

Los Pixel Shaders (o fragment shaders) calculan colores y otras características para cada fragmento, que es como decir cada píxel individual de la pantalla. Los más simples apenas devuelven un color fijo, mientras que los más avanzados generan efectos como luces, sombras, reflejos o transparencia.

Estos shaders también pueden modificar la profundidad de los fragmentos (Z-buffering) o enviar varios colores a diferentes objetivos de renderizado. Aunque no pueden hacer solos efectos complejos de geometría (porque solo "ven" fragmentos individuales), sí conocen la coordenada de pantalla y pueden acceder a píxeles cercanos si toda la pantalla se les manda como textura. Eso permite efectos copados de postprocesado 2D, como desenfoques o detección de bordes estilo cartoon.

Además, los Pixel Shaders son los únicos capaces de actuar como filtros en imágenes o videos que ya fueron procesados, a diferencia de los shaders de vértice que siempre necesitan una escena 3D para operar.

---

## Pipeline de Renderizado

El pipeline de renderizado es el camino paso a paso que sigue una GPU para crear gráficos, especialmente cuando hablamos de gráficos 3D. Todo arranca con el Vertex Shader, donde cada vértice del modelo recibe transformaciones como rotaciones, escalados o desplazamientos para ubicarlos correctamente en la escena.

Después llega la Rasterización, que agarra esas figuras transformadas y las convierte en fragmentos. Cada fragmento es básicamente un píxel potencial con información como posición en la pantalla y otros datos que vienen interpolados desde los vértices originales.

Finalmente aparece el Fragment Shader o Pixel Shader, que toma esos fragmentos y decide exactamente qué color y textura les corresponde, incluso calculando efectos visuales avanzados como luces, sombras y reflejos. Esta etapa define realmente cómo va a lucir la imagen final.

En resumen, el pipeline es una cadena donde cada etapa usa como entrada lo que generó la anterior. Lo importante es que tanto el Vertex Shader como el Fragment Shader son programables, permitiendo personalizar cómo se ven finalmente los gráficos en pantalla.

> Podemos dividirlo en:

Etapas de procesamiento 3D:

- Vertex Shader: Transforma los vértices aplicando rotación, escala y traslación.

- Ensamblaje de primitivas: Agrupa vértices en figuras geométricas.

- Rasterización: Convierte esas figuras en fragmentos asociados a píxeles específicos.

Etapas de procesamiento 2D:

- Interpolación: Genera información intermedia entre vértices para cada fragmento.

- Fragment Shader (Pixel Shader): Aplica colores, texturas y efectos finales a cada fragmento.

- Operaciones finales: Realiza pruebas y combinaciones finales para mostrar la imagen definitiva.

De esta forma, el Pixel Shader es clave dentro del procesamiento 2D, brindando el aspecto final que ves en pantalla.

---

## Conceptos básicos de Post-processing

El post-processing (post-procesado) es una técnica utilizada para mejorar la calidad visual de imágenes o videos después de que ya se renderizó todo lo inicial. Incluye cosas como suavizar bordes (anti-aliasing), agregar desenfoques (blur), correcciones de color, efectos de bloom, profundidad de campo y otros efectos visuales avanzados.

En gráficos 3D, sobre todo en videojuegos, el post-processing se aplica cuando la escena ya está renderizada en un buffer intermedio en la memoria de la placa gráfica. Esto permite meter efectos que necesitan saber cómo quedó toda la imagen final, y no solo de los objetos individuales como en etapas anteriores del renderizado.

¿En qué momento del Pipeline se usa el Post-processing?

El post-processing entra justo después del Fragment Shader (Pixel Shader) en el pipeline de renderizado. Tras completar todas las operaciones de renderizado estándar, la imagen ya generada pasa por diversos filtros o efectos adicionales antes de finalmente mostrarse en pantalla. Estos efectos pueden incluir múltiples pasos de procesamiento, manipulación de vértices, y acceso al buffer de profundidad, aportando mejoras significativas al aspecto visual final.

---

![shadertoy](image-1.png)

## Entradas de shader

Algunas nuevas entradas personalizadas para ShaderToy son las mostradas debajo, que podrían resultar útiles para crear shaders más complejos:

```bash
uniform float iAudioAmplitude;
```

Representa la amplitud del audio en reproducción, permitiendo sincronizar efectos visuales con sonido.

```bash
uniform vec3 iAcceleration;
```

Aceleración del dispositivo (en móviles o controles con sensores), útil para efectos responsivos basados en movimiento.

```bash
uniform vec3 iGyroscope;
```

Rotación actual del dispositivo, ideal para efectos visuales que reaccionan al giro o inclinación.

```bash
uniform float iBatteryLevel;
```

Nivel actual de batería del dispositivo, que permitiría generar efectos que reflejen visualmente el estado de carga.

```bash
uniform float iNetworkSpeed;
```

Velocidad actual de la conexión a internet, útil para shaders que cambian calidad visual en función de la velocidad de carga de datos.

```bash
uniform vec4 iGeoLocation;
```

Coordenadas geográficas actuales del usuario (latitud, longitud, altitud y precisión), permitiendo crear visualizaciones geolocalizadas.

```bash
uniform float iTemperature;
```

Temperatura actual del CPU o GPU, lo que podría afectar efectos gráficos como simulaciones térmicas o metáforas visuales de calor.

---

## Salidas de Pixel Shaders (ShaderToy)

A continuacion se muestra el listado con las salidas posibles de los Pixel Shaders según ShaderToy.

> Shaders de Imagen (2D)

Tipo: out vec4 fragColor

Acá se manda el color final del píxel. El color es un vector con cuatro componentes: rojo, verde, azul y alfa (transparencia). En ShaderToy, el valor alfa hoy en día se ignora, pero queda reservado por si en el futuro meten cosas nuevas.

> Shaders de Sonido

Tipo: vec2 mainSound(float time)

El shader genera audio con una salida estéreo. Devuelve dos valores, uno para el canal izquierdo y otro para el derecho. Cada valor representa la amplitud de la onda sonora en ese momento exacto del tiempo, ideal para hacer sonidos copados sincronizados con los gráficos.

> Shaders para Realidad Virtual (VR)

Tipo: out vec4 fragColor

Similar al shader de imagen, devuelve el color final para cada píxel. La diferencia es que además recibe información sobre la dirección y el origen del rayo (raytracing), que permite generar gráficos tridimensionales inmersivos para sistemas de realidad virtual.

Resumiendo...

Imagen: Salís con colores para pintar en pantalla.

Sonido: Salís con amplitudes para audio estéreo.

VR: Salís con colores, pero usando información espacial (rayos) para 3D en realidad virtual.

---

## Shader “hello world” de ShaderToy

Este documento explica en profundidad el siguiente shader de ejemplo que se sugiere al crear un nuevo ShaderToy:

```glsl
void mainImage( out vec4 fragColor, in vec2 fragCoord ) {
  // Normalized pixel coordinates (from 0 to 1)
  vec2 uv = fragCoord/iResolution.xy;

  // Time varying pixel color
  vec3 col = 0.5 + 0.5*cos(iTime+uv.xyx+vec3(0,2,4));

  // Output to screen
  fragColor = vec4(col,1.0);
}
```

A continuación, se detalla cada parte del shader respondiendo a los siguientes puntos:

### 1. La Función Principal y sus Parámetros

El shader se inicia con la función:

```glsl
void mainImage( out vec4 fragColor, in vec2 fragCoord )
```

- fragColor (out vec4):
Es la salida que le asignamos al píxel. Va a llevar el color final en formato RGBA (rojo, verde, azul y alfa). En este ejemplo se usa alfa = 1.0 (total opacidad).

- fragCoord (in vec2):
Son las coordenadas reales (en píxeles) del píxel actual. Por ejemplo, si la pantalla tiene 800×600 píxeles, fragCoord tendrá valores entre aproximadamente 0.5 y 799.5 en el eje X y entre 0.5 y 599.5 en el eje Y.

### 2.¿Qué representa uv y Por qué trabajar en “uv” y no directamente en “xy”?

La línea que hay que analizar es:

```glsl
vec2 uv = fragCoord / iResolution.xy;
```

Que representa uv: se genera un vector de dos componentes (uv) que contiene las coordenadas del píxel, pero normalizadas entre 0 y 1. Es decir, sin importar el tamaño en píxeles de la pantalla, el valor en uv.x va a estar entre 0 y 1 (0 representa la izquierda y 1 la derecha) y lo mismo para uv.y (0 es abajo y 1 es arriba).

¿Por qué trabajar en uv y no en xy?:

Usar coordenadas normalizadas permite que los efectos sean resolution-independent (independientes de la resolución). Esto significa que el shader se comporta igual, sea cual sea la cantidad de píxeles de la pantalla, facilitando cálculos, escalados y logrando que los efectos visuales se mantengan coherentes en distintos dispositivos.

### 3.Generación de Animación con Entradas “Estáticas”

```glsl
vec3 col = 0.5 + 0.5*cos(iTime + uv.xyx + vec3(0,2,4));
```

Aunque puede parecer que las entradas son “estáticas”, la animación se logra gracias a iTime, una variable uniforme que representa el tiempo transcurrido en segundos. Como el valor de iTime se actualiza constantemente en cada frame, la función cos() cambia su valor de forma continua. Al sumar iTime a las coordenadas normalizadas se genera un patrón que varía con el tiempo, creando la animación.

### 4.¿Cómo puede col ser un vec3 si está igualado a una operación aritmética entre flotantes?

En GLSL se permite la promoción implícita de escalares a vectores cuando operás entre distintos tipos, siempre que se trate de operaciones componente a componente. Por ejemplo: El literal 0.5 se transforma automáticamente en vec3(0.5, 0.5, 0.5) cuando se suma a un vector. La función cos() es aplicada de forma componentwise: si le pasás un vec3, devuelve un vec3 con la función coseno aplicada a cada componente.

Por eso, la operación

```glsl
0.5 + 0.5 * cos(...)
```

Se interpreta en cada componente del vector, haciendo que col sea un vec3 con sus componentes calculadas individualmente.

### 5.Constructores para vec4 y la Salida fragColor

En GLSL, los constructores para tipos vectoriales son flexibles. En un vec4 se puede asignar el mismo valor a a los cuatro componentes, ej.: vec4(0.5) es lo mismo que (0.5, 0.5, 0.5, 0.5).

En nuestro caso, al hacer fragColor = vec4(col, 1.0); se toma el vec3 col y se le agrega 1.0 como el componente alfa, formando el color final, y formando un vec4.

### 6.El Swizzling y Propiedades de Vectores: ¿Qué es uv.xyx y qué otras propiedades tienen?

Swizzling (uv.xyx):
En GLSL los vectores permiten swizzling, que es la forma de reordenar o duplicar sus componentes. uv es un vec2 con componentes x e y. Al escribir uv.xyx se crea un nuevo vec3 donde: El primer componente es uv.x, el segundo es uv.y, el tercero es nuevamente uv.x.
El swizzling te permite manipular y reorganizar los datos de manera muy práctica sin crear variables adicionales ni hacer conversiones explícitas.