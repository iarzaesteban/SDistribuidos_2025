# Hit2

![Palmera](image.png)

## Aprende a pintar con matemáticas

El video muestra cómo crear imágenes mediante código y matemáticas, usando la plataforma ShaderToy, lo que permite ver cómo la computadora transforma números en colores y formas. Inicialmente habla sobre como generar patrones en shaderboy y como se maneja los arrays de pixeles. Explica cómo asignar colores a los píxeles manipulando sus coordenadas y utilizando distancias desde el centro de la pantalla, creando degradados circulares y horizontales.

Se usan funciones matematicas como smoothstep, coseno, seno, exponencial y raíz cuadrada para moldear transiciones, ondas, curvas y texturas naturales. Smoothstep es una funcion que se basa en la distancia de los pixels desde el centro y con eso va oscureciendo los pixeles para lograr las hojas de la palmera. Cos es una funcion que la usa para crear una imagen del tipo de una flor basandose en la funcion matematica del coseno para ir variando la distancia de los pixeles que se van osucreciendo desde el centro (o la amplitud). Se le puede dar un valor de frecuencia que indica la cantidad de petalos a generar. Basicamente tenemos propiedades que varian los tamaños y las frecuencias.
Se puede rotar los petalos y darles curvatura jugando con los parametros del coseno.

Se genera una palmera colocando un “canopy” con picos (coseno), un tronco usando distancias horizontales y formas onduladas, y finalmente se ancla al suelo con una exponencial. Hay herramientas para borrado de forma matematica, con la funcion over, por ej borrando los pixeles superiores del tronco, puedo hacer un borrado con suavizado pero en este caso era necesario que sea un valor absoluto para mostrar el tronco.

Se simula un fondo degradado que va de naranja a amarillo usando coordenadas verticales, enriquecido con raíz cuadrada para mantener el rojo en el horizonte. Sqrt permite bajar los colores naranjas hacia abajo, el px que valia 0.5 pasa a 0.7 aprox, hace los numeros mas grandes(que van entre 0-1) y hacen que sean mas amarillos y menos naranjas.
