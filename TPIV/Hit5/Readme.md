# Hit #5 - Shader Chroma Key

## Conceptos Aplicados

1. **Color de chroma**: definimos el verde chroma como `vec3(0.1, 1.0, 0.1)`
2. **Umbral de distancia**: usamos `distance(vec3, vec3)` para comparar el color de un píxel con el verde chroma.
3. **Función `smoothstep`**: para suavizar la transición entre foreground (Britney) y background (webcam).
4. **Combinación de imágenes**: con `mix` interpolamos entre foreground y background usando el `alpha` calculado.

## Pruebas y Ajustes

Probamos con distintos valores de **`threshold`** y observamos:

| Threshold | Resultado                                 |
| --------- | ----------------------------------------- |
| 0.3       | Fondo verde casi no se elimina            |
| 0.4       | Se empieza a ver el fondo, pero con ruido |
| 0.6       | Fondo eliminado con bordes aceptables     |
| 0.8       | Britney se empieza a recortar demasiado   |

También se agregó un valor `slope = 0.1` para suavizar la transición con `smoothstep`.

## Configuración en Shadertoy

- `iChannel0`: Webcam (video en vivo)
- `iChannel1`: Video de Britney Spears con fondo verde

## Experiencia

¡El filtro funcionó muy bien! Fue divertido ver cómo la cámara en vivo se mezcla con el fondo del videoclip. Modificar el umbral y experimentar con colores fue clave para obtener un buen resultado.

## Conclusión

Este shader muestra cómo se pueden aplicar conceptos simples de geometría y blending para lograr un efecto visual muy usado en televisión y cine. La combinación de `distance` + `smoothstep` + `mix` da un resultado muy satisfactorio.
